"""The implementer's receipt: printed from git, and checked against git when the agent stops.

  python -X utf8 -I tools/hooks/receipt.py --print --base <rev> --package <name>
      prints the receipt block for the checkout in the current directory; the agent fills in
      `gates`, `state`, `hooks in others' files` and `proposed text`, and pastes it last.
  receipt.py --check        (the implementer's Stop hook; the hook input on stdin)
      refuses (exit 2, "receipt refused:") a final message without a receipt, or whose branch,
      head, base, status, commits or signatures differ from git's.

ddon-data (ported from ddon-hook 4c625de): role agents share the main checkout, which holds other
work, so `status` covers only the files the receipt's commits touch, not the whole tree. A second stop in a row
      (`stop_hook_active`) and any internal failure let the agent stop (exit 0).

The block:
    ## Receipt <package>
    - branch: <branch>   head: <sha>
    - base: <sha>   status: clean   (the files the commits touch have no uncommitted changes)
    - commits:
      - <sha> <subject>
    - signed: <n>/<n>
    - gates: <command: result, one per gate>
    - state: done | cut short: <what is left>
    - hooks in others' files: none | <file: lines>
    - proposed text: none | <for coordinator-owned files>
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402

HEX = re.compile(r"^[0-9a-f]{7,40}$")
REFUSED = "receipt refused:"
IGNORED_STATUS = (".claude/settings.local.json",)


def git(cwd, *args):
    run = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=30)
    if run.returncode != 0:
        raise RuntimeError(run.stderr.strip() or f"git {' '.join(args)} failed")
    return run.stdout


def identity(cwd, base):
    """git's view: branch, head, resolved base, dirty paths, commits (sha, subject), signature codes."""
    branch = git(cwd, "rev-parse", "--abbrev-ref", "HEAD").strip()
    head = git(cwd, "rev-parse", "HEAD").strip()
    base_sha = git(cwd, "rev-parse", "--verify", f"{base}^{{commit}}").strip()
    touched = [p for p in git(cwd, "diff", "--name-only", f"{base_sha}..HEAD").splitlines() if p]
    status = [line for line in git(cwd, "status", "--porcelain", "--", *touched).splitlines()
              if line and not line[3:].strip().endswith(IGNORED_STATUS)] if touched else []
    log = git(cwd, "log", "--format=%H %G? %s", f"{base_sha}..HEAD").splitlines()
    commits = [(line.split(" ", 2)[0], line.split(" ", 2)[2] if line.count(" ") >= 2 else "") for line in log]
    signatures = [line.split(" ", 2)[1] for line in log]
    return {"branch": branch, "head": head, "base": base_sha, "status": status, "commits": commits,
            "signatures": signatures}


def render(package, ident):
    signed = sum(code in ("G", "U") for code in ident["signatures"])
    status = "clean" if not ident["status"] else f"{len(ident['status'])} dirty paths"
    lines = [f"## Receipt {package}",
             f"- branch: {ident['branch']}   head: {ident['head'][:10]}",
             f"- base: {ident['base'][:10]}   status: {status}",
             "- commits:"]
    lines += [f"  - {sha[:10]} {subject}" for sha, subject in ident["commits"]] or ["  - none"]
    lines += [f"- signed: {signed}/{len(ident['commits'])}",
              "- gates: <command: result, one per gate>",
              "- state: done",
              "- hooks in others' files: none",
              "- proposed text: none"]
    return "\n".join(lines)


def parse(message):
    """The claimed fields of the last receipt block in `message`, or None."""
    at = message.rfind("## Receipt")
    if at < 0:
        return None
    block = message[at:]
    claimed = {"commits": []}
    in_commits = False
    for line in block.splitlines()[1:]:
        if line.startswith("  - ") and in_commits:
            sha = line[4:].split(" ", 1)[0]
            if sha != "none":
                claimed["commits"].append(sha)
            continue
        in_commits = False
        if not line.startswith("- "):
            continue
        in_commits = line.startswith("- commits:")
        if in_commits:
            continue
        for part in re.split(r"\s{2,}", line[2:].strip()):
            key, _, value = part.partition(":")
            claimed[key.strip().lower()] = value.strip()
    return claimed


def problems(claimed, ident):
    found = []
    if claimed.get("branch") != ident["branch"]:
        found.append(f"branch: the receipt says {claimed.get('branch')!r}, git {ident['branch']}")
    for key in ("head", "base"):
        value = claimed.get(key, "")
        if not (HEX.match(value) and ident[key].startswith(value)):
            found.append(f"{key}: the receipt says {value or 'nothing'!r}, git {ident[key][:10]}")
    if ident["status"]:
        found.append(f"status: files your commits touch have uncommitted changes ({'; '.join(ident['status'][:5])}): "
                     f"commit or revert them")
    elif claimed.get("status", "").lower() != "clean":
        found.append(f"status: the receipt says {claimed.get('status')!r}, git clean")
    actual = [sha for sha, _ in ident["commits"]]
    shas = claimed["commits"]
    if len(shas) != len(actual) or not all(HEX.match(s) and a.startswith(s) for s, a in zip(shas, actual)):
        found.append(f"commits: the receipt lists {shas}, git {[a[:10] for a in actual]}")
    unsigned = [sha[:10] for (sha, _), code in zip(ident["commits"], ident["signatures"]) if code in ("N", "B")]
    if unsigned:
        found.append(f"unsigned or badly signed commits: {', '.join(unsigned)} (stop and report blocked:signing)")
    if not claimed.get("gates") or claimed["gates"].startswith("<"):
        found.append("gates: name each gate's command and result")
    return found


def check(data):
    """0 lets the agent stop, 2 refuses its final message."""
    if data.get("stop_hook_active"):
        return 0
    message = data.get("last_assistant_message")
    if not isinstance(message, str):
        return 0  # this Claude Code version does not pass the message: fail open
    claimed = parse(message)
    if claimed is None:
        print(f"{REFUSED} end your final message with the receipt block: run "
              f"`python -X utf8 -I {Path(__file__).as_posix()} --print --base <base> --package <name>` "
              f"and fill in gates and state.", file=sys.stderr)
        return 2
    base = claimed.get("base", "")
    if not HEX.match(base):
        print(f"{REFUSED} base {base!r} is not a commit id", file=sys.stderr)
        return 2
    ident = identity(data.get("cwd") or ".", base)
    found = problems(claimed, ident)
    if found:
        print(f"{REFUSED} the receipt differs from git:\n- " + "\n- ".join(found), file=sys.stderr)
        return 2
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--print", action="store_true", dest="print_")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--base")
    parser.add_argument("--package", default="<package>")
    args = parser.parse_args()
    if args.check:
        data = hooklib.read_input()
        return check(data) if data else 0
    if args.print_ and args.base:
        print(render(args.package, identity(Path.cwd(), args.base)))
        return 0
    parser.print_usage(sys.stderr)
    return 1


if __name__ == "__main__":
    if "--check" in sys.argv:
        hooklib.fail_open(main)
    sys.exit(main())

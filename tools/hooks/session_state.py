"""The coordinator's state across a compaction, and the instructions its subagents get (002 P2,
ported from the reconstructor's tools/hooks/session_state.py without its worktree and train parts).
One script, one mode per hook event (`.claude/settings.json`):

- `start` (SessionStart, every source; the main session only, a subagent's input carries `agent_id`):
  - records the hash and text of `AGENTS.md`, `CLAUDE.md` and `~/.claude/CLAUDE.md` in
    `.agent-ledger/loaded-instructions.json`: the copy the session loaded, which its subagents get too;
  - after a compaction or a resume (`source` `compact` or `resume`), returns as `additionalContext`
    `tools/orchestration/progress.py`'s block, the `## Running` section and the last `Next:` line of
    each open feature's `tasks.md` (progress.py's discovery), and `git status --short -- tools specs
    .claude` (cut at STATUS_LINES lines; never `client/` or `packets/`).
- `precompact` (PreCompact; the main session only): copies each brief of the session's scratchpad
  (`<scratchpad>/briefs/*.md`) into the brief folder (`briefs/`) of the active feature when no file
  of that name exists there. It copies only, never deletes. The active feature is the open feature
  under the root `specs/` that `.specify/feature.json` names, else the only open one there; with
  none or several, nothing is copied.
- `subagent` (SubagentStart): when an instruction file on disk differs from the recorded copy,
  returns the unified diff (cut at DIFF_CAP characters) as `additionalContext`.

Reads the hook input (JSON) on stdin. Every failure exits 0 silently: a hook never stops the
session it informs. `HOOK_ROOT`, `HOOK_HOME` and `HOOK_SCRATCHPAD` replace the paths in tests.
"""

import datetime as dt
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ORCHESTRATION = Path(__file__).resolve().parents[1] / "orchestration"

DIFF_CAP = 12_000
SECTION_CAP = 3_000
STATUS_LINES = 40
NEXT = re.compile(r"^.*\bNext:.*$", re.M)


def root():
    return Path(os.environ.get("HOOK_ROOT") or Path(__file__).resolve().parents[2])


def instruction_files():
    home = Path(os.environ.get("HOOK_HOME") or Path.home())
    return [root() / "AGENTS.md", root() / "CLAUDE.md", home / ".claude" / "CLAUDE.md"]


def record_path():
    return root() / ".agent-ledger" / "loaded-instructions.json"


def main_session(data):
    return not data.get("agent_id")


def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def record(data):
    """Writes the loaded copy of each instruction file (a missing file is recorded as absent)."""
    files = {}
    for path in instruction_files():
        text = read_text(path)
        files[path.as_posix()] = None if text is None else {"sha256": hashlib.sha256(text.encode()).hexdigest(), "text": text}
    body = {"recorded_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"), "session_id": data.get("session_id"),
            "source": data.get("source"), "files": files}
    target = record_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(body, indent=1), encoding="utf-8")
    temporary.replace(target)


def stale_diff():
    """The unified diff of each instruction file whose text on disk differs from the recorded one
    ('' when none does, or nothing was recorded), cut at DIFF_CAP characters."""
    try:
        loaded = json.loads(record_path().read_text(encoding="utf-8"))["files"]
    except (OSError, ValueError, KeyError):
        return ""
    parts = []
    for name, entry in loaded.items():
        now = read_text(name)
        before = None if entry is None else entry.get("text")
        if now == before:
            continue
        parts.extend(difflib.unified_diff((before or "").splitlines(keepends=True), (now or "").splitlines(keepends=True),
                                          fromfile=f"{name} (loaded)", tofile=f"{name} (on disk)", n=1))
    text = "".join(parts)
    if len(text) > DIFF_CAP:
        text = text[:DIFF_CAP] + f"\n[the diff is cut at {DIFF_CAP} characters: Read the files named above for the rest]\n"
    return text


def run(argv, timeout=60):
    try:
        done = subprocess.run(argv, cwd=root(), capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=timeout, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as error:
        return f"({Path(argv[-1]).name}: {error})"
    return done.stdout.strip() or f"({' '.join(argv[-2:])}: exit {done.returncode}, no output)"


def open_features():
    """progress.py's open features (folders relative to root()); imported here, inside main's guard."""
    if str(ORCHESTRATION) not in sys.path:
        sys.path.insert(0, str(ORCHESTRATION))
    import progress  # noqa: PLC0415
    return [folder for folder, _, _ in progress.features(root())]


def running_and_next(text):
    """The `## Running` section (up to the next `## ` heading) and the last `Next:` line of a tasks.md."""
    lines, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() == "## Running"
            continue
        if inside:
            lines.append(line)
    section = "\n".join(lines).strip() or "(no ## Running section)"
    if len(section) > SECTION_CAP:
        section = section[:SECTION_CAP] + f"\n[cut at {SECTION_CAP} characters]"
    found = NEXT.findall(text)
    return section, (found[-1].strip() if found else "(no Next: line)")


def git_status():
    lines = run(["git", "status", "--short", "--", "tools", "specs", ".claude"]).splitlines()
    if len(lines) > STATUS_LINES:
        lines = lines[:STATUS_LINES] + [f"[{len(lines) - STATUS_LINES} more lines: run git status --short -- tools specs .claude]"]
    return "\n".join(lines) or "(clean)"


def resume_block():
    """The state after a compaction or a resume: progress, each open feature's Running and Next, git status."""
    script = root() / "tools" / "orchestration" / "progress.py"
    parts = ["State after the compaction (tools/hooks/session_state.py); trust this over the summary where they differ.",
             "## Progress", run([sys.executable, "-X", "utf8", "-I", str(script)])]
    quiet = []
    for folder in open_features():
        text = read_text(root() / folder / "tasks.md") or ""
        if "## Running" not in text and not NEXT.search(text):
            quiet.append(f"- {folder}")
            continue
        section, upcoming = running_and_next(text)
        parts += [f"## {folder}/tasks.md: Running", section, f"last {upcoming}"]
    if quiet:
        parts += ["## Open features with no ## Running section and no Next: line", "\n".join(quiet)]
    parts += ["## git status --short -- tools specs .claude", git_status()]
    return "\n\n".join(parts)


def active_feature():
    """The open root feature `.specify/feature.json` names, else the only open root feature, else None."""
    candidates = [f for f in open_features() if f.startswith("specs/")]
    try:
        named = json.loads((root() / ".specify" / "feature.json").read_text(encoding="utf-8"))["feature_directory"]
        named = Path(named).as_posix().removeprefix(root().as_posix() + "/")
    except (OSError, ValueError, KeyError, TypeError):
        named = None
    if named in candidates:
        return named
    return candidates[0] if len(candidates) == 1 else None


def scratchpad(data):
    given = os.environ.get("HOOK_SCRATCHPAD")
    if given:
        return Path(given)
    slug = re.sub(r"[^A-Za-z0-9-]", "-", str(Path(data.get("cwd") or root())))
    return Path(tempfile.gettempdir()) / "claude" / slug / str(data.get("session_id") or "") / "scratchpad"


def copy_briefs(data):
    """Copies the scratchpad's briefs the active feature lacks; returns (feature, names copied)."""
    feature = active_feature()
    source = scratchpad(data) / "briefs"
    known = data.get("session_id") or os.environ.get("HOOK_SCRATCHPAD")
    if not feature or not known or not source.is_dir():
        return feature, []
    target = root() / feature / "briefs"
    copied = []
    for brief in sorted(source.glob("*.md")):
        if not (target / brief.name).exists():
            target.mkdir(parents=True, exist_ok=True)
            shutil.copy2(brief, target / brief.name)
            copied.append(brief.name)
    return feature, copied


def context(event, text):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))


def main(mode):
    data = json.load(sys.stdin)
    if not isinstance(data, dict):
        return
    if mode == "subagent":
        diff = stale_diff()
        if diff:
            context("SubagentStart", "The instruction files changed after the coordinator loaded them, so your "
                    "copy of AGENTS.md or CLAUDE.md is stale where this diff shows; the files on disk hold the "
                    "current rules:\n\n" + diff)
        return
    if not main_session(data):
        return
    if mode == "start":
        record(data)
        if data.get("source") in ("compact", "resume"):
            context("SessionStart", resume_block())
    elif mode == "precompact":
        feature, copied = copy_briefs(data)
        if copied:
            print(json.dumps({"systemMessage": f"session_state: copied {len(copied)} pending briefs into "
                              f"{feature}/briefs: " + ", ".join(copied)}))


if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) > 1 else "")
    except Exception:  # noqa: BLE001 - a hook must never stop the session it informs
        pass
    sys.exit(0)

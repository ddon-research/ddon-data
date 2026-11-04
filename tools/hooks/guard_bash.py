"""PreToolUse guard for the Bash and PowerShell tools.

Enforces AGENTS.md's shell and git rules for every session and role agent, instead of relying on
the prompt. Each refusal names the replacement:
- `grep`/`egrep`/`fgrep` -> `rg`; `find` -> `fd`; `du` -> `dust`; `Select-String -Path` -> `rg`;
- `sed -i` (strips CRs from CRLF files) -> the Edit tool or `sd -F`;
- `cat FILE | head`/`tail` -> the Read tool with offset/limit, `rg -m N`, or `sed -n 'A,Bp'`;
- `sd` with a newline in its pattern but without `-A` (matches nothing, exits 0);
- unsigned or unverified commits (`--no-gpg-sign`, `-c commit.gpgsign=false`, `--no-verify`,
  `commit -n`);
- blanket staging (`git add -A|--all|.|:/`, bare `git add -u`, `git commit -a`, a directory without
  `--`): stage explicit paths, or owned folders as `git add -- <dir> <dir>` (at most MAX_FOLDERS,
  never the checkout, a parent of it or a glob; T020);
- `--pathspec-from-file` (quadratic against the 437k-entry index): `git update-index --add --remove
  -z --stdin` instead (T020);
- a `git commit` without `-- <paths>` (or with `-i`) while the index holds staged paths the same
  command line does not `git add`: other sessions' staged work would ride along (T017);
- forced or deleting pushes, and pushes of any branch other than the current one;
- polling: a `while`/`until` loop around `sleep`, or a wait-and-look command (sleep, date, process
  lists, `tail`) again within 60 s from the same agent: use `run_in_background` and end the turn.

ddon-data additions (AGENTS.md "Preservation and git hygiene"; ported from ddon-hook 4c625de):
- `git worktree add` (the repository is too large for worktrees; agents share the main checkout);
- unbounded output over the large trees (`client/`, `packets/`, except the small hand-authored subtrees
  of SMALL_SUBTREES): `git diff`/`git log -p` without a
  summary flag and with no pathspec or one in a large tree, `ls -R`/`tree`/`fd`/`rg --files`/
  `git ls-files` there without a depth or count bound, and `rg` content searches there without
  `-c`/`-l`/`-m`/`-q`;
- bulk reverts: `git checkout -- <dir|.>`, `git restore <dir|.>`, `git rm -r`: list exact paths and
  ask the user first.

The parsing is best effort (shlex over the command line, heredoc bodies dropped). Exit 2 refuses.
"""

import hashlib
import os
import posixpath
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hooklib  # noqa: E402

POLL_GAP_S = 60
SEPARATORS = {";", "&&", "||", "&", "\n"}
PIPES = {"|", "|&"}
WRAPPERS = {"timeout", "env", "command", "nice", "nohup", "time", "xargs", "exec", "builtin"}
SEARCHERS = {"grep", "egrep", "fgrep"}
READERS = {"cat", "get-content", "gc", "type"}
PAGERS = {"head", "tail"}
WAITS = {"sleep", "start-sleep", "wait", "wait-process", "wait-job", "wait-event"}
PROBES = WAITS | {"date", "get-date", "uptime", "tasklist", "ps", "get-process", "tail"}
LOOPS = {"while", "until"}
COMMIT_VALUED = set("mFCct")
MAX_FOLDERS = 5


def without_heredocs(command):
    """`command` with each heredoc body removed (it is data)."""
    out, lines, i = [], command.splitlines(), 0
    while i < len(lines):
        out.append(lines[i])
        match = re.search(r"<<-?\s*(['\"]?)(\w+)\1", lines[i])
        i += 1
        if match:
            while i < len(lines) and lines[i].strip() != match.group(2):
                i += 1
            i += 1
    return "\n".join(out)


def mark_quoted_newlines(text):
    """`text` with each newline inside quotes replaced by NUL, so the others can separate commands."""
    out, quote, escaped = [], None, False
    for char in text:
        if escaped:
            escaped = False
        elif char == "\\" and quote != "'":
            escaped = True
        elif quote is None and char in "'\"":
            quote = char
        elif char == quote:
            quote = None
        elif char == "\n" and quote:
            char = "\x00"
        out.append(char)
    return "".join(out)


def tokens(command):
    text = mark_quoted_newlines(without_heredocs(command)).replace("\n", " ; ")
    lexer = shlex.shlex(text, posix=True, punctuation_chars=";&|()")
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        return list(lexer)
    except ValueError:  # unbalanced quotes: split crudely rather than let the command through
        return re.sub(r"([;&|()]+)", r" \1 ", text).split()


def pipelines(command):
    """The command line as a list of pipelines, each a list of stages (word lists)."""
    out, pipeline, stage = [], [], []
    for token in tokens(command):
        if token in PIPES:
            pipeline.append(stage)
            stage = []
        elif token in SEPARATORS or token in ("(", ")") or set(token) <= set(";&|()"):
            if stage:
                pipeline.append(stage)
            if pipeline:
                out.append(pipeline)
            pipeline, stage = [], []
        else:
            stage.append(token)
    if stage:
        pipeline.append(stage)
    if pipeline:
        out.append(pipeline)
    return [[unwrapped(s) for s in p] for p in out]


def name_of(word):
    name = Path(word.replace("\\", "/")).name.lower()
    return name[:-4] if name.endswith(".exe") else name


def unwrapped(words):
    """`words` without leading `VAR=x` assignments and wrappers (`timeout 60 grep ...` -> grep)."""
    i = 0
    while i < len(words):
        word = words[i]
        if "=" in word and word.split("=", 1)[0].isidentifier():
            i += 1
            continue
        if name_of(word) in WRAPPERS:
            i += 1
            while i < len(words) and (words[i].startswith("-") or re.fullmatch(r"[\d.]+[smhd]?", words[i])):
                i += 1
            continue
        break
    return words[i:]


def check_tools(stages, shell):
    for index, words in enumerate(stages):
        if not words:
            continue
        name = name_of(words[0])
        if name in SEARCHERS:
            return f"`{name}` is not used here: use `rg` (`rg -F` for literals, `rg -n -m N` to bound output; `git grep -n` for tracked files)."
        if name == "find" and shell == "bash":
            return "`find` is not used here: use `fd` (`fd -e cpp . src`, `fd -H -I` for ignored files) or `rg --files -g GLOB`."
        if name == "find":
            return "`find.exe` is not used here: use `rg` to search text or `fd` to find files."
        if name in ("select-string", "sls") and any(w.lower() in ("-path", "-literalpath") for w in words):
            return "`Select-String -Path` is not used here: use `rg` from Git Bash."
        if name == "du":
            return "`du` is not used here: use `dust` (`dust -b -d 1 DIR`)."
        if name == "sed" and any(w.startswith("--in-place") or (w.startswith("-") and not w.startswith("--") and "i" in w[1:]) for w in words[1:]):
            return "`sed -i` strips the CRs of CRLF files: use the Edit tool, or `sd -F 'old' 'new' FILE` for a one-line literal."
        if name in READERS and index + 1 < len(stages) and stages[index + 1]:
            following = name_of(stages[index + 1][0])
            first_last = following in ("select-object", "select") and any(
                w.lower() in ("-first", "-last") for w in stages[index + 1])
            if following in PAGERS or first_last:
                return ("`cat FILE | head/tail` is not used here: use the Read tool with offset/limit, `rg -n -m N PAT FILE`, "
                        "or `sed -n 'A,Bp' FILE`.")
    return None


def check_sd(command):
    for stages in pipelines(command):
        for words in stages:
            if not words or name_of(words[0]) != "sd":
                continue
            flags = [w for w in words[1:] if w.startswith("-") and w != "--"]
            across = any(w == "--across" or (not w.startswith("--") and "A" in w[1:]) for w in flags)
            rest = [w for w in words[1:] if not w.startswith("-")]
            if rest and "\x00" in rest[0] and not across:
                return "`sd` matches line by line: a pattern with a newline matches nothing unless you pass `-A`. Use the Edit tool for multi-line edits."
    return None


def native_path(path):
    """`/d/x` (Git Bash) as `D:/x`, the directory the shell means; Windows Python reads it as `\\d\\x`."""
    match = re.fullmatch(r"/([a-zA-Z])(/.*)?", path)
    return f"{match[1].upper()}:{match[2] or '/'}" if os.name == "nt" and match else path


def entered(words, cwd):
    """The directory after this command: `cd <dir>` moves the rest of the line; `$VAR` and `cd -` stay unknown."""
    if len(words) == 2 and name_of(words[0]) == "cd" and "$" not in words[1] and words[1] != "-":
        return str(Path(cwd) / native_path(words[1]))
    return cwd


def git_parts(words, cwd):
    settings, directory, i = [], cwd, 1
    while i < len(words) and words[i].startswith("-"):
        option = words[i]
        if option in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") and i + 1 < len(words):
            if option == "-c":
                settings.append(words[i + 1].replace(" ", "").lower())
            if option == "-C":
                directory = str(Path(directory) / native_path(words[i + 1]))
            i += 2
        else:
            i += 1
    if i >= len(words):
        return settings, directory, None, []
    return settings, directory, words[i], words[i + 1:]


def current_branch(directory):
    try:
        run = subprocess.run(["git", "-C", directory, "rev-parse", "--abbrev-ref", "HEAD"],
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return run.stdout.strip() if run.returncode == 0 else None


def short_flags(arguments, valued):
    """The short flag letters before the first `--`, skipping the values of valued options."""
    letters, i = [], 0
    while i < len(arguments):
        word = arguments[i]
        if word == "--":
            break
        if word.startswith("-") and not word.startswith("--") and len(word) > 1:
            for at, letter in enumerate(word[1:]):
                letters.append(letter)
                if letter in valued:
                    if at == len(word) - 2:
                        i += 1  # the value is the next word
                    break
        i += 1
    return letters


def after_dashdash(arguments):
    """The words after the first `--`, or None when there is no `--`."""
    return arguments[arguments.index("--") + 1:] if "--" in arguments else None


def check_add(directory, arguments):
    """Blanket staging is refused; owned folders are staged as `git add -- <dir> ...` (T020)."""
    blanket = {"-A", "--all", ".", "./", ":/", ":", "*", "--no-ignore-removal"}
    letters = short_flags(arguments, set())
    paths = after_dashdash(arguments)
    if blanket & set(arguments) or "A" in letters:
        return "Blanket staging (`git add -A`, `.`, `-u`) is not used here: stage the change's explicit paths (this worktree holds other people's dirty work)."
    if ("u" in letters or "--update" in arguments) and not paths:
        return ("Bare `git add -u` stages every tracked change in the checkout, other people's included: name the "
                "paths after `--` (`git add -u -- <dir>`).")
    # A directory stages every dirty and untracked file under it (2026-10-17, ddon-hook: `git add specs`
    # swept 377 files of other work into a commit). After `--` it is a deliberate folder pathspec for a
    # folder the brief owns (T020, 005 P6: 290k literal paths took 45 min), allowed up to MAX_FOLDERS.
    base = Path(directory or ".")
    if paths is None:
        named = [word for word in arguments if not word.startswith("-")]
        folders = [path for path in named if (base / path).is_dir()]
        if folders:
            return (f"`git add {folders[0]}` stages a whole directory, including other people's dirty and untracked "
                    f"files: stage the change's explicit file paths, or, for folders your brief owns, "
                    f"`git add -- {folders[0]}` (at most {MAX_FOLDERS} folders).")
        return None
    folders = [path for path in paths if (base / path).is_dir()]
    try:
        here = base.resolve()
        broad = [path for path in folders if (base / path).resolve() in (here, *here.parents)]
    except OSError:
        broad = []
    if broad or any(any(ch in path for ch in "*?[") or path.startswith(":") for path in paths):
        return ("`git add --` takes owned folders or files, never the checkout itself, a parent of it, a glob or a "
                "magic pathspec: name the folders your brief owns.")
    if len(folders) > MAX_FOLDERS:
        return (f"`git add --` with {len(folders)} folders: at most {MAX_FOLDERS} folder pathspecs; for a long path "
                "list use `git update-index --add --remove -z --stdin`.")
    return None


def staged_paths(directory):
    """The repository root and the staged paths (root-relative), or None when git cannot say."""
    try:
        top = subprocess.run(["git", "-C", directory, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, encoding="utf-8", timeout=10)
        diff = subprocess.run(["git", "-C", directory, "diff", "--cached", "--name-only", "-z"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if top.returncode != 0 or diff.returncode != 0:
        return None
    return Path(top.stdout.strip()), [p for p in diff.stdout.split("\0") if p]


def check_commit_scope(directory, arguments, letters, added):
    """A commit without `-- <paths>` takes the whole index: refuse it while the index holds paths this
    command line does not stage itself (T017: 002 P4's b204c9daad committed three files another session
    had staged). `-i`/`--include` adds the index to the named paths, so it counts as bare."""
    paths = after_dashdash(arguments)
    if paths and "i" not in letters and "--include" not in arguments:
        return None
    found = staged_paths(directory or ".")
    if found is None:
        return ("Could not read the index to check what a bare `git commit` would take: commit with "
                "`git commit -m <msg> -- <paths or owned folders>`.")
    top, staged = found
    try:
        top = top.resolve()
        mine = [(Path(where) / path).resolve() for where, path in added]
    except OSError:
        mine = []
    others = []
    for path in staged:
        full = (top / path).resolve()
        if not any(full == own or own in full.parents for own in mine):
            others.append(path)
    if not others:
        return None
    sample = ", ".join(others[:3]) + (f" and {len(others) - 3} more" if len(others) > 3 else "")
    return (f"A `git commit` without `-- <paths>` commits the whole index, which holds {len(others)} staged "
            f"paths this command does not stage ({sample}): commit with `git commit -m <msg> -- <your paths "
            "or owned folders>`.")


def added_paths(line, cwd):
    """(directory, path) for every path a `git add` in this command line stages."""
    added = []
    for stages in line:
        for words in stages:
            cwd = entered(words, cwd)
            if words and name_of(words[0]) == "git":
                _, directory, sub, arguments = git_parts(words, cwd)
                if sub == "add":
                    after = after_dashdash(arguments)
                    named = after if after is not None else [w for w in arguments if not w.startswith("-")]
                    added += [(directory, path) for path in named]
    return added


def check_git(words, cwd, added=()):
    settings, directory, sub, arguments = git_parts(words, cwd)
    if sub is None:
        return None
    unsigned = {"commit.gpgsign=false", "commit.gpgsign=0", "commit.gpgsign=no"}
    if sub in ("commit", "merge", "rebase", "cherry-pick", "revert", "am", "pull", "tag", "commit-tree"):
        if "--no-gpg-sign" in arguments or unsigned & set(settings) or "--no-verify" in arguments:
            return "Commits stay signed and verified (AGENTS.md): no `--no-gpg-sign`, `commit.gpgsign=false` or `--no-verify`. If signing fails, stop and report."
    if sub in ("add", "commit", "rm", "restore", "checkout", "reset") and any(
            word == "--pathspec-from-file" or word.startswith("--pathspec-from-file=") for word in arguments):
        return ("`--pathspec-from-file` matches each listed path against the whole index (quadratic: 005 P6's "
                "~290k-path `git add` ran 45 min). Stage owned folders as `git add -- <dir> <dir>`, or a path "
                "list with `git update-index --add --remove -z --stdin < <NUL-separated list>`.")
    if sub == "commit":
        letters = short_flags(arguments, COMMIT_VALUED)
        if "n" in letters:
            return "`git commit -n` skips the hooks (`--no-verify`): commit without it."
        if "a" in letters or "--all" in arguments:
            return "`git commit -a` stages every tracked change: `git add` the change's explicit paths, then commit."
        return check_commit_scope(directory, arguments, letters, added)
    if sub == "add":
        return check_add(directory, arguments)
    if sub == "push":
        return check_push(directory, arguments)
    return None


def check_push(directory, arguments):
    for word in arguments:
        if word in ("-f", "--force", "--mirror", "--all", "--prune", "-d", "--delete") or word.startswith(
                ("--force-with-lease", "--force-if-includes")):
            return f"`git push {word}` is refused: never force, mirror or delete remote refs."
    positional, skip = [], False
    for word in arguments:
        if skip:
            skip = False
        elif word in ("-o", "--push-option", "--repo", "--receive-pack", "--exec") or re.fullmatch(r"\d*(>>?|<)", word):
            skip = True  # an option value or a redirection target (`2>&1` lexes as `2>`, `&`, `1`)
        elif re.match(r"\d*(>>?|<)", word):  # `2>/dev/null`, `>log`
            continue
        elif not word.startswith("-"):
            positional.append(word)
    refspecs = positional[1:]
    branch = current_branch(directory)
    for spec in refspecs:
        if spec.startswith(("+", ":")):
            return f"Refspec `{spec}` forces or deletes a remote ref."
        source, _, destination = spec.partition(":")
        destination = destination or source
        if destination.startswith("refs/tags/") or source.startswith("refs/tags/"):
            continue
        if branch is None:
            return None
        ok = {branch, f"refs/heads/{branch}", "HEAD"}
        if source not in ok or destination not in ok:
            return f"Push only the current branch (`{branch}`): `{spec}` names another. Ask the user for anything else."
    return None


LARGE_TREES = ("client", "packets")
# Hand-authored folders inside packets/, beside the data they produce (009 T003): everyday work, not bulk.
SMALL_SUBTREES = ("packets/patterns", "packets/tools", "packets/tests", "packets/plbatch", "packets/wireshark")
SUMMARY_FLAGS = {"--stat", "--shortstat", "--numstat", "--name-only", "--name-status", "--quiet", "--exit-code",
                 "--check", "--dirstat", "--summary", "--compact-summary", "--raw"}
COUNTERS = {"wc", "dust"}


def in_large_tree(word):
    """True for a path argument inside client/ or packets/ (also as `./client/...` or an absolute path),
    outside SMALL_SUBTREES. Normalized first: `packets/patterns/../decrypted_json` is the data tree."""
    path = posixpath.normpath(word.replace("\\", "/").lower())
    repo = str(hooklib.REPO).replace("\\", "/").lower().rstrip("/")  # d:/ddon-data
    for root in (repo, "/" + repo.replace(":", "", 1), "/mnt/" + repo.replace(":", "", 1)):
        if path.startswith(root + "/"):
            path = path[len(root) + 1:]
            break
    if not any(path == t or path.startswith(t + "/") for t in LARGE_TREES):
        return False
    if any(path == t or path.startswith(t + "/") for t in SMALL_SUBTREES):
        return False
    return not (hooklib.REPO / path).is_file()  # one file (a script in packets/) is fine


def bounded_by_next(stages, index):
    """True when the next pipeline stage counts or cuts the output (wc, dust, head, rg -c/-l/-q/-m)."""
    if index + 1 >= len(stages) or not stages[index + 1]:
        return False
    following = stages[index + 1]
    name = name_of(following[0])
    if name in COUNTERS or name == "head":
        return True
    return name == "rg" and any(w in ("-c", "--count", "-l", "-q", "--quiet") or w.startswith("-m") for w in following)


def check_large_output(stages):
    for index, words in enumerate(stages):
        if not words:
            continue
        name, args = name_of(words[0]), words[1:]
        large = [w for w in args if not w.startswith("-") and in_large_tree(w)]
        if name == "git" and args:
            _, _, sub, rest = git_parts(words, ".")
            if sub == "worktree" and rest[:1] == ["add"]:
                return ("No worktrees in ddon-data (Sam, 2026-10-17: hundreds of thousands of files). Work in the "
                        "main checkout on files no other agent owns; worktrees are fine in small repos such as ddon-hook.")
            if sub in ("diff", "log") and (sub == "diff" or {"-p", "--patch", "-u"} & set(rest)):
                if SUMMARY_FLAGS & {w.split("=", 1)[0] for w in rest} or bounded_by_next(stages, index):
                    continue
                paths = rest[rest.index("--") + 1:] if "--" in rest else []
                if not paths or any(in_large_tree(p) or p in (".", ":/") for p in paths):
                    return (f"`git {sub}` without a pathspec or over client/ or packets/ can print hundreds of thousands "
                            f"of lines: use `git {sub} --stat -- <subdir>` or name the exact files after `--`.")
            if sub == "ls-files" and large and not bounded_by_next(stages, index):
                return "`git ls-files` over client/ or packets/ is unbounded: pipe it to `wc -l`, or use `fd -d 2`."
            if sub in ("checkout", "restore", "rm"):
                reason = check_bulk_revert(sub, rest)
                if reason:
                    return reason
            continue
        if not large:
            continue
        depth = any(w in ("-d", "--max-depth", "-L", "--level") or w.startswith(("--max-depth=", "-d", "-L"))
                    for w in args)
        if name == "ls" and any(w.startswith("-") and not w.startswith("--") and "R" in w for w in args):
            if not bounded_by_next(stages, index):
                return "`ls -R` over client/ or packets/ is unbounded: use `fd -d 2 . <dir>` or `dust -d 1 <dir>`."
        if name in ("fd", "tree") and not depth and not bounded_by_next(stages, index):
            return f"`{name}` over client/ or packets/ needs a depth (`-d 2`) or a count (`| wc -l`)."
        if name == "rg":
            bound = any(w in ("-c", "--count", "--count-matches", "-l", "--files-with-matches", "-q", "--quiet")
                        or w.startswith(("-m", "--max-count")) for w in args)
            if not bound and not bounded_by_next(stages, index):
                what = "`rg --files`" if "--files" in args else "`rg`"
                return (f"{what} over client/ or packets/ (~173k files) needs a bound: `-c`, `-l`, `-m N`, or "
                        f"`| wc -l`.")
    return None


def check_bulk_revert(sub, rest):
    """A refusal for `git checkout --`, `git restore` or `git rm -r` over a directory, `.` or a glob."""
    if sub == "checkout" and "--" not in rest and "." not in rest:
        return None  # a branch switch
    if sub == "rm" and not any(w == "-r" or (w.startswith("-") and not w.startswith("--") and "r" in w) for w in rest):
        return None
    if sub == "restore" and "--staged" in rest and "--worktree" not in rest and "-W" not in rest:
        return None  # unstaging leaves the files alone
    paths = rest[rest.index("--") + 1:] if "--" in rest else [w for w in rest if not w.startswith("-")]
    bulk = [p for p in paths if p in (".", ":/", "*") or p.endswith("/") or any(c in p for c in "*?[")
            or in_large_tree(p) or os.path.isdir(p)]
    if sub == "rm" or bulk or not paths:
        return (f"`git {sub}` over {', '.join(bulk) or 'a directory'} reverts or deletes many files in a checkout that "
                f"holds other work (AGENTS.md): list the exact paths and ask the user first.")
    return None


def is_probe(stages):
    names = [name_of(s[0]) for s in stages if s]
    if not names:
        return False
    if all(n in PROBES or n == "echo" for n in names) and any(n in PROBES for n in names):
        return True
    return names[0] == "get-content" and any(w.lower() in ("-tail", "-wait") for w in stages[0])


def check_polling(data, command, line):
    words = tokens(command)
    lowered = {name_of(w) for w in words}
    if lowered & LOOPS and lowered & WAITS:
        return ("A `while`/`until` loop around `sleep` is a polling loop: start the long command with "
                "run_in_background and end your turn; its completion notifies you.")
    if not line or not all(is_probe(stages) for stages in line):
        return None
    directory = Path(os.environ.get("DDON_HOOK_POLL_DIR") or hooklib.ledger_dir() / "polls")
    stamp = directory / hashlib.sha1(hooklib.caller_key(data).encode()).hexdigest()
    call, now = str(data.get("tool_use_id") or ""), time.time()
    try:
        last = stamp.stat().st_mtime
        if call and stamp.read_text(encoding="utf-8") == call:
            return None  # the same call reached the guard twice
    except OSError:
        last = None
    try:
        directory.mkdir(parents=True, exist_ok=True)
        stamp.write_text(call, encoding="utf-8")
        os.utime(stamp, (now, now))
    except OSError:
        return None
    if last is not None and now - last < POLL_GAP_S:
        return ("Polling: a wait-and-look command again within 60 s. Each call re-reads your whole context. "
                "Start long work with run_in_background and end your turn; its completion (or the coordinator's "
                "message) wakes you.")
    return None


def verdict(data):
    """The refusal text, or None to let the command run."""
    command = (data.get("tool_input") or {}).get("command") or ""
    if not command.strip():
        return None
    shell = "powershell" if data.get("tool_name") == "PowerShell" else "bash"
    cwd = data.get("cwd") or "."
    line = pipelines(command)
    added = added_paths(line, cwd)
    for stages in line:
        reason = check_tools(stages, shell) or check_large_output(stages)
        if reason:
            return reason
        for words in stages:
            cwd = entered(words, cwd)
            if words and name_of(words[0]) == "git":
                reason = check_git(words, cwd, added)
                if reason:
                    return reason
    return check_sd(command) or check_polling(data, command, line)


def main():
    data = hooklib.read_input()
    if not data or data.get("tool_name") not in ("Bash", "PowerShell"):
        return 0
    reason = verdict(data)
    if reason:
        hooklib.record_refusal(data, "guard_bash", reason)
        print(f"Refused: {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    hooklib.fail_open(main)

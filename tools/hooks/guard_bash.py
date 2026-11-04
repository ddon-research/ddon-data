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
- forced or deleting pushes, pushes of any branch other than the current one, and a push naming a
  branch after a directory change that leaves the branch unknown (only a plain `cd <literal>` in an
  unbroken `&&` chain at the top level is followed, and `git -C <literal>`);
- polling: a `while`/`until` loop around `sleep`, or a wait-and-look command (sleep, date, process
  lists, `tail`) again within 60 s from the same agent: use `run_in_background` and end the turn.

ddon-data additions (AGENTS.md "Preservation and git hygiene"; ported from ddon-hook 4c625de):
- `git worktree add` (the repository is too large for worktrees; agents share the main checkout);
- unbounded output over the large trees (`client/`, `packets/`, except the small hand-authored subtrees
  of SMALL_SUBTREES): `git diff`/`git log -p` without a
  summary flag and with no pathspec or one in a large tree, `git show` of a path there without a
  summary flag, `ls -R`/`tree`/`fd`/`rg --files`/`git ls-files` there without a depth or count bound,
  and `rg`/`git grep` content searches there without `-c`/`-l`/`-m`/`-q`. Each argument is resolved
  against the tracked `cd` and `git -C` first; a tool given no path searches its directory;
- bulk reverts: `git checkout -- <dir|.>`, `git restore <dir|.>`, `git rm -r`: list exact paths and
  ask the user first.

The parsing is best effort (shlex over the command line, heredoc bodies dropped). Exit 2 refuses.
"""

import collections
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
SHELL_WORDS = {"if", "then", "elif", "else", "do", "while", "until", "!", "{"}
ENTERS = {"cd", "chdir", "pushd", "set-location", "sl", "push-location"}
MOVERS = ENTERS | {"popd", "pop-location"}
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


def chains(command):
    """The command line as (stages, separator before, separator after, subshell depth), one per pipeline, with the
    stages' words as written. `2>&1` and `&>f` are redirections, not background separators."""
    out, pipeline, stage, before, depth = [], [], [], None, 0
    words = tokens(command)
    for index, token in enumerate(words):
        following = words[index + 1] if index + 1 < len(words) else ""
        if token == "&" and ((stage and re.fullmatch(r"\d*>>?", stage[-1])) or following.startswith(">")):
            continue
        if token in PIPES:
            pipeline.append(stage)
            stage = []
        elif token in SEPARATORS or token in ("(", ")") or set(token) <= set(";&|()"):
            if stage:
                pipeline.append(stage)
            if pipeline:
                out.append((pipeline, before, token, depth))
            pipeline, stage = [], []
            before = token
            depth += token.count("(") - token.count(")")
        else:
            stage.append(token)
    if stage:
        pipeline.append(stage)
    if pipeline:
        out.append((pipeline, before, None, depth))
    return out


def pipelines(command):
    """The command line as a list of pipelines, each a list of stages (word lists)."""
    return [[unwrapped(s) for s in chain[0]] for chain in chains(command)]


def name_of(word):
    name = Path(word.replace("\\", "/")).name.lower()
    return name[:-4] if name.endswith(".exe") else name


def unwrapped(words):
    """`words` without leading `VAR=x` assignments, shell keywords and wrappers (`timeout 60 grep ...` -> grep)."""
    i = 0
    while i < len(words):
        word = words[i]
        if word in SHELL_WORDS or ("=" in word and word.split("=", 1)[0].isidentifier()):
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


def is_literal(word):
    """True for a directory the guard can name: no expansion the shell would do first."""
    return not re.search(r"[$`~*?\[]", word)


def joined(base, word):
    """`word` under `base`, or None when it depends on what the shell expands or on an unknown base."""
    if not is_literal(word):
        return None
    target = native_path(word)
    if re.match(r"[a-zA-Z]:[\\/]", target) or target.startswith(("/", "\\")):
        return str(Path(target))
    return str(Path(base) / target) if base else None


def entered(words, cwd):
    """Best guess of the directory after this command, for the checks of paths: any `cd`, `pushd` naming one literal
    directory moves the rest of the line, whatever its flags; `$VAR` and `cd -` stay put."""
    if not words or name_of(words[0]) not in ENTERS:
        return cwd
    targets = [w for w in words[1:] if not w.startswith("-") and not re.match(r"\d*[<>]", w)]
    moved = joined(cwd, targets[0]) if len(targets) == 1 else None
    return moved or cwd


Stage = collections.namedtuple("Stage", "words known guess bases")


def located(command, cwd):
    """Pipelines of Stages. `known` is the directory the stage certainly runs in, None when unknown: it follows only a
    plain `cd <literal>` in an unbroken `&&` chain at the top level. `guess` follows every `cd`. `bases` are the
    directories to resolve a path against: `known`, or else `guess` and the start."""
    known, guess, followed, out = cwd, cwd, False, []
    for stages, before, after, depth in chains(command):
        row = []
        for raw in stages:
            bases = [known] if known else list(dict.fromkeys((guess, cwd)))
            row.append(Stage(unwrapped(raw), known, guess, bases))
        out.append(row)
        for raw in stages:
            words = unwrapped(raw)
            if not words or name_of(words[0]) not in MOVERS:
                continue
            plain = (len(stages) == 1 and depth == 0 and after in ("&&", None) and "|" not in (before or "")
                     and raw == words and len(words) == 2 and name_of(words[0]) == "cd"
                     and not words[1].startswith("-"))
            known = joined(known, words[1]) if plain else None
            followed = followed or plain
            guess = entered(words, guess)
        if followed and after not in ("&&", None):
            known = None  # a `cd` before this may have failed: the rest runs in either directory
    return out


def git_parts(words, cwd):
    """(settings, directory, subcommand, arguments). The directory is None when no plain path gives it."""
    settings, directory, i = [], cwd, 1
    while i < len(words) and words[i].startswith("-"):
        option = words[i]
        if option in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") and i + 1 < len(words):
            if option == "-c":
                settings.append(words[i + 1].replace(" ", "").lower())
            if option == "-C":
                directory = joined(directory, words[i + 1])
            if option in ("--git-dir", "--work-tree"):
                directory = None
            i += 2
        else:
            if option.startswith(("--git-dir=", "--work-tree=")):
                directory = None
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
                    added += [(directory or cwd, path) for path in named]
    return added


SAME = object()


def check_git(words, cwd, added=(), known=SAME):
    """`cwd` is the best guess of the directory; `known` the certain one for a push, None when unknown."""
    settings, directory, sub, arguments = git_parts(words, cwd)
    if sub is None:
        return None
    directory = directory or cwd
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
        return check_push(git_parts(words, cwd if known is SAME else known)[1], arguments)
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
    branch = current_branch(directory) if directory else None
    for spec in refspecs:
        if spec.startswith(("+", ":")):
            return f"Refspec `{spec}` forces or deletes a remote ref."
        source, _, destination = spec.partition(":")
        destination = destination or source
        if destination.startswith("refs/tags/") or source.startswith("refs/tags/"):
            continue
        if source == "HEAD" and destination == "HEAD":
            continue
        if branch is None:
            return (f"Which branch this push runs on is unknown, so `{spec}` cannot be checked: a directory change "
                    "precedes it that is not a plain `cd <dir> &&`, or the directory is no repository. Run it from the "
                    "repository: a separate `git push ...` there, `cd <dir> && git push ...` or `git -C <dir> push ...`.")
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


def in_large_tree(word, cwd=None):
    """True for a path argument inside client/ or packets/ (also as `./client/...` or an absolute path),
    outside SMALL_SUBTREES. A relative path is taken from `cwd`, or from the repository when `cwd` is relative, absent
    or outside it. Normalized first: `packets/patterns/../decrypted_json` is the data tree."""
    literal = word.replace("\\", "/").lower()
    path = literal
    base = (cwd or "").replace("\\", "/").lower()
    if base and not re.match(r"[a-z]:/|/", literal):
        path = f"{base}/{literal}"
    path = posixpath.normpath(path)
    repo = str(hooklib.REPO).replace("\\", "/").lower().rstrip("/")  # d:/ddon-data
    for root in (repo, "/" + repo.replace(":", "", 1), "/mnt/" + repo.replace(":", "", 1)):
        if path.startswith(root + "/"):
            path = path[len(root) + 1:]
            break
    else:
        if re.match(r"[a-z]:/|/", path):  # another checkout, as `cd /d/ddon-data-s1 && rg x client`
            path = posixpath.normpath(literal)
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


RG_VALUED = {"-g", "--glob", "--iglob", "-t", "--type", "-T", "--type-not", "-A", "-B", "-C", "-m", "--max-count", "-d",
             "--max-depth", "-j", "--threads", "-r", "--replace", "--sort", "--sortr", "-M", "--max-columns", "-E",
             "--encoding", "--engine"}
RG_PATTERN = {"-e", "--regexp", "-f", "--file"}
FD_VALUED = {"-e", "--extension", "-t", "--type", "-E", "--exclude", "-d", "--max-depth", "--min-depth", "--exact-depth",
             "-x", "--exec", "-X", "--exec-batch", "-S", "--size", "-j", "--threads", "--changed-within",
             "--changed-before", "-o", "--owner"}
GIT_LOG_VALUED = set("nSGLOU")
GIT_GREP_VALUED = set("eABCOfm")
FD_PATH_FLAGS = ("--search-path", "--base-directory")


def path_words(name, args):
    """The paths this `rg`, `fd`, `tree` or `ls` is given; with none it searches its directory. A search's first
    word is its pattern, not a path."""
    valued = RG_VALUED | RG_PATTERN if name == "rg" else FD_VALUED if name == "fd" else set()
    positional, i = [], 0
    while i < len(args):
        word = args[i]
        if word in valued:
            i += 1
        elif not word.startswith("-"):
            positional.append(word)
        i += 1
    if name == "fd":
        flags = [w.split("=", 1)[1] for w in args if w.startswith(tuple(f"{f}=" for f in FD_PATH_FLAGS))]
        spaced = [args[at + 1] for at, w in enumerate(args[:-1]) if w in FD_PATH_FLAGS]
        return [*positional[1:], *flags, *spaced]
    if name == "rg" and not any(w in RG_PATTERN or w.startswith(("--regexp=", "--file=", "-e")) or w == "--files" for w in args):
        return positional[1:]
    return positional


def check_git_output(words, stage, stages, index):
    """The refusal for a `git` command that would print a data tree, or None."""
    _, _, sub, rest = git_parts(words, ".")
    if sub == "worktree" and rest[:1] == ["add"]:
        return ("No worktrees in ddon-data (Sam, 2026-10-17: hundreds of thousands of files). Work in the "
                "main checkout on files no other agent owns; worktrees are fine in small repos such as ddon-hook.")
    bases = [git_parts(words, base)[1] or base for base in stage.bases]
    big = lambda word: any(in_large_tree(word, base) for base in bases)  # noqa: E731
    here = any(in_large_tree(".", base) for base in bases)
    after = after_dashdash(rest)
    positional = [w for w in rest if not w.startswith("-")]
    bounded = bounded_by_next(stages, index)
    summary = SUMMARY_FLAGS & {w.split("=", 1)[0] for w in rest}
    if sub in ("diff", "log"):
        letters = short_flags(rest, GIT_LOG_VALUED)
        patch = sub == "diff" or any(w.startswith("--patch") for w in rest) or {"p", "u", "U"} & set(letters)
        if patch and not summary and not bounded:
            paths = after or []
            if not paths or any(big(p) or p in (".", ":/") for p in paths):
                return (f"`git {sub}` without a pathspec or over client/ or packets/ can print hundreds of thousands "
                        f"of lines: use `git {sub} --stat -- <subdir>` or name the exact files after `--`.")
    if sub == "show" and not summary and not bounded and "s" not in short_flags(rest, GIT_LOG_VALUED) and "--no-patch" not in rest:
        if any(big(p) for p in (after if after is not None else positional)):
            return "`git show` over client/ or packets/ can print hundreds of thousands of lines: use `git show --stat <rev> -- <subdir>` or name the exact files."
    if sub == "grep" and not bounded:
        letters = short_flags(rest, GIT_GREP_VALUED)
        bound = {"c", "l", "L", "q", "m"} & set(letters) or {w.split("=", 1)[0] for w in rest} & {
            "--count", "--files-with-matches", "--name-only", "--files-without-match", "--quiet", "--max-count"}
        pattern_given = any(w == "-e" or w.startswith("-e") for w in rest if not w.startswith("--"))
        paths = after if after is not None else positional[0 if pattern_given else 1:]
        if not bound and (any(big(p) for p in paths) or (not paths and here)):
            return "`git grep` over client/ or packets/ needs a bound: `-c`, `-l`, `-m N`, or `| wc -l`."
    if sub == "ls-files" and not bounded:
        paths = after if after is not None else positional
        if any(big(p) for p in paths) or (not paths and here):
            return "`git ls-files` over client/ or packets/ is unbounded: pipe it to `wc -l`, or use `fd -d 2`."
    if sub in ("checkout", "restore", "rm"):
        return check_bulk_revert(sub, rest, bases)
    return None


def check_large_output(located_stages):
    stages = [stage.words for stage in located_stages]
    for index, stage in enumerate(located_stages):
        words = stage.words
        if not words:
            continue
        name, args = name_of(words[0]), words[1:]
        if name == "git":
            reason = check_git_output(words, stage, stages, index) if args else None
            if reason:
                return reason
            continue
        if name not in ("ls", "fd", "tree", "rg"):
            continue
        paths = path_words(name, args) or ["."]
        if not any(in_large_tree(path, base) for path in paths for base in stage.bases):
            continue
        depth = any(w in ("-d", "--max-depth", "-L", "--level") or w.startswith(("--max-depth=", "-d", "-L"))
                    for w in args)
        if name == "ls" and ("--recursive" in args or any(w.startswith("-") and not w.startswith("--") and "R" in w for w in args)):
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


def check_bulk_revert(sub, rest, bases=(".",)):
    """A refusal for `git checkout --`, `git restore` or `git rm -r` over a directory, `.` or a glob."""
    if sub == "checkout" and "--" not in rest and "." not in rest:
        return None  # a branch switch
    if sub == "rm" and not any(w == "-r" or (w.startswith("-") and not w.startswith("--") and "r" in w) for w in rest):
        return None
    if sub == "restore" and "--staged" in rest and "--worktree" not in rest and "-W" not in rest:
        return None  # unstaging leaves the files alone
    paths = rest[rest.index("--") + 1:] if "--" in rest else [w for w in rest if not w.startswith("-")]
    bulk = [p for p in paths if p in (".", ":/", "*") or p.endswith("/") or any(c in p for c in "*?[")
            or any(in_large_tree(p, base) or os.path.isdir(os.path.join(base, p)) for base in bases)]
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
    line = located(command, cwd)
    plain = [[stage.words for stage in row] for row in line]
    added = added_paths(plain, cwd)
    for row, stages in zip(line, plain):
        reason = check_tools(stages, shell) or check_large_output(row)
        if reason:
            return reason
        for stage in row:
            if stage.words and name_of(stage.words[0]) == "git":
                reason = check_git(stage.words, stage.guess, added, stage.known)
                if reason:
                    return reason
    return check_sd(command) or check_polling(data, command, plain)


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

# Gate and hooks

What `tools/check.sh` checks and when, and what each hook in `tools/hooks/` refuses, read from their code. It is for anyone who met a refusal or a `not run` and wants the exact rule. To run the gate, see [Run the gate](../how-to/run-the-gate.md).

## Gate sections

`tools/check.sh` looks at the files changed since its base. With `--since <rev>` the base is `<rev>` and only the commits count; without it the base is the merge base with `main`, and uncommitted and untracked files count too. Changed files are limited to the small trees: `tools`, `research`, `specs`, `docs`, `patches`, `.claude`, `.specify`, `AGENTS.md`, `CLAUDE.md`, `readme.adoc`, `packets/*.sh`, `packets/keys/*.sh`, `packets/patterns`, `packets/tools`, `packets/tests`, `packets/plbatch`, `packets/wireshark`, `binaries/PS4_02020005/elf-dumps/*.sh`. `--all` makes every "changed" condition true; `--quick` skips every section marked below.

| Order | Section | Runs when | Command | `--quick` | Reports `not run` when |
| --- | --- | --- | --- | --- | --- |
| 1 | `hooks` | always | `python -m unittest discover` in `tools/hooks` and `tools/orchestration` | runs | `python` is missing |
| 2 | `shell` | always | `bash -n` of each changed `.sh`; `shellcheck -S warning` when installed | runs | never; 0 scripts passes |
| 3 | `flags` | a file changed matching `research/03040008/flags/(src\|tests\|*.py\|*.toml)` | that project's `unittest discover -s tests` | skipped | no change, or `.venv-cpython314` missing |
| 4 | `kg` | a file changed matching `research/knowledge-graph/(src\|tests\|pyproject)` | `uv run pytest -q`, `ruff check --no-fix .`, `mypy src tests` | skipped | no change, or `uv` missing |
| 4b | `export` | `packets/imhex-export.sh`, `packets/patterns/`, `packets/tools/` or `packets/tests/` changed | `bash packets/tests/imhex-export-select.sh` | skipped | no change |
| 4c | `idacopy` | `research/ida/private-copy.sh` or `research/ida/tests/` changed | `bash research/ida/tests/private-copy.sh` | skipped | no change, or `jq` or `cygpath` missing |
| 4d | `xfer` | a file changed matching `research/03040008/ida-transfer/(*.py\|*.toml\|tests/)` | `uv run pytest -q`, `ruff check --no-fix .` | skipped | no change, or `uv` missing |
| 5 | `mcp` | always | each `--project` path in `.claude/agents/*.md` exists | runs | no such path is named |
| 5b | `docs` | always; `tools/test_docs_check.py` too when `tools/docs_check.py` or its test changed | `tools/docs_check.py` | skipped | `uv` missing, or `markdown-it-py==4.2.0` not resolvable offline |
| 5c | `packet-counts` | `docs/reference/packet-ids.md` or `packets/decrypted_json` changed | `tools/docs_check.py --packet-counts` | skipped | no change, or `python` missing, or `rg` or the JSON tree missing |
| 6 | `imhex` | a file matching `r*-pattern.cpp` changed | none: it never validates | runs | always, and its line is absent with no such change |

`--since` needs a revision. The script stops with exit status 2 without `git` or `rg`, or on an unknown option. Its exit status is 1 when a section failed, else 0. Logs: `.agent-ledger/check-logs/<section>.log`, with `<section>.seconds` beside them, the changed-file list `changed-files.txt` and the script list `shell-files.txt`.

## Hooks

Each hook reads one JSON object on stdin. Exit 0 lets the call run; exit 2 refuses it and shows stderr to the agent. A hook's own failure exits 0: a bug in a hook never blocks work. `.claude/settings.json` wires them for every session; `guard_paths.py` is wired per role in `.claude/agents/*.md`.

| Hook | Event | Does |
| --- | --- | --- |
| `guard_bash.py` | before Bash, PowerShell | the refusals listed below |
| `guard_read.py` | before Read | refuses once the first whole read of a text file of 100 KB or more, or 40 KB for `.md` and `.adoc`, naming `offset` and `limit`; a second whole read runs. Images, PDFs and notebooks pass |
| `guard_ida.py` | before `open_database` of ida-mcp | refuses any path but a private copy, `D:/research/DDON-binaries/IDA9.5/<PC or PS4 folder>/ddon-data-<name>/<file>.i64`; refuses a call with no path and a path with `..` |
| `guard_paths.py` | before Edit, Write, NotebookEdit, per role | `--deny-owned` refuses the coordinator's files and producer output; `--allow <patterns>` refuses everything else |
| `agent_cap.py` | subagent start and stop; before Agent | one subagent at a time; refuses a spawn while a record younger than 4 h runs, or one that is not a project role or not titled `<role> · <spec> <package>: <what>` |
| `receipt.py` | a role agent's stop | refuses a final message without a receipt, or whose branch, head, base, status, commits or signatures differ from git; `--print` writes the block |
| `subagent_stop.py` | subagent stop | records the stop in `.agent-ledger/stops.jsonl` and the message in `.agent-ledger/reports/<agent id>.md`; never blocks |
| `session_state.py` | session start, compaction, subagent start | records the loaded instruction files, restores the coordinator's state after a compaction, gives a subagent the diff of an instruction file that changed |
| `context_watch.py` | after Bash, PowerShell, Agent, SendMessage; on a prompt | one reminder as the main session's context crosses each threshold; never blocks |
| `log_tool.py` | before and after tool calls | one row per call in `.agent-ledger/tool-calls.jsonl`; never blocks |
| `log_usage.py` | after the usage tool | appends the plan's readings to `.agent-ledger/usage-readings.jsonl`; never blocks |
| `hooklib.py` | | shared helpers, not a hook |

### What `guard_bash.py` refuses

| Refused | Use instead |
| --- | --- |
| `grep`, `egrep`, `fgrep` | `rg`, or `git grep -n` |
| `find` | `fd`, or `rg --files -g GLOB` |
| `du` | `dust` |
| `sed -i` | the Edit tool, or `sd -F` |
| `Select-String -Path` | `rg` |
| `cat FILE \| head` or `tail` | the Read tool with `offset` and `limit`, `rg -n -m N`, `sed -n 'A,Bp'` |
| `sd` with a newline in its pattern and no `-A` | the Edit tool: it would match nothing and exit 0 |
| `--no-gpg-sign`, `commit.gpgsign=false`, `--no-verify`, `git commit -n` | signed, verified commits |
| `git add -A`, `--all`, `.`, `:/`, `*`, bare `-u`, a directory without `--`; `git commit -a` | explicit paths, or owned folders as `git add -- <dir>` |
| `git add --` with more than 5 folders, the checkout or a parent of it, a glob or a magic pathspec | at most 5 owned folders; a long list through `git update-index --add --remove -z --stdin` |
| `--pathspec-from-file` | the same `git update-index` form: the option is quadratic against this index |
| `git commit` without `-- <paths>`, or with `-i`, while the index holds paths the line does not stage | `git commit -m <msg> -- <paths>` |
| `git push` forcing, mirroring, pruning or deleting; a refspec of another branch | push the current branch only |
| `git worktree add` | the main checkout: the repository is too large for worktrees |
| `git diff`, or `git log -p`, with no summary flag and with no pathspec or one in `client/` or `packets/` data | `git diff --stat -- <subdir>` or exact files |
| `git ls-files`, `ls -R`, `fd`, `tree`, `rg` or `rg --files` over that data with no bound | `-d 2`, `-c`, `-l`, `-m N`, or a pipe to `wc -l` |
| `git checkout -- <dir or .>`, `git restore <dir or .>`, `git rm -r` | list the exact paths and ask |
| a `while` or `until` loop around `sleep`; a wait-and-look command (`sleep`, `date`, process lists, `tail`) again within 60 s | `run_in_background`, then end the turn |

`packets/patterns`, `packets/tools`, `packets/tests`, `packets/plbatch`, `packets/wireshark` and a single file count as outside the data. The parsing is best effort: shlex over the line, with heredoc bodies dropped.

`.claude/settings.json` also denies these outright, with no hook: `git push --force`, `git push -f`, `git reset --hard`, `git clean`, `git stash`, `git worktree add`, `git commit --no-gpg-sign`, `git commit --no-verify`, and the `save_database` and `close_database` tools of `ida`.

### What `guard_paths.py --deny-owned` protects

| Group | Paths |
| --- | --- |
| The coordinator's files | `AGENTS.md`, `CLAUDE.md`, `.claude/*`, `.specify/memory/constitution.md`, `.specify/feature.json`, `specs/*/tasks.md`, `specs/orchestration.md`, `specs/efficiency-ledger.jsonl`, `research/knowledge-graph/AGENTS.md`, `research/knowledge-graph/.specify/*`, `research/knowledge-graph/specs/*/tasks.md`, `research/knowledge-graph/specs/STATUS.md` |
| Producer output | `client/*`, `packets/encrypted_streams/*`, `packets/decrypted_*`, `packets/keys/keys-all-in-one.csv`, `binaries/PS4_02020005/DDOORBIS*`, `binaries/PS4_02020005/elf-dumps/local/*`, `binaries/PS4_02020005/elf-dumps/archive/*`, `binaries/ANDROID_1500/*`, `research/03040008/flags/generated/*` |

## Other tools

`tools/docs_check.py` is the check behind the `docs` section; its findings are on [Write documentation](../how-to/write-documentation.md). `tools/orchestration/` holds `progress.py` (the progress block), `retro.py` (an efficiency summary of a window's agent work) and `section.py` (prints one section of a Markdown file).

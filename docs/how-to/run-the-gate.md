# Run the gate

This page is for anyone who changed a file in this repository and wants to know whether the change is sound: you run `tools/check.sh` and read its lines. You need Git Bash with `git` and `rg`; the sections name what else they need, and print `not run` without it.

## Run it

Pick the form that fits the change, from the repository root:

| You want | Command |
| --- | --- |
| The checks for everything changed since the merge base with `main`, uncommitted and untracked files included | `bash tools/check.sh` |
| The checks for the commits in a range only, ignoring other uncommitted work | `bash tools/check.sh --since <rev>` |
| Every project's gate, changed or not | `bash tools/check.sh --all` |
| Hook tests and shell syntax only | `bash tools/check.sh --quick` |

A full run with no project change takes under a minute. `--all` runs the project test suites and takes minutes, so run it in the background.

## Read the lines

It prints one header line and one line per section:

```text
check.sh at <commit>, base <commit>:
hooks     passed                                   Ran <n> tests Ran <n> tests (<s> s)
docs      passed                                   Ran <n> tests; docs_check: <n> pages, <n> links, <n> code-span paths, 0 findings (<s> s)
```

Each section says one of three things:

| Word | Meaning | What to do |
| --- | --- | --- |
| `passed` | the check ran and found nothing | nothing |
| `failed` | the check ran and found something; the exit status is 1 | read the log |
| `not run (<reason>)` | the check did not run; it is neither a pass nor a failure | decide from the reason: `no change under ...` is expected, a missing tool means you still lack that evidence |

Report a `not run` as `not run`, with its reason. The exit status is 0 when nothing failed, so 0 alone does not say that everything ran.

A failed section prints the end of its log to stderr. The full logs are `.agent-ledger/check-logs/<section>.log`.

## The sections

| Section | Runs when | Checks |
| --- | --- | --- |
| `hooks` | always | unit tests of `tools/hooks/` and `tools/orchestration/` |
| `shell` | always | `bash -n` of the changed scripts, and `shellcheck` when installed |
| `flags` | `research/03040008/flags/` sources changed | that project's unit tests |
| `kg` | `research/knowledge-graph/` sources changed | pytest, ruff and mypy |
| `export` | `packets/imhex-export.sh`, `packets/patterns/`, `packets/tools/` or `packets/tests/` changed | `packets/tests/imhex-export-select.sh` |
| `idacopy` | `research/ida/private-copy.sh` or its tests changed | `research/ida/tests/private-copy.sh` |
| `xfer` | `research/03040008/ida-transfer/` sources changed | pytest and ruff |
| `mcp` | always | every `--project` path in `.claude/agents/` exists |
| `docs` | always, except `--quick` | `tools/test_docs_check.py`, then `tools/docs_check.py` over the pages; a move anywhere can break a link |
| `imhex` | a resource pattern changed | always `not run`: the validation is `research/scripts/validate_pattern.sh`, per pattern |

To fix a `docs` finding, see [Write documentation](write-documentation.md).

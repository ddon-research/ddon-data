#!/usr/bin/env bash
# The single local gate for ddon-data. Runs each check that applies to the changed files and whose
# tools exist, and prints one line per check: passed, failed, or "not run (<reason>)". A check
# that did not run is never reported as passed.
#
#   tools/check.sh                 checks for the files changed since the base (default: merge-base with main)
#   tools/check.sh --since <rev>   only the files committed in <rev>..HEAD (landing a package)
#   tools/check.sh --all           run every project's gate, changed or not
#   tools/check.sh --quick         hooks and shell syntax only (no project test suites)
#
# Sections: hooks, shell, flags, kg, xfer (research/03040008/ida-transfer), idacopy (research/ida/tests/private-copy.sh), export (packets/tests/imhex-export-select.sh,
# when packets/imhex-export.sh, packets/patterns/, packets/tools/ or packets/tests/ changed), mcp, docs (tools/docs_check.py; its tests when it changed), imhex.
#
# Changed files: `git diff --name-only <base>` plus untracked files, limited to the small trees
# (never client/ or packets/ data). Full logs go to .agent-ledger/check-logs/<check>.log.
# Exit status: 0 when nothing failed, 1 otherwise.
set -o errexit -o nounset -o pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
LOGS="$ROOT/.agent-ledger/check-logs"
FLAGS_DIR=research/03040008/flags
KG_DIR=research/knowledge-graph
SMALL_TREES=(tools research specs docs patches .claude .specify AGENTS.md CLAUDE.md readme.adoc
             'packets/*.sh' 'packets/keys/*.sh' packets/patterns packets/tools packets/tests packets/plbatch packets/wireshark
             'binaries/PS4_02020005/elf-dumps/*.sh')
quick=0 all=0 since=""

while [ $# -gt 0 ]; do
    case "$1" in
        --quick) quick=1 ;;
        --all) all=1 ;;
        --since) since="${2:?--since needs a revision}"; shift ;;
        -h|--help) sed -n '2,16p' "${BASH_SOURCE[0]}"; exit 0 ;;
        *) echo "unknown option: $1" >&2; exit 2 ;;
    esac
    shift
done

for tool in git rg; do
    command -v "$tool" >/dev/null || { echo "check.sh needs $tool" >&2; exit 2; }
done
mkdir -p "$LOGS"
cd "$ROOT"

declare -a lines=()
failed=0

record() {  # record <check> <passed|failed|not run (...)> [detail]
    lines+=("$(printf '%-9s %-40s %s' "$1" "$2" "${3:-}")")
    if [ "$2" = failed ]; then failed=1; fi
}

run_logged() {  # run_logged <check> <command...>: 0 or the command's status; output in the log
    local name=$1 start end status=0
    shift
    start=$(date +%s)
    "$@" >"$LOGS/$name.log" 2>&1 || status=$?
    end=$(date +%s)
    echo "$((end - start))" >"$LOGS/$name.seconds"
    if [ "$status" -ne 0 ]; then
        echo "--- $name failed (exit $status); last lines of $LOGS/$name.log:" >&2
        tail -n 25 "$LOGS/$name.log" >&2
    fi
    return "$status"
}

seconds() { cat "$LOGS/$1.seconds" 2>/dev/null || echo "?"; }

base=${since:-$(git merge-base HEAD main 2>/dev/null || echo HEAD)}
changed="$LOGS/changed-files.txt"
if [ -n "$since" ]; then  # landing a package: its commits only, not others' dirty or untracked work
    git diff --name-only --diff-filter=d "$base" HEAD -- "${SMALL_TREES[@]}" | sort -u >"$changed"
else
    { git diff --name-only --diff-filter=d "$base" -- "${SMALL_TREES[@]}"
      git ls-files --others --exclude-standard -- "${SMALL_TREES[@]}"; } | sort -u >"$changed"
fi
touches() { [ "$all" -eq 1 ] || rg -q "$1" "$changed"; }

# 1. Hook and orchestration unit tests (always).
python_bin=$(command -v python || command -v python3 || true)
if [ -z "$python_bin" ]; then
    record hooks "not run (python missing)"
else
    hook_tests() {
        "$python_bin" -X utf8 -I -m unittest discover -s tools/hooks &&
            "$python_bin" -X utf8 -I -m unittest discover -s tools/orchestration
    }
    if run_logged hooks hook_tests; then
        record hooks passed "$(rg -o 'Ran [0-9]+ tests?' "$LOGS/hooks.log" | paste -sd ' ' -) ($(seconds hooks) s)"
    else
        record hooks failed "see $LOGS/hooks.log"
    fi
fi

# 2. Shell syntax of the changed scripts (bash -n; shellcheck when installed).
scripts="$LOGS/shell-files.txt"
rg '\.sh$' "$changed" >"$scripts" || true
count=$(wc -l <"$scripts" | tr -d ' ')
if [ "$count" -eq 0 ]; then
    record shell passed "0 scripts changed since $(git rev-parse --short "$base")"
else
    syntax() { while IFS= read -r f; do bash -n "$f" || return 1; done <"$scripts"; }
    if run_logged shell syntax; then
        if command -v shellcheck >/dev/null; then
            if run_logged shellcheck xargs -a "$scripts" shellcheck -S warning; then
                record shell passed "$count scripts: bash -n, shellcheck"
            else
                record shell failed "shellcheck on $count scripts"
            fi
        else
            record shell passed "$count scripts: bash -n (shellcheck not run: missing)"
        fi
    else
        record shell failed "bash -n on $count scripts"
    fi
fi

# 3. ddon-flags unit tests (CPython 3.14 venv from its README).
if [ "$quick" -eq 1 ]; then
    record flags "not run (--quick)"
elif ! touches "^$FLAGS_DIR/(src|tests|[^/]+\.(py|toml))"; then
    record flags "not run (no change under $FLAGS_DIR)"
elif [ ! -x "$FLAGS_DIR/.venv-cpython314/Scripts/python.exe" ]; then
    record flags "not run ($FLAGS_DIR/.venv-cpython314 missing: see its README)"
else
    flags_tests() { (cd "$FLAGS_DIR" && .venv-cpython314/Scripts/python.exe -m unittest discover -s tests); }
    if run_logged flags flags_tests; then
        record flags passed "$(rg -o 'Ran [0-9]+ tests?' "$LOGS/flags.log" | tail -n 1) ($(seconds flags) s)"
    else
        record flags failed "see $LOGS/flags.log"
    fi
fi

# 4. Knowledge-graph gates (its AGENTS.md): pytest, ruff, mypy; Neo4j and real-artifact tests stay opt-in.
if [ "$quick" -eq 1 ]; then
    record kg "not run (--quick)"
elif ! touches "^$KG_DIR/(src|tests|pyproject)"; then
    record kg "not run (no change under $KG_DIR)"
elif ! command -v uv >/dev/null; then
    record kg "not run (uv missing)"
else
    kg_gates() {
        (cd "$KG_DIR" && uv run pytest -q && uv run ruff check --no-fix . && uv run mypy src tests)
    }
    if run_logged kg kg_gates; then
        record kg passed "$(rg -o '[0-9]+ passed' "$LOGS/kg.log" | tail -n 1); ruff; mypy ($(seconds kg) s)"
    else
        record kg failed "see $LOGS/kg.log"
    fi
fi

# 4b. Packet export selection tests (stubbed plbatch, synthetic raw files; spec 005 P13, spec 006 TC1).
EXPORT_TEST=packets/tests/imhex-export-select.sh
if [ "$quick" -eq 1 ]; then
    record export "not run (--quick)"
elif ! touches "^(packets/imhex-export\.sh|packets/(patterns|tools|tests)/)"; then
    record export "not run (no change to packets/imhex-export.sh, packets/patterns/, packets/tools/ or packets/tests/)"
else
    if run_logged export bash "$EXPORT_TEST"; then
        record export passed "$(rg -c '^pass: ' "$LOGS/export.log") checks of $EXPORT_TEST ($(seconds export) s)"
    else
        record export failed "see $LOGS/export.log"
    fi
fi

# 4c. IDA private-copy tests (fake recovery record and database in a temp dir; spec 007 T003).
IDACOPY_TEST=research/ida/tests/private-copy.sh
if [ "$quick" -eq 1 ]; then
    record idacopy "not run (--quick)"
elif ! touches "^research/ida/(private-copy\.sh|tests/)"; then
    record idacopy "not run (no change to research/ida/private-copy.sh or its tests)"
elif ! command -v jq >/dev/null 2>&1 || ! command -v cygpath >/dev/null 2>&1; then
    record idacopy "not run (jq or cygpath missing)"
else
    if run_logged idacopy bash "$IDACOPY_TEST"; then
        record idacopy passed "$(rg -c '^pass: ' "$LOGS/idacopy.log") checks of $IDACOPY_TEST ($(seconds idacopy) s)"
    else
        record idacopy failed "see $LOGS/idacopy.log"
    fi
fi

# 4d. Spec 007 IDA transfer extractors (research/03040008/ida-transfer): pytest, ruff.
XFER_DIR=research/03040008/ida-transfer
if [ "$quick" -eq 1 ]; then
    record xfer "not run (--quick)"
elif ! touches "^$XFER_DIR/([^/]+\.(py|toml)|tests/)"; then
    record xfer "not run (no change under $XFER_DIR)"
elif ! command -v uv >/dev/null; then
    record xfer "not run (uv missing)"
else
    xfer_gates() { (cd "$XFER_DIR" && uv run pytest -q && uv run ruff check --no-fix .); }
    if run_logged xfer xfer_gates; then
        record xfer passed "$(rg -o '[0-9]+ passed' "$LOGS/xfer.log" | tail -n 1); ruff ($(seconds xfer) s)"
    else
        record xfer failed "see $LOGS/xfer.log"
    fi
fi

# 5. Role files' MCP servers: each `--project` path in .claude/agents/*.md exists (the plugin cache
#    is versioned, so an ida-mcp update leaves evidence-researcher-ida pointing at a removed folder).
mcp_paths="$LOGS/mcp-projects.txt"
rg -o --no-filename '"--project", "([^"]+)"' -r '$1' .claude/agents/ >"$mcp_paths" 2>/dev/null || true
mcp_count=$(wc -l <"$mcp_paths" | tr -d ' ')
mcp_missing=$(while IFS= read -r p; do [ -d "$p" ] || printf '%s ' "$p"; done <"$mcp_paths")
if [ "$mcp_count" -eq 0 ]; then
    record mcp "not run (no --project path in .claude/agents/)"
elif [ -n "$mcp_missing" ]; then
    record mcp failed "missing: $mcp_missing"
else
    record mcp passed "$mcp_count role-file MCP project paths exist"
fi

# 5b. Documentation: links with git's case, anchors, the index, code-span paths, wording, the opening, the tutorial's
#     inputs. It runs on every change, since a move anywhere can break a link; its own tests only when it changed.
DOCS_LIB=markdown-it-py==4.2.0
docs_python() { uv run --offline --no-project --quiet --with "$DOCS_LIB" python -X utf8 "$@"; }
if [ "$quick" -eq 1 ]; then
    record docs "not run (--quick)"
elif ! command -v uv >/dev/null; then
    record docs "not run (uv missing)"
elif ! docs_python -c 'import markdown_it' >"$LOGS/docs.log" 2>&1; then
    record docs "not run (uv cannot resolve $DOCS_LIB offline: see $LOGS/docs.log)"
else
    if touches '^tools/(test_)?docs_check\.py$'; then
        docs_tests="tests run"
        docs_gate() { docs_python -m unittest discover -s tools -p test_docs_check.py && docs_python tools/docs_check.py; }
    else
        docs_tests="tests not run (no change to tools/docs_check.py)"
        docs_gate() { docs_python tools/docs_check.py; }
    fi
    if run_logged docs docs_gate; then
        record docs passed "$(rg -o 'docs_check: .*' "$LOGS/docs.log" | sed 's/^docs_check: //'); $(rg -o 'Ran [0-9]+ tests?' "$LOGS/docs.log" || echo "$docs_tests") ($(seconds docs) s)"
    else
        record docs failed "see $LOGS/docs.log"
    fi
fi

# 6. ImHex patterns: validation needs the ImHex CLI, which is not on PATH (AGENTS.md).
if touches 'r[A-Za-z0-9]+-pattern\.cpp$'; then
    if command -v imhex >/dev/null; then
        record imhex "not run (run research/scripts/validate_pattern.sh per pattern)"
    else
        record imhex "not run (imhex not on PATH)"
    fi
fi

echo "check.sh at $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- "${SMALL_TREES[@]}" 2>/dev/null || echo ' + uncommitted changes'), base $(git rev-parse --short "$base"):"
printf '%s\n' "${lines[@]}"
exit "$failed"

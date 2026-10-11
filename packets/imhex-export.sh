#!/usr/bin/env bash
# Decode decrypted packets with an ImHex pattern and export them as JSON.
#
# Usage: ./imhex-export.sh [--force] <packet-filter> <pattern-name> [jobs]
#   packet-filter  substring of the file names in decrypted_raw/<stream>/
#                  (e.g. S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES)
#   pattern-name   pattern in ../research/03040008/packets/<name>-pattern.cpp
#                  (e.g. S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES)
#   jobs           parallel ImHex processes (default: nproc)
#   --force        re-export packets whose JSON already exists
#
# Output: decrypted_json/<stream>/<packet-file>.json (one file per packet).
# Failures keep their ImHex error log as <packet-file>.json.err and make the script exit 1.
#
# Environment overrides:
#   IMHEX        ImHex executable (default: imhex on PATH, then the portable install below)
#   RAW_DIR      input root  (default: decrypted_raw)
#   JSON_DIR     output root (default: decrypted_json)
#   PATTERN_DIR  pattern dir (default: ../research/03040008/packets)
#
# Example: ./imhex-export.sh S2C_JOIN_LOBBY_QUEST_INFO_NTC S2C_JOIN_LOBBY_QUEST_INFO_NOTICE 8
#   then:  rg -o -h 'msgId.*' -g '*LOBBY_DATA_MSG_NTC*.json' decrypted_json | sort -u
set -o errexit
set -o nounset
set -o pipefail
shopt -s nullglob globstar

die() { echo "ERROR: $*" >&2; exit 2; }
usage() { sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//' >&2; exit 2; }
require() {
  local cmd
  for cmd in "$@"; do
    command -v "$cmd" >/dev/null 2>&1 || die "required command '$cmd' not found in this environment (use Git Bash, MSYS2, or WSL)"
  done
}

FORCE=0
if [[ ${1:-} == --force ]]; then FORCE=1; shift; fi
[[ $# -ge 2 && $# -le 3 ]] || usage
FILTER=$1
PATTERN_NAME=$2
JOBS=${3:-}

[[ -n "$FILTER" ]] || die "packet filter must not be empty (it would match every packet)"
[[ "$FILTER" != */* && "$PATTERN_NAME" != */* ]] || die "filter and pattern name must not contain '/'"

# Resolve paths relative to this script so it works from any working directory.
cd "$(dirname "${BASH_SOURCE[0]}")"
RAW_DIR=${RAW_DIR:-decrypted_raw}
JSON_DIR=${JSON_DIR:-decrypted_json}
PATTERN_DIR=${PATTERN_DIR:-../research/03040008/packets}
PATTERN="$PATTERN_DIR/$PATTERN_NAME-pattern.cpp"

require basename dirname grep mkdir mktemp mv rm tee xargs
[[ -d "$RAW_DIR" ]] || die "input directory '$RAW_DIR' not found"
[[ -f "$PATTERN" ]] || die "pattern file '$PATTERN' not found"

if [[ -z ${IMHEX:-} ]]; then
  if command -v imhex >/dev/null 2>&1; then
    IMHEX=$(command -v imhex)
  else
    IMHEX="/e/Software/imhex-1.38.1-Windows-Portable-NoGPU-x86_64/imhex.exe"
  fi
fi
[[ -x "$IMHEX" ]] || die "ImHex not found or not executable: '$IMHEX' (set IMHEX=/path/to/imhex)"
"$IMHEX" --pl format --help >/dev/null 2>&1 || die "'$IMHEX' does not support '--pl format' (needs ImHex 1.30+)"

if [[ -z "$JOBS" ]]; then
  JOBS=$(nproc 2>/dev/null || getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1)
fi
if [[ ! "$JOBS" =~ ^[0-9]+$ ]] || (( JOBS < 1 )); then
  die "jobs must be a positive integer, got '$JOBS'"
fi

inputs=("$RAW_DIR"/**/*"$FILTER"*)
(( ${#inputs[@]} > 0 )) || die "no packets in '$RAW_DIR' match '*$FILTER*'"

# Export one packet. ImHex refuses to overwrite its output, so write to a temp file and
# move it into place: an interrupted run never leaves a truncated JSON behind.
export_one() {
  local input=$1 rel out tmp
  rel=${input#"$RAW_DIR"/}
  out="$JSON_DIR/$rel.json"
  if [[ -e "$out" && $FORCE -eq 0 ]]; then
    echo "skip $rel"
    return 0
  fi
  mkdir -p "$(dirname "$out")"
  tmp="$out.tmp.$$"
  # Native Windows ImHex cannot create files whose path exceeds MAX_PATH (260 characters).
  if command -v cygpath >/dev/null 2>&1; then
    local winpath
    winpath=$(cygpath -aw "$tmp")
    # shellcheck disable=SC1003  # literal \\?\ long-path prefix, not an escape
    winpath=${winpath#'\\?\'}
    if (( ${#winpath} >= 260 )); then
      echo "path too long (${#winpath} chars, Windows limit 260): $winpath" >"$out.err"
      echo "FAIL $rel (see $out.err)"
      return 1
    fi
  fi
  rm -f "$tmp"
  if "$IMHEX" --pl format --pattern "$PATTERN" --input "$input" --output "$tmp" >"$out.err" 2>&1 \
      && [[ -s "$tmp" ]]; then
    mv -f "$tmp" "$out"
    rm -f "$out.err"
    echo "ok   $rel"
  else
    rm -f "$tmp"
    echo "FAIL $rel (see $out.err)"
    return 1
  fi
}
export -f export_one
export IMHEX PATTERN RAW_DIR JSON_DIR FORCE

echo "Exporting ${#inputs[@]} packet(s) matching '$FILTER' with $PATTERN ($JOBS job(s))"
log=$(mktemp)
trap 'rm -f "$log"' EXIT
# xargs exits non-zero when any export fails; the per-packet log below is the source of truth.
# shellcheck disable=SC2016  # $1 is expanded by the inner bash, not here
printf '%s\0' "${inputs[@]}" \
  | xargs -0 -P "$JOBS" -I {} bash -c 'export_one "$1"' _ {} | tee "$log" || true

ok=$(grep -c '^ok ' "$log" || true)
skip=$(grep -c '^skip ' "$log" || true)
fail=$(grep -c '^FAIL ' "$log" || true)
echo "Done: $ok exported, $skip skipped, $fail failed"
(( ok + skip + fail == ${#inputs[@]} )) || { echo "ERROR: $(( ${#inputs[@]} - ok - skip - fail )) packet(s) reported no result" >&2; exit 1; }
(( fail == 0 )) || exit 1

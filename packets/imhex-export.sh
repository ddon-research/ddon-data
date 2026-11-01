#!/usr/bin/env bash
# Decode decrypted packets with an ImHex pattern and export them as JSON.
#
# Usage: ./imhex-export.sh [--force] <packet-filter> <pattern-name> [jobs]
#   packet-filter  substring of the file names in decrypted_raw/<stream>/
#                  (e.g. S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES)
#   pattern-name   pattern in ../research/03040008/packets/<name>-pattern.cpp
#                  (e.g. S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES)
#   jobs           parallel worker processes (default: nproc with plbatch, nproc/2 with ImHex)
#   --force        re-export packets whose JSON already exists
#
# Output: decrypted_json/<stream>/<packet-file>.json (one file per packet).
# Failures keep their error log as <packet-file>.json.err and make the script exit 1.
#
# Engine: plbatch (research/imhex/plbatch, PatternLanguage at the commit ImHex 1.38.1 embeds, so the
# JSON is byte-identical to `imhex --pl format`) when built, one long-lived process per shard;
# otherwise one `imhex --pl format` process per packet.
#
# Environment overrides:
#   PLBATCH      plbatch executable (default: ../research/imhex/plbatch/build/bin/plbatch.exe if
#                built); PLBATCH=none forces the ImHex path
#   IMHEX        ImHex executable (default: imhex on PATH, then the portable install below); with
#                plbatch, its includes/ folder supplies the std library
#   RAW_DIR      input root  (default: decrypted_raw)
#   JSON_DIR     output root (default: decrypted_json)
#   PATTERN_DIR  pattern dir (default: ../research/03040008/packets); its include/ folder, when
#                present, is passed with -I, so patterns can share
#                `#include "nNetMsg.hexpat"` and the like
#
# Example: ./imhex-export.sh --force C2S_PARTY_SEND_BINARY_MSG_NTC C2S_PARTY_SEND_BINARY_MSG_NTC 16
#   then:  fd -g '*_C2S_PARTY_SEND_BINARY_MSG_NTC_*.json' decrypted_json -X jq -r '.packet | "\(.msgId) \(.msgFits)"' | sort | uniq -c
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

require grep mkdir mktemp mv rm tee xargs
[[ -d "$RAW_DIR" ]] || die "input directory '$RAW_DIR' not found"
[[ -f "$PATTERN" ]] || die "pattern file '$PATTERN' not found"

# Native Windows programs need Windows paths; convert each root once, never per packet.
winpath() { if command -v cygpath >/dev/null 2>&1; then cygpath -aw "$1"; else printf '%s\n' "$1"; fi; }

# Shared pattern headers.
INCLUDE_DIR=
if [[ -d "$PATTERN_DIR/include" ]]; then INCLUDE_DIR=$(winpath "$PATTERN_DIR/include"); fi

if [[ -z ${IMHEX:-} ]]; then
  if command -v imhex >/dev/null 2>&1; then
    IMHEX=$(command -v imhex)
  else
    IMHEX="/e/Software/imhex-1.38.1-Windows-Portable-NoGPU-x86_64/imhex.exe"
  fi
fi

if [[ -z ${PLBATCH:-} && -x ../research/imhex/plbatch/build/bin/plbatch.exe ]]; then
  PLBATCH=../research/imhex/plbatch/build/bin/plbatch.exe
fi
[[ ${PLBATCH:-} != none ]] || PLBATCH=

if [[ -n "${PLBATCH:-}" ]]; then
  [[ -x "$PLBATCH" ]] || die "plbatch not found or not executable: '$PLBATCH' (build: research/imhex/plbatch/build.sh, or PLBATCH=none)"
  # The std library (std.mem, std.io, ...) that `imhex --pl` adds by itself.
  STD_DIR=${IMHEX_INCLUDES:-$(dirname "$IMHEX")/includes}
  [[ -d "$STD_DIR" ]] || die "ImHex std library not found: '$STD_DIR' (set IMHEX_INCLUDES or IMHEX)"
  STD_DIR=$(winpath "$STD_DIR")
  ENGINE=plbatch
else
  [[ -x "$IMHEX" ]] || die "ImHex not found or not executable: '$IMHEX' (set IMHEX=/path/to/imhex)"
  "$IMHEX" --pl format --help >/dev/null 2>&1 || die "'$IMHEX' does not support '--pl format' (needs ImHex 1.30+)"
  ENGINE=imhex
fi

if [[ -z "$JOBS" ]]; then
  JOBS=$(nproc 2>/dev/null || getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1)
  # Each ImHex packet costs several MSYS process creations, which contend with each other.
  [[ $ENGINE == plbatch ]] || JOBS=$(( JOBS > 1 ? JOBS / 2 : 1 ))
fi
if [[ ! "$JOBS" =~ ^[0-9]+$ ]] || (( JOBS < 1 )); then
  die "jobs must be a positive integer, got '$JOBS'"
fi

inputs=("$RAW_DIR"/**/*"$FILTER"*)
(( ${#inputs[@]} > 0 )) || die "no packets in '$RAW_DIR' match '*$FILTER*'"

echo "Exporting ${#inputs[@]} packet(s) matching '$FILTER' with $PATTERN ($JOBS $ENGINE job(s))"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
log=$work/log

if [[ $ENGINE == plbatch ]]; then
  # File list relative to RAW_DIR, built with parameter expansion only, dealt round-robin into
  # JOBS shards; one plbatch process per shard writes JSON_DIR/<rel>.json and the ok/skip/FAIL lines.
  shards=()
  for (( k = 0; k < JOBS; k++ )); do shards+=(""); done
  for (( i = 0; i < ${#inputs[@]}; i++ )); do
    shards[i % JOBS]+="${inputs[i]#"$RAW_DIR"/}"$'\n'
  done
  plargs=(--pattern "$(winpath "$PATTERN")" -I "$STD_DIR" --in-root "$(winpath "$RAW_DIR")")
  [[ -z "$INCLUDE_DIR" ]] || plargs+=(-I "$INCLUDE_DIR")
  mkdir -p "$JSON_DIR"
  plargs+=(--out-root "$(winpath "$JSON_DIR")")
  (( FORCE == 0 )) || plargs+=(--force)
  for (( k = 0; k < JOBS; k++ )); do
    [[ -n "${shards[k]}" ]] || continue
    printf '%s' "${shards[k]}" > "$work/shard.$k"
    # plbatch exits 1 when a packet failed; the per-packet log below is the source of truth.
    { "$PLBATCH" "${plargs[@]}" < "$work/shard.$k" || true; } > "$work/out.$k" &
  done
  wait
  cat "$work"/out.* | tee "$log"
else
  # Export one packet. ImHex refuses to overwrite its output, so write to a temp file and move
  # it into place: an interrupted run never leaves a truncated JSON behind. No subshells here:
  # with many jobs every MSYS process creation costs hundreds of ms.
  export_one() {
    local input=$1 rel out tmp wtmp
    rel=${input#"$RAW_DIR"/}
    out="$JSON_DIR/$rel.json"
    if [[ -e "$out" && $FORCE -eq 0 ]]; then
      echo "skip $rel"
      return 0
    fi
    tmp="$out.tmp.$$"
    # Native Windows ImHex cannot create files whose path exceeds MAX_PATH (260 characters).
    wtmp="$JSON_ROOT_WIN\\${tmp#"$JSON_DIR"/}"
    wtmp=${wtmp//\//\\}
    if (( ${#wtmp} >= 260 )); then
      echo "path too long (${#wtmp} chars, Windows limit 260): $wtmp" >"$out.err"
      echo "FAIL $rel (see $out.err)"
      return 1
    fi
    local includes=() errlog="$WORK/err.$$"
    [[ -z "$INCLUDE_DIR" ]] || includes=(-I "$INCLUDE_DIR")
    if "$IMHEX" --pl format "${includes[@]}" --pattern "$PATTERN" --input "$input" --output "$tmp" >"$errlog" 2>&1 \
        && [[ -s "$tmp" ]]; then
      mv -f "$tmp" "$out"
      [[ ! -e "$out.err" ]] || rm -f "$out.err"
      echo "ok   $rel"
    else
      [[ ! -e "$tmp" ]] || rm -f "$tmp"
      mv -f "$errlog" "$out.err"
      echo "FAIL $rel (see $out.err)"
      return 1
    fi
  }
  # Create every output directory with one mkdir before the jobs start.
  mkdir -p "$JSON_DIR"
  JSON_ROOT_WIN=$(winpath "$JSON_DIR")
  declare -A dirs=()
  for input in "${inputs[@]}"; do
    rel=${input#"$RAW_DIR"/}
    [[ $rel != */* ]] || dirs["$JSON_DIR/${rel%/*}"]=1
  done
  (( ${#dirs[@]} == 0 )) || printf '%s\0' "${!dirs[@]}" | xargs -0 mkdir -p
  WORK=$work
  export -f export_one
  export IMHEX PATTERN RAW_DIR JSON_DIR JSON_ROOT_WIN FORCE INCLUDE_DIR WORK
  # xargs exits non-zero when any export fails; the per-packet log below is the source of truth.
  # shellcheck disable=SC2016  # $1 is expanded by the inner bash, not here
  printf '%s\0' "${inputs[@]}" \
    | xargs -0 -P "$JOBS" -I {} bash -c 'export_one "$1"' _ {} | tee "$log" || true
fi

ok=$(grep -c '^ok ' "$log" || true)
skip=$(grep -c '^skip ' "$log" || true)
fail=$(grep -c '^FAIL ' "$log" || true)
echo "Done: $ok exported, $skip skipped, $fail failed"
(( ok + skip + fail == ${#inputs[@]} )) || { echo "ERROR: $(( ${#inputs[@]} - ok - skip - fail )) packet(s) reported no result" >&2; exit 1; }
(( fail == 0 )) || exit 1

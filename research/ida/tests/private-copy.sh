#!/usr/bin/env bash
# Focused tests of research/ida/private-copy.sh (spec 007 T003), on a fake CURRENT-RECOVERY.json
# and a small fake database in a temp dir (DDON_RECOVERY_JSON, test only). No real database is
# read or copied: every pc/ps4 case is refused before the original is touched.
#
# Usage: research/ida/tests/private-copy.sh
# Checks:
#   1. an unknown target and a bad name are refused (exit 2), for pc-accepted, pc and ps4
#   2. pc-accepted refuses a sha256 mismatch and copies nothing
#   3. pc-accepted refuses an accepted path outside the record's folder, and one with '..' parts
#   4. pc-accepted copies the accepted database to <record folder>/ddon-data-<name>/, not into the
#      feature folder, and the copy's bytes equal the original's
#   5. pc-accepted refuses to replace a copy that a worker holds open (.id0 present)
#   6. a record without accepted_PC.sha256 is refused
set -o errexit -o nounset -o pipefail

die() { echo "ERROR: $*" >&2; exit 2; }
for cmd in mktemp rm mkdir printf jq sha256sum cmp dirname cygpath; do
  command -v "$cmd" >/dev/null 2>&1 || die "$cmd not found"
done

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
script=$here/../private-copy.sh
[[ -f $script ]] || die "script not found: $script"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
work=$(cygpath -m "$tmp")   # C:/... form: /tmp is a mount, which private-copy.sh does not resolve
root=$work/PC_DDON_03040008
feature=$root/feature008-test
db=$feature/2022_01_29_DDO_DUMP_FIX.exe.i64
other=$work/outside/2022_01_29_DDO_DUMP_FIX.exe.i64
mkdir -p "$feature" "$work/outside"
printf 'fake i64\n' > "$db"
printf 'other\n' > "$other"
sha=$(sha256sum "$db" | cut -d' ' -f1)
other_sha=$(sha256sum "$other" | cut -d' ' -f1)
win() { cygpath -w "$1"; }   # the real record holds Windows paths with backslashes
record() { jq -n --arg p "$1" --arg s "$2" '{accepted_PC: {path: $p, sha256: $s}}' > "$root/CURRENT-RECOVERY.json"; }
export DDON_RECOVERY_JSON=$root/CURRENT-RECOVERY.json

fails=0
pass() { echo "pass: $*"; }
fail() { echo "FAIL: $*"; fails=$((fails + 1)); }
# expect_refused <label> <error substring> <args...>: exit status 2 with that error
expect_refused() {
  local label=$1 why=$2; shift 2
  local rc=0; bash "$script" "$@" >"$work/out" 2>"$work/err" || rc=$?
  if [[ $rc -eq 2 && $(<"$work/err") == *"$why"* ]]; then pass "$label ($(<"$work/err"))"
  else fail "$label: exit $rc, $(<"$work/err")"; fi
}
no_copy() { [[ ! -e $root/ddon-data-t003 ]] && pass "$1 copied nothing" || fail "$1 left $root/ddon-data-t003"; }

record "$(win "$db")" "$sha"

# 1
expect_refused "unknown target" "target must be" pc-latest t003
expect_refused "bad name pc-accepted" "name must be" pc-accepted "../x"
expect_refused "bad name pc" "name must be" pc "a b"
expect_refused "bad name ps4" "name must be" ps4 "-lead"

# 2
record "$(win "$db")" "$(printf '0%.0s' {1..64})"
expect_refused "sha mismatch" "differs from its record" pc-accepted t003
no_copy "sha mismatch"

# 3
record "$(win "$other")" "$other_sha"
expect_refused "path outside the record folder" "is outside" pc-accepted t003
record "$root/../outside/2022_01_29_DDO_DUMP_FIX.exe.i64" "$other_sha"
expect_refused "path with .. parts" "'..' parts" pc-accepted t003
no_copy "refused paths"

# 4
record "$(win "$db")" "$sha"
rc=0; out=$(bash "$script" pc-accepted t003 2>"$work/err") || rc=$?
copy=$root/ddon-data-t003/2022_01_29_DDO_DUMP_FIX.exe.i64
if [[ $rc -eq 0 && -f $copy ]] && cmp -s "$copy" "$db"; then pass "copy made at $out"
else fail "copy: exit $rc, out '$out', err '$(<"$work/err")'"; fi
[[ ! -e $feature/ddon-data-t003 ]] && pass "nothing inside the feature folder" || fail "copy landed in the feature folder"

# 5
: > "$root/ddon-data-t003/2022_01_29_DDO_DUMP_FIX.exe.id0"
expect_refused "copy open in a worker" "open in a worker" pc-accepted t003
[[ -e $root/ddon-data-t003/2022_01_29_DDO_DUMP_FIX.exe.id0 ]] && pass "open copy kept" || fail "open copy deleted"

# 6
jq -n --arg p "$(win "$db")" '{accepted_PC: {path: $p}}' > "$root/CURRENT-RECOVERY.json"
expect_refused "record without sha256" "no accepted_PC.sha256" pc-accepted t004

if [[ $fails -ne 0 ]]; then echo "$fails check(s) failed"; exit 1; fi
echo "all checks passed"

#!/usr/bin/env bash
# Focused tests of the `@` selection in packets/imhex-export.sh (spec 005 P13, R2 F2), on synthetic
# raw files in a temp dir. A stub stands in for plbatch and reports "ok" for every file it is
# given, so the export log lists exactly the selected files; no pattern is compiled.
#
# Usage: research/03040008/packets/tests/imhex-export-select.sh
# Checks:
#   1. `@` on an id shared by login-server and game-server files, without `// packet-select:`,
#      refuses (exit 2) and names the fix
#   2. `@` with `// packet-select: C2L_LOGIN_REQ` takes only the C2L_LOGIN_REQ file of that id
#   3. `@` on an unshared id takes every file of the id, whatever its name
#   4. `// packet-select:` with a name no file of the id carries refuses
set -o errexit -o nounset -o pipefail

die() { echo "ERROR: $*" >&2; exit 2; }
for cmd in mktemp rm mkdir printf chmod dirname; do command -v "$cmd" >/dev/null 2>&1 || die "$cmd not found"; done

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
script=$(cd "$here/../../../../packets" && pwd)/imhex-export.sh
[[ -f $script ]] || die "export script not found: $script"

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/raw/s1" "$work/raw/s2" "$work/json" "$work/pat" "$work/std"
: > "$work/raw/s1/1_C2L_LOGIN_REQ_2019-07-06T11_05_33.1-07_00.0_1_1"
: > "$work/raw/s2/2_C2S_CONNECTION_LOGIN_REQ_2019-07-06T11_05_34.1-07_00.0_1_1"
: > "$work/raw/s1/3_S2C_CONTEXT_GET_SET_CONTEXT_RES_2019-07-06T11_05_35.1-07_00.35_7_2"
: > "$work/raw/s2/4_S2C_UNKNOWN_OLD_NAME_2019-07-06T11_05_36.1-07_00.35_7_2"
printf '#!/usr/bin/env bash\nwhile IFS= read -r f; do echo "ok   $f"; done\n' > "$work/plbatch"
chmod +x "$work/plbatch"
pattern() { printf '%s\n' "// test pattern" "$@" "#pragma endian big" > "$work/pat/$name-pattern.cpp"; }

fails=0
check() { if eval "$2"; then echo "pass: $1"; else echo "FAIL: $1"; fails=$((fails + 1)); fi; }
run() {
  rc=0
  log=$(PLBATCH="$work/plbatch" IMHEX_INCLUDES="$work/std" RAW_DIR="$work/raw" JSON_DIR="$work/json" \
    PATTERN_DIR="$work/pat" bash "$script" --force @ "$name" 1 2>&1) || rc=$?
}

name=SHARED; pattern "// packet-id: 0.1.1"
run
check "shared id without packet-select refuses" '(( rc == 2 )) && [[ $log == *"shared by login-server"* && $log == *"packet-select"* ]]'

name=LOGIN; pattern "// packet-id: 0.1.1" "// packet-select: C2L_LOGIN_REQ"
run
check "packet-select takes only its name" '(( rc == 0 )) && [[ $log == *"ok   s1/1_C2L_LOGIN_REQ_"* && $log != *CONNECTION_LOGIN* && $log == *"Done: 1 exported"* ]]'

name=CONTEXT; pattern "// packet-id: 35.7.2"
run
check "unshared id takes every name" '(( rc == 0 )) && [[ $log == *"Done: 2 exported"* ]]'

name=MISSING; pattern "// packet-id: 0.1.1" "// packet-select: L2C_LOGIN_RES"
run
check "packet-select without a match refuses" '(( rc == 2 )) && [[ $log == *"with the name '"'"'L2C_LOGIN_RES'"'"'"* ]]'

(( fails == 0 )) || { echo "$fails check(s) failed" >&2; exit 1; }
echo "all checks passed"

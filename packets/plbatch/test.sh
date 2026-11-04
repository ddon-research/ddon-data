#!/usr/bin/env bash
# Focused tests of plbatch's output checks (spec 005 P10, R1 F1/F2), on synthetic inputs in a temp dir.
#
# Usage: research/imhex/plbatch/test.sh [plbatch.exe]
#   default binary: research/imhex/plbatch/build/bin/plbatch.exe (build.sh)
# Checks:
#   1. a finite f32 writes valid JSON and reports "ok"
#   2. a NaN f32 reports "ok-nan" and keeps the formatter text (bare nan) by default
#   3. --json-nonfinite=null reports "ok-null" and writes valid JSON with null
#   4. a failing input under --force removes the JSON an earlier run left (no stale JSON)
#   5. without --force an existing JSON is skipped
#   6. strings come out as UTF-8 JSON strings (no %XX percent encoding)
set -o errexit -o nounset -o pipefail

die() { echo "ERROR: $*" >&2; exit 2; }
for cmd in mktemp rm mkdir printf grep; do command -v "$cmd" >/dev/null 2>&1 || die "$cmd not found"; done

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PLBATCH=${1:-$here/build/bin/plbatch.exe}
[[ -x $PLBATCH ]] || die "plbatch not built: $PLBATCH (run build.sh)"

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/in" "$work/out"
printf '\x3f\x80\x00\x00' > "$work/in/finite"    # 1.0f
printf '\x7f\xc0\x00\x00' > "$work/in/nan"       # NaN
printf '\x00\x00\x00\x00' > "$work/in/bad"      # first byte 0: the pattern divides by it
# The guard makes a data-dependent runtime error (PatternLanguage does not fail on a short file).
printf 'struct S { be float value; }; S s @ 0x00;\nu8 b @ 0x00;\nu8 guard = 1 / b;\n' > "$work/pattern.pat"

fails=0
check() { if eval "$2"; then echo "pass: $1"; else echo "FAIL: $1"; fails=$((fails + 1)); fi; }
run() { printf '%s\n' "$@" | "$PLBATCH" --pattern "$work/pattern.pat" --in-root "$work/in" --out-root "$work/out" "${opts[@]}" || true; }

opts=(--force)
log=$(run finite nan)
check "finite is ok" '[[ $log == *"ok   finite"* ]] && grep -q "1" "$work/out/finite.json"'
check "nan is ok-nan, kept as printed" '[[ $log == *"ok-nan nan"* ]] && grep -q "nan" "$work/out/nan.json"'

opts=(--force --json-nonfinite=null)
log=$(run nan)
check "nan with null option is ok-null" '[[ $log == *"ok-null nan"* ]] && grep -q "null" "$work/out/nan.json" && ! grep -q "nan" "$work/out/nan.json"'

printf '{ "stale": true }\n' > "$work/out/bad.json"
opts=(--force)
log=$(run bad)
check "failure removes the stale JSON" '[[ $log == *"FAIL bad"* && ! -e $work/out/bad.json ]] && grep -q "Division by zero" "$work/out/bad.json.err"'

opts=()
log=$(run finite)
check "existing JSON is skipped without --force" '[[ $log == *"skip finite"* ]]'

# 6. Strings are UTF-8 JSON strings (PatternLanguage f910448, pinned since spec 006 T001d): valid
#    UTF-8 as is, a quote escaped, an invalid byte as \u00XX; never the old %XX percent encoding.
#    Bytes: 'Rumi A"' + U+901A U+4FE1 (E9 80 9A E4 BF A1) + a lone 0x80.
printf 'Rumi A"\xe9\x80\x9a\xe4\xbf\xa1\x80' > "$work/in/text"
printf 'char s[14] @ 0x00;\n' > "$work/string.pat"
log=$(printf 'text\n' | "$PLBATCH" --pattern "$work/string.pat" --in-root "$work/in" --out-root "$work/out" --force || true)
want=$(printf '"s": "Rumi A\\"\xe9\x80\x9a\xe4\xbf\xa1\\u0080"')
check "strings are UTF-8 JSON strings, not percent-encoded" '[[ $log == *"ok   text"* ]] && grep -qF -- "$want" "$work/out/text.json" && ! grep -qF "%20" "$work/out/text.json"'

(( fails == 0 )) || { echo "$fails check(s) failed" >&2; exit 1; }
echo "all checks passed"

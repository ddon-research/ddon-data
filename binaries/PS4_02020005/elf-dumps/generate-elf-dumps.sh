#!/usr/bin/env bash
# Generate the PS4 02020005 DDOORBIS.elf static dump set (see README.adoc).
#
# Contract: specs/001-ps4-static-dumps/contracts/generator-cli.md
#
#   generate-elf-dumps.sh [--only <id-glob>] [--skip-local] [--dry-run]
#   generate-elf-dumps.sh --verify
#   generate-elf-dumps.sh --exec <tool> <args...>
#   generate-elf-dumps.sh --publish-run <.staging/run-...>   (finish an interrupted publish)
#
# Exit status: 0 all entries ok; 1 precondition or input-guard failure (nothing published);
# 2 at least one dump failed or timed out (recorded in manifest.jsonl, the rest published).
#
# The original ELF is only read once, to make a hash-verified copy in .staging/input/. Every tool
# runs with that directory as its working directory and reads the copy.
#
# Only the preferred output per category is published. Intermediate tool outputs that feed derived
# files are recorded in the manifest (storage "staging") but not published. The earlier
# tool-comparison generator is kept as archive/generate-elf-dumps.full.sh.

set -o errexit -o nounset -o pipefail
export MSYS_NO_PATHCONV=1
export LC_ALL=C.UTF-8

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -W)  # D:/... form: native tools get MSYS_NO_PATHCONV=1
ORIG=${DDON_PS4_ELF:-D:/research/DDON-binaries/IDA9.3/PS4_DDON_02020005_2016_12_21/DDOORBIS.elf}
SDK_ROOT=${SCE_SDK_ROOT:-D:/SCE/ORBIS SDKs}
LLVM_BIN=${LLVM_BIN:-C:/msys64/ucrt64/bin}
DUMP_TIMEOUT=${DUMP_TIMEOUT:-}    # seconds; empty (default) = no time limit
LOCAL_TIMEOUT=${LOCAL_TIMEOUT:-}  # same, for local-only dumps (the DWARF info dump takes about an hour)

EXPECT_SHA=4236f598acc8f15893181455ed195e39dfa4dbfda4eeda8b56fcbd82312c63c0
EXPECT_SIZE=800622848
TXT_MAX=$((10 * 1024 * 1024))
ZST_MAX=$((50 * 1024 * 1024))

REQUIRED_COMMANDS=(jq zstd sha256sum sed rg xxd cut sort tee wc timeout uv cp mv fd stat date awk head tail mkdir cmp diff basename dirname tr)

die() { echo "error: $*" >&2; exit 1; }
jq() { command jq -b "$@"; }   # Windows jq writes CRLF unless --binary
log() { echo "[$(date +%H:%M:%S)] $*" >&2; }

# ------------------------------------------------------------------ options

ONLY='*' SKIP_LOCAL=0 DRY=0 MODE=generate
EXEC_ARGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --only) ONLY=${2:?--only needs a glob}; shift 2 ;;
    --skip-local) SKIP_LOCAL=1; shift ;;
    --dry-run) DRY=1; shift ;;
    --verify) MODE=verify; shift ;;
    --exec) MODE=exec; shift; EXEC_ARGS=("$@"); break ;;
    --publish-run) MODE=publish; PUBLISH_RUN=${2:?--publish-run needs a run directory}; shift 2 ;;
    -h|--help) sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) die "unknown option: $1" ;;
  esac
done

for c in "${REQUIRED_COMMANDS[@]}"; do
  command -v "$c" >/dev/null 2>&1 || die "required command not found: $c"
done

SDK12="$SDK_ROOT/12.000/host_tools/bin"
declare -A T=(
  [orbis-bin]="$SDK12/orbis-bin.exe"
  [orbis-strings]="$SDK12/orbis-strings.exe"
  [orbis-addr2line]="$SDK12/orbis-addr2line.exe"   # --exec only: address -> line with inline chain
  [llvm-readelf]="$LLVM_BIN/llvm-readelf.exe"
  [llvm-objdump]="$LLVM_BIN/llvm-objdump.exe"
  [llvm-dwarfdump]="$LLVM_BIN/llvm-dwarfdump.exe"
  [llvm-nm]="$LLVM_BIN/llvm-nm.exe"
  [llvm-objcopy]="$LLVM_BIN/llvm-objcopy.exe"
)
for k in "${!T[@]}"; do [ -x "${T[$k]}" ] || die "tool not executable: $k (${T[$k]})"; done
STAGE="$HERE/.staging"
STAGED_DIR="$STAGE/input"
STAGED="$STAGED_DIR/DDOORBIS.elf"
HELPER="$HERE/tools/elfslice.py"
MANIFEST="$HERE/manifest.jsonl"
ORIG_DIR=$(dirname "$ORIG")
TODAY=$(date +%F)
helper() { uv run --quiet --no-project --python 3.14 --script "$HELPER" "$@"; }

# ------------------------------------------------------------------ input

file_sha() { sha256sum "$1" | cut -d' ' -f1; }

check_input() {
  [ -f "$ORIG" ] || die "input not found: $ORIG"
  local size; size=$(stat -c %s "$ORIG")
  [ "$size" = "$EXPECT_SIZE" ] || die "input size $size != $EXPECT_SIZE"
  if [ ! -f "$STAGED" ] || [ "$(stat -c %s "$STAGED")" != "$EXPECT_SIZE" ] || [ "$(file_sha "$STAGED")" != "$EXPECT_SHA" ]; then
    [ "$DRY" = 1 ] && { log "dry-run: would copy $ORIG to $STAGED"; return; }
    [ "$(file_sha "$ORIG")" = "$EXPECT_SHA" ] || die "input SHA-256 mismatch: $ORIG"
    mkdir -p "$STAGED_DIR"
    cp "$ORIG" "$STAGED.tmp"
    [ "$(file_sha "$STAGED.tmp")" = "$EXPECT_SHA" ] || die "staged copy SHA-256 mismatch"
    mv "$STAGED.tmp" "$STAGED"
  fi
}

snapshot() { # every file in the original folder: name size mtime sha256
  local f
  for f in "$ORIG_DIR"/*; do
    [ -f "$f" ] || continue
    printf '%s\t%s\t%s\t%s\n' "$(basename "$f")" "$(stat -c %s "$f")" "$(stat -c %Y "$f")" "$(file_sha "$f")"
  done
}

# ------------------------------------------------------------------ tool identity

declare -A TVER TSHA
tool_identity() { # $1 tool key
  local k=$1 p=${T[$1]} v
  [ -n "${TVER[$k]:-}" ] && return
  case "$k" in
    orbis-bin) v=$(cd "$STAGED_DIR" && "$p" -ver 2>&1 | head -1 | tr -d '\r' | sed 's/^.*orbis-bin\.exe //; s/ [A-Z]:\\.*$//') ;;
    llvm-*) v=$("$p" --version 2>&1 | tr -d '\r' | rg -m1 -o 'LLVM version \S+') ;;
    *) v=$("$p" --version 2>&1 | head -1 | tr -d '\r') ;;
  esac
  TVER[$k]=$v
  TSHA[$k]=$(file_sha "$p")
}

# ------------------------------------------------------------------ verify / exec modes

if [ "$MODE" = verify ]; then
  [ -f "$MANIFEST" ] || die "no manifest"
  bad=0
  while IFS=$'\t' read -r id file storage sha; do
    path="$HERE/$file"
    if [ ! -f "$path" ]; then echo "MISSING $id $file"; bad=1; continue; fi
    case "$storage" in txt) got=$(sha256sum < "$path" | cut -d' ' -f1) ;; *) got=$(zstd -dcqq "$path" | sha256sum | cut -d' ' -f1) ;; esac
    [ "$got" = "$sha" ] || { echo "MISMATCH $id $file"; bad=1; }
  done < <(jq -r 'select(.kind=="tool" or .kind=="derived") | select(.storage != "staging") | [.id, .file, .storage, .output.sha256] | @tsv' "$MANIFEST")
  [ "$bad" = 0 ] && echo "verify: all published files match the manifest"
  exit "$bad"
fi

check_input

if [ "$MODE" = exec ]; then
  [ ${#EXEC_ARGS[@]} -gt 0 ] || die "--exec needs a tool"
  key=${EXEC_ARGS[0]}; [ -n "${T[$key]:-}" ] || die "unknown tool for --exec: $key (known: ${!T[*]})"
  before=$(stat -c '%n %s %Y' "$ORIG_DIR"/*)
  (cd "$STAGED_DIR" && "${T[$key]}" "${EXEC_ARGS[@]:1}") | sed 's/\r$//'
  rc=${PIPESTATUS[0]}
  [ "$before" = "$(stat -c '%n %s %Y' "$ORIG_DIR"/*)" ] || die "input folder changed during --exec"
  exit "$rc"
fi

# ------------------------------------------------------------------ run state

if [ "$MODE" = publish ]; then
  RUN=$(cd "$PUBLISH_RUN" && pwd -W)
  [ -f "$RUN/manifest.new.jsonl" ] && [ -f "$RUN/input-snapshot.before.tsv" ] || die "not a run directory: $PUBLISH_RUN"
else
  RUN="$STAGE/run-$(date +%Y%m%d-%H%M%S)"
fi
RAW="$RUN/raw"; ERR="$RUN/err"; PUB="$RUN/pub"; NEW="$RUN/manifest.new.jsonl"
declare -A OLD_SHA OLD_FILE NEW_SHA REGEN
FAILED=0
if [ -f "$MANIFEST" ]; then
  while IFS=$'\t' read -r id sha file; do OLD_SHA[$id]=$sha; OLD_FILE[$id]=$file; done \
    < <(jq -r 'select(.output.sha256 != null) | [.id, .output.sha256, (.file // "")] | @tsv' "$MANIFEST")
fi
if [ "$MODE" = publish ]; then
  while IFS=$'	' read -r id st; do
    REGEN[$id]=1; [ "$st" = ok ] || [ "$st" = null ] || FAILED=1
  done < <(jq -r '[.id, (.status // "null")] | @tsv' "$NEW")
elif [ "$DRY" = 0 ]; then
  mkdir -p "$RAW" "$ERR" "$PUB"
  : > "$NEW"
  snapshot > "$RUN/input-snapshot.before.tsv"
fi

want() { # $1 id, $2.. input ids; true if selected by --only or an input was regenerated
  local id=$1; shift
  # shellcheck disable=SC2053
  [[ $id == $ONLY ]] && return 0
  local i; for i in "$@"; do [ -n "${REGEN[$i]:-}" ] && return 0; done
  return 1
}

ensure_raw() { # make $RAW/<id>.txt available for an id produced in an earlier run
  local id=$1
  [ -f "$RAW/$id.txt" ] && return 0
  local f=${OLD_FILE[$id]:-}; [ -n "$f" ] && [ -f "$HERE/$f" ] || die "input $id is not available; regenerate it"
  case "$f" in *.zst) zstd -dcqq "$HERE/$f" > "$RAW/$id.txt" ;; *) cp "$HERE/$f" "$RAW/$id.txt" ;; esac
}

# finish <id> <cats> <role> <kind> <expected> <rc> <rel> <hint> <seconds> <toolkey|""> <argv-json> <extra-json>
finish() {
  local id=$1 cats=$2 role=$3 kind=$4 expected=$5 rc=$6 rel=$7 hint=$8 secs=$9 tkey=${10} argv=${11} extra=${12}
  local raw="$RAW/$id.txt" err="$ERR/$id.txt" sha size lines storage file stored status
  sed -i 's/\r$//' "$err"
  if [ "$role" = intermediate ]; then
    sha=$(file_sha "$raw"); size=$(stat -c %s "$raw"); lines=$(wc -l < "$raw")
    storage=staging; file=""; stored=0
  elif [ "$hint" = local ]; then
    file="local/$rel.zst"; storage=local
    sha=$(zstd -dcqq "$PUB/$file" | sha256sum | cut -d' ' -f1)
    read -r lines size < <(zstd -dcqq "$PUB/$file" | wc -lc)
    stored=$(stat -c %s "$PUB/$file")
  else
    sha=$(file_sha "$raw"); size=$(stat -c %s "$raw"); lines=$(wc -l < "$raw")
    if [ "$size" -le "$TXT_MAX" ]; then storage=txt; file=$rel; else storage=zst; file="$rel.zst"; fi
    if [ "${OLD_SHA[$id]:-}" = "$sha" ] && [ -f "$HERE/${OLD_FILE[$id]}" ] && [[ ${OLD_FILE[$id]} != local/* ]]; then
      file=${OLD_FILE[$id]}; case "$file" in *.zst) storage=zst ;; *) storage=txt ;; esac
      stored=$(stat -c %s "$HERE/$file")
    else
      mkdir -p "$(dirname "$PUB/$rel")"
      if [ "$storage" = txt ]; then
        cp "$raw" "$PUB/$file"
      else
        zstd -q -19 --long=27 "$raw" -o "$PUB/$file"
        if [ "$(stat -c %s "$PUB/$file")" -gt "$ZST_MAX" ]; then
          rm -f "${PUB:?}/$file"; file="local/$rel.zst"; storage=local
          mkdir -p "$(dirname "$PUB/$file")"
          zstd -q -10 --long=27 -T0 "$raw" -o "$PUB/$file"
        fi
      fi
      stored=$(stat -c %s "$PUB/$file")
    fi
  fi
  if [ "$rc" = "$expected" ]; then status=ok; elif [ "$rc" = 124 ]; then status=timeout; else status=failed; fi
  [ "$status" = ok ] || { FAILED=1; log "  $id: status=$status rc=$rc"; }
  local errlines errfirst errfile=null
  errlines=$(wc -l < "$err")
  errfirst=$(head -1 "$err" | cut -c1-200)
  local tooljson
  if [ -z "$tkey" ] && [ -n "${DTOOL_JSON:-}" ]; then
    tooljson=$DTOOL_JSON
  elif [ -n "$tkey" ]; then
    tooljson=$(jq -nc --arg n "$tkey" --arg p "${T[$tkey]}" --arg v "${TVER[$tkey]}" --arg s "${TSHA[$tkey]}" '{name:$n,path:$p,version:$v,sha256:$s}')
  else
    tooljson=$(jq -nc --arg p "$HELPER" --arg v "$PYVER" --arg s "$(file_sha "$HELPER")" '{name:"elfslice.py",path:"tools/elfslice.py",version:$v,sha256:$s}')
  fi
  jq -nc --arg id "$id" --arg kind "$kind" --arg cats "$cats" --arg role "$role" --arg file "$file" \
    --arg storage "$storage" --argjson tool "$tooljson" --argjson argv "$argv" \
    --arg origin "$ORIG" --arg sha "$sha" --argjson size "$size" --argjson lines "$lines" \
    --argjson stored "$stored" --argjson errfile "$errfile" --argjson errlines "$errlines" --arg errfirst "$errfirst" \
    --argjson exit "$rc" --argjson expected "$expected" --arg status "$status" --argjson secs "$secs" \
    --arg gen "$TODAY" --argjson extra "$extra" --arg esha "$EXPECT_SHA" --argjson esize "$EXPECT_SIZE" \
    '{id:$id, kind:$kind, categories:($cats|split(",")), role:$role, file:(if $file == "" then null else $file end), storage:$storage,
      tool:$tool, argv:$argv, cwd:".staging/input",
      input:{path:".staging/input/DDOORBIS.elf", origin:$origin, sha256:$esha, size:$esize},
      output:{sha256:$sha, size:$size, lines:$lines, stored_size:$stored},
      stderr:{file:$errfile, lines:$errlines, first:$errfirst},
      exit:$exit, expected_exit:$expected, status:$status, seconds:$secs, generated:$gen} + $extra' >> "$NEW"
  NEW_SHA[$id]=$sha; REGEN[$id]=1
  log "  $id -> ${file:-(staging only)} ($storage, $size bytes, $lines lines, ${secs}s)"
}

now() { date +%s.%N; }
limit() { # limit <seconds|""> <cmd...>: run with a time limit only when one is set
  local s=$1; shift
  if [ -n "$s" ]; then timeout "$s" "$@"; else "$@"; fi
}
crlf() { # strip line-final CR from the orbis-* tools (they print CRLF); LLVM output passes through
  case "$1" in orbis-*) sed 's/\r$//' ;; *) cat ;; esac
}
elapsed() { awk -v a="$1" -v b="$(now)" 'BEGIN{printf "%.2f", b-a}'; }

# dump <id> <cats> <role> <expected> <hint auto|local> <rel> <toolkey> <args...>
# SLICE=<section> pipes that section's bytes into the tool's stdin instead of naming the file.
dump() {
  local id=$1 cats=$2 role=$3 expected=$4 hint=$5 rel=$6 tkey=$7; shift 7
  want "$id" || [ "$role" = intermediate ] || return 0
  if [ "$hint" = local ] && [ "$SKIP_LOCAL" = 1 ]; then log "skip (local) $id"; return 0; fi
  local tool=${T[$tkey]} argv tmo=${DUMP_TIMEOUT:-}
  [ "$hint" = local ] && tmo=${LOCAL_TIMEOUT:-}
  if [ -n "${SLICE:-}" ]; then
    argv=$(jq -nc --arg s "$SLICE" --arg t "$tkey" '$ARGS.positional | ["elfslice.py","slice","DDOORBIS.elf","--section",$s,"|",$t] + .' --args -- "$@")
  else
    argv=$(jq -nc --arg t "$tkey" '[$t] + $ARGS.positional' --args -- "$@")
  fi
  if [ "$DRY" = 1 ]; then echo "$id: $argv -> $rel ($hint)"; return 0; fi
  tool_identity "$tkey"
  log "dump $id"
  local start rc; start=$(now)
  set +o errexit
  if [ "$hint" = local ]; then
    mkdir -p "$(dirname "$PUB/local/$rel")"
    (cd "$STAGED_DIR" && limit "$tmo" "$tool" "$@") 2>"$ERR/$id.txt" | crlf "$tkey" \
      | zstd -q -10 --long=27 -T0 -o "$PUB/local/$rel.zst"
    rc=${PIPESTATUS[0]}
  elif [ -n "${SLICE:-}" ]; then
    (cd "$STAGED_DIR" && helper slice DDOORBIS.elf --section "$SLICE" | limit "$tmo" "$tool" "$@") 2>"$ERR/$id.txt" \
      | crlf "$tkey" > "$RAW/$id.txt"
    rc=${PIPESTATUS[0]}
  else
    (cd "$STAGED_DIR" && limit "$tmo" "$tool" "$@") 2>"$ERR/$id.txt" | crlf "$tkey" > "$RAW/$id.txt"
    rc=${PIPESTATUS[0]}
  fi
  set -o errexit
  finish "$id" "$cats" "$role" tool "$expected" "$rc" "$rel" "$hint" "$(elapsed "$start")" "$tkey" "$argv" '{}'
}

# derived <id> <cats> <role> <inferred> <inputs,> <rel> <description> -- <command...>
# The command runs in $RAW (input dumps are <id>.txt there) and writes to stdout.
derived() {
  local id=$1 cats=$2 role=$3 inferred=$4 inputs=$5 rel=$6 desc=$7; shift 8
  local -a ins; IFS=, read -r -a ins <<< "$inputs"
  want "$id" "${ins[@]}" || return 0
  local argv; argv=$(jq -nc '$ARGS.positional' --args -- "$@")
  if [ "$DRY" = 1 ]; then echo "$id: derived from $inputs: $argv -> $rel"; return 0; fi
  set_dtool "$1"
  local i; for i in "${ins[@]}"; do ensure_raw "$i"; done
  log "derive $id"
  local start rc; start=$(now)
  set +o errexit
  (cd "$RAW" && "$@") 2>"$ERR/$id.txt" > "$RAW/$id.txt"
  rc=$?
  set -o errexit
  local injson="[]"
  for i in "${ins[@]}"; do
    injson=$(jq -c --arg i "$i" --arg s "${NEW_SHA[$i]:-${OLD_SHA[$i]}}" '. + [{id:$i, sha256:$s}]' <<< "$injson")
  done
  local extra; extra=$(jq -nc --argjson ins "$injson" --argjson inf "$inferred" --arg d "$desc" '{inputs:$ins, inferred:$inf, notes:$d}')
  finish "$id" "$cats" "$role" derived 0 "$rc" "$rel" auto "$(elapsed "$start")" "" "$argv" "$extra"
}

declare -A DTOOL_CACHE
set_dtool() { # tool identity for a derived command: bash -c => elfslice.py, else the named command
  local c=$1 p v
  if [ "$c" = bash ]; then DTOOL_JSON=""; return; fi
  if [ -z "${DTOOL_CACHE[$c]:-}" ]; then
    p=$(command -v "$c"); v=$("$c" --version 2>&1 | head -1 | tr -d '\r')
    DTOOL_CACHE[$c]=$(jq -nc --arg n "$c" --arg p "$p" --arg v "$v" --arg s "$(file_sha "$p")" '{name:$n,path:$p,version:$v,sha256:$s}')
  fi
  DTOOL_JSON=${DTOOL_CACHE[$c]}
}

# not_produced <id> <cats> <evidence-id> <reason>
not_produced() {
  local id=$1 cats=$2 ev=$3 reason=$4
  want "$id" "$ev" || return 0
  [ "$DRY" = 1 ] && { echo "$id: not produced ($reason)"; return 0; }
  jq -nc --arg id "$id" --arg cats "$cats" --arg ev "$ev" --arg r "$reason" --arg gen "$TODAY" \
    '{id:$id, kind:"not-produced", categories:($cats|split(",")), reason:$r, evidence:$ev, generated:$gen}' >> "$NEW"
  REGEN[$id]=1
}

if [ "$DRY" = 0 ]; then
  PYVER=$(uv run --quiet --no-project --python 3.14 python --version 2>&1 | tr -d '\r')
else
  PYVER=dry-run
fi

# ================================================================== catalogue
# Order matters: derived entries follow their inputs. The whole catalogue is one compound command,
# so bash parses it before running it (editing the script mid-run cannot shift what runs).
if [ "$MODE" = generate ]; then

# ---- headers
dump file-header.orbis-bin            file-header         primary 0 auto headers/file-header.orbis-bin.txt orbis-bin -dh DDOORBIS.elf
dump program-headers.orbis-bin        program-headers     primary 0 auto headers/program-headers.orbis-bin.txt orbis-bin -dph DDOORBIS.elf
dump sections.orbis-bin               sections            primary 0 auto headers/sections.orbis-bin.txt orbis-bin -dsh DDOORBIS.elf
dump section-sizes.orbis-bin          section-sizes       primary 0 auto headers/section-sizes.orbis-bin.txt orbis-bin -dsi DDOORBIS.elf
dump section-segment-map.orbis-bin.file section-segment-map primary 0 auto headers/section-segment-map.orbis-bin.file.txt orbis-bin -dfl DDOORBIS.elf
not_produced elf-notes.none           elf-notes           sections.orbis-bin "The ELF has no SHT_NOTE section or PT_NOTE segment (.note.GNU-stack is PROGBITS of size 0)."
not_produced symbol-versioning.none   symbol-versioning   sections.orbis-bin "The ELF has no .gnu.version* sections."

# ---- dynamic
dump dynamic.orbis-bin                dynamic,dynlib      primary 0 auto headers/dynamic.orbis-bin.txt orbis-bin -ddy DDOORBIS.elf
dump dynsym.orbis-bin                 dynsym              primary 0 auto symbols/dynsym.orbis-bin.txt orbis-bin --dump-dynsym -v DDOORBIS.elf
dump dynstr.orbis-bin                 dynstr              primary 0 auto symbols/dynstr.orbis-bin.txt orbis-bin --dump-dynstr DDOORBIS.elf

# ---- symbols
dump symtab.llvm-readelf              symtab              primary 0 auto symbols/symtab.llvm-readelf.txt llvm-readelf -s -W DDOORBIS.elf
dump symtab.llvm-nm                   symtab              intermediate 0 auto symbols/symtab.llvm-nm.txt llvm-nm -C -S --defined-only -n DDOORBIS.elf
derived functions.derived      functions    primary false symtab.llvm-nm symbols/functions.derived.txt "llvm-nm symbols of type t/T (address size type demangled-name)" -- rg '^[0-9a-f]+ [0-9a-f]+ [tT] ' symtab.llvm-nm.txt
derived data-objects.derived   data-objects primary false symtab.llvm-nm symbols/data-objects.derived.txt "llvm-nm symbols of type d/D/b/B/r/R" -- rg '^[0-9a-f]+ [0-9a-f]+ [dDbBrR] ' symtab.llvm-nm.txt
derived rtti-vtables.derived   rtti-vtables primary false symtab.llvm-readelf symbols/rtti-vtables.derived.txt "llvm-readelf symtab rows for _ZTV (vtable), _ZTI (typeinfo), _ZTS (typeinfo name)" -- rg ' _ZT[VIS]' symtab.llvm-readelf.txt
derived plt-stubs.derived      plt-stubs    primary false symtab.llvm-readelf symbols/plt-stubs.derived.txt "llvm-readelf symtab rows for linker stubs /PL* (PLT stub), /PG* (PLT GOT slot), /G* (GOT slot), /GC*" -- rg ' /(PL|PG|GC|G)\S*$' symtab.llvm-readelf.txt

# ---- relocations, RELRO, GOT
dump relocations.orbis-bin            relocations         primary 0 auto relocations/relocations.orbis-bin.txt orbis-bin -r DDOORBIS.elf
dump relro-got.llvm-objdump           relro-got           primary 0 auto relocations/relro-got.llvm-objdump.txt llvm-objdump -s -j .data.rel.ro -j .got -j .got.plt DDOORBIS.elf
dump ctors.llvm-objdump               ctors               primary 0 auto relocations/ctors.llvm-objdump.txt llvm-objdump -s -j .ctors -j .dtors DDOORBIS.elf

# ---- SCE sections
dump sce-version.orbis-bin            sce-version         primary 0 auto sce/sce-version.orbis-bin.txt orbis-bin --dump-sections=.sceversion DDOORBIS.elf
dump sce-process-param.llvm-objdump   sce-process-param,prodg-metadata,sce-comment primary 0 auto sce/sce-process-param.llvm-objdump.txt llvm-objdump -s -j .sce_process_param -j .prodg_meta_data DDOORBIS.elf

# ---- strings
SLICE=.rodata dump strings-rodata.orbis-strings      strings-rodata      intermediate 0 auto strings/strings-rodata.orbis-strings.txt orbis-strings -a -t x
SLICE=.rodata dump strings-rodata-utf8.orbis-strings strings-rodata-utf8 intermediate 0 auto strings/strings-rodata-utf8.orbis-strings.txt orbis-strings -a -t x -e S
dump strings-all.orbis-strings        strings-all         primary 0 auto strings/strings-all.orbis-strings.txt orbis-strings -a -t x DDOORBIS.elf
RODATA_VADDR=1bea460
derived strings-rodata.rebased      strings-rodata      primary false strings-rodata.orbis-strings      strings/strings-rodata.rebased.tsv "orbis-strings slice offsets rebased to virtual addresses (.rodata vaddr 0x$RODATA_VADDR)" -- bash -c "$(declare -f helper); HELPER='$HELPER'; helper rebase-strings $RODATA_VADDR < strings-rodata.orbis-strings.txt"
derived strings-rodata-utf8.rebased strings-rodata-utf8 primary false strings-rodata-utf8.orbis-strings strings/strings-rodata-utf8.rebased.tsv "orbis-strings -e S slice offsets rebased to virtual addresses" -- bash -c "$(declare -f helper); HELPER='$HELPER'; helper rebase-strings $RODATA_VADDR < strings-rodata-utf8.orbis-strings.txt"

# ---- stack
dump stack-sizes.orbis-bin            stack-sizes         primary 0 auto stack/stack-sizes.orbis-bin.txt orbis-bin -dss DDOORBIS.elf

# ---- DWARF
dump dwarf-section-sizes.llvm-dwarfdump dwarf-section-sizes primary 0 auto dwarf/dwarf-section-sizes.llvm-dwarfdump.txt llvm-dwarfdump --show-section-sizes DDOORBIS.elf
dump dwarf-statistics.llvm-dwarfdump    dwarf-statistics    primary 0 auto dwarf/dwarf-statistics.llvm-dwarfdump.json llvm-dwarfdump --statistics DDOORBIS.elf
dump dwarf-verify.llvm-dwarfdump        dwarf-verify        primary 1 auto dwarf/dwarf-verify.llvm-dwarfdump.txt llvm-dwarfdump --verify DDOORBIS.elf
dump dwarf-abbrev.llvm-dwarfdump        dwarf-abbrev        primary 0 auto dwarf/dwarf-abbrev.llvm-dwarfdump.txt llvm-dwarfdump --debug-abbrev DDOORBIS.elf
dump dwarf-loc.llvm-dwarfdump           dwarf-loc,register-locations primary 0 auto dwarf/dwarf-loc.llvm-dwarfdump.txt llvm-dwarfdump --debug-loc DDOORBIS.elf
dump dwarf-ranges.llvm-dwarfdump        dwarf-ranges        primary 0 auto dwarf/dwarf-ranges.llvm-dwarfdump.txt llvm-dwarfdump --debug-ranges DDOORBIS.elf
dump dwarf-str.llvm-dwarfdump           dwarf-str           primary 0 auto dwarf/dwarf-str.llvm-dwarfdump.txt llvm-dwarfdump --debug-str DDOORBIS.elf
dump dwarf-frame.llvm-dwarfdump         dwarf-frame         primary 0 auto dwarf/dwarf-frame.llvm-dwarfdump.txt llvm-dwarfdump --debug-frame DDOORBIS.elf
dump dwarf-cu-list.llvm-dwarfdump       dwarf-cu-list       primary 0 auto dwarf/dwarf-cu-list.llvm-dwarfdump.txt llvm-dwarfdump --debug-info --recurse-depth=0 DDOORBIS.elf
not_produced dwarf-aranges.none   dwarf-aranges   dwarf-section-sizes.llvm-dwarfdump "The ELF has no .debug_aranges section (see --show-section-sizes)."
not_produced dwarf-pubnames.none  dwarf-pubnames  dwarf-section-sizes.llvm-dwarfdump "The ELF has no .debug_pubnames section (see --show-section-sizes)."
not_produced dwarf-pubtypes.none  dwarf-pubtypes  dwarf-section-sizes.llvm-dwarfdump "The ELF has no .debug_pubtypes section (see --show-section-sizes)."
not_produced dwarf-index.none     dwarf-index     dwarf-section-sizes.llvm-dwarfdump "The ELF has no accelerator tables (.debug_names, .apple_*, .gdb_index) and no .debug_types, .debug_macinfo, .debug_rnglists or .debug_loclists."
derived dwarf-source-files.derived dwarf-source-files primary false dwarf-cu-list.llvm-dwarfdump dwarf/dwarf-source-files.derived.tsv "DW_AT_name and DW_AT_comp_dir of each compile unit, in .debug_info order" -- \
  awk 'BEGIN{print "cu_offset\tname\tcomp_dir"} /Compile Unit:/{cu=$1; sub(":","",cu)} /DW_AT_name/{n=$0; sub(/^[^(]*\("/,"",n); sub(/"\)$/,"",n)} /DW_AT_comp_dir/{d=$0; sub(/^[^(]*\("/,"",d); sub(/"\)$/,"",d); print cu "\t" n "\t" d}' dwarf-cu-list.llvm-dwarfdump.txt

# ---- DWARF line tables (.debug_line is not contiguous: each table is copied out by DW_AT_stmt_list)
if want dwarf-line.derived dwarf-cu-list.llvm-dwarfdump; then
  if [ "$DRY" = 1 ]; then echo "dwarf-line.derived: line-copy + llvm-objcopy + llvm-dwarfdump --debug-line"
  else
    ensure_raw dwarf-cu-list.llvm-dwarfdump
    DTOOL_JSON=""
    L="$RUN/line"; mkdir -p "$L"
    helper line-copy "$STAGED" "$RAW/dwarf-cu-list.llvm-dwarfdump.txt" "$L/line.bin" "$RAW/dwarf-line-map.derived.txt" "$RAW/dwarf-line-gaps.derived.txt" 2>"$ERR/dwarf-line-copy.txt"
    (cd "$L" && "${T[llvm-objcopy]}" -I binary -O elf64-x86-64 --rename-section .data=.debug_line,contents,readonly line.bin line.elf)
    tool_identity llvm-dwarfdump; tool_identity llvm-objcopy
    start=$(now); set +o errexit
    (cd "$L" && "${T[llvm-dwarfdump]}" --debug-line line.elf) 2>"$ERR/dwarf-line.derived.txt" | sed 's/\r$//' > "$RAW/dwarf-line.derived.txt"
    rc=${PIPESTATUS[0]}; set -o errexit
    : > "$ERR/dwarf-line-map.derived.txt"; : > "$ERR/dwarf-line-gaps.derived.txt"
    line_ins=$(jq -nc --arg s "${NEW_SHA[dwarf-cu-list.llvm-dwarfdump]:-${OLD_SHA[dwarf-cu-list.llvm-dwarfdump]}}" '[{id:"dwarf-cu-list.llvm-dwarfdump", sha256:$s}]')
    finish dwarf-line-map.derived dwarf-line supplement derived 0 0 dwarf/dwarf-line-map.derived.tsv auto 0 "" \
      '["elfslice.py","line-copy","DDOORBIS.elf","dwarf-cu-list.llvm-dwarfdump.txt","line.bin","map.tsv","gaps.tsv"]' \
      "$(jq -nc --argjson i "$line_ins" '{inputs:$i, inferred:false, notes:"orig_offset (in .debug_line) -> new_offset (in the contiguous copy) for every CU line table"}')"
    finish dwarf-line-gaps.derived dwarf-line-gaps primary derived 0 0 dwarf/dwarf-line-gaps.derived.tsv auto 0 "" \
      '["elfslice.py","line-copy","DDOORBIS.elf","dwarf-cu-list.llvm-dwarfdump.txt","line.bin","map.tsv","gaps.tsv"]' \
      "$(jq -nc --argjson i "$line_ins" '{inputs:$i, inferred:false, notes:"byte ranges of .debug_line between line tables (offset, length, any non-zero byte, first 16 bytes)"}')"
    finish dwarf-line.derived dwarf-line primary derived 0 "$rc" dwarf/dwarf-line.derived.txt auto "$(elapsed "$start")" llvm-dwarfdump \
      '["elfslice.py line-copy","|","llvm-objcopy","-I","binary","-O","elf64-x86-64","--rename-section",".data=.debug_line,contents,readonly","line.bin","line.elf","|","llvm-dwarfdump","--debug-line","line.elf"]' \
      "$(jq -nc --argjson i "$line_ins" '{inputs:$i, inferred:false, notes:"All 2305 CU line tables, copied byte for byte into a contiguous .debug_line and decoded; table offsets are new_offset values, see dwarf-line-map.derived"}')"
  fi
fi

# ---- registers and unwind
dump unwind-cfa.llvm-readelf          unwind-cfa          primary 0 auto registers/unwind-cfa.llvm-readelf.txt llvm-readelf --unwind DDOORBIS.elf
derived register-usage.derived register-usage primary false dwarf-loc.llvm-dwarfdump registers/register-usage.derived.tsv "count of DW_OP_reg*/DW_OP_breg* register operands in .debug_loc location lists" -- \
  bash -c "$(declare -f helper); HELPER='$HELPER'; helper register-usage dwarf-loc.llvm-dwarfdump.txt"

# ---- hashes
derived section-hashes.derived section-hashes primary false file-header.orbis-bin headers/section-hashes.derived.tsv "SHA-256 of each section's file bytes (NOBITS: empty)" -- \
  bash -c "$(declare -f helper); HELPER='$HELPER'; helper hashes '$STAGED' sections"
derived segment-hashes.derived segment-hashes primary false file-header.orbis-bin headers/segment-hashes.derived.tsv "SHA-256 of each program header's file bytes" -- \
  bash -c "$(declare -f helper); HELPER='$HELPER'; helper hashes '$STAGED' segments"

# ---- string references (inferred: RELATIVE relocation addend = start of a .rodata string)
derived string-refs.derived string-refs primary true relocations.orbis-bin,strings-rodata.rebased relocations/string-refs.derived.tsv "INFERRED: R_X86_64_RELATIVE slots whose addend is the start of a .rodata string" -- \
  bash -c "$(declare -f helper); HELPER='$HELPER'; helper string-refs relocations.orbis-bin.txt strings-rodata.rebased.txt"

# ---- local-only (gitignored)
dump dwarf-info.llvm-dwarfdump        dwarf-info          primary 0 local dwarf-info.llvm-dwarfdump.txt llvm-dwarfdump --debug-info -v DDOORBIS.elf
dump disassembly.llvm-objdump         disassembly         primary 0 local disassembly.llvm-objdump.txt llvm-objdump -d -l --demangle -w DDOORBIS.elf

# ---- committed stand-ins (summaries) for the local-only dumps
standin() { # <id> <cats> <input-id> <rel> <kind> <desc>
  local id=$1 cats=$2 in=$3 rel=$4 kind=$5 desc=$6
  want "$id" "$in" || return 0
  [ "$DRY" = 1 ] && { echo "$id: stand-in for $in"; return 0; }
  local f=local/$in.txt.zst src
  if [ -f "$PUB/$f" ]; then src="$PUB/$f"; elif [ -f "$HERE/$f" ]; then src="$HERE/$f"; else log "skip $id: $f not available"; return 0; fi
  log "derive $id"
  DTOOL_JSON=""
  local start rc; start=$(now)
  set +o errexit
  zstd -dcqq "$src" | helper standin "$kind" > "$RAW/$id.txt" 2>"$ERR/$id.txt"
  rc=${PIPESTATUS[1]}
  set -o errexit
  local s=${NEW_SHA[$in]:-${OLD_SHA[$in]:-}}
  local extra; extra=$(jq -nc --arg i "$in" --arg s "$s" --arg d "$desc" '{inputs:[{id:$i, sha256:$s}], inferred:false, notes:$d}')
  finish "$id" "$cats" supplement derived 0 "$rc" "$rel" auto "$(elapsed "$start")" "" "[\"elfslice.py\",\"standin\",\"$kind\"]" "$extra"
}
standin disassembly.standin        disassembly       disassembly.llvm-objdump         derived/disassembly.standin.tsv        disassembly "instruction count per function in the local llvm-objdump disassembly"

fi  # MODE = generate

[ "$DRY" = 1 ] && { log "dry-run: tools and input OK, nothing written"; exit 0; }

# ------------------------------------------------------------------ guard and publish

snapshot > "$RUN/input-snapshot.after.tsv"
if ! cmp -s "$RUN/input-snapshot.before.tsv" "$RUN/input-snapshot.after.tsv"; then
  diff "$RUN/input-snapshot.before.tsv" "$RUN/input-snapshot.after.tsv" >&2 || true
  die "input folder changed during the run; nothing published"
fi

meta=$(jq -nc --arg gen "$TODAY" --arg z "$(zstd --version | head -1)" --arg p "$PYVER" --arg u "$(uv --version)" \
  --arg s "$(file_sha "$HERE/generate-elf-dumps.sh")" \
  '{id:"run.meta", kind:"meta", generated:$gen, zstd_version:$z, python_version:$p, uv_version:$u, script_sha256:$s, volatile:["generated","seconds","stderr.first"]}')

{
  echo "$meta"
  if [ -f "$MANIFEST" ]; then
    jq -s 'map(.id)' "$NEW" > "$RUN/new-ids.json"
    jq -c --slurpfile new "$RUN/new-ids.json" 'select(.id != "run.meta") | select(.id as $i | ($new[0] | index($i)) | not)' "$MANIFEST"
  fi
  cat "$NEW"
} | jq -sc 'sort_by(if .id == "run.meta" then "" else .id end) | .[]' > "$RUN/manifest.jsonl"

# move changed files into place
( cd "$PUB" && fd -t f -H . ) | while IFS= read -r f; do
  mkdir -p "$(dirname "$HERE/$f")"
  mv -f "$PUB/$f" "$HERE/$f"
done
# remove published files of regenerated ids whose storage class changed
jq -r 'select(.file != null) | .file' "$RUN/manifest.jsonl" | sort > "$RUN/files.keep"
for id in "${!REGEN[@]}"; do
  old=${OLD_FILE[$id]:-}
  if [ -n "$old" ] && ! rg -qxF "$old" "$RUN/files.keep" && [ -f "$HERE/$old" ]; then rm -f "${HERE:?}/$old"; fi
done
mv -f "$RUN/manifest.jsonl" "$MANIFEST.tmp" && mv -f "$MANIFEST.tmp" "$MANIFEST"
mkdir -p "$STAGE/last"
cp "$RUN/input-snapshot.before.tsv" "$RUN/input-snapshot.after.tsv" "$STAGE/last/"
echo "${RUN##*/}" > "$STAGE/last/run"
log "published; manifest has $(wc -l < "$MANIFEST") entries"
if [ "$FAILED" = 1 ]; then log "some dumps failed or timed out (see manifest status)"; exit 2; fi
exit 0

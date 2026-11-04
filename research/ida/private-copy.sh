#!/usr/bin/env bash
# Make an agent's private copy of a DDON IDA 9.5 database for the headless ida-mcp server.
#
# Usage: bash research/ida/private-copy.sh <pc|pc-accepted|pc-handlers|ps4> <name>
#   pc           PC 03040008   D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/2022_01_29_DDO_DUMP_FIX.exe.i64
#   pc-accepted  PC 03040008   ddon-hook's accepted database: `accepted_PC.path` of
#                D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/CURRENT-RECOVERY.json, refused
#                unless it lies inside PC_DDON_03040008/ and its sha256 equals `accepted_PC.sha256`
#   pc-handlers  PC 03040008   the annotated database: PC_DDON_03040008/spec007-packet-handlers-20261103-wave2/
#                2022_01_29_DDO_DUMP_FIX.exe.i64
#   ps4          PS4 02020005  D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/DDOORBIS.elf.i64
#   name letters, digits, '_' and '-' (at most 64); the copy goes to
#        <database folder>/ddon-data-<name>/<database file>, beside the original as ddon-hook's
#        feature copies are (never inside this repository). For pc-accepted and pc-handlers the
#        database folder is PC_DDON_03040008/ itself, not the folder that holds the database.
#
# The ida-mcp worker saves what it opens (on close, on shutdown, after execute_python), so it must
# never open the user's .i64, which may be open in the IDA GUI. The original is only read: hashed
# and copied. An existing copy of the same name is replaced only if nothing holds it open.
# Prints the copy's path (forward slashes) for open_database.
#
# Test only: DDON_RECOVERY_JSON names another CURRENT-RECOVERY.json (research/ida/tests/private-copy.sh).
# The accepted path must then lie inside that file's folder, and the copy goes there; the guard_ida
# hook still allows opening only copies under the real IDA9.5 folders. DDON_PC_FOLDER likewise names
# another PC_DDON_03040008 folder for pc-handlers.
set -o errexit -o nounset -o pipefail

die() { echo "ERROR: $*" >&2; exit 2; }
for cmd in sha256sum cp mkdir rm dirname basename; do
  command -v "$cmd" >/dev/null 2>&1 || die "required command '$cmd' not found"
done

# D:\a\b or D:/a/b or /d/a/b -> /d/a/b
posix_path() {
  local p=${1//\\//}
  if [[ $p =~ ^([A-Za-z]):/(.*)$ ]]; then p="/${BASH_REMATCH[1],,}/${BASH_REMATCH[2]}"; fi
  printf '%s' "$p"
}

[[ $# -eq 2 ]] || die "usage: $0 <pc|pc-accepted|pc-handlers|ps4> <name>"
want=""
pc_folder=""
case $1 in
  pc)  original=/d/research/DDON-binaries/IDA9.5/PC_DDON_03040008/2022_01_29_DDO_DUMP_FIX.exe.i64 ;;
  ps4) original=/d/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/DDOORBIS.elf.i64 ;;
  pc-accepted) ;;
  pc-handlers)
    pc_folder=$(posix_path "${DDON_PC_FOLDER:-/d/research/DDON-binaries/IDA9.5/PC_DDON_03040008}")
    original=$pc_folder/spec007-packet-handlers-20261103-wave2/2022_01_29_DDO_DUMP_FIX.exe.i64
    ;;
  *)   die "target must be pc, pc-accepted, pc-handlers or ps4, got '$1'" ;;
esac
[[ $2 =~ ^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$ ]] || die "name must be letters, digits, '_' and '-' (at most 64)"

if [[ $1 == pc-accepted ]]; then
  command -v jq >/dev/null 2>&1 || die "required command 'jq' not found"
  recovery=$(posix_path "${DDON_RECOVERY_JSON:-/d/research/DDON-binaries/IDA9.5/PC_DDON_03040008/CURRENT-RECOVERY.json}")
  [[ -f $recovery ]] || die "recovery record not found: $recovery"
  root=$(dirname "$recovery")
  original=$(jq -er '.accepted_PC.path | strings' "$recovery") || die "$recovery has no accepted_PC.path"
  want=$(jq -er '.accepted_PC.sha256 | strings' "$recovery") || die "$recovery has no accepted_PC.sha256"
  [[ $want =~ ^[0-9a-f]{64}$ ]] || die "accepted_PC.sha256 is not a sha256: '$want'"
  original=$(posix_path "$original")
  [[ $original != *"/../"* && $original != *"/./"* ]] || die "accepted path has '.' or '..' parts: $original"
  root_lc=${root,,} original_lc=${original,,}
  [[ $original_lc == "$root_lc"/* ]] || die "accepted path is outside $root/: $original"
  [[ ! -L $original ]] || die "accepted database is a link: $original"
fi
[[ -f $original ]] || die "database not found: $original"

if [[ $1 == pc-accepted ]]; then
  got=$(sha256sum "$original" | cut -d' ' -f1)
  [[ $got == "$want" ]] || die "accepted database differs from its record ($got != $want): nothing copied"
  folder="$root/ddon-data-$2"
else
  want=$(sha256sum "$original" | cut -d' ' -f1)
  folder="${pc_folder:-$(dirname "$original")}/ddon-data-$2"
fi
copy="$folder/$(basename "$original")"
[[ ! -L $folder ]] || die "$folder is a link: refused, nothing deleted"

if [[ -e $folder ]]; then
  # The unpacked .id0/.id1/... files exist only while a worker holds the copy open.
  for part in "$folder"/*.id0 "$folder"/*.id1 "$folder"/*.nam "$folder"/*.til; do
    [[ ! -e $part ]] || die "$folder is open in a worker ($part): reuse it (list_databases) or pick another name"
  done
  rm -rf -- "$folder"
fi
mkdir -p -- "$folder"
cp -- "$original" "$copy"
got=$(sha256sum "$copy" | cut -d' ' -f1)
[[ $got == "$want" ]] || die "copy differs from the original ($got != $want)"
echo "${copy/#\/d\//D:/}"

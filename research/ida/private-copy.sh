#!/usr/bin/env bash
# Make an agent's private copy of a DDON IDA 9.5 database for the headless ida-mcp server.
#
# Usage: bash research/ida/private-copy.sh <pc|ps4> <name>
#   pc   PC 03040008   D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/2022_01_29_DDO_DUMP_FIX.exe.i64
#   ps4  PS4 02020005  D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/DDOORBIS.elf.i64
#   name letters, digits, '_' and '-' (at most 64); the copy goes to
#        <database folder>/ddon-data-<name>/<database file>, beside the original as ddon-hook's
#        feature copies are (never inside this repository).
#
# The ida-mcp worker saves what it opens (on close, on shutdown, after execute_python), so it must
# never open the user's .i64, which may be open in the IDA GUI. The original is only read: hashed
# and copied. An existing copy of the same name is replaced only if nothing holds it open.
# Prints the copy's path (forward slashes) for open_database.
set -o errexit -o nounset -o pipefail

die() { echo "ERROR: $*" >&2; exit 2; }
for cmd in sha256sum cp mkdir rm dirname basename; do
  command -v "$cmd" >/dev/null 2>&1 || die "required command '$cmd' not found"
done

[[ $# -eq 2 ]] || die "usage: $0 <pc|ps4> <name>"
case $1 in
  pc)  original=/d/research/DDON-binaries/IDA9.5/PC_DDON_03040008/2022_01_29_DDO_DUMP_FIX.exe.i64 ;;
  ps4) original=/d/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/DDOORBIS.elf.i64 ;;
  *)   die "target must be pc or ps4, got '$1'" ;;
esac
[[ $2 =~ ^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$ ]] || die "name must be letters, digits, '_' and '-' (at most 64)"
[[ -f $original ]] || die "database not found: $original"

folder="$(dirname "$original")/ddon-data-$2"
copy="$folder/$(basename "$original")"
[[ ! -L $folder ]] || die "$folder is a link: refused, nothing deleted"

want=$(sha256sum "$original" | cut -d' ' -f1)
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

#!/usr/bin/env bash
# 008 T003: run read_funcs.py headless on a private copy (read-only: the script sets DBFL_KILL).
# usage: run.sh <copy.i64> <OUT.txt> <log> [VA-or-name ...]   (VAs or names)
set -o errexit -o nounset -o pipefail
IDAT="C:/Program Files/IDA Professional 9.5/idat.exe"
[ -x "$IDAT" ] || { echo "idat not found: $IDAT" >&2; exit 2; }
db=$1 out=$2 log=$3; shift 3
here=$(cd "$(dirname "$0")" && pwd -W)
MSYS_NO_PATHCONV=1 "$IDAT" -A -L"$log" -S"$here/read_funcs.py $out $*" "$db"

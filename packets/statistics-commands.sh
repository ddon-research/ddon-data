#!/usr/bin/env bash
#
# statistics-commands.sh
#
# Single-pass packet statistics over the Arrowgene CLI annotated dumps in decrypted_annotated/.
#
# Writes (next to this script, replaced atomically only after a successful run):
#   decrypted-tcp-streams-unique-{c2s,s2c,c2l,l2c,unknown}-packets-count.txt
#       "(group.id.sub) NAME,count" per packet type, by direction
#   packets-missing-structure-dumps.txt
#       "NAME group.id.sub" for packet types the CLI has no C# structure for (no StructDump line)
#   packets-structure-parse-failures.txt
#       "(group.id.sub) NAME,count" for packets whose C# structure failed to parse
#       (StructDump line without a JSON structure; see README-decrypt-annotate-streams.adoc)
#   decrypted-tcp-streams-unique-*-packets.txt   only with -k
#
# Usage:
#   ./statistics-commands.sh [-k|--keep-unique] [-f|--freq-sort] [-h|--help]
#
set -o errexit
set -o nounset
set -o pipefail

ANNOTATED_DIR=${ANNOTATED_DIR:-decrypted_annotated}
DIRECTIONS=(c2s s2c c2l l2c unknown)

print_help() {
  sed -n '3,19p' "$0" | sed 's/^# \{0,1\}//'
  cat <<'USAGE'
Options:
  -k, --keep-unique    Also write the unique packet lists (decrypted-tcp-streams-unique-*-packets.txt).
  -f, --freq-sort      Sort count files by count (descending), then by key. Default: by key.
  -h, --help           Show this help and exit.
USAGE
}

die() { echo "ERROR: $*" >&2; exit 2; }

parse_args() {
  KEEP_UNIQUE=0
  FREQ_SORT=0
  while (( $# )); do
    case "$1" in
      -k|--keep-unique) KEEP_UNIQUE=1; shift ;;
      -f|--freq-sort)   FREQ_SORT=1;   shift ;;
      -h|--help)        print_help; exit 0 ;;
      *) echo "Unknown option: $1" >&2; print_help >&2; exit 2 ;;
    esac
  done
}

validate_env() {
  local cmd
  for cmd in awk sort mktemp mv rm sed; do
    command -v "$cmd" >/dev/null 2>&1 || die "required command '$cmd' not found (use Git Bash, MSYS2, or WSL)"
  done
  [[ -d "$ANNOTATED_DIR" ]] || die "annotated directory not found: $ANNOTATED_DIR"
  shopt -s nullglob
  INPUTS=("$ANNOTATED_DIR"/*.yaml.annotated.txt)
  shopt -u nullglob
  (( ${#INPUTS[@]} > 0 )) || die "no *.yaml.annotated.txt files in $ANNOTATED_DIR"

  # A stream must be present either unsplit or as _1.._N pieces, never both (double counting).
  local dupes
  dupes=$(printf '%s\n' "${INPUTS[@]##*/}" | sed -E 's/(_[0-9]+)?\.yaml\.annotated\.txt$//' \
    | LC_ALL=C sort | uniq -c | awk '$1 > 1 { print $2 }' \
    | while read -r stem; do
        [[ -e "$ANNOTATED_DIR/$stem.yaml.annotated.txt" ]] && echo "$stem"
      done || true)
  [[ -z "$dupes" ]] || die "streams present both unsplit and split (would be counted twice): $dupes"
}

# One awk pass. A packet starts at a header line
#   "Client #000041 (18.0.1) C2S_..._REQ Pcap(No:10289 Ts:...)"
# and ends at the next header or end of file. Only header lines are counted; the packet's
# StructDump line (if any) tells whether a C# structure exists and whether it parsed.
run_awk() {
  LC_ALL=C awk -v outdir="$1" -v keep="$KEEP_UNIQUE" '
  function finish() {
    if (name == "") return
    if (!has_struct) missing[name " " id] = 1
    else if (!struct_ok) failed["(" id ") " name]++
    name = ""
  }
  function direction(n) {
    p = substr(n, 1, 4)
    if (p == "C2S_") return "c2s"
    if (p == "S2C_") return "s2c"
    if (p == "C2L_") return "c2l"
    if (p == "L2C_") return "l2c"
    return "unknown"
  }
  FNR == 1 { finish() }
  /^(Client|Server) #[0-9]+ \([0-9]+\.[0-9]+\.[0-9]+\) [^ ]+ Pcap\(/ {
    finish()
    match($0, /\([0-9]+\.[0-9]+\.[0-9]+\)/)
    id = substr($0, RSTART + 1, RLENGTH - 2)
    rest = substr($0, RSTART + RLENGTH + 1)
    name = substr(rest, 1, index(rest, " ") - 1)
    has_struct = 0; struct_ok = 0
    key = "(" id ") " name
    counts[direction(name) SUBSEP key]++
    headers++
    next
  }
  name != "" && /^StructDump:/ {
    has_struct = 1
    struct_ok = ($0 ~ /^StructDump: \{/)
  }
  END {
    finish()
    for (k in counts) {
      split(k, a, SUBSEP)
      print a[2] "," counts[k] > (outdir "/decrypted-tcp-streams-unique-" a[1] "-packets-count.txt")
      if (keep) print a[2] > (outdir "/decrypted-tcp-streams-unique-" a[1] "-packets.txt")
    }
    for (k in missing) print k > (outdir "/packets-missing-structure-dumps.txt")
    for (k in failed) print k "," failed[k] > (outdir "/packets-structure-parse-failures.txt")
    printf "%d packets, %d packet types, %d without structure, %d failing to parse\n",
      headers, length(counts), length(missing), length(failed) > "/dev/stderr"
  }
  ' "${INPUTS[@]}"
}

sort_outputs() {
  local f
  for f in "$1"/*.txt; do
    if [[ "$f" == *-count.txt || "$f" == *parse-failures.txt ]] && (( FREQ_SORT )); then
      LC_ALL=C sort -t, -k2,2nr -k1,1 -o "$f" "$f"
    else
      LC_ALL=C sort -o "$f" "$f"
    fi
  done
}

main() {
  parse_args "$@"
  cd "$(dirname "${BASH_SOURCE[0]}")"
  validate_env

  local d f
  # Global, not local: the EXIT trap runs after main has returned.
  STAGE=$(mktemp -d ./.statistics.XXXXXX)
  trap 'rm -rf "${STAGE:?}"' EXIT
  local stage=$STAGE

  # Every output exists even when empty, so a vanished category is visible as an empty file.
  for d in "${DIRECTIONS[@]}"; do
    : >"$stage/decrypted-tcp-streams-unique-$d-packets-count.txt"
    if (( KEEP_UNIQUE )); then : >"$stage/decrypted-tcp-streams-unique-$d-packets.txt"; fi
  done
  : >"$stage/packets-missing-structure-dumps.txt"
  : >"$stage/packets-structure-parse-failures.txt"

  echo "Reading ${#INPUTS[@]} annotated dump(s) from $ANNOTATED_DIR" >&2
  run_awk "$stage"
  sort_outputs "$stage"

  # Publish only after everything succeeded. Drop an empty "unknown" file instead of adding it.
  (( KEEP_UNIQUE )) || rm -f ./decrypted-tcp-streams-unique-*-packets.txt
  for f in "$stage"/*.txt; do
    if [[ ! -s "$f" && "$f" == *-unknown-* ]]; then rm -f "./${f##*/}"; continue; fi
    mv -f "$f" "./${f##*/}"
  done
  echo "Done (unique lists kept: $KEEP_UNIQUE; freq-sort: $FREQ_SORT)." >&2
}

main "$@"

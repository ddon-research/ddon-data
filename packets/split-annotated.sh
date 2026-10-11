#!/usr/bin/env bash
# Split an Arrowgene CLI annotated dump into pieces of at most MAX_BYTES, cutting only between
# packets so no packet dump is torn across files. Automates `split -C 50M` plus manually moving
# each cut-off packet into the next piece.
#
# Usage: ./split-annotated.sh [--force] <annotated.txt> [out_dir] [max_bytes]
#   annotated.txt  e.g. encrypted_streams/stream85-marked.pcapng_tcp-stream-11.yaml.annotated.txt
#   out_dir        default: decrypted_annotated
#   max_bytes      default: 52428800 (50 MiB, the same unit as `split -C 50M`)
#   --force        replace existing pieces for this stream in out_dir
#
# Output: <stream>_1.yaml.annotated.txt ... <stream>_N.yaml.annotated.txt, or the unsuffixed
# <stream>.yaml.annotated.txt when the dump already fits. Pieces are byte-exact: concatenating
# them reproduces the input (verified with cmp before anything is published).
set -o errexit
set -o nounset
set -o pipefail

die() { echo "ERROR: $*" >&2; exit 2; }
usage() { sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//' >&2; exit 2; }
for cmd in awk cat cmp ls mkdir mktemp mv rm sort stat tail truncate; do
  command -v "$cmd" >/dev/null 2>&1 || die "required command '$cmd' not found (use Git Bash, MSYS2, or WSL)"
done

FORCE=0
if [[ ${1:-} == --force ]]; then FORCE=1; shift; fi
[[ $# -ge 1 && $# -le 3 ]] || usage
INPUT=$1
OUT_DIR=${2:-decrypted_annotated}
MAX_BYTES=${3:-52428800}

[[ -f "$INPUT" ]] || die "input '$INPUT' not found"
[[ "$INPUT" == *.yaml.annotated.txt ]] || die "input must be a *.yaml.annotated.txt dump"
[[ -d "$OUT_DIR" ]] || die "output directory '$OUT_DIR' not found"
if [[ ! "$MAX_BYTES" =~ ^[0-9]+$ ]] || (( MAX_BYTES < 1 )); then
  die "max_bytes must be a positive integer"
fi

stem=$(basename "$INPUT" .yaml.annotated.txt)
existing=("$OUT_DIR/$stem".yaml.annotated.txt "$OUT_DIR/$stem"_[0-9]*.yaml.annotated.txt)
present=()
for f in "${existing[@]}"; do [[ -e "$f" ]] && present+=("$f"); done
if (( ${#present[@]} > 0 && FORCE == 0 )); then
  printf 'existing piece: %s\n' "${present[@]}" >&2
  die "pieces for '$stem' already exist in '$OUT_DIR' (pass --force to replace them)"
fi

# Stage next to the output so the final mv is a rename on the same filesystem.
stage=$(mktemp -d "$OUT_DIR/.split-$stem.XXXXXX")
trap 'rm -rf "${stage:?}"' EXIT

size=$(stat -c %s "$INPUT")
if (( size <= MAX_BYTES )); then
  cat "$INPUT" >"$stage/$stem.yaml.annotated.txt"
else
  # A packet starts at a "Client #NNNNNN (g.h.s) NAME" or "Server #NNNNNN (...)" line. Buffer one
  # packet at a time and start a new piece when adding it would exceed MAX_BYTES. LC_ALL=C makes
  # length() count bytes; RS/ORS are "\n" so CR bytes inside the dump are kept as they are.
  # BINMODE=3: MSYS/Git Bash gawk otherwise opens files in text mode and silently drops the CR of
  # every CRLF, corrupting the dump (the cmp check below catches that).
  LC_ALL=C awk -v BINMODE=3 -v max="$MAX_BYTES" -v prefix="$stage/${stem}_" '
    function flush_packet() {
      if (pkt_len == 0) return
      if (piece == 0 || (piece_len > 0 && piece_len + pkt_len > max)) {
        if (piece > 0) close(out)
        piece++; piece_len = 0
        out = prefix piece ".yaml.annotated.txt"
      }
      printf "%s", pkt > out
      piece_len += pkt_len; pkt = ""; pkt_len = 0
    }
    /^(Client|Server) #[0-9]+ \(/ { flush_packet() }
    { pkt = pkt $0 "\n"; pkt_len += length($0) + 1 }
    END { flush_packet(); if (piece > 0) close(out) }
  ' "$INPUT"
  # awk terminates the last line with "\n"; drop it again if the input did not end with one.
  if [[ -n $(tail -c 1 "$INPUT") ]]; then
    last=$(ls "$stage" | sort -V | tail -1)
    truncate -s -1 "$stage/$last"
  fi
fi

pieces=()
while IFS= read -r p; do pieces+=("$stage/$p"); done < <(ls "$stage" | sort -V)
(( ${#pieces[@]} > 0 )) || die "no output produced"
cmp -s "$INPUT" <(cat "${pieces[@]}") || die "concatenated pieces differ from the input; nothing published"

for p in "${pieces[@]}"; do
  psize=$(stat -c %s "$p")
  (( psize <= MAX_BYTES )) || echo "WARNING: $(basename "$p") is $psize bytes: a single packet exceeds $MAX_BYTES" >&2
done

# Publish: remove the old pieces of this stream only, then move the new ones into place.
for f in "${present[@]}"; do rm -f -- "${f:?}"; done
for p in "${pieces[@]}"; do
  mv -- "$p" "$OUT_DIR/"
  echo "$OUT_DIR/$(basename "$p") $(stat -c %s "$OUT_DIR/$(basename "$p")") bytes"
done
echo "Split $INPUT ($size bytes) into ${#pieces[@]} piece(s); cat of the pieces matches the input."

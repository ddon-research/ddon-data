#!/usr/bin/env bash
#
# fast-count-packets.sh
#
# Single-pass normalization + counting for decrypted packet annotations.
# - much faster than grepping per-unique-line (one awk pass instead)
# - optional: keep unique packet text files (-k)
# - optional: sort count files by frequency (-f)
#
# Usage:
#   ./fast-count-packets.sh [-k|--keep-unique] [-f|--freq-sort] [-h|--help]
#
set -euo pipefail

# ---- Configuration (change if you must) -------------------------------------
ANNOTATED_DIR="decrypted_annotated"
OUTDIR="../"
# -----------------------------------------------------------------------------


# Print help and exit
print_help() {
  cat <<'USAGE'
fast-count-packets.sh

Single-pass normalize & count annotated packet lines.

Usage:
  fast-count-packets.sh [options]

Options:
  -k, --keep-unique    Write and keep the unique packet files:
                       decrypted-tcp-streams-unique-*-packets.txt
  -f, --freq-sort      Sort the count files by frequency (descending).
                       Default sorting is alphabetical by key.
  -h, --help           Show this help and exit.

Behavior:
  - Reads files under packets/decrypted_annotated (same as your old script).
  - Produces count files in the parent directory (same names as before).
  - Keeps the unique files only if -k is provided.
USAGE
}


# Parse CLI flags
parse_args() {
  KEEP_UNIQUE=0
  FREQ_SORT=0

  while (( "$#" )); do
    case "$1" in
      -k|--keep-unique) KEEP_UNIQUE=1; shift ;;
      -f|--freq-sort)   FREQ_SORT=1;   shift ;;
      -h|--help)        print_help; exit 0 ;;
      *) echo "Unknown option: $1" >&2; print_help; exit 2 ;;
    esac
  done
}


# Ensure environment (directories, required tools)
validate_env() {
  if [ ! -d "$ANNOTATED_DIR" ]; then
    echo "Error: annotated directory not found: $ANNOTATED_DIR" >&2
    exit 1
  fi
  # awk and sort are required; available on any reasonable POSIX system
  if ! command -v awk >/dev/null 2>&1; then
    echo "Error: awk not found" >&2
    exit 1
  fi
  if ! command -v sort >/dev/null 2>&1; then
    echo "Error: sort not found" >&2
    exit 1
  fi
}


# Remove old output files produced by previous runs
cleanup_old_outputs() {
  rm -f "${OUTDIR}decrypted-tcp-streams-unique-"*"-packets.txt" \
        "${OUTDIR}decrypted-tcp-streams-unique-"*"-packets-count.txt"
}


# Run the single-pass awk normalization + counting
# Writes per-tag count files and (optionally) per-tag unique files.
run_awk() {
  cd "$ANNOTATED_DIR"

  # Pass keep flag into awk as numeric 0/1
  awk -v outdir="$OUTDIR" -v keep="$KEEP_UNIQUE" '
  # normalize(s): trim, remove "Server"/"Client", drop "Pcap..." suffix, remove "#digits", collapse whitespace
  function normalize(s) {
    gsub(/Server|Client/,"",s)
    sub(/Pcap.*$/,"",s)
    gsub(/#[0-9]+/,"",s)
    gsub(/[[:space:]]+/," ",s)
    gsub(/^[[:space:]]+|[[:space:]]+$/,"",s)
    return s
  }

  {
    tag = ""
    if (index($0,"C2S")) tag="C2S"
    else if (index($0,"S2C")) tag="S2C"
    else if (index($0,"L2C")) tag="L2C"
    else if (index($0,"C2L")) tag="C2L"
    else if (index($0,"Unknown Pcap")) tag="Unknown"
    else next

    key = normalize($0)
    if (key == "") next

    counts[tag SUBSEP key]++

    if (keep == 1) {
      # print unique keys once per tag
      if (!printed[tag SUBSEP key]++) {
        if (tag == "C2S") fname = outdir "decrypted-tcp-streams-unique-c2s-packets.txt"
        else if (tag == "S2C") fname = outdir "decrypted-tcp-streams-unique-s2c-packets.txt"
        else if (tag == "L2C") fname = outdir "decrypted-tcp-streams-unique-l2c-packets.txt"
        else if (tag == "C2L") fname = outdir "decrypted-tcp-streams-unique-c2l-packets.txt"
        else fname = outdir "decrypted-tcp-streams-unique-unknown-packets.txt"
        print key >> fname
      }
    }
  }

  END {
    for (k in counts) {
      split(k, a, SUBSEP)
      tag = a[1]; key = a[2]
      if (tag == "C2S") fname = outdir "decrypted-tcp-streams-unique-c2s-packets-count.txt"
      else if (tag == "S2C") fname = outdir "decrypted-tcp-streams-unique-s2c-packets-count.txt"
      else if (tag == "L2C") fname = outdir "decrypted-tcp-streams-unique-l2c-packets-count.txt"
      else if (tag == "C2L") fname = outdir "decrypted-tcp-streams-unique-c2l-packets-count.txt"
      else fname = outdir "decrypted-tcp-streams-unique-unknown-packets-count.txt"
      print key "," counts[k] >> fname
    }
  }
  ' *
}


# Sort the output files to match previous behavior
# - unique files: alphabetical
# - count files: alphabetical by key OR by frequency (if requested)
sort_outputs() {
  shopt -s nullglob
  for f in "${OUTDIR}"decrypted-tcp-streams-unique-*-packets*.txt; do
    [ -f "$f" ] || continue
    if [[ "$f" == *-packets-count.txt ]]; then
      if [ "$FREQ_SORT" -eq 1 ]; then
        # sort by frequency (second field), numeric, descending
        sort -t, -k2,2nr -o "$f" "$f"
      else
        sort -o "$f" "$f"
      fi
    else
      # unique files: alphabetical
      sort -o "$f" "$f"
    fi
  done
  shopt -u nullglob
}


# Remove the unique packet files unless the user asked to keep them
remove_unique_if_needed() {
  if [ "$KEEP_UNIQUE" -eq 0 ]; then
    rm -f "${OUTDIR}decrypted-tcp-streams-unique-"*"-packets.txt"
  fi
}


# Main orchestration
main() {
  parse_args "$@"
  validate_env
  cleanup_old_outputs
  run_awk
  sort_outputs
  remove_unique_if_needed

  echo "Done. Count files are in ${OUTDIR} (unique kept: $KEEP_UNIQUE; freq-sort: $FREQ_SORT)."
}

main "$@"

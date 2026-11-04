#!/usr/bin/env bash
# Decrypt every captured stream and export one raw file per packet.
#
# Usage: ./decrypt-export-streams.sh [stream-yaml ...]
#   Without arguments every encrypted_streams/*.yaml is exported.
#
# Output: $OUT_DIR/<yaml name>/<pcap no>_<PacketId.Name>_<timestamp>.<group>_<id>_<sub>
# (header + payload as the CLI resolved it; names come from the CLI's PacketId table).
# A stream whose output folder already exists is refused: move it away first, so that files
# of an older export (other names) never mix with a new one.
#
# The CLI writes <yaml>.annotated.txt beside its input, so each YAML is copied into a
# temporary folder first: encrypted_streams/ is never written to. Streams run one at a time,
# because parallel CLI instances share one log file and crash on it
# (docs/how-to/reannotate-streams.md).
#
# Environment overrides:
#   CLI_PATH   Arrowgene.Ddon.Cli.exe (default: the patched Upstream build, docs/how-to/patch-the-arrowgene-cli.md)
#   KEYS_FILE  default keys/keys-all-in-one.csv
#   STREAM_DIR default encrypted_streams
#   OUT_DIR    default decrypted_raw
set -o errexit
set -o nounset
set -o pipefail

die() { echo "ERROR: $*" >&2; exit 2; }
for cmd in awk cp mkdir mktemp rm cygpath; do
  command -v "$cmd" >/dev/null 2>&1 || die "required command '$cmd' not found (use Git Bash)"
done

cd "$(dirname "${BASH_SOURCE[0]}")"
CLI_PATH=${CLI_PATH:-"/c/Users/morph/Documents/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Upstream/Arrowgene.Ddon.Cli/bin/Debug/net10.0/Arrowgene.Ddon.Cli.exe"}
KEYS_FILE=${KEYS_FILE:-"keys/keys-all-in-one.csv"}
STREAM_DIR=${STREAM_DIR:-"encrypted_streams"}
OUT_DIR=${OUT_DIR:-"decrypted_raw"}

[[ -x "$CLI_PATH" ]] || die "CLI not found or not executable: '$CLI_PATH' (set CLI_PATH)"
[[ -f "$KEYS_FILE" ]] || die "keys file not found: '$KEYS_FILE'"
mkdir -p "$OUT_DIR"
OUT_ABS=$(cd "$OUT_DIR" && pwd)

if (( $# > 0 )); then
  streams=("$@")
else
  shopt -s nullglob
  streams=("$STREAM_DIR"/*.yaml)
  shopt -u nullglob
fi
(( ${#streams[@]} > 0 )) || die "no stream YAML files found"

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

ok=0
failed=()
for f in "${streams[@]}"; do
  name=$(basename "$f" .yaml)
  if [[ ! $f =~ (stream[0-9]+).*tcp-stream-([0-9]+) ]]; then
    echo "skip (name does not match streamN...tcp-stream-M): $f"
    failed+=("$name")
    continue
  fi
  streamName=${BASH_REMATCH[1]}
  tcpStreamNumber=${BASH_REMATCH[2]}
  key=$(awk -F',' -v s="$streamName" -v t="$tcpStreamNumber" '
    match($1, /(stream[0-9]+)/, m) { if (m[1] == s && $5 == t) { print $10; exit } }
  ' "$KEYS_FILE")
  if [[ -z "$key" ]]; then
    echo "FAIL $name: no decryption key for $streamName tcp-stream-$tcpStreamNumber"
    failed+=("$name")
    continue
  fi
  if [[ -e "$OUT_ABS/$name" ]]; then
    echo "FAIL $name: $OUT_DIR/$name already exists (move it away first)"
    failed+=("$name")
    continue
  fi
  cp "$f" "$work/$name.yaml"
  rc=0
  # The CLI creates the per-stream folder in its working directory.
  (cd "$OUT_ABS" && "$CLI_PATH" packet "$(cygpath -aw "$work/$name.yaml")" --key="$key" \
      --export-decrypted-packets) >"$work/$name.log" 2>&1 || rc=$?
  rm -f "$work/$name.yaml" "$work/$name.yaml.annotated.txt"
  if (( rc != 0 )) || [[ ! -d "$OUT_ABS/$name" ]]; then
    echo "FAIL $name (exit $rc); log:"
    sed -n '1,40p' "$work/$name.log"
    failed+=("$name")
    continue
  fi
  echo "ok   $name"
  ok=$(( ok + 1 ))
done

echo "Done: $ok exported, ${#failed[@]} failed"
(( ${#failed[@]} == 0 )) || { printf 'failed: %s\n' "${failed[@]}" >&2; exit 1; }

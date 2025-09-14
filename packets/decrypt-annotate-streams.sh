#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# === Config (override via env if you like) ===
MAX_JOBS=${MAX_JOBS:-}
if [[ -z "$MAX_JOBS" ]]; then
  if command -v nproc >/dev/null 2>&1; then
    MAX_JOBS=$(nproc)
  else
    MAX_JOBS=$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1)
  fi
fi
(( MAX_JOBS < 1 )) && MAX_JOBS=1

CLI_PATH=${CLI_PATH:-"Arrowgene.Ddon.Cli.exe"}
KEYS_FILE=${KEYS_FILE:-"keys/keys-all-in-one.csv"}
STREAM_DIR=${STREAM_DIR:-"encrypted_streams"}

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

wait_for_slot() {
  while :; do
    running=$(jobs -rp | wc -l)
    if (( running < MAX_JOBS )); then
      break
    fi
    sleep 0.08
  done
}

# iterate files safely
while IFS= read -r -d '' f; do
  if [[ $f =~ (stream[0-9]+).*tcp-stream-([0-9]+) ]]; then
    streamName="${BASH_REMATCH[1]}"
    tcpStreamNumber="${BASH_REMATCH[2]}"

    decryptionKey=$(awk -F',' -v s="$streamName" -v t="$tcpStreamNumber" '
      match($1,/(stream[0-9]+)/,m) {
        if (m[1]==s && $5==t) print $10
      }
    ' "$KEYS_FILE" | head -n1 || true)

    safe_name="${streamName}_tcp${tcpStreamNumber}"
    log="$tmpdir/${safe_name}.log"

    wait_for_slot

    (
      set -o errexit
      set -o nounset
      rc=0

      if [[ -z "${decryptionKey:-}" ]]; then
        rc=2
        echo "ERROR: missing decryption key for ${streamName} tcp:${tcpStreamNumber}" > "$log"
      else
        "$CLI_PATH" packet "${f}" --key="${decryptionKey}" --byte-dump=, --byte-dump-prefix=0x --structure-dump --utf8-dump >"$log" 2>&1 || rc=$?
      fi

      # Print JOB DONE header only now
      echo "==== JOB DONE: ${safe_name} (exit ${rc}) ===="
      echo "file=${f}"
      echo "streamName=${streamName}, tcpStreamNumber=${tcpStreamNumber}"
      echo "---- log start ----"
      sed -n '1,2000p' "$log" || true
      echo "---- log end ----"

      # keep per-job logs in tmpdir for forensics (tmpdir is cleaned on exit)
      exit $rc
    ) &

  else
    echo "skipping (pattern mismatch): $f"
  fi
done < <(find "$STREAM_DIR" -maxdepth 1 -type f -name '*.yaml' -print0)

wait

echo "All jobs finished."

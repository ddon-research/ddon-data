#!/bin/bash
# Decrypt every L2C_LOGIN_SERVER_CERT_NOTICE (default Camellia key) in the captures; print file,frame,modulus,exponent.
set -o errexit -o nounset -o pipefail
for c in tshark ./cbcdec.exe; do command -v "$c" >/dev/null || { echo "missing $c" >&2; exit 1; }; done
dir="$1"
for f in "$dir"/*.pcapng; do
  tshark -r "$f" -Y 'tcp.srcport==52100 && data.len==306' -T fields -e frame.number -e data 2>/dev/null |
  while read -r fr d; do
    pt=$(./cbcdec.exe f23e98HafJdSoaj80QBjhh23oajgklSa "${d:4}" | tr -d '\r\n')
    echo "$(basename "$f"),$fr,${pt:0:512},${pt:512:32}"
  done
done

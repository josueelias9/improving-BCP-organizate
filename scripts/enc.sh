#!/usr/bin/env bash
set -euo pipefail

EXPORTS_DIR="files/exports"
ENC_DIR="files/exports-enc"
DEC_DIR="files/exports"
AGE_KEY_FILE="${SOPS_AGE_KEY_FILE:-$HOME/key.txt}"

usage() {
  echo "Usage: $0 <encrypt|decrypt>"
  exit 1
}

[[ $# -ne 1 ]] && usage

case "$1" in
  encrypt)
    mkdir -p "$ENC_DIR"
    for f in "$EXPORTS_DIR"/*.csv; do
      base=$(basename "$f")
      sops encrypt --input-type binary --output-type binary "$f" > "$ENC_DIR/${base}.enc"
      echo "  encrypted: $f -> $ENC_DIR/${base}.enc"
    done
    ;;
  decrypt)
    mkdir -p "$DEC_DIR"
    for f in "$ENC_DIR"/*.enc; do
      base=$(basename "$f" .enc)
      SOPS_AGE_KEY_FILE="$AGE_KEY_FILE" sops decrypt --input-type binary --output-type binary "$f" > "$DEC_DIR/${base}"
      echo "  decrypted: $f -> $DEC_DIR/${base}"
    done
    ;;
  *)
    usage
    ;;
esac

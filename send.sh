#!/usr/bin/env bash
set -euo pipefail

BASE="$HOME/iot-sensor"
SRC="$BASE/logs/parts"
DST="$BASE/vps_inbox"

mkdir -p "$DST"

shopt -s nullglob
for f in "$SRC"/part_*.csv.ready; do
  name="$(basename "$f")"
  cp -v "$f" "$DST/$name"
  mv -v "$f" "${f%.ready}.sent"
done

echo "[send] selesai — semua .ready dikirim ke vps_inbox"

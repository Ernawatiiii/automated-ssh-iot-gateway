#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="$HOME/iot-sensor/logs/parts"
DST="$HOME/iot-sensor/vps_inbox"  # nanti diganti ke alamat VPS beneran
LOG="$HOME/iot-sensor/logs/push-realtime.log"

echo "$(date -Is) starting realtime sender..." >> "$LOG"

# pastikan inotify-tools terinstall
command -v inotifywait >/dev/null 2>&1 || { 
    echo "Error: inotify-tools belum diinstall. Jalankan: sudo apt install inotify-tools -y" >&2; 
    exit 1; 
}

# pantau folder logs/parts dan kirim otomatis setiap ada file .ready
inotifywait -m -e close_write,move,create "$SRC_DIR" | while read -r dir action file; do
  if [[ "$file" == *.csv.ready ]]; then
    f="$SRC_DIR/$file"
    echo "$(date -Is) detected $file ($action)" >> "$LOG"
    if cp "$f" "$DST/"; then
      mv "$f" "${f%.ready}.sent"
      echo "$(date -Is) SENT $file" >> "$LOG"
    else
      echo "$(date -Is) FAIL $file" >> "$LOG"
    fi
  fi
done

#!/usr/bin/env python3
import os, sys, time, datetime, logging, serial

PORT = os.environ.get("PORT", "/dev/ttyUSB0")
BAUD = int(os.environ.get("BAUD", "115200"))
BASE = os.path.expanduser("~/iot-sensor")
LOGDIR = os.path.join(BASE, "logs", "parts")
MAX_BYTES = 256 * 1024  # DEMO: kecil biar cepat rotasi
RECONNECT_DELAY = 2.0
LINE_TIMEOUT = 2.0
DEVICE_ID = os.environ.get("DEVICE_ID", "esp32a")

os.makedirs(LOGDIR, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
HEADER = "device_id,event_time_utc,ingest_time_utc,temp_c,rh_pct,seq\n"
utc = lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")



import glob
import re
import csv

def _has_data(path):
    """True kalau file punya >= 2 baris (header + 1 data)."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in range(2) if f.readline()) >= 2
    except Exception:
        return False

def _archive_empty(path):
    """Pindahkan part kosong ke logs/empty_parts biar folder parts rapi."""
    try:
        if not path or not os.path.exists(path): 
            return
        if _has_data(path):
            return
        empty_dir = os.path.abspath(os.path.join(os.path.dirname(path), '..', 'empty_parts'))
        os.makedirs(empty_dir, exist_ok=True)
        dst = os.path.join(empty_dir, os.path.basename(path))
        os.replace(path, dst)
        logging.info(f"[rotate] move empty part -> {dst}")
    except Exception as e:
        logging.warning(f"[rotate] archive empty failed: {e}")

def list_parts():
    return sorted(
        glob.glob(os.path.join(LOGDIR, 'part_*.csv')),
        key=os.path.getmtime, reverse=True
    )

def next_idx():
    """Cari index part berikutnya dari nama file yang ada."""
    files = list_parts()
    if not files:
        return 1
    m = re.search(r'part_(\d+)\.csv$', os.path.basename(files[0]))
    if not m:
        return 1
    return int(m.group(1)) + 1

current_idx = None
current_path = None
fp = None
writer = None

def _open_part(idx):
    """Buka part dan pastikan header ditulis sekali."""
    global current_idx, current_path, fp, writer
    current_idx = idx
    current_path = os.path.join(LOGDIR, f"part_{idx:04d}.csv")
    # append supaya kalau sempat ada isi, lanjut
    fp = open(current_path, 'a', newline='', encoding='utf-8')
    need_header = (os.stat(current_path).st_size == 0)
    writer = csv.writer(fp)
    if need_header:
        fp.write(HEADER)  # HEADER sudah string berakhiran '\n'
        fp.flush()
        logging.info(f"[open] new part -> {current_path}")

def _rotate_if_needed():
    """Rotasi bila ukuran melebihi MAX_BYTES. Bersihkan part lama jika kosong."""
    global current_idx, current_path, fp
    try:
        size = os.path.getsize(current_path) if current_path and os.path.exists(current_path) else 0
        if size >= MAX_BYTES:
            # tutup lama
            if fp:
                fp.flush()
                fp.close()
            # arsipkan kalau kosong
            _archive_empty(current_path)
            # buka baru
            _open_part(current_idx + 1)
    except Exception as e:
        logging.warning(f"[rotate] failed: {e}")

def _parse_line(raw):
    """
    Terima format dari ESP32:
      'esp32a,23.4,63.7,8376'
      atau bisa 'esp32a,nan,nan,123'
    Kembalikan tuple (device_id, temp, rh, seq).
    """
    raw = raw.strip()
    if not raw:
        return None
    parts = [p.strip() for p in raw.split(',')]
    # fallback kalau device_id tidak terkirim
    if len(parts) == 3:
        parts = [DEVICE_ID] + parts
    if len(parts) < 4:
        return None
    dev, t, h, s = parts[0], parts[1], parts[2], parts[3]
    # normalisasi
    try: temp = float(t) if t.lower() != 'nan' else None
    except: temp = None
    try: rh   = float(h) if h.lower() != 'nan' else None
    except: rh   = None
    try: seq  = int(float(s))
    except: seq  = None
    dev = dev or DEVICE_ID
    return dev, temp, rh, seq

def _write_record(dev, temp, rh, seq):
    """Tulis satu baris CSV standar."""
    global writer, fp
    now = utc()
    # kalau sensor nan, tetap tulis 'nan' di CSV
    temp_s = "nan" if temp is None else f"{temp:.1f}"
    rh_s   = "nan" if rh   is None else f"{rh:.1f}"
    seq_s  = "" if seq is None else str(seq)
    line = f"{dev},{now},{now},{temp_s},{rh_s},{seq_s}\n"
    fp.write(line)
    fp.flush()

def _open_serial():
    """Buka port serial dengan retry loop."""
    while True:
        try:
            logging.info(f"[serial] open {PORT} @ {BAUD}")
            ser = serial.Serial(PORT, BAUD, timeout=LINE_TIMEOUT)
            return ser
        except Exception as e:
            logging.warning(f"[serial] open failed: {e}; retry {RECONNECT_DELAY}s")
            time.sleep(RECONNECT_DELAY)

def main():
    # buka part pertama
    _open_part(next_idx())

    ser = _open_serial()
    while True:
        try:
            raw = ser.readline().decode('utf-8', 'ignore')
            if not raw:
                # timeout read
                continue
            parsed = _parse_line(raw)
            if not parsed:
                continue
            dev, temp, rh, seq = parsed
            _write_record(dev, temp, rh, seq)
            _rotate_if_needed()
        except serial.SerialException as e:
            logging.warning(f"[serial] error: {e}; reconnecting ...")
            try:
                ser.close()
            except Exception:
                pass
            time.sleep(RECONNECT_DELAY)
            ser = _open_serial()
        except Exception as e:
            logging.warning(f"[loop] unexpected error: {e}")
            time.sleep(0.2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

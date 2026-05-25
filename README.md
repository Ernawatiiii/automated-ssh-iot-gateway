# Automated and Secure Sensor Data Pipeline using ESP32 and SSH Gateway

Proyek ini mengimplementasikan sistem otomatisasi pengiriman data sensor dari perangkat IoT (ESP32) menuju gateway secara aman menggunakan enkripsi SSH, Python, dan Shell Scripting. Sistem ini berfokus pada **Automation** dan **Data Engineering Pipeline** yang efisien.

## Fitur Utama
- **Automated Data Pipeline**: Pemrosesan dan pengiriman data dari perangkat ke server berjalan otomatis tanpa intervensi manusia (*Backend Automation*).
- **Secure Transmission**: Menggunakan protokol SSH untuk memastikan pengiriman data ke gateway terenkripsi dengan aman.
- **Python Serial Reader**: Menggunakan skrip Python untuk membaca, memvalidasi, dan mengelola aliran data log secara real-time dari komunikasi serial.
- **Shell Script Automation**: Mengotomatiskan manajemen berkas, otomatisasi pengiriman berkas log secara berkala, dan penanganan backup data di sisi Linux gateway.

## Teknologi & Bahasa Pemrograman
- **Python**: Digunakan untuk manajemen data log dan pembacaan data serial (`read_serial.py`).
- **Shell Script / Bash**: Digunakan untuk otomatisasi sistem, pipeline data, dan transfer file aman (`push_realtime.sh`, `send.sh`).
- **C++ (Arduino IDE)**: Digunakan untuk memprogram logika mikrokontroler ESP32 (`sketch_oct21a.ino`).
- **HTML**: Monitoring data sederhana melalui web interface (`table.html`).
- **OS & Protokol**: Linux Gateway & Secure Shell (SSH).


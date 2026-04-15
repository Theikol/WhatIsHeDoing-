# 🖥️ ExplorerGuard — Employee Activity Monitoring System

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white"/>
  <img src="https://img.shields.io/badge/Language-Python%203.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Status-Production%20Ready-28a745?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge"/>
</p>

> **Sistem pemantauan aktivitas karyawan berbasis desktop** yang merekam layar secara otomatis saat File Explorer aktif dan mengambil snapshot webcam saat folder sensitif diakses.

---

## 📋 Daftar Isi

- [Latar Belakang](#-latar-belakang)
- [Tujuan Sistem](#-tujuan-sistem)
- [Fitur Utama](#-fitur-utama)
- [Arsitektur Sistem](#-arsitektur-sistem)
- [Alur Kerja](#-alur-kerja)
- [Kebutuhan Sistem](#-kebutuhan-sistem)
- [Instalasi](#-instalasi)
- [Konfigurasi](#-konfigurasi)
- [Struktur Direktori](#-struktur-direktori)
- [Panduan Penggunaan](#-panduan-penggunaan)
- [Kebijakan Privasi & Etika](#-kebijakan-privasi--etika)
- [Tim Pengembang](#-tim-pengembang)

---

## 📌 Latar Belakang

Di lingkungan kerja modern, akses terhadap data perusahaan yang bersifat rahasia dan sensitif merupakan risiko keamanan yang tidak dapat diabaikan. Kebocoran data internal, baik disengaja maupun tidak, dapat merugikan perusahaan secara material dan reputasional.

**ExplorerGuard** hadir sebagai solusi pengawasan internal berbasis desktop yang berjalan secara *background* di komputer karyawan, memantau aktivitas File Explorer secara pasif tanpa mengganggu produktivitas kerja.

Sistem ini dikembangkan sesuai prinsip-prinsip **Rekayasa Perangkat Lunak (RPL)** dengan pendekatan *modular*, *maintainable*, dan *scalable*.

---

## 🎯 Tujuan Sistem

| No | Tujuan |
|----|--------|
| 1 | Merekam aktivitas File Explorer karyawan secara otomatis |
| 2 | Mengidentifikasi siapa yang mengakses folder sensitif perusahaan |
| 3 | Menyimpan bukti visual (screenshot webcam) saat folder kritis dibuka |
| 4 | Memberikan laporan audit trail kepada manajemen |
| 5 | Mencegah akses dan pencurian data internal secara dini |

---

## ✨ Fitur Utama

### 🎬 Screen Recording Otomatis
- Rekaman layar dimulai secara otomatis ketika File Explorer dibuka
- Rekaman berhenti dan disimpan otomatis ketika Explorer ditutup
- Format video: AVI (XVID), 10 FPS

### 📷 Webcam Snapshot
- Mengambil foto pengguna secara otomatis saat folder yang ditandai (*watched folder*) diakses
- Cooldown 5 detik untuk mencegah duplikasi snapshot
- Disimpan dalam format JPG dengan timestamp

### 🔍 Folder Monitoring
- Memantau folder tertentu yang ditetapkan administrator
- Deteksi real-time perpindahan direktori di File Explorer
- Mendukung multiple watched folders

### 🕵️ Stealth Mode
- Berjalan tanpa jendela konsol yang terlihat
- Tidak muncul sebagai proses mencurigakan di taskbar
- Dapat dikonfigurasi sebagai startup otomatis via Task Scheduler

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────┐
│                   ExplorerGuard Core                    │
│                                                         │
│  ┌─────────────┐   ┌──────────────┐  ┌──────────────┐  │
│  │  Explorer   │   │   Screen     │  │   Webcam     │  │
│  │  Monitor    │──▶│   Recorder   │  │   Capture    │  │
│  │  (Thread 1) │   │  (Thread 2)  │  │  (Thread 3)  │  │
│  └──────┬──────┘   └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
│         ▼                 ▼                 ▼           │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Output Manager                      │   │
│  │    /Videos/ExplorerRecords/  (Video .avi)        │   │
│  │    /Videos/ExplorerRecords/FaceCam/  (.jpg)      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Komponen Utama

| Komponen | Fungsi | File/Modul |
|---|---|---|
| Explorer Monitor | Mendeteksi window & path aktif File Explorer | `get_explorer_windows()`, `get_active_explorer_path()` |
| Screen Recorder | Merekam layar ke file video | `_record_loop()`, `start_recording()`, `stop_recording()` |
| Webcam Capture | Mengambil snapshot dari webcam | `capture_webcam()` |
| Monitor Loop | Orkestrasi semua komponen | `monitor_loop()` |

---

## 🔄 Alur Kerja

```
START
  │
  ▼
Program berjalan di background
  │
  ▼
File Explorer dibuka? ──── TIDAK ──── (loop tunggu)
  │ YA
  ▼
Mulai Screen Recording
  │
  ▼
Cek folder aktif setiap 1 detik
  │
  ├── Bukan watched folder ──── (lanjut monitoring)
  │
  └── Watched folder terdeteksi
        │
        ▼
      Ambil Snapshot Webcam
        │
        ▼
      Simpan ke FaceCam/face_[timestamp].jpg
  │
  ▼
File Explorer ditutup?
  │ YA
  ▼
Stop Recording → Simpan video
  │
  ▼
Kembali ke loop monitoring
```

---

## 💻 Kebutuhan Sistem

### Perangkat Keras
| Komponen | Minimum | Rekomendasi |
|---|---|---|
| OS | Windows 10 64-bit | Windows 11 64-bit |
| RAM | 4 GB | 8 GB |
| Storage | 10 GB free | 50 GB free |
| Webcam | Built-in / USB | HD 720p+ |
| CPU | Intel Core i3 | Intel Core i5+ |

### Perangkat Lunak
| Komponen | Versi |
|---|---|
| Python | 3.10 atau lebih baru |
| OpenCV | `opencv-python >= 4.5` |
| MSS | `mss >= 6.1` |
| PyWin32 | `pywin32 >= 305` |
| NumPy | `numpy >= 1.21` |

---

## 🚀 Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/namaorganisasi/explorerguard.git
cd explorerguard
```

### 2. Buat Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependensi
```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
opencv-python>=4.5.0
mss>=6.1.0
pywin32>=305
numpy>=1.21.0
```

### 4. Jalankan sebagai Administrator
```bash
# Klik kanan pada terminal → Run as Administrator
python explorer_recorder.py
```

### 5. (Opsional) Auto Startup via Task Scheduler
```
Task Scheduler → Create Task
  General     : Run whether user is logged on or not
  Trigger     : At startup
  Action      : Start a program → pythonw.exe explorer_recorder.py
  Run As      : Administrator
```

---

## ⚙️ Konfigurasi

Edit bagian `CONFIG` di dalam `explorer_recorder.py`:

```python
# ─── CONFIG ───────────────────────────────────────
OUTPUT_DIR       = Path.home() / "Videos" / "ExplorerRecords"
WEBCAM_DIR       = Path.home() / "Videos" / "ExplorerRecords" / "FaceCam"
FPS              = 10           # Frame per detik rekaman layar
CHECK_DELAY      = 1.0          # Interval cek folder aktif (detik)
CAPTURE_COOLDOWN = 5            # Jeda minimum antar snapshot (detik)

WATCHED_FOLDERS  = [
    r"D:\DataRahasia",          # Tambah folder yang ingin dipantau
    r"C:\ProjectKlasifikasi",
]
```

| Parameter | Default | Keterangan |
|---|---|---|
| `FPS` | `10` | Semakin tinggi = file lebih besar |
| `CHECK_DELAY` | `1.0` | Interval polling dalam detik |
| `CAPTURE_COOLDOWN` | `5` | Cegah duplikasi snapshot |
| `WATCHED_FOLDERS` | `[r"D:"]` | List path folder yang dipantau |

---

## 📁 Struktur Direktori

```
explorerguard/
│
├── explorer_recorder.py     # File utama program
├── requirements.txt         # Daftar dependensi
├── README.md                # Dokumentasi ini
│
└── output/ (generated)
    └── ~/Videos/ExplorerRecords/
        ├── explorer_2025-01-15_09-30-00.avi   # Video rekaman layar
        ├── explorer_2025-01-15_10-15-00.avi
        └── FaceCam/
            ├── face_2025-01-15_09-45-22.jpg   # Snapshot webcam
            └── face_2025-01-15_10-20-11.jpg
```

---

## 📖 Panduan Penggunaan

### Untuk Administrator IT

1. **Deploy** program ke komputer karyawan via Group Policy atau remote installer
2. **Konfigurasi** `WATCHED_FOLDERS` sesuai folder aset perusahaan
3. **Verifikasi** program berjalan di background (Task Manager → pythonw.exe)
4. **Kumpulkan** hasil rekaman secara berkala dari folder output

### Membaca Hasil Rekaman
- Video tersimpan di: `%USERPROFILE%\Videos\ExplorerRecords\`
- Snapshot webcam di: `%USERPROFILE%\Videos\ExplorerRecords\FaceCam\`
- Nama file menggunakan format timestamp: `YYYY-MM-DD_HH-MM-SS`

### Audit Trail
Setiap file dapat dikorelasikan berdasarkan timestamp untuk mengetahui:
- **Jam berapa** File Explorer dibuka/ditutup
- **Folder apa** yang diakses
- **Siapa** yang berada di depan komputer (foto webcam)

---

## 🔒 Kebijakan Privasi & Etika

> ⚠️ **PENTING — Baca sebelum deployment**

Sistem ini **HANYA boleh** digunakan pada:
- ✅ Komputer milik perusahaan
- ✅ Karyawan yang telah menandatangani persetujuan pemantauan (*monitoring consent form*)
- ✅ Sesuai dengan kebijakan IT dan HR perusahaan
- ✅ Dalam koridor hukum ketenagakerjaan yang berlaku di yurisdiksi masing-masing

Sistem ini **DILARANG** digunakan untuk:
- ❌ Komputer pribadi tanpa izin pemilik
- ❌ Pelanggaran privasi individu di luar konteks kerja
- ❌ Tujuan di luar keamanan data perusahaan

**Penggunaan di luar ketentuan di atas adalah tanggung jawab penuh pengguna.**

---

## 👥 Tim Pengembang

| Nama | Role | Kontak |
|---|---|---|
| Adrian H | Pemancing | github.com/Theikol |
| — | Backend Developer | — |
| — | System Analyst | — |
| — | QA Engineer | — |

---

## 📄 Lisensi

Perangkat lunak ini bersifat **proprietary** dan hanya untuk penggunaan internal perusahaan. Dilarang mendistribusikan, memodifikasi, atau menggunakan di luar lingkungan yang diizinkan tanpa persetujuan tertulis.

---

<p align="center">© 2025 Adrian HAikal. All Rights Reserved.</p>

# 🚀 LeadPilot

> **Mesin Kualifikasi & Triage Prospek (Lead) Otomatis Berbasis AI Lokal dan Skoring Deterministik.**  
> 100% Privat, Cepat, Tanpa Ketergantungan Cloud API atau SaaS Eksternal.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-e92063.svg)](https://docs.pydantic.dev/)
[![Ollama](https://img.shields.io/badge/Ollama-granite4.2%3A3b-black.svg)](https://ollama.com/)
[![Tests](https://img.shields.io/badge/Tests-98%20Passing-brightgreen.svg)]()

---

## 📌 Daftar Isi
- [Tentang LeadPilot](#-tentang-leadpilot)
- [Arsitektur & Cara Kerja](#-arsitektur--cara-kerja)
- [Fitur Utama](#-fitur-utama)
- [Aturan Skoring & Klasifikasi](#-aturan-skoring--klasifikasi)
- [Prasyarat Sistem](#-prasyarat-sistem)
- [Panduan Instalasi Cepat](#-panduan-instalasi-cepat)
- [Cara Penggunaan](#-cara-penggunaan)
  - [1. Batch Processing CSV (Alur Kerja Utama)](#1-batch-processing-csv-alur-kerja-utama)
  - [2. Web GUI Single-Lead Demo](#2-web-gui-single-lead-demo)
  - [3. REST API Langsung](#3-rest-api-langsung)
- [Format & Spesifikasi Data](#-format--spesifikasi-data)
  - [Format CSV Input](#format-csv-input)
  - [Struktur Output (`lp_*`)](#struktur-output-lp_)
- [Pengujian (Testing & Smoke Test)](#-pengujian-testing--smoke-test)
- [Konfigurasi Lingkungan (Environment Variables)](#-konfigurasi-lingkungan-environment-variables)
- [Struktur Direktori Proyek](#-struktur-direktori-proyek)
- [Catatan & Praktik Terbaik](#-catatan--praktik-terbaik)

---

## 🎯 Tentang LeadPilot

**LeadPilot** adalah sistem otomasi kualifikasi prospek bisnis (*lead triage*) yang mengombinasikan kekuatan **Local LLM (`granite4.2:3b` via Ollama)** untuk pemahaman konteks semantik teks bahasa alami (Bahasa Indonesia & Inggris), dengan **mesin skoring deterministik berbasis Python murni**.

Berbeda dengan solusi otomatisasi cloud atau SaaS pihak ketiga (seperti n8n cloud, Zapier, atau OpenAI API), LeadPilot berjalan **sepenuhnya di mesin lokal (on-premise / localhost)**. Data calon pelanggan yang sensitif (nama, email, budget, pesan internal) **tidak pernah keluar ke internet**.

---

## 🏗️ Arsitektur & Cara Kerja

LeadPilot memisahkan interpretasi bahasa alami (LLM) dengan perhitungan skor bisnis (Python) agar hasil kualifikasi objektif, konsisten, dan transparan:

```
[ Input Lead ]
 (CSV / Web GUI / JSON API)
            │
            ▼
[ 1. Normalisasi & Validasi Data ]
 (Pydantic v2: sanitasi spasi, validasi email, parsing angka budget IDR)
            │
            ▼
[ 2. Analisis Semantik LLM ]
 (Ollama: granite4.2:3b dengan JSON Schema kaku & temperature=0)
  ├── Intent (purchase / research / support / spam / unknown)
  ├── Urgency (high / medium / low / unknown)
  ├── Service Match (True/False terhadap otomasi/integrasi Python)
  ├── Strong Intent & Clear Requirement
  └── Confidence (0.0 - 1.0)
            │
            ▼
[ 3. Mesin Skoring Deterministik Python ]
 (Aturan matematis: kalkulasi poin budget, ukuran perusahaan, & sinyal LLM)
            │
            ▼
[ Output Terstruktur ]
 (Skor 0-100, Tier HOT/WARM/COLD, Rekomendasi Review Manusia, Alasan Skoring)
```

---

## ✨ Fitur Utama

- 🔒 **100% Privasi & Keamanan Data**: Tidak ada data pelanggan yang dikirim ke cloud. Semua proses berjalan secara lokal melalui Ollama.
- ⚡ **Batch CSV Processing Andal**:
  - Dukungan pemilih file/folder bawaan Windows (`File Picker GUI`).
  - Pemrosesan sekuensial hemat memori & VRAM.
  - **Sistem Checkpoint & Resume**: Jika proses terputus (Ctrl+C atau listrik padam), cukup jalankan kembali. Baris yang sudah sukses otomatis dilewati (*skip*).
  - **Spreadsheet Safe**: Otomatis menambahkan UTF-8 BOM untuk kompatibilitas Microsoft Excel dan meng-escape karakter formula (`=`, `+`, `-`, `@`) untuk mencegah *CSV formula injection*.
  - **Isolasi Checksum**: Perubahan pada file CSV atau logika Python otomatis menghasilkan folder batch baru untuk menjaga integritas data riwayat.
  - **Lock Mechanism**: Menggunakan `run.lock` untuk mencegah dua proses menulis ke batch yang sama secara bersamaan.
- 🖥️ **Web GUI Interaktif**: Antarmuka berbasis browser siap pakai tanpa Node.js/npm. Menyediakan contoh lead siap uji, indikator waktu proses riil, dan fitur **Mode Short** (tampilan vertikal untuk demo dan rekaman video).
- 🔌 **REST API Siap Integrasi**: Endpoint FastAPI terdokumentasi rapi via Swagger UI (`/docs`).
- 🧪 **Kualitas Teruji**: Dilengkapi 98 unit tests dan pengujian integrasi langsung (*live smoke test*).

---

## 📊 Aturan Skoring & Klasifikasi

Skor dihitung secara deterministik dengan batas maksimum **100 poin**:

| Parameter / Sinyal | Kriteria | Poin |
|---|---|:---:|
| **Anggaran (Budget)** | $\ge$ Rp 5.000.000 | **30** |
| | $\ge$ Rp 2.000.000 (dan < Rp 5.000.000) | **20** |
| | $>$ Rp 0 (dan < Rp 2.000.000) | **10** |
| **Ukuran Perusahaan (Company Size)** | 20 – 200 karyawan | **20** |
| | $\ge$ 5 karyawan (termasuk > 200) | **10** |
| **Kesesuaian Layanan (Service Match)** | Cocok dengan Otomasi AI/Workflow atau Integrasi Python/API/LLM | **20** |
| **Urgensi Waktu (Urgency)** | *High Urgency* (hari ini, minggu ini, minggu depan, s/d 2 minggu) | **20** |
| | *Medium Urgency* (bulan ini, segera) | **10** |
| **Keseriusan Pembelian** | Intent bernilai `purchase` **DAN** `strong_intent = True` | **10** |

### Klasifikasi Tier & Tinjauan Manusia
- 🔥 **HOT** : Skor **$\ge$ 80** (Prioritas utama tim sales untuk segera dihubungi).
- ⛅ **WARM** : Skor **50 – 79** (Prospek potensial, lakukan *follow-up* standar).
- ❄️ **COLD** : Skor **< 50** (Kebutuhan riset, belum siap beli, atau tidak cocok).
- ⚠️ **Human Review Flag (`requires_human_review = True`)**: Otomatis aktif jika tingkat keyakinan (*confidence*) model LLM **< 0.60**.

> [!NOTE]
> Poin anggaran hanya diberikan jika kolom numerik `budget` terisi. Penyebutan nominal pada teks bebas pesan hanya akan menandai `budget_mentioned = true` tanpa menambah poin numerik secara otomatis.

---

## 💻 Prasyarat Sistem

1. **Sistem Operasi**: Windows 10/11 (atau Linux/macOS dengan penyesuaian path).
2. **Python**: Versi **3.11** atau yang lebih baru.
3. **Ollama**: Terpasang dan berjalan di mesin lokal ([Download Ollama](https://ollama.com/)).
4. **Model LLM**: `granite4.2:3b`.

---

## 🛠️ Panduan Instalasi Cepat

Buka terminal **PowerShell** di folder proyek ini:

```powershell
# 1. Buat virtual environment Python
py -3.11 -m venv .venv

# 2. Pasang dependensi yang dibutuhkan
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. Unduh model LLM pada Ollama
ollama pull granite4.2:3b

# 4. Jalankan pengujian unit untuk memastikan semua komponen siap
.\.venv\Scripts\python.exe -m pytest -q
```

*(Opsional) Untuk mereproduksi versi dependensi yang sudah terkunci secara persis, gunakan `pip install -r requirements-lock.txt`.*

---

## 🚀 Cara Penggunaan

### 1. Batch Processing CSV (Alur Kerja Utama)

Mode ini dirancang untuk memproses ratusan hingga ribuan lead dari file CSV secara otomatis tanpa membuka browser.

#### Cara Termudah (Klik Dua Kali pada Windows Explorer):
- **`Start-LeadPilot.cmd`** atau **`Batch-CSV.cmd`**: Membuka kotak dialog Windows untuk memilih satu file CSV.
- **`Batch-Folder.cmd`**: Membuka dialog pemilih folder untuk memproses seluruh file `*.csv` di dalam folder tersebut.
- **`Demo-Batch-50.cmd`**: Langsung mengeksekusi demo dataset 50 lead dummy bawaan (`samples/dummy-leads-50.csv`).

#### Melalui Perintah Terminal:
```powershell
# Memproses file CSV tertentu
.\.venv\Scripts\python.exe batch_process.py samples\dummy-leads-50.csv

# Menggunakan pemilih file interaktif Windows
.\.venv\Scripts\python.exe batch_process.py --pick file

# Memproses seluruh CSV dalam sebuah folder ke lokasi output kustom
.\.venv\Scripts\python.exe batch_process.py "C:\Data\Leads" --output "C:\Data\HasilLead"

# Uji coba cepat hanya pada 3 baris pertama
.\.venv\Scripts\python.exe batch_process.py samples\dummy-leads-50.csv --limit 3
```

> [!TIP]
> **Interupsi & Lanjut Kerja:** Tekan `Ctrl + C` kapan saja untuk menghentikan proses. Anda dapat menjalankannya kembali nanti pada file yang sama; LeadPilot akan membaca `checkpoint.json` dan langsung melanjutkan baris yang belum selesai tanpa membuang waktu.

---

### 2. Web GUI Single-Lead Demo

Antarmuka web interaktif yang cocok untuk demo langsung, pengujian manual satu per satu, atau pembuatan materi presentasi.

1. Klik dua kali **`Start-Web-Demo.cmd`** (atau jalankan perintah di bawah):
   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
   ```
2. Buka browser di **http://127.0.0.1:8001**.
3. **Fitur GUI:**
   - Tombol template cepat (**Siap beli**, **Riset**, **Dukungan Pelanggan**).
   - Indikator waktu analisis riil dari model lokal.
   - **Mode Short**: Mengubah tata letak menjadi satu kolom vertikal yang pas untuk rekaman layar video/shorts.
   - Tombol **Export JSON** untuk mengunduh hasil analisis.

---

### 3. REST API Langsung

Untuk integrasi ke aplikasi backend lain, jalankan server API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- Buka **http://127.0.0.1:8000/docs** untuk melihat dokumentasi interaktif Swagger UI.
- **Endpoint Tersedia:**
  - `GET /health` : Pengecekan status liveness aplikasi.
  - `POST /triage` : Menerima data lead dan mengembalikan analisis semantik serta skoring lengkap.

Contoh cURL / PowerShell:
```powershell
$lead = @{
    name = "Budi Pratama"
    email = "budi@perusahaan.co.id"
    company = "PT Maju Terus"
    company_size = 45
    budget = 15000000
    service = "Otomasi Lead ke WhatsApp dan Google Sheets"
    timeline = "minggu depan"
    message = "Kami butuh otomasi integrasi form website langsung ke WhatsApp tim sales kami secepatnya."
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/triage -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($lead))
```

---

## 📋 Format & Spesifikasi Data

### Format CSV Input

Gunakan encoding **UTF-8**. Pemisah yang didukung: koma (`,`), titik koma (`;`), atau tab (`\t`). Header harus menggunakan huruf kecil persis seperti tabel berikut:

| Kolom | Tipe | Wajib? | Keterangan & Contoh |
|---|---|:---:|---|
| `name` | Teks | **Ya** | Nama kontak prospek. |
| `email` | Email | **Ya** | Alamat email valid (otomatis diubah ke lowercase). |
| `message` | Teks | **Ya** | Isi pesan/kebutuhan (5 – 8.000 karakter). |
| `company` | Teks | Tidak | Nama perusahaan/organisasi. |
| `company_size` | Angka | Tidak | Bilangan bulat positif (contoh: `25`). |
| `budget` | Angka | Tidak | Angka bulat dalam Rupiah tanpa titik/Rp (contoh: `5000000`). |
| `service` | Teks | Tidak | Layanan yang diminati. |
| `timeline` | Teks | Tidak | Target waktu mulai (contoh: `minggu depan`). |
| `source` | Teks | Tidak | Asal lead (default: `csv` atau `website`). |
| `lead_id` / lainnya | Any | Tidak | Kolom kustom tambahan akan tetap dipertahankan pada output. |

### Struktur Output (`lp_*`)

Hasil batch processing disimpan di folder `batch_output/<nama_file>-<hash>/`:
1. **`results.csv`**: Seluruh baris input ditambah kolom analisis berawalan `lp_`.
2. **`errors.csv`**: Daftar baris yang gagal diproses beserta detail kesalahannya.
3. **`checkpoint.json`**: Status pengerjaan per baris data.

| Kolom Output | Keterangan |
|---|---|
| `lp_row` | Nomor urut record data (mulai dari 1). |
| `lp_status` | Status baris: `ok`, `error`, atau `pending`. |
| `lp_error` | Pesan galat jika baris gagal divalidasi atau diproses. |
| `lp_intent` | Klasifikasi niat: `purchase`, `research`, `support`, `spam`, `unknown`. |
| `lp_urgency` | Tingkat urgensi: `high`, `medium`, `low`, `unknown`. |
| `lp_category` | Kategori ringkas layanan yang diidentifikasi model. |
| `lp_service_match` | `True` jika cocok dengan bidang layanan otomasi/integrasi. |
| `lp_summary` | Ringkasan faktual kebutuhan lead dalam 1-2 kalimat. |
| `lp_confidence` | Skor keyakinan model LLM (0.00 – 1.00). |
| `lp_score` | Skor akhir deterministik (0 – 100). |
| `lp_tier` | Klasifikasi prioritas: `HOT`, `WARM`, atau `COLD`. |
| `lp_requires_human_review` | `True` jika skor confidence rendah (< 0.60). |
| `lp_reasons` | Rincian breakdown penambahan poin aturan bisnis. |

---

## 🧪 Pengujian (Testing & Smoke Test)

LeadPilot dilengkapi dengan rangkaian pengujian komprehensif:

```powershell
# 1. Jalankan Unit Tests (98 tests)
# Menguji normalisasi input, skoring, proteksi formula CSV, penanganan error tanpa memanggil LLM nyata
.\.venv\Scripts\python.exe -m pytest -q

# 2. Jalankan Live Smoke Test
# Menguji pipeline penuh secara nyata langsung ke Ollama lokal (granite4.2:3b)
.\.venv\Scripts\python.exe smoke_test.py
```

Hasil uji coba integrasi live model yang berhasil akan disimpan ke file [smoke-result.json](smoke-result.json).

---

## ⚙️ Konfigurasi Lingkungan (Environment Variables)

Secara default, aplikasi akan langsung berjalan tanpa konfigurasi tambahan. Namun, variabel berikut dapat diatur jika diperlukan:

| Variabel | Nilai Default | Keterangan |
|---|---|---|
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | URL host layanan Ollama. |
| `OLLAMA_TIMEOUT_SECONDS` | `120` | Batas waktu tunggu respons model (detik). |

Contoh penyesuaian di PowerShell:
```powershell
$env:OLLAMA_TIMEOUT_SECONDS = "180"
```

---

## 📁 Struktur Direktori Proyek

```plaintext
LeadPilot/
├── app/
│   ├── __init__.py
│   ├── batch.py             # Logika batch CSV, checkpoint, resume, & proteksi spreadsheet
│   ├── llm.py               # Integrasi Ollama, prompt template, & JSON schema enforcement
│   ├── main.py              # Endpoint REST API FastAPI & Web GUI mount
│   ├── pipeline.py          # Orkestrasi alur lead -> LLM -> skoring
│   ├── schemas.py           # Kontrak data Pydantic (LeadInput, LeadAnalysis, ScoringResult)
│   ├── scoring.py           # Mesin skoring aturan bisnis deterministik
│   ├── validation.py        # Validasi & normalisasi data tambahan
│   └── static/              # Asset Web GUI (HTML, CSS, JS lokal murni)
├── batch_output/            # Folder penyimpanan hasil pemrosesan batch CSV
├── samples/
│   ├── dummy-leads-50.csv   # 50 dataset lead sintetis untuk demo & pengujian
│   └── hot-lead.json        # Contoh payload lead JSON bernilai tinggi
├── tests/                   # Suite pengujian unit & integrasi (pytest)
├── batch_process.py         # Skrip CLI untuk batch processing dengan dukungan dialog GUI
├── generate_dummy.py        # Generator dataset dummy sintetis
├── smoke_test.py            # Skrip verifikasi integrasi model Ollama riil
├── Start-LeadPilot.cmd      # Shortcut Windows untuk memilih file CSV
├── Batch-CSV.cmd            # Shortcut Windows pemilih file CSV
├── Batch-Folder.cmd         # Shortcut Windows pemilih folder CSV
├── Demo-Batch-50.cmd        # Shortcut Windows eksekusi langsung demo 50 lead
├── Start-Web-Demo.cmd       # Shortcut Windows menjalankan Web GUI
├── requirements.txt         # Daftar dependensi utama
├── requirements-lock.txt    # Daftar dependensi terkunci (reproducible)
├── BATCH.md                 # Dokumentasi teknis alur kerja batch
├── VALIDATION.md            # Catatan status validasi & pengujian historis
└── README.md                # Dokumentasi utama proyek
```

---

## 💡 Catatan & Praktik Terbaik

1. **Kunci File di Windows (Excel File Lock)**:
   Tutup file hasil (`results.csv`) di Microsoft Excel selama proses batch sedang berjalan. Windows dapat mengunci file yang sedang dibuka di Excel, sehingga aplikasi gagal memperbarui checkpoint secara periodik.
2. **Review Manual untuk Kasus Khusus**:
   Aturan skoring bersifat aditif. Lead dengan pesan komplain/dukungan (*support*) atau promosi (*spam*) yang menyebutkan budget dan ukuran perusahaan besar dapat memperoleh skor angka yang tinggi. Selalu periksa kolom `lp_intent` dan `lp_requires_human_review` sebelum menindaklanjuti prospek.
3. **Nilai Anggaran Kosong vs Nol**:
   Biarkan kolom `budget` kosong jika prospek belum memberikan informasi anggaran. Mengisi nilai `0` berarti prospek secara eksplisit menyatakan anggarannya adalah Rp 0.

---

<p align="center">
  Dibuat dengan ❤️ untuk efisiensi & privasi kualifikasi prospek bisnis.
</p>

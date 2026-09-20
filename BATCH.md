# LeadPilot: proses data lead perusahaan

## Mulai paling cepat

1. Pastikan Ollama berjalan dan `granite4.2:3b` tersedia.
2. Klik dua kali `Demo-Batch-50.cmd` untuk mencoba 50 lead dummy.
3. Tunggu progres `[1/50]` sampai selesai di terminal.
4. Buka `batch_output`, lalu subfolder yang disebutkan terminal, kemudian `results.csv`.

Tidak perlu menyalakan FastAPI atau membuka browser. Python memanggil model
Ollama langsung. File dipilih dari komputer dan tidak diunggah ke layanan cloud
dengan konfigurasi Ollama lokal bawaan.

## Data perusahaan sendiri

- `Start-LeadPilot.cmd` atau `Batch-CSV.cmd`: membuka pemilih satu file CSV Windows.
- `Batch-Folder.cmd`: membuka pemilih folder, kemudian memproses setiap `*.csv`
  di folder itu secara berurutan. Subfolder tidak dipindai.
- Pemilih dapat dibatalkan tanpa memulai analisis.

Simpan input dalam folder khusus. Folder hasil dibuat terpisah. Kolom tambahan,
misalnya `lead_id`, tetap dibawa ke hasil; hanya kolom lead yang dikenal dikirim
ke model. Input asli tidak diubah.

### Format CSV

Gunakan UTF-8 / CSV UTF-8 dari Excel. Pemisah koma, titik koma, dan tab didukung.
Header menggunakan nama berikut, huruf kecil tanpa spasi tambahan.

| Kolom | Isi |
|---|---|
| `name` | Wajib, nama kontak |
| `email` | Wajib, alamat email valid |
| `message` | Wajib, pesan 5–8000 karakter |
| `company` | Opsional, nama perusahaan |
| `company_size` | Opsional, bilangan bulat minimal 1 |
| `budget` | Opsional, rupiah bulat tanpa pemisah, contoh `5000000` |
| `service` | Opsional, layanan yang dibutuhkan |
| `timeline` | Opsional, target mulai |
| `source` | Opsional, sumber lead; kosong menjadi `csv` |
| `lead_id` atau kolom lain | Opsional, metadata yang dipertahankan |

Budget dan jumlah karyawan yang tidak diketahui boleh kosong. `0` pada budget
berarti nol, bukan data hilang. Jangan mengisi `Rp5.000.000`, `5 juta`, atau angka
desimal pada kolom budget. Budget yang hanya disebut dalam pesan belum mendapat
poin budget; isi kolom numeriknya bila nilainya sudah diketahui.

`samples/dummy-leads-50.csv` berisi 50 kontak fiktif dengan ID unik, alamat
`example.com`, perusahaan bertanda Dummy, variasi ukuran/budget dan pesan Indonesia
atau Inggris. Skenario meliputi pembelian automation, riset, dukungan pelanggan,
permintaan desain, promosi, serta pesan belum jelas. Urutan diacak dengan seed
tetap supaya demo dapat diulang. Dataset ini bukan data pelanggan asli atau
benchmark akurasi berlabel.

## Hasil

Setiap input mempunyai subfolder hasil tersendiri:

- `results.csv`: semua baris input, ditambah kolom analisis berawalan `lp_`.
- `errors.csv`: hanya baris gagal, beserta penyebabnya.
- `checkpoint.json`: hasil per baris untuk melanjutkan proses.

Kolom hasil meliputi intent, urgency, kategori, kecocokan layanan, ringkasan,
confidence model, skor, tier, alasan skor, dan flag tinjauan manusia.
`lp_row` adalah nomor record data (mulai 1), bukan nomor baris fisik file karena
pesan dapat mengandung newline. `lp_status` berisi `ok`, `error`, atau `pending`.
Jangan menganggap nilai analisis kosong pada baris error/pending sebagai skor nol.

Hasil disimpan setiap satu lead selesai. CSV memakai UTF-8 BOM agar mudah dibuka
di Excel. Teks yang berpotensi dibaca sebagai formula Excel diberi awalan apostrof
pada export. Tutup file hasil di Excel selama batch berjalan agar Windows tidak
mengunci file saat diperbarui.

Untuk review sales, filter `lp_status=ok`, periksa `lp_intent`, lalu urutkan
`lp_score` dari terbesar. Skor masih mengikuti aturan penjumlahan semula:
support/spam bisa mendapat poin dari sinyal lain. Tinjau intent dan
`lp_requires_human_review` sebelum follow-up; confidence model tidak terkalibrasi.

## Berhenti dan lanjut

Tekan Ctrl+C untuk berhenti. Jalankan input yang sama lagi; baris sukses dilewati,
baris error dicoba ulang, dan baris pending diproses. Mengubah isi CSV atau kode
pipeline menghasilkan folder hasil baru agar hasil lama tidak tercampur.

Jika proses ditutup paksa, `run.lock` dapat tertinggal. Pastikan proses batch lama
sudah tidak berjalan, kemudian hapus hanya `run.lock` di folder hasil terkait.
Jangan hapus checkpoint untuk melanjutkan proses.

## Lewat terminal

Jalankan dari folder project:

```powershell
.\.venv\Scripts\python.exe batch_process.py samples\dummy-leads-50.csv
.\.venv\Scripts\python.exe batch_process.py --pick file
.\.venv\Scripts\python.exe batch_process.py --pick folder
.\.venv\Scripts\python.exe batch_process.py "C:\Data\Leads" --output "C:\Data\HasilLead"
```

Untuk uji kecil, tambahkan `--limit 3`. Batas berlaku per file untuk baris yang
dicoba pada run tersebut, bukan total kumulatif. Jalankan ulang tanpa batas untuk
melanjutkan. Proses sequential agar model lokal tidak menerima 50 request sekaligus.
Durasi bergantung perangkat dan panjang pesan; terminal menampilkan progres nyata.

## Alur rekaman demo

Buka CSV sumber di Excel untuk menunjukkan banyak lead. Tutup file hasil jika
sedang terbuka, jalankan `Demo-Batch-50.cmd`, rekam progres terminal, lalu buka
hasil dan filter intent/tier. Agar demo diulang dari nol tanpa menghapus hasil,
gunakan `--output batch_output_demo_baru` di command terminal. Eksekusi normal
memakai checkpoint dan akan melewati baris yang sudah sukses.

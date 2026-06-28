# 🎯 PPG Tracker v2 — Pengumuman Calon Guru

Bot otomatis yang memantau halaman berita PPG Kemendikdasmen, **hanya**
fokus ke pengumuman yang judulnya cocok dengan kata kunci tertentu
(default: **"calon guru"** + **"2026"**), lalu mengirim email berisi:

- Judul & tanggal pengumuman
- Teks lengkap isi PDF pengumuman (sudah diekstrak otomatis)
- Link artikel asli & link PDF asli
- **File PDF asli dilampirkan langsung** di email

Email hanya terkirim kalau ada pengumuman **baru** atau **PDF yang sudah
ada isinya berubah** — bukan setiap kali script jalan.

---

## 📁 Struktur File

```
ppg-tracker/
├── ppg_tracker.py                    # Script utama (jangan perlu diedit kecuali nambah fitur)
├── config.py                         # ⭐ Semua setting yang BOLEH diubah ada di sini
├── requirements.txt                  # Dependency Python
├── ppg_cache.json                    # Auto-generated, jangan diedit manual
├── pdf_downloads/                    # Auto-generated, PDF disimpan sementara di sini
└── .github/workflows/ppg-tracker.yml # Jadwal otomatis (GitHub Actions)
```

---

## ⚙️ Cara Ganti Keyword Filter (paling sering dibutuhkan)

Buka `config.py`, cari bagian ini:

```python
KEYWORDS_WAJIB_ADA = ["calon guru", "2026"]
MODE_FILTER = "all"   # "all" = semua keyword wajib ada, "any" = salah satu cukup
```

Contoh kalau mau ganti jadi pantau "Guru Tertentu 2026" juga:

```python
KEYWORDS_WAJIB_ADA = ["guru tertentu", "2026"]
```

Tidak perlu sentuh `ppg_tracker.py` sama sekali untuk ini.

---

## 🚀 Setup dari Awal

### 1. Setup Gmail App Password
1. Aktifkan 2-Step Verification di https://myaccount.google.com/security
2. Buat **App Password** (16 karakter) khusus untuk "Mail"
3. Simpan password ini, dipakai di step 3

### 2. Push project ini ke GitHub
```bash
git init
git add .
git commit -m "Setup PPG Tracker v2"
git remote add origin https://github.com/USERNAME/ppg-tracker.git
git push -u origin main
```

### 3. Setup GitHub Secrets
Di repo GitHub → **Settings → Secrets and variables → Actions** → New repository secret:

| Secret Name | Isi |
|---|---|
| `EMAIL_SENDER` | Email Gmail pengirim |
| `EMAIL_PASSWORD` | App Password 16 karakter (bukan password Gmail biasa) |
| `EMAIL_RECIPIENT` | Email tujuan notifikasi |

### 4. Selesai
Workflow otomatis jalan jam **07:00 & 19:00 WIB** setiap hari.
Untuk test manual tanpa menunggu jadwal: tab **Actions** → pilih workflow
**"PPG Tracker - Cek Pengumuman Calon Guru"** → **Run workflow**.

---

## 🧪 Test Lokal (opsional)

```bash
pip install -r requirements.txt --break-system-packages
playwright install --with-deps chromium

export EMAIL_SENDER="emailmu@gmail.com"
export EMAIL_PASSWORD="app_password_16_karakter"
export EMAIL_RECIPIENT="tujuan@gmail.com"

python ppg_tracker.py
```

---

## 🔍 Cara Kerja Singkat

1. Buka `news/type/all` pakai **Playwright** (browser headless, supaya
   tidak diblokir sistem keamanan website — website ini memang melakukan
   blokir terhadap request HTTP biasa/non-browser)
2. Ambil semua judul+link berita, **filter** yang cocok keyword
3. Untuk tiap berita yang cocok, buka halaman detailnya, cari link PDF
   resminya (ada di tombol/link viewer PDF), download PDF-nya
4. Ekstrak teks dari PDF, hitung hash isinya
5. Bandingkan hash dengan `ppg_cache.json` dari pengecekan sebelumnya:
   - Belum pernah ada → tandai **BARU**
   - Sudah ada tapi hash beda (isi PDF diganti) → tandai **DIPERBARUI**
   - Hash sama → diabaikan, tidak ada email
6. Kalau ada yang BARU/DIPERBARUI → kirim email dengan PDF terlampir,
   lalu update `ppg_cache.json`

---

## 🆘 Troubleshooting

**Email tidak pernah terkirim padahal ada pengumuman baru di website**
- Cek tab Actions → lihat log run terakhir, cari baris yang menyebutkan jumlah berita yang lolos filter
- Mungkin keyword di `config.py` tidak cocok dengan judul aslinya → sesuaikan

**Error `playwright not found` saat test lokal**
```bash
pip install playwright --break-system-packages
playwright install chromium
```

**SMTP Authentication Error**
- Pastikan pakai App Password (16 karakter), bukan password Gmail biasa
- Pastikan 2-Step Verification sudah aktif

**Website berubah struktur HTML, parsing jadi gagal**
- Jalankan `python ppg_tracker.py` lokal, lihat output debug-nya
- Kemungkinan perlu update selector di `scrape_daftar_berita()` atau
  `ekstrak_url_pdf_asli()` di `ppg_tracker.py`

---

## 📝 Catatan Migrasi dari v1

Versi sebelumnya punya beberapa masalah yang sudah diperbaiki di v2 ini:

| Masalah di v1 | Perbaikan di v2 |
|---|---|
| Folder `.github/workflows/` tidak ada sama sekali | Sudah dibuat & divalidasi |
| `requirements.txt` tidak include `playwright` | Sudah disinkronkan |
| Semua berita (relevan atau tidak) dikirim ke email | Difilter keyword di `config.py` |
| Tidak ada pemrosesan PDF sama sekali | PDF didownload, diekstrak, dilampirkan |
| Deteksi "berubah" dibandingkan sebagai satu blok besar | Dibandingkan per-artikel via hash |

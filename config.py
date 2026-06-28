#!/usr/bin/env python3
"""
============================================================
KONFIGURASI PPG TRACKER
============================================================
File ini berisi semua setting yang boleh diubah-ubah.
TIDAK perlu sentuh file ppg_tracker.py kalau cuma mau ganti
keyword, URL, atau jadwal pengecekan.
============================================================
"""

# ------------------------------------------------------------
# 1. WEBSITE TARGET
# ------------------------------------------------------------
PPG_WEBSITE_BASE = "https://ppg.kemendikdasmen.go.id"
PPG_NEWS_URL = "https://ppg.kemendikdasmen.go.id/news/type/all"

# ------------------------------------------------------------
# 2. KEYWORD FILTER JUDUL BERITA
# ------------------------------------------------------------
# Berita yang di-proses HANYA yang judulnya mengandung SEMUA
# keyword di bawah ini (case-insensitive / besar-kecil huruf
# tidak masalah).
#
# Contoh:
#   ["calon guru", "2026"]
#   -> cuma lolos kalau judul punya "calon guru" DAN "2026"
#      misal: "Seleksi Pendidikan Profesi Guru (PPG) bagi
#      Calon Guru Tahun 2026" -> LOLOS
#      tapi  "Pelaksanaan PPG bagi Guru Tertentu Tahun 2026"
#      -> TIDAK LOLOS (gak ada "calon guru")
#
# Mau pantau topik lain? Tinggal ganti list ini, contoh:
#   ["guru tertentu", "2026"]   -> pantau PPG Guru Tertentu
#   ["calon guru"]              -> pantau semua tahun
KEYWORDS_WAJIB_ADA = ["calon guru", "2026"]

# Kalau mau pakai logika "salah satu boleh" (OR) bukan "semua
# wajib ada" (AND), ganti MODE_FILTER jadi "any".
# "all" = semua keyword di atas harus ada di judul (default)
# "any" = cukup salah satu keyword saja yang ada di judul
MODE_FILTER = "all"

# ------------------------------------------------------------
# 3. BERAPA HALAMAN BERITA YANG DICEK
# ------------------------------------------------------------
# Website PPG ada paginasi (?page=1, ?page=2, dst). Berita
# terbaru selalu di halaman 1. Biasanya 1 halaman cukup,
# tapi kalau mau jaga-jaga bisa naikkan ke 2 atau 3.
JUMLAH_HALAMAN_DICEK = 1

# ------------------------------------------------------------
# 4. EMAIL
# ------------------------------------------------------------
import os
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

# ------------------------------------------------------------
# 5. FILE-FILE LOKAL
# ------------------------------------------------------------
CACHE_FILE = "ppg_cache.json"
PDF_DOWNLOAD_DIR = "pdf_downloads"  # PDF disimpan sementara di sini sebelum dikirim

# ------------------------------------------------------------
# 6. LAIN-LAIN
# ------------------------------------------------------------
# Berapa banyak artikel teratas yang dicek detailnya per running
# (untuk hemat waktu & resource, gak semua 15+ artikel dibuka
# satu-satu, cukup yang match keyword saja yang dibuka detailnya)
MAX_ARTIKEL_DIBUKA_DETAIL = 10

# Panjang maksimal teks PDF yang ditampilkan di body email
# (PDF aslinya tetap dilampirkan lengkap, ini cuma buat body email
# biar gak kepanjangan banget kalau PDF-nya puluhan halaman)
MAX_KARAKTER_TEKS_PDF_DI_EMAIL = 8000

# 🚀 QUICK START - Setup dalam 5 Menit

## 1️⃣ Persiapan GitHub

```bash
# Clone/buat repo di GitHub
git clone https://github.com/USERNAME/ppg-tracker.git
cd ppg-tracker

# Copy file-file ke folder
# - ppg_tracker.py
# - requirements.txt
# - .github/workflows/ppg-tracker.yml

git add .
git commit -m "Init PPG Tracker"
git push origin main
```

## 2️⃣ Setup Gmail (5 menit)

1. **Enable 2-Step Verification:**
   - Go: https://myaccount.google.com/security
   - Search "2-Step Verification"
   - Follow instruksi

2. **Get App Password:**
   - Go: https://myaccount.google.com/apppasswords
   - Select: Mail + Windows Computer
   - Copy 16-char password

## 3️⃣ Setup GitHub Secrets

1. Buka GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Buat 3 secrets:

```
EMAIL_SENDER = emailmu@gmail.com
EMAIL_PASSWORD = abcd efgh ijkl mnop  (16-char App Password)
EMAIL_RECIPIENT = emailmu@gmail.com
```

## 4️⃣ Setup Selesai!

Website URL sudah di-set ke: `https://ppg.kemendikdasmen.go.id`

Script sudah dioptimasi untuk track:
- ✅ Pengumuman & berita PPG
- ✅ Judul-judul penting (PPG Calon Guru, Guru Tertentu, dll)
- ✅ Informasi seleksi dan registrasi
- ✅ Link penting (jadwal konsultasi, dll)

## 5️⃣ Test Lokal (Optional - Recommended!)

```bash
pip install -r requirements.txt
python test_scrape.py
```

Lihat output untuk identify elemen yang tepat.

## 6️⃣ Deploy!

Push ke GitHub, selesai! 🎉

Script akan otomatis jalan:
- **Pagi:** 07:00 WIB
- **Malam:** 19:00 WIB

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Email tidak masuk | Check GitHub Secrets, verify App Password |
| Tidak detect perubahan | Update CSS selectors, run `python test_scrape.py` |
| GitHub Actions error | Check Actions log tab di GitHub |

---

## 📞 Butuh bantuan?

Cek `README.md` untuk dokumentasi lengkap!

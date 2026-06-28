# 🪟 WINDOWS SETUP GUIDE - PPG Tracker dengan Playwright

## 🎯 Tujuan

Setup dan test PPG Tracker di Windows sebelum deploy ke GitHub.

---

## 📋 Prerequisites

Pastikan sudah punya:
- ✅ Python 3.8+ terinstall
- ✅ Git terinstall
- ✅ Internet connection
- ✅ GitHub repo sudah ada

---

## 🚀 Step-by-Step Setup

### **Step 1: Navigate ke Folder Project**

```bash
cd C:\Users\daryd\ITSME\AI\files\ppg-tracker
# Atau folder project kamu di mana saja
```

### **Step 2: Create `.env` File**

Buat file baru bernama `.env` di folder project:

```
EMAIL_SENDER=darydimas32@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
EMAIL_RECIPIENT=darydimas32@gmail.com
```

**Cara buat file `.env`:**
1. Buka Notepad
2. Paste content di atas
3. Save As → nama file: `.env` (bukan `.env.txt`!)
4. Location: folder project
5. Encoding: UTF-8

**Atau gunakan Command Line:**
```bash
# Windows Command Prompt
echo EMAIL_SENDER=darydimas32@gmail.com > .env
echo EMAIL_PASSWORD=your_app_password >> .env
echo EMAIL_RECIPIENT=darydimas32@gmail.com >> .env
```

### **Step 3: Install Dependencies**

```bash
# Install Python packages
pip install playwright beautifulsoup4 python-dotenv --break-system-packages

# Download Chrome browser (~200MB, tunggu beberapa menit)
playwright install chromium
```

### **Step 4: Test Run**

```bash
python ppg_tracker_playwright.py
```

**Expected Output:**

Kalau berhasil, akan terlihat:
```
================================================================================
🔍 PPG TRACKER (Playwright) | 2026-06-28 13:51:39
================================================================================

🌐 Membuka browser headless...
📡 Mengakses: https://ppg.kemendikdasmen.go.id/news/type/all
⏳ Menunggu content load...
✅ Berhasil! Ditemukan X berita

🔔 Ada perubahan! Mengirim email...
✅ Email dikirim ke darydimas32@gmail.com
✅ Cache diupdate

================================================================================
✅ Selesai!
================================================================================
```

---

## 🎨 Alternative: Gunakan Batch Script (Recommended)

Buat file `run_tracker.bat` di folder project:

```batch
@echo off
setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo PPG TRACKER - Windows Runner
echo ================================================================================
echo.

REM Set environment variables dari .env file
for /f "tokens=*" %%A in ('type .env') do set %%A

echo EMAIL_SENDER: %EMAIL_SENDER%
echo EMAIL_RECIPIENT: %EMAIL_RECIPIENT%
echo.

REM Run tracker
python ppg_tracker_playwright.py

pause
```

**Cara pakai:**
1. Buat file `run_tracker.bat` (sama seperti `.env`, save as `.bat`)
2. Double-click file tersebut untuk run

---

## 🔑 App Password Setup (Important!)

Sebelum isi `EMAIL_PASSWORD` di `.env`, harus **generate App Password** dari Gmail:

### **Cara Generate App Password:**

1. **Enable 2-Step Verification:**
   - Go: https://myaccount.google.com/security
   - Cari "2-Step Verification"
   - Follow instruksi

2. **Generate App Password:**
   - Go: https://myaccount.google.com/apppasswords
   - Select: **Mail** & **Windows Computer**
   - Google akan kasih 16-character password
   - **Copy password itu** ke `.env` file sebagai `EMAIL_PASSWORD`

**Example .env:**
```
EMAIL_SENDER=darydimas32@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
EMAIL_RECIPIENT=darydimas32@gmail.com
```

---

## ⚠️ Troubleshooting

### **Error: "No module named 'playwright'"**

```bash
pip install playwright --break-system-packages
playwright install chromium
```

### **Error: "403 Client Error: Forbidden"**

Berarti Playwright belum installed dengan benar. Try:

```bash
playwright install --with-deps chromium
```

### **Error: "Email/Password salah"**

- Pastikan App Password (bukan Gmail password)
- Pastikan 2-Step Verification sudah enabled
- Cek kembali di `.env` file - pastikan benar

### **Error: "File .env not found"**

Pastikan:
1. `.env` file ada di folder project
2. Nama file tepat: `.env` (bukan `.env.txt`, `.env.bat`, dll)
3. Location: same folder dengan `ppg_tracker_playwright.py`

### **Error: "Browser crashed"**

Coba:
```bash
# Uninstall dan reinstall
playwright install --force chromium
```

---

## 📊 File Structure

Folder project harus ada:

```
ppg-tracker/
├── ppg_tracker_playwright.py     (main script)
├── .env                           (environment variables) ← IMPORTANT
├── .github/
│   └── workflows/
│       └── ppg-tracker.yml       (GitHub Actions workflow)
├── ppg_cache.json                (auto-created saat first run)
├── requirements.txt              (optional, untuk deploy)
└── run_tracker.bat               (optional, untuk Windows convenience)
```

---

## 🎬 Workflow Testing

Setelah test berhasil lokal, langkah selanjutnya:

### **1. Update GitHub Secrets**

Go: GitHub Repo → Settings → Secrets and variables → Actions

Buat 3 secrets:
```
EMAIL_SENDER = darydimas32@gmail.com
EMAIL_PASSWORD = app_password_16_char
EMAIL_RECIPIENT = darydimas32@gmail.com
```

### **2. Verify Workflow File**

Pastikan `.github/workflows/ppg-tracker.yml` sudah updated dengan Playwright setup.

### **3. Commit & Push**

```bash
git add .
git commit -m "Setup Playwright for Windows and Linux"
git push origin main
```

### **4. Test GitHub Actions**

- Go GitHub Repo → Actions tab
- Click workflow "PPG Tracker - Check Schedule"
- Click "Run workflow" → "Run workflow"
- Wait for execution
- Check output/logs

---

## ✅ Checklist Sebelum Deploy

- [ ] `.env` file sudah created dengan benar
- [ ] App Password sudah generated dari Gmail
- [ ] `pip install` semua dependencies
- [ ] `playwright install chromium` sudah done
- [ ] `python ppg_tracker_playwright.py` berhasil (lihat "✅ Berhasil!")
- [ ] Email notification received
- [ ] GitHub Secrets sudah di-set (EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT)
- [ ] Workflow file updated
- [ ] Code pushed to GitHub

---

## 🎯 Expected Behavior

Setelah semua setup:

✅ **Lokal (Windows):**
- Run `python ppg_tracker_playwright.py`
- Script scrape berita PPG
- Jika ada perubahan → email kirim notifikasi
- Cache di-update

✅ **GitHub Actions (Otomatis):**
- Setiap hari jam 07:00 & 19:00 WIB
- Jalankan script otomatis
- Hasil sama seperti lokal

---

## 💡 Tips

1. **Test run pertama akan lambat** - Browser perlu download (~200MB)
2. **Setelah itu lebih cepat** - Chache browser sudah ada
3. **Di GitHub Actions juga lebih lambat** - Karena server cloud
4. **Tapi it's okay** - Pengecekan hanya 2x/hari anyway

---

## 📞 Q&A

**Q: Kenapa harus `.env` file?**
A: Lebih aman dan rapi. Bisa ignore dari git (add `.env` ke `.gitignore`)

**Q: Bisa langsung set environment variable tanpa `.env`?**
A: Bisa, tapi `.env` lebih convenient di Windows.

**Q: Script berapa lama running?**
A: ~10-15 detik (termasuk browser startup)

**Q: Harus test lokal dulu?**
A: Recommended, untuk pastikan semua berfungsi sebelum deploy

**Q: Kalau test lokal sukses, apakah GitHub Actions juga sukses?**
A: Mostly yes, tapi good practice tetap verify di GitHub Actions juga.

---

## 🎉 Selesai!

Setelah semua step selesai, bot akan:
- ✅ Tracking berita PPG otomatis
- ✅ 2x sehari (pagi & malam)
- ✅ Email notifikasi jika ada update
- ✅ Run tanpa intervensi manual

Happy tracking! 🔔

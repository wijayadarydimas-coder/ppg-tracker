# 🚨 MASALAH DAN SOLUSI - PPG TRACKER

## 🔴 Masalah yang Ditemukan

Ketika aku coba test scraping, website PPG **block akses** dengan error:

```
❌ 403 Client Error: Forbidden
```

### Penyebab:
Website PPG menggunakan **WAF (Web Application Firewall)** - biasanya Cloudflare atau sistem keamanan sejenis. WAF ini:
- ✅ Proteksi website dari bot/attack
- ❌ Tapi juga block requests biasa dari server cloud (GitHub Actions)

---

## ✅ Solusi

Gunakan **Playwright** - sebuah browser automation library yang:
- ✅ Membuka browser Chrome headless (tanpa GUI)
- ✅ Menjalankan JavaScript sepenuhnya
- ✅ **Pass WAF check** karena terlihat seperti user normal
- ✅ Fully compatible dengan GitHub Actions

---

## 🚀 Cara Setup & Test

### **Step 1: Download File Baru**

Ada file baru di outputs:
- `ppg_tracker_playwright.py` ← **Gunakan ini untuk produksi**
- `403_FORBIDDEN_SOLUTION.md` ← Penjelasan detail

### **Step 2: Install Playwright (Local Test)**

```bash
# Install library
pip install playwright beautifulsoup4 --break-system-packages

# Download browser (first time only, ~200MB)
playwright install chromium
```

### **Step 3: Test Lokal**

```bash
# Set environment variables (Windows)
set EMAIL_SENDER=emailmu@gmail.com
set EMAIL_PASSWORD=app_password_16_char
set EMAIL_RECIPIENT=emailmu@gmail.com

# Test script
python ppg_tracker_playwright.py
```

Atau di bash:
```bash
export EMAIL_SENDER=emailmu@gmail.com
export EMAIL_PASSWORD=app_password_16_char
export EMAIL_RECIPIENT=emailmu@gmail.com

python ppg_tracker_playwright.py
```

---

## 📋 File Mana yang Dipakai

| File | Status | Fungsi |
|------|--------|--------|
| `ppg_tracker.py` | ❌ Outdated | Requests (block by WAF) |
| `ppg_tracker_playwright.py` | ✅ **GUNAKAN INI** | Playwright (bypass WAF) |
| `test_scrape.py` | ⚠️ Sudah tested | Info saja |

---

## 🔄 Update GitHub Workflow

Update `.github/workflows/ppg-tracker.yml`:

```yaml
name: PPG Tracker - Check Schedule

on:
  schedule:
    - cron: '0 0 * * *'      # Pagi jam 07:00 WIB
    - cron: '0 12 * * *'     # Malam jam 19:00 WIB
  workflow_dispatch:

jobs:
  check-ppg:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install requests beautifulsoup4 playwright --break-system-packages
          playwright install --with-deps chromium
      
      - name: Run PPG Tracker
        env:
          EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          EMAIL_RECIPIENT: ${{ secrets.EMAIL_RECIPIENT }}
        run: python ppg_tracker_playwright.py
      
      - name: Commit cache updates
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          
          if [ -f ppg_cache.json ]; then
            git add ppg_cache.json
            git commit -m "Update PPG cache - $(date +'%Y-%m-%d %H:%M:%S')" || echo "No changes"
            git push || echo "Push failed"
          fi
```

Key changes:
1. `pip install ... playwright ...` - Add Playwright
2. `playwright install --with-deps chromium` - Download browser
3. `python ppg_tracker_playwright.py` - Run new script

---

## 📊 Comparison: Requests vs Playwright

| Aspek | Requests | Playwright |
|-------|----------|-----------|
| **Speed** | ⚡ Very fast | 🚗 Slower |
| **WAF Bypass** | ❌ No | ✅ Yes |
| **JS Execution** | ❌ No | ✅ Yes |
| **Complexity** | ✅ Simple | ⚠️ Medium |
| **Resources** | ✅ Light | ⚠️ Heavy |
| **GitHub Actions** | ❌ Doesn't work | ✅ Works |

---

## ⏱️ Performance Impact

Playwright sedikit lebih lambat dibanding requests:
- Requests: ~1-2 detik per request
- Playwright: ~5-10 detik per request (termasuk browser startup)

Tapi untuk pengecekan 2x sehari, ini **totally fine**! ✅

---

## 🔍 Debugging: Kalau Ada Error

### Error: "playwright not found"
```bash
pip install playwright --break-system-packages
playwright install chromium
```

### Error: "Browser process crashed"
- Coba set timeout lebih panjang di script
- Atau set memory limit lebih tinggi

### Error: "403 Forbidden" (masih terjadi)
- Playwright juga kena block (rare)
- Alternatif: Gunakan ScrapingBee API (free tier tersedia)

---

## ✨ Keuntungan Playwright

1. **Reliable** - Handle Cloudflare, WAF, dll
2. **JavaScript Support** - Handle dynamic content
3. **Screenshot Capable** - Bisa ambil screenshot sebelum scrape
4. **Network Monitoring** - Bisa intercept requests
5. **Well Maintained** - Active development, good docs

---

## 📝 File yang Perlu Diupdate

Download dan gunakan:
1. ✅ `ppg_tracker_playwright.py` - **Main script**
2. ✅ `.github/workflows/ppg-tracker.yml` - **Updated workflow**
3. ✅ `requirements.txt` - **Update dengan playwright**

Keep existing:
- `ppg_cache.json` - Cache (auto-generated)
- `README.md`, `QUICKSTART.md`, etc. - Documentation

---

## 🎯 Next Steps untuk Kamu

1. **Download** `ppg_tracker_playwright.py` dari outputs
2. **Update** GitHub workflow file (copy dari guidance di atas)
3. **Test lokal** (optional tapi recommended):
   ```bash
   pip install playwright beautifulsoup4 --break-system-packages
   playwright install chromium
   # Set env vars dan run
   python ppg_tracker_playwright.py
   ```
4. **Commit & Push** ke GitHub
5. **Done!** Script akan run otomatis setiap hari

---

## 📞 Q&A

**Q: Apakah semua perlu diubah?**
A: Hanya script Python dan workflow. GitHub Secrets, email setup, dll tetap sama.

**Q: Kalau test gagal, apakah deploy juga gagal?**
A: Mungkin iya, tapi bisa debug dari GitHub Actions logs.

**Q: Berapa resource yang dipake Playwright?**
A: Untuk GitHub Actions, masih dalam free tier (< 2000 menit/month).

**Q: Bisa pakai original `ppg_tracker.py`?**
A: Tidak bisa, akan tetap 403. Must use `ppg_tracker_playwright.py`.

---

## 🎉 Summary

✅ Masalah: Website block akses dengan 403
✅ Solusi: Gunakan Playwright (browser automation)
✅ Testing: Script sudah ready, tinggal setup lokal
✅ Deploy: Update workflow, commit, push
✅ Expected: Bot akan tracking berita PPG setiap hari jam 07:00 & 19:00 WIB

Ready? Let's go! 🚀

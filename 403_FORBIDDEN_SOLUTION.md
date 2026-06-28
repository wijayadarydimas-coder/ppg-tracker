# ⚠️ 403 Forbidden Error - Solusi & Cara Kerja

## 🔴 Masalah

Website PPG menggunakan **WAF (Web Application Firewall)** yang block akses dari:
- IP Server (GitHub Actions)
- Bot/Scraper biasa
- Request tanpa context yang tepat

Error yang muncul:
```
❌ 403 Client Error: Forbidden
```

---

## 🤔 Kenapa Ini Terjadi?

Website pemerintah sering menggunakan:
1. **Cloudflare Protection** - Block bot/scraper
2. **IP-based Firewall** - Hanya allow IP tertentu
3. **JavaScript-rendered Content** - Content dimuat via JS, bukan HTML statis
4. **Rate Limiting** - Block akses terlalu sering

---

## ✅ Solusi yang Bisa Dipakai

### **Solusi 1: Gunakan Playwright (Recommended)**

Playwright/Selenium adalah browser automation yang **pass WAF** karena:
- Menjalankan JavaScript real
- Terlihat seperti user normal
- Support Cloudflare bypass

**Setup:**

```bash
pip install playwright --break-system-packages

# Download browser (first time only)
playwright install chromium
```

**Script:**

```python
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

def scrape_with_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("🌐 Opening webpage...")
        page.goto("https://ppg.kemendikdasmen.go.id/news/type/all", timeout=30000)
        
        print("⏳ Waiting for content to load...")
        page.wait_for_timeout(2000)  # Wait 2 seconds for JS to render
        
        # Get page content
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Now scrape like normal
        news_items = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if '/news/' in href:
                title = link.get_text(strip=True)
                if title:
                    news_items.append({
                        "title": title,
                        "url": href
                    })
        
        browser.close()
        
        return news_items

if __name__ == "__main__":
    print("Scraping dengan Playwright...\n")
    items = scrape_with_playwright()
    print(f"\n✅ Ditemukan {len(items)} berita:")
    for idx, item in enumerate(items[:5], 1):
        print(f"{idx}. {item['title']}")
        print(f"   {item['url']}\n")
```

---

### **Solusi 2: Gunakan Requests dengan Proxy**

Jika ada proxy gratis/paid yang available:

```python
import requests

proxies = {
    'http': 'http://proxy-ip:port',
    'https': 'http://proxy-ip:port',
}

response = requests.get(
    'https://ppg.kemendikdasmen.go.id/news/type/all',
    proxies=proxies,
    timeout=10
)
```

---

### **Solusi 3: Gunakan Headless Browser Cloud Service**

Service seperti **ScrapingBee** atau **Apify** yang sudah handle Cloudflare:

```python
import requests

# ScrapingBee example
url = 'https://app.scrapingbee.com/api/v1/'
params = {
    'api_key': 'YOUR_API_KEY',
    'url': 'https://ppg.kemendikdasmen.go.id/news/type/all',
}

response = requests.get(url, params=params)
html = response.text
```

---

### **Solusi 4: Akses Langsung (Kalau Punya VPN/Public IP)**

Kalau kamu punya:
- Komputer pribadi (bukan server)
- VPN
- Public IP yang tidak di-block

Bisa jalankan script langsung dari komputer tanpa masalah WAF.

---

## 🎯 Rekomendasi untuk Kamu

Karena kamu pakai:
- ✅ GitHub Actions (gratis)
- ✅ Butuh scraping otomatis setiap hari

### **Best Practice:**

1. **Gunakan Playwright di GitHub Actions**
   - Setup:
     ```yaml
     - name: Install Playwright
       run: |
         pip install playwright --break-system-packages
         playwright install --with-deps
     ```
   
   - Pros: Free, reliable, handle WAF
   - Cons: Sedikit lebih lambat, butuh resources lebih

2. **Alternatif: Gunakan ScrapingBee Free Tier**
   - Pros: Cepat, reliable, 100 requests/month gratis
   - Cons: Butuh API key, limited free tier

3. **Alternatif: Akses dari Komputer Pribadi**
   - Setup cron job lokal atau Windows Task Scheduler
   - Pros: No WAF issue, faster
   - Cons: Butuh komputer always-on

---

## 🚀 Setup Playwright untuk GitHub Actions

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
        run: python ppg_tracker.py
      
      - name: Commit cache updates
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          
          if [ -f ppg_cache.json ]; then
            git add ppg_cache.json
            git commit -m "Update PPG cache" || echo "No changes"
            git push || echo "Push failed"
          fi
```

Update `ppg_tracker.py` untuk gunakan Playwright:

```python
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_ppg_info_with_playwright():
    """Scrape dengan Playwright untuk bypass WAF"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            page.goto(PPG_NEWS_URL, timeout=30000)
            page.wait_for_timeout(2000)  # Wait for JS
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # ... rest of scraping logic ...
            
            browser.close()
            return info_data
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        }
```

---

## 🧪 Test Playwright Lokal

Sebelum deploy ke GitHub:

```bash
# Install
pip install playwright --break-system-packages
playwright install chromium

# Test script
python ppg_tracker_playwright.py
```

---

## 📝 Summary

| Method | Pros | Cons | Cost |
|--------|------|------|------|
| **Requests (current)** | Simple, light | Blocked by WAF | Free |
| **Playwright** | Bypass WAF, reliable | Heavier, slower | Free |
| **ScrapingBee** | Very reliable, fast | Limited free tier | $0-5/mo |
| **VPN/Proxy** | Can work | Slow, unreliable | $1-5/mo |
| **Local Computer** | No WAF | Butuh always-on | Free |

---

## ❓ Q&A

**Q: Apa itu WAF?**
A: Web Application Firewall - protect website dari bot/attack

**Q: Kenapa website pake WAF?**
A: Security - proteksi dari DDoS, scraper, hacker

**Q: Playwright itu apa?**
A: Browser automation - membuka Chrome secara headless dan jalankan JavaScript

**Q: Apakah scraping legal?**
A: Tergantung:
- ✅ Scrape data publik → Legal
- ✅ Untuk personal use → Legal  
- ❌ Scrape data private/akun → Illegal
- ❌ Violate Terms of Service → Illegal

Untuk kasus PPG, scrape halaman berita publik adalah legal.

---

## 🔗 Resources

- Playwright Docs: https://playwright.dev/python/
- ScrapingBee: https://www.scrapingbee.com/
- Cloudflare Bypass: https://github.com/VenoMKO/CloudflareBypasser

---

Tanya kalau perlu bantuan setup Playwright! 😊

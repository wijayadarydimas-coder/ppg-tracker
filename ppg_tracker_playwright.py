#!/usr/bin/env python3
"""
PPG Tracker dengan Playwright - untuk bypass Cloudflare/WAF
Menggunakan headless browser untuk scraping yang lebih reliable
"""

import os
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from playwright.sync_api import sync_playwright
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Dependencies belum terinstall")
    print("\nInstall dengan:")
    print("  pip install playwright beautifulsoup4 --break-system-packages")
    print("  playwright install chromium")
    exit(1)

# ============ KONFIGURASI ============
PPG_WEBSITE_BASE = "https://ppg.kemendikdasmen.go.id"
PPG_NEWS_URL = "https://ppg.kemendikdasmen.go.id/news/type/all"
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

CACHE_FILE = "ppg_cache.json"

# ============ FUNGSI SCRAPING DENGAN PLAYWRIGHT ============
def scrape_ppg_info_playwright():
    """
    Scrape PPG news menggunakan Playwright (bypass WAF/Cloudflare)
    """
    try:
        print("🌐 Membuka browser headless...")
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Tambah header user-agent
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            print(f"📡 Mengakses: {PPG_NEWS_URL}")
            
            # Navigate with timeout
            page.goto(PPG_NEWS_URL, timeout=30000, wait_until='domcontentloaded')
            
            print("⏳ Menunggu content load...")
            # Wait untuk JavaScript render
            page.wait_for_timeout(3000)
            
            # Get page content
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            browser.close()
            
            # ============ EXTRACT BERITA ============
            info_data = {
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "news_items": [],
                "total_news": 0
            }
            
            # Cari link dengan /news/ di URL
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                # Filter: hanya link yang berisi /news/
                if '/news/' in href and title and len(title) > 5:
                    # Convert relative URL ke absolute
                    if href.startswith('/'):
                        href = PPG_WEBSITE_BASE + href
                    
                    info_data["news_items"].append({
                        "title": title[:150],
                        "url": href
                    })
            
            # Remove duplicates
            seen = set()
            unique_items = []
            for item in info_data["news_items"]:
                if item['url'] not in seen:
                    seen.add(item['url'])
                    unique_items.append(item)
            
            info_data["news_items"] = unique_items[:15]  # Max 15
            info_data["total_news"] = len(info_data["news_items"])
            info_data["jadwal"] = json.dumps(info_data["news_items"], ensure_ascii=False, indent=2)
            
            return info_data
            
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e),
            "news_items": [],
            "total_news": 0,
            "jadwal": f"Error: {str(e)}"
        }

# ============ FUNGSI CACHE ============
def load_cache():
    """Load data sebelumnya"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def save_cache(data):
    """Simpan data ke cache"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def is_content_changed(old_data, new_data):
    """Deteksi perubahan"""
    if not old_data:
        return True
    
    old_jadwal = old_data.get("jadwal", "")
    new_jadwal = new_data.get("jadwal", "")
    
    return old_jadwal != new_jadwal

# ============ FUNGSI EMAIL ============
def send_email(subject, body, content_html=None):
    """Kirim email notifikasi"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECIPIENT
        
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)
        
        if content_html:
            html_part = MIMEText(content_html, 'html')
            msg.attach(html_part)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email dikirim ke {EMAIL_RECIPIENT}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Email/Password salah")
        return False
    except Exception as e:
        print(f"❌ Error email: {str(e)}")
        return False

# ============ FUNGSI EMAIL HTML ============
def create_notification_html(info_data):
    """Buat HTML email"""
    
    if info_data.get("status") == "error":
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px;">
                <h2 style="margin: 0; color: #856404;">⚠️ Error Scraping Website PPG</h2>
                <p style="margin: 10px 0; color: #856404;">
                    <strong>Error:</strong> {info_data.get('error', 'Unknown error')}
                </p>
                <p style="margin: 10px 0; color: #666; font-size: 12px;">
                    Waktu: {info_data.get('timestamp', '')}
                </p>
            </div>
        </body>
        </html>
        """
    else:
        # Build news list
        news_html = ""
        try:
            news_items = json.loads(info_data.get('jadwal', '[]'))
            if isinstance(news_items, list):
                for idx, item in enumerate(news_items[:10], 1):
                    title = item.get('title', 'No title')
                    url = item.get('url', '')
                    
                    if url:
                        link_html = f'<a href="{url}" style="color: #0066cc; text-decoration: none;">{title}</a>'
                    else:
                        link_html = title
                    
                    news_html += f"""
                    <div style="background-color: #f9f9f9; padding: 12px; margin: 8px 0; border-left: 3px solid #0066cc; border-radius: 3px;">
                        <strong>{idx}. {link_html}</strong>
                    </div>
                    """
        except:
            news_html = f"""
            <div style="background-color: #f9f9f9; padding: 12px;">
                <p>{info_data.get('jadwal', 'Tidak ada informasi')}</p>
            </div>
            """
        
        total = info_data.get('total_news', 0)
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
            <div style="background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                <h2 style="margin: 0; color: #155724;">✅ Update Pengumuman PPG</h2>
                <p style="margin: 5px 0; color: #155724;">
                    Ada perubahan pengumuman di halaman berita PPG!<br>
                    📰 Total berita: <strong>{total}</strong>
                </p>
            </div>
            
            <div style="background-color: white; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                <h3 style="color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px;">
                    📋 Berita Terbaru
                </h3>
                {news_html}
            </div>
            
            <div style="background-color: #f9f9f9; padding: 12px; border-radius: 5px; font-size: 12px; color: #666;">
                <p style="margin: 5px 0;">
                    🌐 <a href="{PPG_NEWS_URL}" style="color: #0066cc; text-decoration: none;">Buka Website PPG</a>
                </p>
                <p style="margin: 5px 0;">
                    ⏰ Waktu: {info_data.get('timestamp', '')}
                </p>
                <p style="margin: 5px 0; color: #999;">
                    Bot pengecekan otomatis setiap hari jam 07:00 & 19:00 WIB
                </p>
            </div>
        </body>
        </html>
        """
    
    return html

# ============ MAIN FUNCTION ============
def main():
    print("=" * 80)
    print(f"🔍 PPG TRACKER (Playwright) | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Cek config
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT]):
        print("❌ Environment variables belum di-setup!")
        return
    
    # Scrape
    print("\n📡 Scraping website PPG dengan Playwright...")
    new_data = scrape_ppg_info_playwright()
    
    if new_data.get("status") == "error":
        print(f"❌ Error: {new_data.get('error')}")
        send_email(
            subject="❌ PPG Tracker - Error Scraping",
            body=f"Error: {new_data.get('error')}",
            content_html=create_notification_html(new_data)
        )
        return
    
    print(f"✅ Berhasil! Ditemukan {new_data.get('total_news', 0)} berita")
    
    # Check changes
    old_data = load_cache()
    
    if is_content_changed(old_data, new_data):
        print("🔔 Ada perubahan! Mengirim email...")
        
        send_email(
            subject="✅ PPG Tracker - Update Pengumuman PPG",
            body=f"""
Assalamu'alaikum,

Ada update pengumuman di halaman berita PPG!

Total berita terdeteksi: {new_data.get('total_news', 0)}

Silahkan cek: {PPG_NEWS_URL}

Waktu: {new_data.get('timestamp')}

---
PPG Tracker Bot (Powered by Playwright)
            """,
            content_html=create_notification_html(new_data)
        )
        
        save_cache(new_data)
        print("✅ Cache diupdate")
    else:
        print("✅ Tidak ada perubahan")
    
    print("=" * 80)
    print("✅ Selesai!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⛔ Dibatalkan")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

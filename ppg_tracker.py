import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

# ============ KONFIGURASI ============
PPG_WEBSITE_BASE = "https://ppg.kemendikdasmen.go.id"  # Website PPG resmi
PPG_NEWS_URL = "https://ppg.kemendikdasmen.go.id/news/type/all"  # Halaman berita PPG
EMAIL_SENDER = os.getenv("EMAIL_SENDER")  # Email pengirim (dari GitHub Secrets)
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Password/App Password
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")  # Email penerima

# Lokasi file untuk menyimpan data sebelumnya (untuk deteksi perubahan)
CACHE_FILE = "ppg_cache.json"

# ============ FUNGSI SCRAPING ============
def scrape_ppg_info():
    """
    Scrape informasi jadwal PPG dari website
    Sesuaikan selector CSS sesuai struktur HTML website PPG
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(PPG_NEWS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # ⚠️ PENTING: Sesuaikan selector CSS dibawah dengan struktur HTML website PPG
        # Contoh selector yang mungkin diperlukan:
        # - Cari class/id yang berisi "jadwal", "pembukaan", "pengumuman"
        # - Gunakan browser DevTools (F12) untuk inspect element
        
        info_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "news_items": [],
            "total_news": 0
        }
        
        # ============ SCRAPE DAFTAR BERITA ============
        # Cari semua item berita dari halaman /news/type/all
        
        news_items = []
        
        # Strategy 1: Cari element dengan berbagai kemungkinan class
        news_selectors = [
            'div.news-item',
            'article.news',
            'div.blog-item',
            'li.news',
            'a[href*="/news/"]',
            'div[class*="news"]',
            'div[class*="article"]'
        ]
        
        for selector in news_selectors:
            try:
                found_items = soup.select(selector)
                if found_items and len(found_items) > 2:
                    news_items = found_items
                    break
            except:
                pass
        
        # Extract informasi dari setiap berita
        for item in news_items[:15]:  # Ambil max 15 berita terbaru
            try:
                # Jika item adalah link
                if item.name == 'a' and item.get('href'):
                    title = item.get_text(strip=True)
                    url = item.get('href', '')
                    if url.startswith('/'):
                        url = PPG_WEBSITE_BASE + url
                    
                    if title and len(title) > 5:
                        info_data["news_items"].append({
                            "title": title[:150],
                            "url": url
                        })
                else:
                    # Jika item adalah container, cari link di dalamnya
                    link = item.find('a', href=True)
                    if link:
                        title = link.get_text(strip=True)
                        url = link.get('href', '')
                        if url.startswith('/'):
                            url = PPG_WEBSITE_BASE + url
                        
                        if title and len(title) > 5:
                            info_data["news_items"].append({
                                "title": title[:150],
                                "url": url
                            })
            except:
                pass
        
        info_data["total_news"] = len(info_data["news_items"])
        
        # Format untuk cache dan display
        info_data["jadwal"] = json.dumps(info_data["news_items"], ensure_ascii=False, indent=2)
        
        if not info_data["news_items"]:
            info_data["status"] = "warning"
            info_data["jadwal"] = "Tidak ada berita terdeteksi dari halaman /news"
        
        return info_data
        
    except requests.exceptions.RequestException as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e),
            "news_items": [],
            "total_news": 0,
            "jadwal": f"Error: {str(e)}"
        }

# ============ FUNGSI DETEKSI PERUBAHAN ============
def load_cache():
    """Load data sebelumnya dari cache file"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def save_cache(data):
    """Simpan data ke cache file"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def is_content_changed(old_data, new_data):
    """Deteksi apakah ada perubahan konten"""
    if not old_data:
        return True
    
    old_jadwal = old_data.get("jadwal", "")
    new_jadwal = new_data.get("jadwal", "")
    
    return old_jadwal != new_jadwal

# ============ FUNGSI EMAIL ============
def send_email(subject, body, content_html=None):
    """
    Kirim notifikasi email
    """
    try:
        # Setup email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECIPIENT
        
        # Plain text version
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)
        
        # HTML version (opsional)
        if content_html:
            html_part = MIMEText(content_html, 'html')
            msg.attach(html_part)
        
        # Kirim via SMTP Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email berhasil dikirim ke {EMAIL_RECIPIENT}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ ERROR: Email/Password salah atau App Password belum di-setup")
        return False
    except Exception as e:
        print(f"❌ ERROR saat mengirim email: {str(e)}")
        return False

# ============ FUNGSI EMAIL HTML ============
def create_notification_html(info_data):
    """Buat notifikasi email dengan format HTML yang nice"""
    
    if info_data.get("status") == "error":
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0;">
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
        # Build list of news items
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
                        <strong style="color: #333;">{idx}. {link_html}</strong>
                    </div>
                    """
        except:
            news_html = f"""
            <div style="background-color: #f9f9f9; padding: 12px; margin: 8px 0; border-radius: 3px;">
                <p>{info_data.get('jadwal', 'Tidak ada informasi')}</p>
            </div>
            """
        
        total_news = info_data.get('total_news', 0)
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
            <div style="background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 10px 0; border-radius: 5px;">
                <h2 style="margin: 0; color: #155724;">✅ Update Pengumuman PPG</h2>
                <p style="margin: 5px 0; color: #155724;">
                    Ada perubahan pengumuman di halaman berita PPG!
                </p>
                <p style="margin: 5px 0; color: #155724; font-size: 14px;">
                    📰 Total berita terdeteksi: <strong>{total_news}</strong>
                </p>
            </div>
            
            <div style="background-color: white; padding: 15px; margin: 10px 0; border-radius: 5px;">
                <h3 style="color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px;">
                    📋 Berita Terbaru
                </h3>
                {news_html}
            </div>
            
            <div style="background-color: #f9f9f9; padding: 12px; margin: 10px 0; border-radius: 5px; font-size: 12px; color: #666;">
                <p style="margin: 5px 0;">
                    <strong>🌐 Website:</strong> <a href="{PPG_NEWS_URL}" style="color: #0066cc; text-decoration: none;">{PPG_NEWS_URL}</a>
                </p>
                <p style="margin: 5px 0;">
                    <strong>⏰ Waktu Pengecekan:</strong> {info_data.get('timestamp', '')}
                </p>
                <p style="margin: 5px 0; color: #999;">
                    Bot ini melakukan pengecekan otomatis setiap hari pukul 07:00 WIB dan 19:00 WIB
                </p>
            </div>
        </body>
        </html>
        """
    
    return html

# ============ MAIN FUNCTION ============
def main():
    print("=" * 60)
    print(f"🔍 Memulai tracking PPG | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Cek konfigurasi
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT]):
        print("❌ ERROR: Environment variables belum di-setup!")
        print("   Pastikan EMAIL_SENDER, EMAIL_PASSWORD, dan EMAIL_RECIPIENT sudah di-set")
        return
    
    # Scrape website
    print("\n📡 Scraping website PPG...")
    new_data = scrape_ppg_info()
    
    if new_data.get("status") == "error":
        print(f"❌ Gagal scrape: {new_data.get('error')}")
        send_email(
            subject="❌ PPG Tracker - Error Scraping",
            body=f"Error: {new_data.get('error')}",
            content_html=create_notification_html(new_data)
        )
        return
    
    print(f"✅ Berhasil scrape website")
    
    # Load data sebelumnya
    old_data = load_cache()
    
    # Cek perubahan
    if is_content_changed(old_data, new_data):
        print("🔔 ADA PERUBAHAN! Mengirim email notifikasi...")
        
        send_email(
            subject="🔔 PPG Tracker - Ada Update Jadwal Pembukaan PPG!",
            body=f"""
Assalamu'alaikum,

Ada update informasi jadwal pembukaan PPG!

Informasi terbaru:
{new_data.get('jadwal', 'Tidak ada informasi')}

Silahkan cek website resmi PPG: {PPG_WEBSITE_URL}

Waktu pengecekan: {new_data.get('timestamp')}

---
PPG Tracker Bot
Pengecekan otomatis setiap pagi jam 07:00 dan malam jam 19:00
            """,
            content_html=create_notification_html(new_data)
        )
        
        # Update cache
        save_cache(new_data)
        print("✅ Cache diupdate")
        
    else:
        print("✅ Tidak ada perubahan, tidak mengirim email")
    
    print("=" * 60)
    print("✅ Selesai!")
    print("=" * 60)

if __name__ == "__main__":
    main()

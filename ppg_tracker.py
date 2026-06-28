import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

# ============ KONFIGURASI ============
PPG_WEBSITE_URL = "https://ppg.kemendikdasmen.go.id"  # Website PPG resmi
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
        
        response = requests.get(PPG_WEBSITE_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # ⚠️ PENTING: Sesuaikan selector CSS dibawah dengan struktur HTML website PPG
        # Contoh selector yang mungkin diperlukan:
        # - Cari class/id yang berisi "jadwal", "pembukaan", "pengumuman"
        # - Gunakan browser DevTools (F12) untuk inspect element
        
        info_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "jadwal": None,
            "pengumuman": None,
            "raw_html": soup.prettify()[:500]  # Simpan preview untuk debugging
        }
        
        # Extract informasi PPG dari berbagai sumber
        jadwal_info = []
        
        # 1. Ambil informasi dari section news/pengumuman
        news_section = soup.find('div', class_='news d-flex flex-column')
        if news_section:
            news_text = news_section.get_text(strip=True)
            jadwal_info.append(f"📰 Berita: {news_text[:150]}")
        
        # 2. Ambil semua h2 yang berisi info PPG (ini adalah judul-judul penting)
        for h2 in soup.find_all('h2'):
            h2_text = h2.get_text(strip=True)
            if any(keyword in h2_text.lower() for keyword in ['ppg', 'seleksi', 'administrasi', 'calon', 'guru']):
                jadwal_info.append(f"📌 {h2_text}")
        
        # 3. Ambil dari span yang berisi pengumuman penting
        for span in soup.find_all('span'):
            span_text = span.get_text(strip=True)
            if any(keyword in span_text.lower() for keyword in ['ppg', 'seleksi', 'tahun 2026', 'pendaftaran']):
                if len(span_text) > 15:  # Hindari span kosong
                    jadwal_info.append(f"✓ {span_text}")
        
        # 4. Ambil dari links yang berisi jadwal/konsultasi
        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True)
            if any(keyword in link_text.lower() for keyword in ['jadwal', 'konsultasi', 'seleksi']):
                jadwal_info.append(f"🔗 {link_text}")
        
        # Gabungkan semua informasi
        if jadwal_info:
            info_data["jadwal"] = "\n".join(jadwal_info)[:500]
        else:
            # Fallback: ambil text dari body
            body_text = soup.get_text()[:300]
            info_data["jadwal"] = body_text
        
        # Jika tidak ketemu, ambil semua text dari body (debugging)
        if not info_data["jadwal"]:
            body_text = soup.get_text()[:500]
            info_data["jadwal"] = body_text
        
        return info_data
        
    except requests.exceptions.RequestException as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
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
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
            <div style="background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 10px 0;">
                <h2 style="margin: 0; color: #155724;">✅ Update Informasi PPG</h2>
                <p style="margin: 10px 0; color: #155724;">
                    Ada perubahan informasi jadwal pembukaan PPG!
                </p>
            </div>
            
            <div style="background-color: white; padding: 15px; margin: 10px 0; border-radius: 5px;">
                <h3 style="color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px;">
                    📋 Informasi Terbaru
                </h3>
                <p style="color: #555; line-height: 1.6;">
                    {info_data.get('jadwal', 'Tidak ada informasi')}
                </p>
            </div>
            
            <div style="background-color: #f9f9f9; padding: 10px; margin: 10px 0; border-radius: 5px; font-size: 12px; color: #666;">
                <p>
                    <strong>Waktu Pengecekan:</strong> {info_data.get('timestamp', '')}<br>
                    <strong>Website:</strong> <a href="{PPG_WEBSITE_URL}">{PPG_WEBSITE_URL}</a>
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

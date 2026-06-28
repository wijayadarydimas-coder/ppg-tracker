#!/usr/bin/env python3
"""
Script untuk test scraping website PPG lokal
Gunakan ini untuk debug sebelum deploy ke GitHub
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def test_scrape():
    """Test scraping website PPG"""
    
    PPG_URL = "https://ppg.kemendikdasmen.go.id"  # ← Ganti dengan URL yang benar
    
    print("=" * 70)
    print(f"🔍 TEST SCRAPING PPG | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    print(f"\n📡 Mencoba akses: {PPG_URL}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(PPG_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"✅ Status Code: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Cari berbagai tipe elemen yang mungkin berisi info jadwal
        print("\n📋 Mencari elemen-elemen penting...\n")
        
        # Cari semua heading (h1, h2, h3)
        print("🔹 HEADINGS (H1, H2, H3):")
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            text = heading.get_text(strip=True)
            if text:
                print(f"   - [{heading.name}] {text[:80]}")
        
        # Cari divs dengan class tertentu
        print("\n🔹 DIVS DENGAN CLASS:")
        for div in soup.find_all('div', class_=True):
            classes = ' '.join(div.get('class', []))
            if any(word in classes.lower() for word in ['jadwal', 'pengumuman', 'info', 'berita', 'news']):
                text = div.get_text(strip=True)
                print(f"   - class='{classes}' → {text[:80]}")
        
        # Cari span/p dengan informasi penting
        print("\n🔹 SPAN/PARAGRAPH PENTING:")
        for tag in soup.find_all(['span', 'p']):
            text = tag.get_text(strip=True)
            if len(text) > 20 and any(word in text.lower() for word in ['jadwal', 'pembukaan', 'ppg', 'pendaftaran']):
                print(f"   - [{tag.name}] {text[:100]}")
        
        # Cari links (mungkin link ke jadwal)
        print("\n🔹 LINKS PENTING:")
        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True)
            href = link.get('href', '')
            if any(word in text.lower() or word in href.lower() for word in ['jadwal', 'pembukaan', 'download']):
                print(f"   - {text} → {href}")
        
        # Tampilkan preview raw HTML
        print("\n🔹 PREVIEW RAW HTML (500 char pertama):")
        print("-" * 70)
        print(soup.prettify()[:500])
        print("-" * 70)
        
        print("\n✅ Test selesai!")
        print("\n💡 INSTRUKSI SELANJUTNYA:")
        print("   1. Identifikasi class/id yang berisi jadwal/pengumuman dari hasil di atas")
        print("   2. Update 'selectors_to_try' di ppg_tracker.py dengan selector yang tepat")
        print("   3. Contoh selector: '.jadwal-pembukaan', '#pengumuman', '.informasi'")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {str(e)}")
        print("\n💡 Pastikan:")
        print(f"   - URL sudah benar: {PPG_URL}")
        print("   - Internet connection aktif")
        print("   - Website tidak di-block oleh firewall")

if __name__ == "__main__":
    test_scrape()

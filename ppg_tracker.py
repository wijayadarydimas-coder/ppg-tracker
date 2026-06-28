#!/usr/bin/env python3
"""
============================================================
PPG TRACKER v2 - Fokus Pengumuman + Ringkasan PDF
============================================================
Apa yang beda dari versi lama:
  1. Hanya proses berita yang judulnya match KEYWORDS_WAJIB_ADA
     di config.py (default: "calon guru" + "2026")
  2. Otomatis buka tiap artikel yang match, cari link PDF-nya,
     download, lalu ekstrak teksnya
  3. Email isi: judul, tanggal, teks lengkap PDF, link asli,
     DAN PDF asli dilampirkan sebagai attachment
  4. Status disimpan PER-ARTIKEL (bukan gabungan semua berita),
     jadi tahu mana yang "baru" vs mana yang "PDF-nya diupdate"
  5. Tetap pakai Playwright supaya aman dari WAF/anti-bot
============================================================
"""

import os
import json
import hashlib
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import urllib.request
import urllib.parse

from bs4 import BeautifulSoup

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Dependencies belum lengkap. Install dengan:")
    print("  pip install playwright beautifulsoup4 pdfplumber --break-system-packages")
    print("  playwright install --with-deps chromium")
    raise SystemExit(1)

try:
    import pdfplumber
except ImportError:
    print("pdfplumber belum terinstall. Install dengan:")
    print("  pip install pdfplumber --break-system-packages")
    raise SystemExit(1)

import config


# ============================================================
# 1. SCRAPE LIST BERITA (PAKAI PLAYWRIGHT)
# ============================================================
def ambil_html_dengan_playwright(url, tunggu_detik=3, cari_selector=None):
    """
    Buka satu URL dengan browser headless dan kembalikan HTML-nya.

    Kalau cari_selector diisi (contoh: 'a[href*="viewer.html"]'), Playwright
    akan menunggu sampai elemen itu BENAR-BENAR muncul di halaman (maksimal
    10 detik) sebelum mengambil HTML-nya. Ini lebih reliable dibanding cuma
    delay statis, karena javascript di tiap halaman bisa beda-beda lamanya.
    Kalau elemen tidak ditemukan dalam waktu itu, tetap lanjut ambil HTML
    apa adanya (supaya tidak macet selamanya).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        page.goto(url, timeout=30000, wait_until="domcontentloaded")

        if cari_selector:
            try:
                page.wait_for_selector(cari_selector, timeout=10000)
            except Exception:
                print(f"    [INFO] Selector '{cari_selector}' tidak muncul dalam 10s, lanjut pakai delay biasa.")

        page.wait_for_timeout(tunggu_detik * 1000)
        html = page.content()
        browser.close()
        return html


def judul_lolos_filter(judul):
    """Cek apakah judul berita lolos filter keyword di config.py."""
    judul_lower = judul.lower()
    keywords_lower = [k.lower() for k in config.KEYWORDS_WAJIB_ADA]

    if config.MODE_FILTER == "any":
        return any(k in judul_lower for k in keywords_lower)
    # default: "all" -> semua keyword wajib ada
    return all(k in judul_lower for k in keywords_lower)


def scrape_daftar_berita():
    """
    Buka halaman daftar berita PPG, ambil semua judul+link,
    lalu filter hanya yang match keyword di config.py.

    Return: list of dict [{judul, url, tanggal_text}, ...]
    """
    berita_lolos = []

    for halaman in range(1, config.JUMLAH_HALAMAN_DICEK + 1):
        url = config.PPG_NEWS_URL if halaman == 1 else f"{config.PPG_NEWS_URL}?page={halaman}"
        print(f"  Membuka halaman berita #{halaman}: {url}")

        html = ambil_html_dengan_playwright(url)
        soup = BeautifulSoup(html, "html.parser")

        # Judul berita biasanya dibungkus <h2><a>...</a></h2>. Tapi kalau
        # website ganti tema dan headingnya bukan <h2> lagi, fallback ke
        # SEMUA link yang mengarah ke /news/<slug> (bukan /news/category/
        # atau /news/type/ atau /news/tag/, karena itu link navigasi, bukan
        # artikel).
        kandidat_link = []
        for h2 in soup.find_all(["h2", "h3"]):
            a_tag = h2.find("a", href=True)
            if a_tag:
                kandidat_link.append(a_tag)

        if not kandidat_link:
            print("    (heading h2/h3 tidak ditemukan, pakai fallback: semua link /news/...)")
            kandidat_link = soup.find_all("a", href=True)

        for a_tag in kandidat_link:
            judul = a_tag.get_text(strip=True)
            href = a_tag["href"]

            if not judul or len(judul) < 8:
                continue
            if "/news/" not in href:
                continue
            # Skip link navigasi: /news/category/..., /news/type/..., /news/tag/...
            if any(seg in href for seg in ["/news/category/", "/news/type/", "/news/tag/"]):
                continue

            if href.startswith("/"):
                href = config.PPG_WEBSITE_BASE + href

            if judul_lolos_filter(judul):
                # Coba cari tanggal di teks sekitar (naik 2 level parent dari
                # link, biasanya di situ ada tanggal publikasi & kategori)
                tanggal_text = ""
                parent = a_tag.find_parent()
                for _ in range(2):
                    if parent and parent.find_parent():
                        parent = parent.find_parent()
                if parent:
                    teks_parent = parent.get_text(" ", strip=True)
                    match_tanggal = re.search(
                        r"\d{1,2}\s+\w+\s+\d{4}\s+pkl\.\s+\d{2}:\d{2}", teks_parent
                    )
                    if match_tanggal:
                        tanggal_text = match_tanggal.group(0)

                berita_lolos.append({
                    "judul": judul,
                    "url": href,
                    "tanggal_text": tanggal_text,
                })

    # Hilangkan duplikat berdasarkan URL
    unik = {}
    for b in berita_lolos:
        unik[b["url"]] = b

    hasil = list(unik.values())[: config.MAX_ARTIKEL_DIBUKA_DETAIL]
    print(f"  -> {len(hasil)} berita lolos filter keyword {config.KEYWORDS_WAJIB_ADA}")
    return hasil


# ============================================================
# 2. BUKA ARTIKEL, CARI & DOWNLOAD PDF
# ============================================================
def ekstrak_url_pdf_asli(html):
    """
    Halaman artikel PPG menampilkan link ke PDF viewer dengan format:
      https://cdn.appgtk.id/.../pdfreader/web/viewer.html?file=https://cdn.appgtk.id/.../namafile.pdf
    Fungsi ini mengembalikan URL PDF ASLI (setelah ?file=...), bukan
    URL viewer-nya, supaya bisa langsung di-download.

    Catatan: link aslinya kadang berisi SPASI MENTAH yang belum di-encode
    (contoh: ".../2026/0240 [SHARED] Pengumuman ....pdf"), jadi parsing-nya
    dibuat lapis-lapis (anchor tag dulu, fallback regex ke seluruh HTML)
    supaya tetap kebaca walau formatnya agak berantakan.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Lapis 1: cari di <a href="...">
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "pdfreader/web/viewer.html" in href and "file=" in href:
            url_pdf = href.split("file=", 1)[1].strip()
            if url_pdf:
                return url_pdf

    # Lapis 2: fallback - cari pola "viewer.html?file=....pdf" langsung di
    # raw HTML pakai regex (jaga-jaga kalau link-nya dirender beda, misal
    # lewat JS attribute lain seperti data-href, onclick, dll).
    # PENTING: nama file PDF asli sering mengandung SPASI MENTAH
    # (contoh: ".../0240 [SHARED] Pengumuman ....pdf"), jadi regex ini
    # SENGAJA mengizinkan spasi di dalam URL, cuma berhenti di quote,
    # kurung sudut HTML, atau baris baru.
    pola = r"viewer\.html\?file=(https?://[^\"'<>\n\r]+?\.pdf)"
    match = re.search(pola, html, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Lapis 3: fallback paling longgar - cari link .pdf apapun di halaman
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.lower().rstrip().endswith(".pdf") or ".pdf" in href.lower():
            return href.strip()

    return None


def debug_print_semua_link(html, maksimal=20):
    """Dipanggil saat gagal nemu PDF, supaya log GitHub Actions kasih info
    cukup untuk debugging tanpa perlu Bos cek manual ke website."""
    soup = BeautifulSoup(html, "html.parser")
    semua_href = [a["href"] for a in soup.find_all("a", href=True)]
    print(f"    [DEBUG] Total link ditemukan di halaman ini: {len(semua_href)}")
    relevan = [h for h in semua_href if "pdf" in h.lower() or "viewer" in h.lower() or "cdn.appgtk" in h.lower()]
    if relevan:
        print(f"    [DEBUG] Link yang mengandung 'pdf'/'viewer'/'cdn.appgtk' ({len(relevan)}):")
        for h in relevan[:maksimal]:
            print(f"      - {h}")
    else:
        print("    [DEBUG] Tidak ada link yang mengandung 'pdf'/'viewer'/'cdn.appgtk' sama sekali.")
        print(f"    [DEBUG] Contoh {min(maksimal, len(semua_href))} link pertama di halaman:")
        for h in semua_href[:maksimal]:
            print(f"      - {h}")


def rapikan_url(url):
    """
    URL PDF asli dari website PPG sering mengandung SPASI MENTAH dan
    karakter khusus seperti '[' ']' yang belum di-encode (contoh nama
    file: "0240 [SHARED] Pengumuman ....pdf"). Python's urllib menolak
    URL semacam itu ("URL can't contain control characters").

    Fungsi ini meng-encode ulang URL dengan benar TANPA merusak bagian
    skema/domain/parameter (':// ' , '?', '=' tetap apa adanya), supaya
    hasilnya valid untuk di-download.
    """
    bagian = urllib.parse.urlsplit(url)
    path_aman = urllib.parse.quote(bagian.path, safe="/")
    query_aman = urllib.parse.quote(bagian.query, safe="=&")
    return urllib.parse.urlunsplit(
        (bagian.scheme, bagian.netloc, path_aman, query_aman, bagian.fragment)
    )


def download_pdf(url_pdf, simpan_ke):
    """Download file PDF dari url_pdf, simpan ke path simpan_ke."""
    os.makedirs(os.path.dirname(simpan_ke), exist_ok=True)
    url_pdf_aman = rapikan_url(url_pdf)
    req = urllib.request.Request(
        url_pdf_aman,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        data = response.read()
    with open(simpan_ke, "wb") as f:
        f.write(data)
    return simpan_ke


def ekstrak_teks_pdf(path_pdf):
    """Ekstrak semua teks dari file PDF menggunakan pdfplumber."""
    teks_semua_halaman = []
    with pdfplumber.open(path_pdf) as pdf:
        for halaman in pdf.pages:
            teks = halaman.extract_text() or ""
            teks_semua_halaman.append(teks)
    return "\n".join(teks_semua_halaman).strip()


def hash_konten(teks):
    """Buat hash pendek dari suatu teks, dipakai untuk deteksi perubahan."""
    return hashlib.sha256(teks.encode("utf-8")).hexdigest()


def proses_satu_artikel(berita):
    """
    Buka 1 artikel, cari PDF-nya, download, ekstrak teks.
    Return dict berisi semua info, atau None kalau gagal/gak ada PDF.
    """
    print(f"  Membuka artikel: {berita['judul'][:70]}...")
    html = ambil_html_dengan_playwright(
        berita["url"], tunggu_detik=4, cari_selector='a[href*="viewer.html"], a[href$=".pdf"]'
    )

    url_pdf = ekstrak_url_pdf_asli(html)
    if not url_pdf:
        print("    Tidak ada PDF di artikel ini (atau gagal terdeteksi), dilewati.")
        debug_print_semua_link(html)
        return None

    nama_file = os.path.basename(url_pdf.split("?")[0])
    path_lokal = os.path.join(config.PDF_DOWNLOAD_DIR, nama_file)

    try:
        download_pdf(url_pdf, path_lokal)
        teks_pdf = ekstrak_teks_pdf(path_lokal)
    except Exception as e:
        print(f"    Gagal download/ekstrak PDF: {e}")
        return None

    return {
        "judul": berita["judul"],
        "url_artikel": berita["url"],
        "tanggal_text": berita["tanggal_text"],
        "url_pdf": url_pdf,
        "path_pdf_lokal": path_lokal,
        "nama_file_pdf": nama_file,
        "teks_pdf": teks_pdf,
        "hash_pdf": hash_konten(teks_pdf),
    }


# ============================================================
# 3. CACHE / STATE PER-ARTIKEL
# ============================================================
def load_cache():
    if os.path.exists(config.CACHE_FILE):
        try:
            with open(config.CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache):
    with open(config.CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def bandingkan_dengan_cache(hasil_artikel, cache):
    """
    Bandingkan tiap artikel hasil scraping dengan cache lama.
    Return list of dict yang sudah ditandai status-nya:
      "baru"      -> artikel ini belum pernah ada di cache
      "diperbarui"-> artikel sudah ada, tapi hash PDF beda
      "tidak_berubah" -> tidak ada yang berubah, gak perlu email
    """
    hasil_dengan_status = []
    for item in hasil_artikel:
        url = item["url_artikel"]
        cache_lama = cache.get(url)

        if cache_lama is None:
            status = "baru"
        elif cache_lama.get("hash_pdf") != item["hash_pdf"]:
            status = "diperbarui"
        else:
            status = "tidak_berubah"

        item["status"] = status
        hasil_dengan_status.append(item)

    return hasil_dengan_status


def update_cache(cache, hasil_artikel):
    for item in hasil_artikel:
        cache[item["url_artikel"]] = {
            "judul": item["judul"],
            "hash_pdf": item["hash_pdf"],
            "url_pdf": item["url_pdf"],
            "terakhir_dicek": datetime.now().isoformat(),
        }
    return cache


# ============================================================
# 4. EMAIL
# ============================================================
def potong_teks(teks, maks):
    if len(teks) <= maks:
        return teks
    return teks[:maks] + "\n\n[... teks dipotong, lihat PDF lampiran untuk versi lengkap ...]"


def buat_html_email(artikel_baru_dan_update):
    blok_artikel = ""
    for item in artikel_baru_dan_update:
        badge = "🆕 BARU" if item["status"] == "baru" else "🔄 DIPERBARUI"
        warna_badge = "#28a745" if item["status"] == "baru" else "#fd7e14"

        teks_pdf_dipotong = potong_teks(item["teks_pdf"], config.MAX_KARAKTER_TEKS_PDF_DI_EMAIL)
        teks_pdf_html = teks_pdf_dipotong.replace("\n", "<br>")

        blok_artikel += f"""
        <div style="background-color:#ffffff; border:1px solid #e0e0e0; border-radius:8px; padding:20px; margin-bottom:20px;">
            <span style="display:inline-block; background-color:{warna_badge}; color:white; font-size:11px; font-weight:bold; padding:3px 10px; border-radius:12px; margin-bottom:10px;">{badge}</span>
            <h3 style="margin:8px 0 4px 0; color:#1a1a1a;">{item['judul']}</h3>
            <p style="margin:0 0 12px 0; color:#777; font-size:13px;">📅 {item['tanggal_text'] or 'Tanggal tidak terdeteksi'}</p>
            <p style="margin:0 0 12px 0;">
                <a href="{item['url_artikel']}" style="color:#0066cc; text-decoration:none; font-size:14px;">🔗 Buka artikel asli</a>
                &nbsp;|&nbsp;
                <a href="{item['url_pdf']}" style="color:#0066cc; text-decoration:none; font-size:14px;">📄 Buka PDF asli</a>
            </p>
            <div style="background-color:#f9f9f9; border-left:3px solid #0066cc; padding:14px; border-radius:4px; font-size:13px; line-height:1.6; color:#333; max-height:500px; overflow:auto;">
                <strong>Isi PDF (lengkap):</strong><br><br>
                {teks_pdf_html}
            </div>
            <p style="margin-top:10px; font-size:12px; color:#999;">📎 File PDF asli dilampirkan di email ini ({item['nama_file_pdf']})</p>
        </div>
        """

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color:#f0f2f5; padding:20px; margin:0;">
        <div style="max-width:680px; margin:0 auto;">
            <div style="background-color:#0d6efd; padding:20px; border-radius:8px 8px 0 0;">
                <h2 style="margin:0; color:white;">📢 Update Pengumuman PPG Calon Guru</h2>
                <p style="margin:6px 0 0 0; color:#dce8ff; font-size:13px;">
                    Ditemukan {len(artikel_baru_dan_update)} pengumuman baru/diperbarui yang cocok dengan filter: {", ".join(config.KEYWORDS_WAJIB_ADA)}
                </p>
            </div>
            <div style="padding:20px; background-color:#f0f2f5;">
                {blok_artikel}
            </div>
            <div style="background-color:#f9f9f9; padding:15px; border-radius:0 0 8px 8px; font-size:12px; color:#777; text-align:center;">
                🌐 <a href="{config.PPG_NEWS_URL}" style="color:#0066cc;">Buka halaman berita PPG</a><br>
                ⏰ Dicek pada: {datetime.now().strftime('%d %B %Y, %H:%M')} WIB<br>
                Bot pengecekan otomatis PPG Tracker
            </div>
        </div>
    </body>
    </html>
    """
    return html


def kirim_email(subject, html_body, daftar_lampiran_pdf):
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = config.EMAIL_SENDER
    msg["To"] = config.EMAIL_RECIPIENT

    bagian_html = MIMEMultipart("alternative")
    bagian_html.attach(MIMEText("Email ini berisi HTML, mohon buka dengan email client yang support HTML.", "plain"))
    bagian_html.attach(MIMEText(html_body, "html"))
    msg.attach(bagian_html)

    for path_pdf in daftar_lampiran_pdf:
        try:
            with open(path_pdf, "rb") as f:
                lampiran = MIMEApplication(f.read(), _subtype="pdf")
                lampiran.add_header(
                    "Content-Disposition", "attachment", filename=os.path.basename(path_pdf)
                )
                msg.attach(lampiran)
        except Exception as e:
            print(f"    Gagal melampirkan {path_pdf}: {e}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(config.EMAIL_SENDER, config.EMAIL_PASSWORD)
        server.send_message(msg)

    print(f"  Email terkirim ke {config.EMAIL_RECIPIENT}")


# ============================================================
# 5. MAIN
# ============================================================
def main():
    print("=" * 70)
    print(f"PPG TRACKER v2 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Filter keyword judul: {config.KEYWORDS_WAJIB_ADA} (mode: {config.MODE_FILTER})")
    print("=" * 70)

    if not all([config.EMAIL_SENDER, config.EMAIL_PASSWORD, config.EMAIL_RECIPIENT]):
        print("Environment variable EMAIL_SENDER / EMAIL_PASSWORD / EMAIL_RECIPIENT belum di-set!")
        return

    print("\n[1/4] Scraping daftar berita...")
    daftar_berita = scrape_daftar_berita()

    if not daftar_berita:
        print("Tidak ada berita yang cocok dengan filter keyword saat ini. Selesai.")
        return

    print("\n[2/4] Membuka tiap artikel & mengekstrak PDF...")
    hasil_artikel = []
    for berita in daftar_berita:
        hasil = proses_satu_artikel(berita)
        if hasil:
            hasil_artikel.append(hasil)

    if not hasil_artikel:
        print("Tidak ada artikel dengan PDF yang berhasil diproses. Selesai.")
        return

    print("\n[3/4] Membandingkan dengan cache sebelumnya...")
    cache = load_cache()
    hasil_dengan_status = bandingkan_dengan_cache(hasil_artikel, cache)

    perlu_dikirim = [x for x in hasil_dengan_status if x["status"] in ("baru", "diperbarui")]

    for x in hasil_dengan_status:
        print(f"  - [{x['status'].upper()}] {x['judul'][:60]}")

    if not perlu_dikirim:
        print("\nTidak ada perubahan. Email tidak dikirim.")
        return

    print(f"\n[4/4] Mengirim email untuk {len(perlu_dikirim)} pengumuman baru/diperbarui...")
    html_email = buat_html_email(perlu_dikirim)
    daftar_lampiran = [x["path_pdf_lokal"] for x in perlu_dikirim]

    judul_singkat = perlu_dikirim[0]["judul"][:50]
    subject = f"📢 PPG Tracker: {judul_singkat}" if len(perlu_dikirim) == 1 else f"📢 PPG Tracker: {len(perlu_dikirim)} pengumuman Calon Guru 2026 diupdate"

    kirim_email(subject, html_email, daftar_lampiran)

    cache = update_cache(cache, hasil_dengan_status)
    save_cache(cache)
    print("\nCache diupdate. Selesai!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDibatalkan oleh user.")
    except Exception as e:
        print(f"\nError tak terduga: {e}")
        import traceback
        traceback.print_exc()

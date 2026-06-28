# 📋 PPG Tracker - Informasi Website & Tracking

## 🌐 Website Target

**URL:** https://ppg.kemendikdasmen.go.id  
**Nama:** Direktorat Pendidikan Profesi Guru (PPG) - Kemendikdasmen

---

## 📊 Apa yang Di-Track

Script akan mengumpulkan dan monitor perubahan pada:

### 1. **Pengumuman & Berita (News Section)**
- Section dengan class `news d-flex flex-column`
- Berisi pengumuman terbaru tentang PPG

### 2. **Judul-Judul Penting (H2 Elements)**
Mengambil semua H2 yang berisi keyword:
- ✅ PPG bagi Calon Guru (Prajabatan)
- ✅ PPG bagi Guru Tertentu (Dalam Jabatan)
- ✅ Seleksi Administrasi PPG Bagi Guru Tertentu Tahun 2026
- ✅ Dan pengumuman terbaru lainnya

### 3. **Informasi Terstruktur (Span/Paragraph)**
- Seleksi Pendidikan Profesi Guru (PPG) bagi Calon Guru Tahun 2026
- Pelaksanaan PPG bagi Guru Tertentu Tahun 2026 Tahap 2
- Dan informasi penting lainnya

### 4. **Link Penting**
- Jadwal Konsultasi Daring
- Link ke halaman seleksi
- Dan link penting lainnya

---

## 🔔 Kapan Email Dikirim?

Email **HANYA** dikirim jika ada **perubahan** di salah satu section di atas, seperti:
- ✅ Ada pengumuman baru
- ✅ Jadwal diupdate
- ✅ Informasi seleksi berubah
- ✅ Link baru ditambahkan

Jika tidak ada perubahan, email tidak dikirim (hemat inbox! 😊)

---

## 📅 Jadwal Pengecekan

Bot akan otomatis mengecek website:
- **Pagi:** 07:00 WIB (00:00 UTC)
- **Malam:** 19:00 WIB (12:00 UTC)

Jadi setiap hari ada 2x pengecekan, maksimal 2 email notifikasi per hari (jika ada perubahan).

---

## 📧 Format Email Notifikasi

Jika ada perubahan, kamu akan menerima email dengan format seperti:

```
Subject: 🔔 PPG Tracker - Ada Update Jadwal Pembukaan PPG!

Assalamu'alaikum,

Ada update informasi jadwal pembukaan PPG!

Informasi terbaru:
📰 Berita: [Berita terbaru dari website]
📌 [Judul-judul penting]
✓ [Informasi detail]
🔗 [Link-link penting]

Silahkan cek website resmi PPG: https://ppg.kemendikdasmen.go.id

Waktu pengecekan: [Timestamp]

---
PPG Tracker Bot
Pengecekan otomatis setiap pagi jam 07:00 dan malam jam 19:00
```

---

## 🔍 Debugging Tips

Kalau perlu debug atau cek struktur HTML lebih detail:

1. **Buka DevTools:**
   - Kunjungi https://ppg.kemendikdasmen.go.id
   - Tekan **F12**
   - Inspect elemen yang ingin dicek

2. **Run test script lokal:**
   ```bash
   python test_scrape.py
   ```
   
   Script ini akan menampilkan semua heading, div, span, dan link yang terdeteksi.

3. **Check GitHub Actions log:**
   - Buka repository di GitHub
   - Tab **Actions**
   - Klik workflow terakhir
   - Lihat output dari step "Run PPG Tracker"

---

## 🛠️ Customize Tracking

Kalau mau add/remove tracking element, edit `ppg_tracker.py` di fungsi `scrape_ppg_info()`:

### Contoh: Add tracking untuk section tertentu

```python
# Cari div dengan id tertentu
special_section = soup.find('div', id='section-id-tertentu')
if special_section:
    jadwal_info.append(f"🎯 {special_section.get_text(strip=True)}")
```

### Contoh: Track table data

```python
# Cari dan ambil dari table
for table in soup.find_all('table'):
    table_text = table.get_text(strip=True)
    jadwal_info.append(f"📊 {table_text[:100]}")
```

---

## ⚠️ Catatan Penting

1. **Scraping bukan hacking!** Kita hanya membaca konten publik dari website.

2. **Website mungkin berubah struktur:**
   - Jika website di-redesign/ubah struktur HTML, script mungkin perlu di-adjust
   - Kalau terjadi, bisa run `python test_scrape.py` lagi untuk identifikasi struktur baru

3. **Rate limiting:**
   - Script hanya access 2x per hari, sangat lightweight
   - Tidak akan cause beban ke server website PPG

4. **Cache system:**
   - Script menyimpan snapshot di file `ppg_cache.json`
   - Digunakan untuk detect perubahan dan avoid duplikat notifikasi

---

## 📞 Need Help?

- Check `README.md` untuk dokumentasi lengkap
- Check `QUICKSTART.md` untuk setup cepat
- Run `python test_scrape.py` untuk debug struktur HTML

Semoga tracker ini membantu! 🚀

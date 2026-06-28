# 🔄 UPDATE PPG TRACKER - OPTIMIZED FOR /NEWS PAGE

## 📰 Apa Yang Berubah

Script sekarang **fokus scraping halaman pengumuman/berita** untuk hasil yang lebih akurat:

### Link yang di-track:
- **Main:** `https://ppg.kemendikdasmen.go.id/news/type/all` (Semua berita)
- **Base:** `https://ppg.kemendikdasmen.go.id` (untuk resolve relative links)

---

## 📊 Cara Kerja Scraper

### 1. **Akses halaman /news/type/all**
   - Mengambil daftar berita/pengumuman PPG terbaru

### 2. **Ekstrak informasi berita**
   - Judul (title)
   - URL link ke detail berita
   - Max 15 berita terbaru

### 3. **Deteksi perubahan**
   - Bandingkan dengan cache sebelumnya (`ppg_cache.json`)
   - Jika ada perubahan → kirim email

### 4. **Format Email**
   - Tampilkan daftar berita dengan link yang bisa diklik
   - Numbered list (1. 2. 3. dst)
   - Direct link ke setiap berita

---

## 📧 Format Email Notifikasi

Ketika ada perubahan berita, email akan terlihat seperti:

```
Subject: ✅ Update Pengumuman PPG

---

✅ UPDATE PENGUMUMAN PPG
Ada perubahan pengumuman di halaman berita PPG!
📰 Total berita terdeteksi: 12

---

📋 BERITA TERBARU

1. [JUDUL BERITA 1]
   Link: https://ppg.kemendikdasmen.go.id/news/...

2. [JUDUL BERITA 2]
   Link: https://ppg.kemendikdasmen.go.id/news/...

...dst

---

🌐 Website: https://ppg.kemendikdasmen.go.id/news/type/all
⏰ Waktu Pengecekan: 2026-06-28 07:00:00
Bot pengecekan otomatis: Setiap hari jam 07:00 & 19:00 WIB
```

---

## 🔍 Debugging: Run Test Script

Kalau perlu verify bahwa scraper berfungsi:

```bash
# Install dependencies
pip install requests beautifulsoup4

# Run test
python test_scrape.py
```

Output akan menampilkan:
- ✅ Website bisa diakses
- ✅ Daftar semua link yang terdeteksi
- ✅ Preview struktur HTML

---

## 📋 Data Structure Cache

Script menyimpan info berita di `ppg_cache.json`:

```json
{
  "timestamp": "2026-06-28T07:00:00",
  "status": "success",
  "total_news": 12,
  "news_items": [
    {
      "title": "Seleksi Pendidikan Profesi Guru (PPG) bagi Calon Guru Tahun 2026",
      "url": "https://ppg.kemendikdasmen.go.id/news/seleksi-pendidikan-profesi-guru..."
    },
    {
      "title": "Pelaksanaan PPG bagi Guru Tertentu Tahun 2026 Tahap 2",
      "url": "https://ppg.kemendikdasmen.go.id/news/pelaksanaan-ppg-bagi-guru-tertentu..."
    }
    // ... dst
  ]
}
```

---

## 🎯 Apa yang di-Track

✅ **Judul berita/pengumuman PPG**
✅ **URL link ke detail berita**
✅ **Jumlah total berita**
✅ **Perubahan/penambahan berita baru**

---

## ⏰ Jadwal Pengecekan

- **Pagi:** 07:00 WIB (00:00 UTC)
- **Malam:** 19:00 WIB (12:00 UTC)

GitHub Actions akan otomatis trigger script pada waktu-waktu tersebut.

---

## 🛠️ Customization

### Kalau mau ubah jumlah berita yang di-track:
Edit `ppg_tracker.py` line ~74:
```python
for item in news_items[:15]:  # ← Ubah angka 15
```

### Kalau mau track berita dari kategori spesifik:
Ganti `PPG_NEWS_URL` dengan kategori yang diinginkan:
```python
# Contoh - hanya seleksi:
PPG_NEWS_URL = "https://ppg.kemendikdasmen.go.id/news/type/seleksi"

# Contoh - hanya pengumuman:
PPG_NEWS_URL = "https://ppg.kemendikdasmen.go.id/news/type/pengumuman"
```

---

## ⚠️ Jika Website Structure Berubah

Kalau website di-redesign dan scraper tidak bekerja:

1. Run test script:
   ```bash
   python test_scrape.py
   ```

2. Lihat output dan identifikasi selector baru

3. Update `ppg_tracker.py` di function `scrape_ppg_info()`:
   ```python
   news_selectors = [
       'div.news-item',     # ← Add selectors baru di sini
       'article.news',
       # ...
   ]
   ```

4. Test lagi, push ke GitHub

---

## 🎉 Setup Checklist

- [x] Script sudah optimize untuk halaman /news
- [x] Email template sudah updated
- [x] Cache system ready
- [x] Test script updated
- [x] Dokumentasi lengkap

**Ready to deploy!** 🚀

---

## 📞 Pertanyaan Umum

**Q: Berapa sering berita dicek?**
A: 2x sehari - pagi jam 07:00 WIB dan malam jam 19:00 WIB

**Q: Email dikirim setiap kali cek?**
A: Tidak! Hanya jika ada perubahan berita dibanding cek sebelumnya

**Q: Bisa track berita kategori tertentu?**
A: Bisa! Update `PPG_NEWS_URL` ke link kategori yang diinginkan

**Q: Berapa berita maksimal yang ditampilkan?**
A: Default 15 berita terbaru. Bisa diubah di script

**Q: Bagaimana kalau website error/down?**
A: Script akan log error dan retry di pengecekan berikutnya

---

Semoga update ini membantu! Happy tracking! 🔔

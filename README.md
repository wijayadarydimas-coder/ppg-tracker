# 🎯 PPG Tracker - Panduan Setup Lengkap

Aplikasi untuk otomatis tracking jadwal pembukaan PPG dan kirim notifikasi email.

---

## 📋 Apa yang Dilakukan

✅ Scrape website PPG setiap hari 2x (pagi jam 7:00 & malam jam 19:00)  
✅ Deteksi perubahan informasi jadwal pembukaan  
✅ Kirim email notifikasi otomatis jika ada perubahan  
✅ Simpan histori perubahan di file `ppg_cache.json`  

---

## 🚀 Step-by-Step Setup

### **STEP 1: Persiapan GitHub Repository**

1. Buat repository baru di GitHub (atau gunakan yang sudah ada)
2. Clone ke komputer lokal:
   ```bash
   git clone https://github.com/USERNAME/ppg-tracker.git
   cd ppg-tracker
   ```

3. Copy file-file yang sudah dibuat:
   - `ppg_tracker.py`
   - `requirements.txt`
   - `.github/workflows/ppg-tracker.yml` (buat folder `.github/workflows/` terlebih dahulu)

4. Push ke GitHub:
   ```bash
   git add .
   git commit -m "Initial commit: PPG Tracker setup"
   git push origin main
   ```

---

### **STEP 2: Setup Gmail (Email Sender)**

Gmail tidak memperbolehkan password biasa untuk aplikasi pihak ketiga. Kita perlu **App Password**:

1. **Enable 2-Step Verification di akun Google:**
   - Ke https://myaccount.google.com/
   - Pilih "Security" di sidebar kiri
   - Scroll ke "How you sign in to Google"
   - Klik "2-Step Verification" dan ikuti langkahnya

2. **Generate App Password:**
   - Setelah 2-Step Verification aktif, balik ke Security page
   - Cari "App passwords" (di bawah 2-Step Verification)
   - Pilih "Mail" dan "Windows Computer" (atau sesuai device mu)
   - Google akan generate password unik (16 karakter)
   - **Copy password ini!** (kita butuh di step selanjutnya)

---

### **STEP 3: Setup GitHub Secrets**

GitHub Secrets adalah tempat aman untuk menyimpan password/API key.

1. Buka repository di GitHub
2. Klik **Settings** → **Secrets and variables** → **Actions**
3. Klik tombol **"New repository secret"**
4. Buat 3 secrets berikut:

   | Secret Name | Nilai |
   |-------------|-------|
   | `EMAIL_SENDER` | Email Gmail mu (contoh: `namaku@gmail.com`) |
   | `EMAIL_PASSWORD` | App Password dari step sebelumnya (16 karakter) |
   | `EMAIL_RECIPIENT` | Email tujuan (bisa sama dengan EMAIL_SENDER atau email lain) |

   Contoh:
   ```
   EMAIL_SENDER = my.account@gmail.com
   EMAIL_PASSWORD = abcd efgh ijkl mnop  (16 char App Password)
   EMAIL_RECIPIENT = my.account@gmail.com
   ```

---

### **STEP 4: Update Website URL**

Sesuaikan URL website PPG yang ingin di-track:

1. Buka file `ppg_tracker.py`
2. Cari baris ini (biasanya di awal):
   ```python
   PPG_WEBSITE_URL = "https://www.ppg.kemdikbud.go.id/"
   ```
3. Ganti dengan URL yang benar dari situs PPG resmi

---

### **STEP 5: Customize CSS Selectors (PENTING!)**

Ini adalah langkah paling krusial! Kita perlu tahu struktur HTML website PPG untuk scrape dengan benar.

**Cara mencari selector CSS:**

1. Buka website PPG di browser
2. Tekan **F12** untuk buka DevTools
3. Klik tombol **"Inspect Element"** (atau tekan Ctrl+Shift+C)
4. Klik elemen yang berisi jadwal/pengumuman
5. Di DevTools, lihat struktur HTML-nya
6. Catat nama class atau ID-nya

Contoh yang mungkin ketemu:
- `<div class="jadwal-ppg">Jadwal Pembukaan...</div>` → selector: `.jadwal-ppg`
- `<h2 id="pengumuman">Pengumuman PPG</h2>` → selector: `#pengumuman`

Setelah ketemu selector, buka `ppg_tracker.py` dan update bagian ini:

```python
selectors_to_try = [
    "div.jadwal-ppg",        # ← Ganti ini dengan selector yang benar
    "div.pengumuman", 
    ".announcement",
    # ... dst
]
```

---

## ✅ Testing Lokal (Opsional)

Kalau pengin test script-nya lokal sebelum deploy:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (di terminal)
export EMAIL_SENDER="your_email@gmail.com"
export EMAIL_PASSWORD="your_app_password"
export EMAIL_RECIPIENT="recipient@gmail.com"

# Run script
python ppg_tracker.py
```

---

## 🕐 Jadwal Pengecekan

Script akan otomatis berjalan di GitHub setiap hari pada:

- **Pagi:** 07:00 WIB (00:00 UTC)
- **Malam:** 19:00 WIB (12:00 UTC)

⚠️ **Catatan:** GitHub Actions menggunakan timezone UTC. Jika jadwal tidak tepat, kita bisa adjust cron expression di `.github/workflows/ppg-tracker.yml`

---

## 🔍 Monitoring & Debugging

### Cek log eksekusi:
1. Buka repository di GitHub
2. Klik tab **Actions**
3. Pilih workflow **"PPG Tracker - Check Schedule"**
4. Lihat detail eksekusi terbaru
5. Expand section untuk lihat output (success/error messages)

### Troubleshooting:

**❌ "Email/Password salah atau App Password belum di-setup"**
- Pastikan App Password sudah di-generate dengan benar
- Jangan pakai password Gmail biasa, harus App Password
- Pastikan 2-Step Verification sudah diaktifkan

**❌ "Tidak ada informasi ditemukan"**
- CSS selectors mungkin tidak sesuai dengan struktur HTML
- Buka DevTools lagi dan update selectors
- Coba test dengan scrape manual dulu

**❌ "SMTP Connection Error"**
- Pastikan email yang di-set sudah benar
- Cek apakah Gmail sudah allow "Less secure app access" (jarang tapi bisa jadi issue)

---

## 📝 Struktur File

```
ppg-tracker/
├── ppg_tracker.py              # Main script scraping & email
├── requirements.txt            # Python dependencies
├── ppg_cache.json              # Cache hasil scraping (di-generate otomatis)
├── README.md                   # File ini
└── .github/
    └── workflows/
        └── ppg-tracker.yml     # GitHub Actions workflow
```

---

## 🎨 Customize Email Template

Kalau mau ubah format email, edit fungsi `create_notification_html()` di `ppg_tracker.py`.

Contoh: menambah logo, ubah warna, format text, dll.

---

## 💡 Tips & Tricks

1. **Test workflow tanpa menunggu schedule:**
   - Buka GitHub → Actions → PPG Tracker workflow
   - Klik "Run workflow" → trigger manual

2. **Disable notifikasi jika tidak ada perubahan:**
   - Sudah di-built in! Script hanya kirim email jika ada perubahan

3. **Tambah lebih banyak info:**
   - Ubah scraper untuk extract informasi lainnya (kontak, persyaratan, dll)

4. **Kirim ke multiple email:**
   - Modify `send_email()` function untuk loop through email list

---

## 🆘 Butuh Bantuan?

Jika ada error atau butuh customize lebih lanjut:
1. Check GitHub Actions logs (Actions tab)
2. Lihat error message di console output
3. Verify kembali:
   - URL website sudah benar
   - CSS selectors cocok dengan struktur HTML
   - GitHub Secrets sudah di-set dengan benar

---

## 📄 Lisensi

Bebas digunakan dan dimodifikasi sesuai kebutuhan.

Semoga membantu! 🚀

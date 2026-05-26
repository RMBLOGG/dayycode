# 🛒 Dayy Code — Source Code Marketplace

Platform jual beli source code website & aplikasi berbasis **Flask + Supabase**, deploy ke **Vercel**.

[![Facebook](https://img.shields.io/badge/Facebook-Dayy%20Code-1877F2?style=for-the-badge&logo=facebook&logoColor=white)](https://www.facebook.com/profile.php?id=61590162582037)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-082320781747-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/6282320781747)
[![Website](https://img.shields.io/badge/Website-dayycode.vercel.app-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://dayycode.vercel.app)

---

## ✨ Fitur

### Publik
- **Beranda** — produk unggulan, produk terbaru, statistik penjualan
- **Katalog Produk** — filter kategori, pencarian, sortir (terbaru / terlaris / harga)
- **Detail Produk** — deskripsi, fitur, screenshot, review, produk terkait
- **Pembelian** — form order, validasi voucher, konfirmasi via WhatsApp
- **Cek Pesanan** — tracking status order by nomor pesanan / email
- **Wishlist** — simpan produk favorit di localStorage
- **Review** — submit review setelah order dikonfirmasi
- **Halaman Info** — FAQ, Kebijakan Privasi, Syarat & Ketentuan

### Admin (`/admin`)
- **Dashboard** — statistik orders, revenue, produk terlaris
- **Manajemen Produk** — tambah / edit / hapus produk, upload gambar ke Cloudinary
- **Manajemen Order** — konfirmasi, approve, kirim link download
- **Voucher** — buat kode diskon (persen atau nominal), atur limit & expiry
- **Review Moderasi** — approve / hapus review pelanggan
- **Settings** — nama toko, kontak, metode pembayaran, warna tema

---

## 🛠 Tech Stack

| Layer | Teknologi |
|---|---|
| Backend | Python / Flask |
| Database | Supabase (PostgreSQL) |
| Storage Gambar | Cloudinary |
| Frontend | Jinja2 + Tailwind CSS |
| Deploy | Vercel (Serverless) |

---

## 📁 Struktur Proyek

```
dayycode-main/
├── api/
│   └── index.py          # Entry point Vercel
├── templates/
│   ├── base.html          # Layout utama (navbar, footer)
│   ├── index.html         # Beranda
│   ├── products_page.html # Katalog produk
│   ├── product_detail.html
│   ├── buy.html           # Form pembelian
│   ├── track.html         # Cek pesanan
│   ├── order_page.html    # Detail order setelah beli
│   ├── wishlist.html
│   ├── faq.html
│   ├── kebijakan_privasi.html
│   ├── syarat_ketentuan.html
│   ├── 404.html
│   ├── download_expired.html
│   ├── partials/
│   │   └── product_card.html
│   └── admin/
│       ├── base.html
│       ├── dashboard.html
│       ├── products.html
│       ├── orders.html
│       ├── order_detail.html
│       ├── vouchers.html
│       ├── reviews.html
│       ├── settings.html
│       └── login.html
├── static/
│   └── icon.png
├── app.py                 # Routes & logic utama
├── database.py            # Supabase client, helpers, seed
├── requirements.txt
├── vercel.json
└── supabase_schema.sql    # Schema tabel Supabase
```

---

## ⚙️ Setup Lokal

### 1. Clone & Install

```bash
git clone <repo-url>
cd dayycode-main
pip install -r requirements.txt
```

### 2. Buat Project Supabase

1. Buka [supabase.com](https://supabase.com) → buat project baru
2. Masuk ke **SQL Editor**, jalankan isi `supabase_schema.sql`
3. Salin **Project URL**, **Service Role Key**, dan **Anon Key** dari Settings → API

### 3. Buat Project Cloudinary

1. Buka [cloudinary.com](https://cloudinary.com) → buat akun
2. Salin **Cloud Name**, **API Key**, **API Secret** dari dashboard

### 4. Konfigurasi Environment

Buat file `.env` di root project (atau set langsung di terminal):

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_ANON_KEY=eyJ...
CLOUDINARY_CLOUD_NAME=nama-cloud
CLOUDINARY_API_KEY=123456789
CLOUDINARY_API_SECRET=abc123xyz
SECRET_KEY=ganti-dengan-random-string-panjang
```

### 5. Jalankan

```bash
python app.py
```

Buka `http://localhost:5000`

Login admin default:
- Username: `kalajengking`
- Password: `Dayynime`

> ⚠️ **Ganti password admin** setelah pertama login lewat Settings.

---

## 🚀 Deploy ke Vercel

### 1. Push ke GitHub

```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/username/dayycode.git
git push -u origin main
```

### 2. Import ke Vercel

1. Buka [vercel.com](https://vercel.com) → **Add New Project**
2. Import repo GitHub
3. Framework Preset: **Other**
4. Tambahkan Environment Variables di Vercel dashboard:

| Key | Value |
|---|---|
| `SUPABASE_URL` | URL project Supabase |
| `SUPABASE_SERVICE_KEY` | Service role key |
| `SUPABASE_ANON_KEY` | Anon key |
| `CLOUDINARY_CLOUD_NAME` | Cloud name |
| `CLOUDINARY_API_KEY` | API key |
| `CLOUDINARY_API_SECRET` | API secret |
| `SECRET_KEY` | Random string panjang |

5. Klik **Deploy**

---

## 🗄 Skema Database

Tabel utama di Supabase:

| Tabel | Deskripsi |
|---|---|
| `products` | Produk (judul, harga, deskripsi, gambar, dll) |
| `categories` | Kategori produk |
| `orders` | Data pesanan pembeli |
| `admins` | Akun admin |
| `vouchers` | Kode diskon |
| `reviews` | Review produk dari pembeli |
| `settings` | Konfigurasi toko (nama, kontak, pembayaran) |

Lihat `supabase_schema.sql` untuk DDL lengkap.

---

## 🔐 Keamanan

> ⚠️ Sebelum production, pastikan:

- [ ] Ubah `SECRET_KEY` ke nilai random yang kuat
- [ ] Ganti password admin default
- [ ] Hapus fallback hardcoded credentials di `database.py` (gunakan env var saja)
- [ ] Aktifkan RLS (Row Level Security) di Supabase jika diperlukan
- [ ] Batasi Cloudinary upload hanya dari server (preset unsigned dinonaktifkan)

---

## 📦 Alur Pembelian

```
Pembeli buka produk
    → Klik Beli
    → Isi form (nama, email, WhatsApp)
    → Opsional: masukkan kode voucher
    → Pilih metode pembayaran (DANA / OVO / GoPay)
    → Konfirmasi via WhatsApp ke admin
    → Admin verifikasi pembayaran di /admin/orders
    → Admin approve → sistem kirim link download
    → Pembeli download (max 3x, expired 48 jam)
```

---

## 📝 Kustomisasi

Semua pengaturan toko bisa diubah dari **Admin → Settings**:

- Nama & tagline toko
- Email & nomor WhatsApp
- Nomor rekening / e-wallet (DANA, OVO, GoPay)
- Warna tema utama
- Batas download & masa aktif link

---

## 📄 Lisensi

Source code ini dijual sebagai produk komersial oleh **Dayy Code**.  
Dilarang mendistribusikan ulang tanpa izin.

---

## 📬 Kontak

| Platform | Link |
|---|---|
| 🌐 Website | [dayycode.vercel.app](https://dayycode.vercel.app) |
| 📘 Facebook | [Dayy Code](https://www.facebook.com/profile.php?id=61590162582037) |
| 💬 WhatsApp | [082320781747](https://wa.me/6282320781747) |

---

*Built with ❤️ by [Dayy Code](https://dayycode.vercel.app)*

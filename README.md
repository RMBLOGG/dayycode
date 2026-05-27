# Dayy Code — Source Code Marketplace

Platform jual beli source code website & aplikasi berbasis **Flask + Supabase**, deploy ke **Vercel**.

[![Facebook](https://img.shields.io/badge/Facebook-Dayy%20Code-1877F2?style=for-the-badge&logo=facebook&logoColor=white)](https://www.facebook.com/profile.php?id=61590162582037)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-082320781747-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/6282320781747)
[![Website](https://img.shields.io/badge/Website-dayycode.vercel.app-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://dayycode.vercel.app)

---

## Fitur

### Publik
[![Beranda](https://img.shields.io/badge/Beranda-produk%20unggulan%20%26%20terbaru-4F46E5?style=flat-square&logo=home&logoColor=white)]()
[![Katalog](https://img.shields.io/badge/Katalog-filter%20%7C%20cari%20%7C%20sortir-4F46E5?style=flat-square&logo=search&logoColor=white)]()
[![Pembelian](https://img.shields.io/badge/Pembelian-voucher%20%26%20konfirmasi%20WA-4F46E5?style=flat-square&logo=shoppingcart&logoColor=white)]()
[![Wishlist](https://img.shields.io/badge/Wishlist-simpan%20produk%20favorit-4F46E5?style=flat-square&logo=heart&logoColor=white)]()
[![Review](https://img.shields.io/badge/Review-submit%20setelah%20order-4F46E5?style=flat-square&logo=star&logoColor=white)]()
[![Tracking](https://img.shields.io/badge/Cek%20Pesanan-by%20nomor%20%2F%20email-4F46E5?style=flat-square&logo=package&logoColor=white)]()

### Admin (`/admin`)
[![Dashboard](https://img.shields.io/badge/Dashboard-statistik%20%26%20revenue-6D28D9?style=flat-square&logo=barchart&logoColor=white)]()
[![Produk](https://img.shields.io/badge/Produk-tambah%20%7C%20edit%20%7C%20hapus-6D28D9?style=flat-square&logo=box&logoColor=white)]()
[![Order](https://img.shields.io/badge/Order-approve%20%26%20kirim%20download-6D28D9?style=flat-square&logo=clipboardlist&logoColor=white)]()
[![Voucher](https://img.shields.io/badge/Voucher-diskon%20persen%20%2F%20nominal-6D28D9?style=flat-square&logo=tag&logoColor=white)]()
[![Review Mod](https://img.shields.io/badge/Moderasi-approve%20%2F%20hapus%20review-6D28D9?style=flat-square&logo=shield&logoColor=white)]()

---

## Tech Stack

[![Python](https://img.shields.io/badge/Python-Flask-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)]()
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Image%20Storage-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white)]()
[![Tailwind](https://img.shields.io/badge/Tailwind-CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)]()
[![Vercel](https://img.shields.io/badge/Vercel-Deploy-000000?style=for-the-badge&logo=vercel&logoColor=white)]()

---

## Struktur Proyek

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

## Setup Lokal

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

Buat file `.env` di root project:

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

> [![Warning](https://img.shields.io/badge/Penting-Ganti%20password%20admin%20setelah%20login%20pertama-orange?style=flat-square&logo=alerttriangle&logoColor=white)]()

---

## Deploy ke Vercel

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
4. Tambahkan Environment Variables:

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

## Skema Database

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

## Keamanan

[![Secret Key](https://img.shields.io/badge/--Ubah%20SECRET__KEY%20ke%20nilai%20random%20kuat-red?style=flat-square&logo=key&logoColor=white)]()
[![Admin Pass](https://img.shields.io/badge/--Ganti%20password%20admin%20default-red?style=flat-square&logo=lock&logoColor=white)]()
[![Credentials](https://img.shields.io/badge/--Hapus%20hardcoded%20credentials%20di%20database.py-red?style=flat-square&logo=shield&logoColor=white)]()
[![RLS](https://img.shields.io/badge/--Aktifkan%20RLS%20di%20Supabase-red?style=flat-square&logo=database&logoColor=white)]()

---

## Alur Pembelian

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

## Kustomisasi

Semua pengaturan toko bisa diubah dari **Admin → Settings**:

- Nama & tagline toko
- Email & nomor WhatsApp
- Nomor rekening / e-wallet (DANA, OVO, GoPay)
- Warna tema utama
- Batas download & masa aktif link

---

## Lisensi

Source code ini dijual sebagai produk komersial oleh **Dayy Code**.
Dilarang mendistribusikan ulang tanpa izin.

---

## Kontak

[![Website](https://img.shields.io/badge/Website-dayycode.vercel.app-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://dayycode.vercel.app)
[![Facebook](https://img.shields.io/badge/Facebook-Dayy%20Code-1877F2?style=for-the-badge&logo=facebook&logoColor=white)](https://www.facebook.com/profile.php?id=61590162582037)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-082320781747-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/6282320781747)

---

*Built with [![Flask](https://img.shields.io/badge/-Flask-000000?style=flat&logo=flask&logoColor=white)]() by [Dayy Code](https://dayycode.vercel.app)*

# 🏠 Katalog Lelang Properti — NTB & NTT

Aplikasi Streamlit untuk menjelajahi katalog lelang properti dari Booklet PDF KPKNL.

## Struktur Direktori

```
lelang_app/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Dependencies
├── Booklet.pdf             # ← Letakkan PDF kamu di sini
├── README.md
├── utils/
│   ├── parser.py           # Parser PDF → DataFrame
│   └── renderer.py         # Render halaman PDF → gambar
└── cache/                  # Cache gambar (auto-generated)
```

## Cara Pakai

### 1. Install dependencies

```bash
cd lelang_app
pip install -r requirements.txt
```

> **macOS:** perlu install `poppler` dulu untuk pdf2image:
> ```bash
> brew install poppler
> ```
>
> **Ubuntu/Debian:**
> ```bash
> sudo apt-get install poppler-utils
> ```

### 2. Letakkan PDF

Salin `Booklet.pdf` ke dalam folder `lelang_app/`:
```bash
cp /path/to/Booklet.pdf ./Booklet.pdf
```

### 3. Jalankan

```bash
streamlit run app.py
```

Buka browser di `http://localhost:8501`

---

## Fitur

- 🔍 **Search** — cari berdasarkan alamat, kawasan, fasilitas
- 📍 **Filter Wilayah** — Mataram, Lombok Timur, Bima, Kupang, dll
- 🏷️ **Filter Tipe** — Rumah, Tanah, Ruko, Gudang
- 💰 **Filter Harga** — slider range harga limit
- 📐 **Filter Luas Tanah** — slider m²
- 📅 **Filter Jadwal** — hanya yang sudah ada tanggal lelang
- 🔃 **Sortir** — harga, luas, wilayah
- 🖼️ **Preview Halaman PDF** — tiap kartu menampilkan gambar halaman asli
- 📊 **Statistik** — grafik sebaran wilayah, tipe properti, distribusi harga
- 📋 **Detail View** — expander dengan info lengkap + gambar full

---

## Catatan

- Render gambar PDF membutuhkan waktu di run pertama, setelah itu di-cache otomatis
- PDF bisa juga di-upload langsung lewat sidebar tanpa mengganti file default

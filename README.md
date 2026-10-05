# Pemantauan Pemulihan Pascabencana Banjir Bandang Sumatera 2025

Dasbor interaktif yang memetakan dampak dan pemulihan **674 kecamatan** di 52 kabupaten/kota terdampak banjir bandang dan tanah longsor November 2025 di Provinsi **Aceh, Sumatera Utara, dan Sumatera Barat**, dengan memadukan data Badan Pusat Statistik (BPS) dan citra satelit.

**Dasbor:** _(tautan Streamlit Cloud)_

Proyek UAS mata kuliah Visualisasi Data dan Informasi, Politeknik Statistika STIS, 2026.
Burhanudin Alfadlil Prastyo · 222313022 · 3SD2

## Pertanyaan yang dijawab

1. Kecamatan mana yang paling terdampak, dilihat dari perubahan cahaya malam dan vegetasi?
2. Sejauh mana kecamatan sudah pulih hingga Juli–Agustus 2026?
3. Apakah kondisi sosial-ekonomi sebelum bencana berkaitan dengan besarnya dampak dan pemulihan?

## Isi dasbor

| Halaman | Visualisasi | Topik |
|---|---|---|
| Ringkasan | Peta status pemulihan, angka kunci, komposisi per provinsi, temuan utama | Geospasial |
| Peta dampak | Choropleth 5 indikator, simbol proporsional cahaya yang hilang, peringkat kecamatan | Geospasial |
| Profil kab/kota | Biplot PCA, peta klaster, parallel coordinates, heatmap terklaster (brushing & linking) | Multivariat |
| Hierarki | Treemap dan sunburst provinsi → kab/kota → kecamatan | Hierarki |
| Tentang | Sumber data, periode citra, keterbatasan | – |

## Data

**Data utama (BPS), tingkat kab/kota, 2024:** persentase penduduk miskin (P0), indeks kedalaman kemiskinan (P1), IPM, rata-rata lama sekolah, umur harapan hidup, pengeluaran per kapita, tingkat pengangguran terbuka, PDRB per kapita ADHB, dan kepadatan penduduk. Judul tabel, URL, dan tanggal akses tercantum di `data/processed/bps_kabkota_2024.xlsx` (sheet `sumber`).

**Data pendukung:**
- Cahaya malam: NOAA VIIRS DNB bulanan (VCMSLCFG), ±500 m
- Vegetasi: NASA MODIS MOD13Q1 NDVI, 250 m
- Curah hujan: CHIRPS harian, ±5,5 km
- Batas kecamatan: Badan Informasi Geospasial (edisi Juli 2026); kode Kemendagri dicocokkan dengan kode BPS

**Periode citra:** sebelum bencana Jun–Okt 2025; pembanding musiman Des 2024–Jan 2025; saat bencana Des 2025–Jan 2026; pemulihan Jul–Agu 2026.

## Metode singkat

- **Dampak** = perubahan cahaya malam Des 2025–Jan 2026 dibanding **musim yang sama setahun sebelumnya** (Des 2024–Jan 2025), agar efek musim hujan tidak terbaca sebagai dampak bencana.
- **Pemulihan** = cahaya malam Jul–Agu 2026 dibanding Jun–Okt 2025.
- Kecamatan dengan radiance awal < 0,5 nW/cm²/sr dianggap terlalu gelap untuk dihitung rasionya.
- Analisis multivariat 52 kab/kota (13 variabel): standardisasi, PCA, k-means (k = 4, dipilih dengan skor silhouette), klaster hierarki Ward untuk heatmap, dan korelasi Spearman.

## Struktur repositori

```
├── app.py                      # dasbor Streamlit
├── requirements.txt
├── .streamlit/config.toml      # tema
├── assets/logo_stis.png
├── gee/gee_zonal_kecamatan.js  # zonal statistics di Google Earth Engine
├── scripts/
│   ├── olah_data.py            # indikator per kecamatan + gabung dengan BPS
│   ├── analisis.py             # PCA, klaster, korelasi
│   └── buat_latar.py           # lapisan latar peta 3 provinsi
└── data/
    ├── raw/                    # hasil ekspor GEE, kompilasi tabel BPS
    ├── reference/              # 52 kab/kota terdampak + kode BPS & Kemendagri
    ├── geo/                    # batas kecamatan & latar peta
    └── processed/              # data olahan & hasil analisis
```

## Menjalankan secara lokal

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Untuk mereproduksi data olahan dari awal:

1. Unggah `data/geo/kecamatan_terdampak.zip` ke Google Earth Engine sebagai asset, lalu jalankan `gee/gee_zonal_kecamatan.js` dan simpan CSV hasilnya ke `data/raw/`.
2. `python scripts/olah_data.py`
3. `python scripts/analisis.py`
4. (Opsional) `pip install geopandas` lalu `python scripts/buat_latar.py "<path batas kecamatan BIG .shp>"`

## Keterbatasan

- Cahaya malam mengukur aktivitas, bukan kesejahteraan; lampu dapat menyala karena hunian sementara, posko, atau proyek rekonstruksi.
- 348 kecamatan terlalu gelap untuk diukur dengan cahaya malam.
- Perubahan cahaya juga dipengaruhi pertumbuhan perkotaan dari tahun ke tahun.
- Resolusi MODIS 250 m terlalu kasar untuk longsor kecil; data BPS hanya tersedia di tingkat kab/kota.

## Deklarasi penggunaan AI

Asisten AI (Claude, Anthropic) digunakan sebagai alat bantu dalam penyusunan kode pengolahan data, analisis, dan dasbor. Seluruh pilihan data, rancangan, hasil, dan interpretasi telah diperiksa dan menjadi tanggung jawab penulis.

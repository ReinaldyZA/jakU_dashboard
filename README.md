# 🌿 JakU - Pantau Udara, Jaga Jakarta

Dashboard publik kualitas udara DKI Jakarta berbasis **data ISPU 2024** dengan prediksi machine learning (**XGBoost**).

Dibangun sebagai bagian dari skripsi:

> **Implementasi Metodologi CRISP-DM Menggunakan Machine Learning dengan Pendekatan User Centered Design sebagai Sistem Pendukung Keputusan Kualitas Udara di Provinsi DKI Jakarta Berdasarkan Data ISPU**

## ✨ Fitur

- **Dashboard (Beranda)** — ringkasan ISPU rata-rata DKI Jakarta, peta 6 wilayah, tren 7 hari, prediksi besok / 3 hari / 7 hari, rekomendasi aktivitas.
- **Detail Wilayah** — info kualitas udara per wilayah administratif (6 wilayah: Pusat, Utara, Barat, Timur, Selatan, Kep. Seribu) lengkap dengan komposisi polutan, tren, pola harian, dan prediksi.
- **Prediksi & Analisis** — chart prediksi multi-hari dengan rentang kepercayaan, polutan dominan, korelasi parameter, distribusi kategori tahunan, dan **prediksi interaktif manual** (input 6 polutan → output kategori XGBoost).
- **Edukasi & Insight** — penjelasan 5 kategori ISPU resmi, dampak kesehatan, sumber polusi Jakarta, waktu puncak polusi, dan tips kesehatan.

## 🛠 Stack

| Layer | Tech |
|---|---|
| Frontend | Streamlit + custom CSS (Inter / Plus Jakarta Sans) |
| Charts | Plotly |
| Model | XGBoost (3 kelas: BAIK / SEDANG / TIDAK SEHAT) |
| Pipeline | CRISP-DM (cleaning, imputasi median, IQR outlier, stratified 80/20, GridSearchCV) |
| Data | Data ISPU DKI Jakarta tahun 2024 (5 stasiun BMKG) |

## 📁 Struktur

```
jaku/
├── app.py                          # Entry point Streamlit (navigasi)
├── views/                          # 4 halaman
│   ├── dashboard.py
│   ├── detail_wilayah.py
│   ├── prediksi_analisis.py
│   └── edukasi_insight.py
├── utils/
│   ├── train_model.py              # Pipeline CRISP-DM (auto-train sekali)
│   ├── data_loader.py              # Load CSV + model, snapshot, prediksi
│   ├── ispu_helper.py              # Mapping wilayah, kategori, rekomendasi
│   ├── components.py               # Komponen reusable (cards, charts)
│   └── styles.py                   # Custom CSS
├── data/
│   └── Data_ISPU.csv               # Dataset ISPU (sumber)
├── .streamlit/config.toml          # Tema light + primary blue
├── requirements.txt
└── README.md
```

Artifact model (`.pkl`, `.parquet`, `metadata.json`) **tidak di-commit** — auto-generate saat aplikasi pertama kali dijalankan via `_ensure_artifacts()` di `utils/data_loader.py`.

## 🚀 Cara Menjalankan Lokal

```bash
# 1. Clone repo
git clone https://github.com/<username>/jaku-dashboard.git
cd jaku-dashboard

# 2. (Opsional) virtual environment
python -m venv venv
source venv/bin/activate   # atau venv\Scripts\activate di Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Jalankan
streamlit run app.py
```

Pertama kali dijalankan, model XGBoost akan **otomatis di-train** dari `data/Data_ISPU.csv` (sekitar 5–10 detik), lalu di-cache untuk run berikutnya.

## ☁️ Deploy ke Streamlit Cloud (Gratis)

1. **Push ke GitHub**

   Pastikan struktur file & `requirements.txt` sudah ada di root repo.

   ```bash
   git init
   git add .
   git commit -m "Initial commit JakU dashboard"
   git branch -M main
   git remote add origin https://github.com/<username>/jaku-dashboard.git
   git push -u origin main
   ```

2. **Sign in ke [share.streamlit.io](https://share.streamlit.io)**

   Login dengan akun GitHub.

3. **New app → pilih repo**

   - **Repository**: `<username>/jaku-dashboard`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - Klik **Deploy**

4. **Tunggu build selesai** (sekitar 2–4 menit pertama untuk install xgboost dll).

5. URL publik tersedia di format `https://<your-app>.streamlit.app`.

### Catatan Streamlit Cloud

- Free tier: 1 GB RAM, cukup untuk dataset 2024 ini (1.7K rows).
- Cold-start ~ 10 detik saat aplikasi sudah idle.
- Model di-train otomatis di first run setelah deploy, lalu di-cache via `@st.cache_resource`.

## 📊 Performa Model

Hasil training dari `data/Data_ISPU.csv` (filter 2024 saja):

| Metric | Nilai |
|---|---|
| Test Accuracy | ~97% |
| F1 Macro | ~0.94 |
| CV Accuracy (k=5) | ~97% (± 0.7%) |
| Polutan paling berpengaruh | **PM2.5** (~51%) |

## 🎨 Design Reference

Layout & palette mengikuti mockup Figma JakU:
- **Primary**: `#2563EB` (biru)
- **Success**: `#22C55E` (hijau)
- **Warning**: `#FACC15` / `#F97316` (kuning/oranye)
- **Danger**: `#EF4444` (merah)
- **Background**: `#F8FAFC` (light gray)
- **Card**: white + soft shadow + radius 16–20px

## ⚠️ Disclaimer

- **Data bukan realtime.** Bersumber dari sampel ISPU 2024 yang sudah dipublikasi.
- Tanggal "hari ini" di dashboard menggunakan **15 Juni 2024** sebagai snapshot tetap.
- Data untuk **Kep. Seribu tidak tersedia** di sumber asli — nilai yang ditampilkan adalah estimasi karakteristik geografis pulau.
- Aplikasi ini bukan pengganti pemantauan resmi BMKG / DLH DKI Jakarta.

## 📝 Lisensi

Akademis — penggunaan untuk skripsi dan penelitian.

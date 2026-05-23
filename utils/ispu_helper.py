"""
Helper fungsi ISPU & wilayah Jakarta.

- Mapping stasiun → wilayah administratif
- Penentuan kategori dari nilai ISPU
- Color palette per kategori
- Rekomendasi aktivitas berdasarkan kategori
"""
from __future__ import annotations

# Mapping stasiun BMKG → wilayah DKI Jakarta
STASIUN_WILAYAH = {
    "DKI1 Bunderan HI": "Jakarta Pusat",
    "DKI2 Kelapa Gading": "Jakarta Utara",
    "DKI3 Jagakarsa": "Jakarta Selatan",
    "DKI4 Lubang Buaya": "Jakarta Timur",
    "DKI5 Kebon Jeruk": "Jakarta Barat",
}

WILAYAH_LIST = [
    "Jakarta Pusat",
    "Jakarta Utara",
    "Jakarta Barat",
    "Jakarta Timur",
    "Jakarta Selatan",
    "Kep. Seribu",
]

# Kategori ISPU resmi (PerMenLH P.14/2020)
KATEGORI_RANGE = [
    ("Baik", 0, 50, "#22C55E"),
    ("Sedang", 51, 100, "#2563EB"),
    ("Tidak Sehat", 101, 200, "#FACC15"),
    ("Sangat Tidak Sehat", 201, 300, "#F97316"),
    ("Berbahaya", 301, 500, "#EF4444"),
]

KATEGORI_COLOR = {nama: warna for nama, _, _, warna in KATEGORI_RANGE}
KATEGORI_COLOR_BG = {
    "Baik": "#DCFCE7",
    "Sedang": "#DBEAFE",
    "Tidak Sehat": "#FEF3C7",
    "Sangat Tidak Sehat": "#FFEDD5",
    "Berbahaya": "#FEE2E2",
}

# Polutan: label tampilan, satuan, mapping nama kolom
POLUTAN_INFO = {
    "pm_duakomalima": {
        "label": "PM2.5",
        "satuan": "µg/m³",
        "deskripsi": "Partikel halus diameter ≤ 2,5 µm, dapat menembus paru-paru.",
    },
    "pm_sepuluh": {
        "label": "PM10",
        "satuan": "µg/m³",
        "deskripsi": "Partikel debu diameter ≤ 10 µm dari debu jalan, konstruksi.",
    },
    "nitrogen_dioksida": {
        "label": "NO₂",
        "satuan": "µg/m³",
        "deskripsi": "Gas dari pembakaran kendaraan bermotor.",
    },
    "sulfur_dioksida": {
        "label": "SO₂",
        "satuan": "µg/m³",
        "deskripsi": "Gas dari pembakaran bahan bakar fosil & industri.",
    },
    "karbon_monoksida": {
        "label": "CO",
        "satuan": "mg/m³",
        "deskripsi": "Gas dari pembakaran tidak sempurna kendaraan.",
    },
    "ozon": {
        "label": "O₃",
        "satuan": "µg/m³",
        "deskripsi": "Ozon permukaan, terbentuk dari reaksi polutan + sinar matahari.",
    },
}


def kategori_dari_ispu(ispu: float) -> str:
    """Konversi nilai ISPU numerik ke nama kategori."""
    if ispu is None or ispu != ispu:  # NaN check
        return "Sedang"
    for nama, lo, hi, _ in KATEGORI_RANGE:
        if lo <= ispu <= hi:
            return nama
    return "Berbahaya"


def warna_kategori(kategori: str) -> str:
    return KATEGORI_COLOR.get(kategori, "#94A3B8")


def warna_kategori_bg(kategori: str) -> str:
    return KATEGORI_COLOR_BG.get(kategori, "#F1F5F9")


def deskripsi_kategori(kategori: str) -> str:
    teks = {
        "Baik": "Udara bersih, aman untuk semua aktivitas.",
        "Sedang": "Udara masih dapat diterima untuk beraktivitas di luar ruangan.",
        "Tidak Sehat": "Kurangi aktivitas luar ruangan, terutama bagi kelompok sensitif.",
        "Sangat Tidak Sehat": "Hindari aktivitas luar ruangan. Gunakan masker jika harus keluar.",
        "Berbahaya": "Hindari semua aktivitas luar ruangan. Tetap di dalam ruangan.",
    }
    return teks.get(kategori, "")


def rekomendasi_aktivitas(kategori: str) -> dict:
    """Return dict rekomendasi 4 aspek aktivitas berdasarkan kategori udara."""
    base = {
        "Baik": {
            "olahraga": ("Aman", "#22C55E", "Aktivitas luar ruangan aman dilakukan."),
            "masker": ("Tidak Perlu", "#22C55E", "Kualitas udara aman tanpa masker."),
            "sensitif": ("Aman", "#22C55E", "Tidak ada risiko khusus bagi kelompok rentan."),
            "jendela": ("Aman", "#22C55E", "Sirkulasi udara dalam ruangan aman."),
        },
        "Sedang": {
            "olahraga": ("Aman", "#22C55E", "Aktivitas luar ruangan aman dilakukan."),
            "masker": ("Disarankan", "#FACC15", "Gunakan masker jika Anda sensitif terhadap polusi."),
            "sensitif": ("Waspada", "#FACC15", "Jaga kesehatan dan hindari area dengan polusi tinggi."),
            "jendela": ("Aman", "#22C55E", "Sirkulasi udara di dalam ruangan masih aman."),
        },
        "Tidak Sehat": {
            "olahraga": ("Kurangi", "#F97316", "Batasi aktivitas fisik berat di luar ruangan."),
            "masker": ("Wajib", "#EF4444", "Gunakan masker N95 saat di luar ruangan."),
            "sensitif": ("Hindari", "#EF4444", "Kelompok sensitif sebaiknya tetap di dalam rumah."),
            "jendela": ("Tutup", "#F97316", "Tutup jendela, gunakan air purifier jika ada."),
        },
        "Sangat Tidak Sehat": {
            "olahraga": ("Hindari", "#EF4444", "Hindari semua aktivitas fisik di luar ruangan."),
            "masker": ("Wajib", "#EF4444", "Wajib pakai masker N95/KN95."),
            "sensitif": ("Tetap di Rumah", "#EF4444", "Kelompok sensitif wajib tetap di dalam rumah."),
            "jendela": ("Tutup", "#EF4444", "Tutup rapat semua jendela dan ventilasi."),
        },
        "Berbahaya": {
            "olahraga": ("Hindari", "#EF4444", "Sangat berbahaya untuk semua aktivitas luar."),
            "masker": ("Wajib", "#EF4444", "Wajib pakai masker N95 bahkan di dalam rumah."),
            "sensitif": ("Darurat", "#EF4444", "Cari fasilitas dengan udara bersih."),
            "jendela": ("Tutup Rapat", "#EF4444", "Tutup rapat semua akses udara luar."),
        },
    }
    return base.get(kategori, base["Sedang"])

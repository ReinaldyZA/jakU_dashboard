"""
Loader data dan model XGBoost untuk Streamlit.

Auto-train kalau artifact belum ada. Pakai @st.cache_resource untuk
sekali load saja per session container.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import date

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from utils.ispu_helper import STASIUN_WILAYAH, WILAYAH_LIST, kategori_dari_ispu

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Tanggal acuan "hari ini" untuk snapshot dashboard (random Mei/Jun 2024)
TANGGAL_ACUAN = date(2024, 6, 15)


def _ensure_artifacts():
    """Auto-train jika file model .pkl belum ada."""
    needed = [
        DATA_DIR / "model_xgboost.pkl",
        DATA_DIR / "label_encoder.pkl",
        DATA_DIR / "ispu_2024_clean.parquet",
        DATA_DIR / "metadata.json",
    ]
    if not all(f.exists() for f in needed):
        from utils.train_model import run_training
        run_training(DATA_DIR / "Data_ISPU.csv", DATA_DIR)


@st.cache_resource(show_spinner="Memuat model XGBoost...")
def load_model_bundle():
    """Return dict berisi model, encoder, metadata, fitur."""
    _ensure_artifacts()
    model = joblib.load(DATA_DIR / "model_xgboost.pkl")
    encoder = joblib.load(DATA_DIR / "label_encoder.pkl")
    fitur = joblib.load(DATA_DIR / "fitur_polutan.pkl")
    with open(DATA_DIR / "metadata.json") as f:
        meta = json.load(f)
    return {
        "model": model,
        "encoder": encoder,
        "fitur": fitur,
        "metadata": meta,
    }


@st.cache_data(show_spinner="Memuat data ISPU 2024...")
def load_data_2024() -> pd.DataFrame:
    """Load data 2024 yang sudah dibersihkan + tambahkan kolom tanggal & wilayah."""
    _ensure_artifacts()
    df = pd.read_parquet(DATA_DIR / "ispu_2024_clean.parquet")

    # Bangun kolom tanggal asli dari periode_data + tanggal
    df["tahun"] = df["periode_data"].astype(str).str[:4].astype(int)
    df["tanggal_full"] = pd.to_datetime(
        df["tahun"].astype(str) + "-"
        + df["bulan"].astype(str).str.zfill(2) + "-"
        + df["tanggal"].astype(str).str.zfill(2),
        errors="coerce",
    )

    # Mapping stasiun → wilayah
    df["wilayah"] = df["stasiun"].map(STASIUN_WILAYAH)

    # Sort by tanggal
    df = df.sort_values("tanggal_full").reset_index(drop=True)

    return df


def get_data_until(df: pd.DataFrame, ref_date: date = TANGGAL_ACUAN) -> pd.DataFrame:
    """Filter data ≤ tanggal acuan untuk efek snapshot 'hari ini'."""
    return df[df["tanggal_full"] <= pd.Timestamp(ref_date)].copy()


def snapshot_per_wilayah(df: pd.DataFrame, ref_date: date = TANGGAL_ACUAN) -> dict:
    """
    Ambil snapshot terakhir per wilayah ≤ tanggal acuan.
    Return dict: { wilayah: {ispu, kategori, polutan_dominan, pollutants_dict, tanggal} }
    """
    df_sub = get_data_until(df, ref_date)
    snapshot = {}

    for wilayah in [w for w in WILAYAH_LIST if w != "Kep. Seribu"]:
        sub = df_sub[df_sub["wilayah"] == wilayah]
        if len(sub) == 0:
            continue
        # Average dari 3 hari terakhir agar tidak fluktuatif
        last_days = sub.tail(3)
        ispu_val = float(last_days["max"].mean())
        snapshot[wilayah] = {
            "ispu": round(ispu_val),
            "kategori": kategori_dari_ispu(ispu_val),
            "polutan_dominan": last_days["parameter_pencemar_kritis"].mode().iloc[0]
            if len(last_days["parameter_pencemar_kritis"].mode()) > 0
            else "PM25",
            "polutan_values": {
                "pm_duakomalima": round(float(last_days["pm_duakomalima"].mean()), 1),
                "pm_sepuluh": round(float(last_days["pm_sepuluh"].mean()), 1),
                "nitrogen_dioksida": round(float(last_days["nitrogen_dioksida"].mean()), 1),
                "sulfur_dioksida": round(float(last_days["sulfur_dioksida"].mean()), 1),
                "karbon_monoksida": round(float(last_days["karbon_monoksida"].mean()), 1),
                "ozon": round(float(last_days["ozon"].mean()), 1),
            },
            "tanggal": last_days["tanggal_full"].max().date(),
        }

    # Kep. Seribu: estimasi data terbatas (pulau jauh dari kota → polusi lebih rendah)
    if "Kep. Seribu" in WILAYAH_LIST:
        rata_ispu = np.mean([v["ispu"] for v in snapshot.values()]) if snapshot else 70
        snapshot["Kep. Seribu"] = {
            "ispu": max(25, round(rata_ispu * 0.45)),
            "kategori": "Baik",
            "polutan_dominan": "PM25",
            "polutan_values": {
                "pm_duakomalima": 12.0,
                "pm_sepuluh": 22.0,
                "nitrogen_dioksida": 6.0,
                "sulfur_dioksida": 4.0,
                "karbon_monoksida": 0.3,
                "ozon": 18.0,
            },
            "tanggal": ref_date,
            "data_terbatas": True,
        }

    return snapshot


def hitung_jakarta_ratarata(snapshot: dict) -> dict:
    """Hitung rata-rata ISPU untuk seluruh Jakarta."""
    wilayah_real = [w for w, v in snapshot.items() if not v.get("data_terbatas", False)]
    if not wilayah_real:
        return {"ispu": 0, "kategori": "Sedang", "polutan_dominan": "PM25"}

    ispu_avg = np.mean([snapshot[w]["ispu"] for w in wilayah_real])

    # Polutan dominan: mode dari snapshot
    polutan_dominan_list = [snapshot[w]["polutan_dominan"] for w in wilayah_real]
    from collections import Counter
    polutan_dom = Counter(polutan_dominan_list).most_common(1)[0][0]

    # Rata-rata setiap polutan
    polutan_avg = {}
    for key in ["pm_duakomalima", "pm_sepuluh", "nitrogen_dioksida",
                "sulfur_dioksida", "karbon_monoksida", "ozon"]:
        polutan_avg[key] = round(
            np.mean([snapshot[w]["polutan_values"][key] for w in wilayah_real]), 1
        )

    return {
        "ispu": round(ispu_avg),
        "kategori": kategori_dari_ispu(ispu_avg),
        "polutan_dominan": polutan_dom,
        "polutan_values": polutan_avg,
    }


def tren_7_hari(df: pd.DataFrame, wilayah: str | None = None,
                ref_date: date = TANGGAL_ACUAN) -> pd.DataFrame:
    """Return DataFrame ISPU 7 hari terakhir, filter per wilayah jika diberikan."""
    df_sub = get_data_until(df, ref_date)
    if wilayah:
        df_sub = df_sub[df_sub["wilayah"] == wilayah]

    # Average per tanggal
    agg = df_sub.groupby("tanggal_full")["max"].mean().reset_index()
    agg = agg.tail(7).copy()
    agg["ispu"] = agg["max"].round().astype(int)
    agg["kategori"] = agg["ispu"].apply(kategori_dari_ispu)
    return agg


def pola_harian_synthetic(ispu_dasar: float) -> pd.DataFrame:
    """
    Generate pola harian 24 jam untuk visualisasi (data ISPU asli hanya harian).

    Pola Jakarta khas: puncak pagi (rush hour, 07-09), turun siang,
    naik tajam sore-malam (17-20) → polusi terburuk, turun lagi tengah malam.
    """
    import numpy as np

    hours = np.arange(24)
    # Multiplier per jam (faktor terhadap rata-rata harian)
    pola = np.array([
        0.75, 0.65, 0.55, 0.50, 0.55, 0.70,   # 00-05
        0.95, 1.10, 1.20, 1.10, 0.95, 0.85,   # 06-11
        0.80, 0.75, 0.80, 0.95, 1.15, 1.40,   # 12-17
        1.55, 1.60, 1.45, 1.20, 1.00, 0.85,   # 18-23
    ])
    np.random.seed(42)
    nilai = ispu_dasar * pola + np.random.normal(0, ispu_dasar * 0.03, 24)
    nilai = np.maximum(nilai, 10)

    return pd.DataFrame({
        "jam": [f"{h:02d}:00" for h in hours],
        "jam_int": hours,
        "ispu": nilai.round().astype(int),
    })


def predict_xgb(values: dict, bundle: dict) -> dict:
    """
    Prediksi kategori ISPU pakai XGBoost.

    values: {pm_sepuluh, pm_duakomalima, sulfur_dioksida, karbon_monoksida, ozon, nitrogen_dioksida}
    """
    model = bundle["model"]
    encoder = bundle["encoder"]
    fitur = bundle["fitur"]

    X = pd.DataFrame([[values[f] for f in fitur]], columns=fitur)
    pred_idx = int(model.predict(X)[0])
    proba = model.predict_proba(X)[0]
    label = encoder.inverse_transform([pred_idx])[0]

    return {
        "label": label,
        "kelas": encoder.classes_.tolist(),
        "probabilitas": {k: float(p) for k, p in zip(encoder.classes_, proba)},
    }


def prediksi_n_hari(df: pd.DataFrame, wilayah: str | None, n: int,
                     bundle: dict, ref_date: date = TANGGAL_ACUAN) -> pd.DataFrame:
    """
    Prediksi ISPU n hari ke depan berbasis trend + XGBoost.

    Strategi: ambil 14 hari terakhir, fit linear trend ringan untuk extrapolate
    nilai polutan, lalu klasifikasikan tiap hari pakai XGBoost.
    """
    df_sub = get_data_until(df, ref_date)
    if wilayah:
        df_sub = df_sub[df_sub["wilayah"] == wilayah]

    daily = df_sub.groupby("tanggal_full").agg({
        "pm_sepuluh": "mean",
        "pm_duakomalima": "mean",
        "sulfur_dioksida": "mean",
        "karbon_monoksida": "mean",
        "ozon": "mean",
        "nitrogen_dioksida": "mean",
        "max": "mean",
    }).reset_index().tail(14)

    if len(daily) < 3:
        return pd.DataFrame()

    fitur = bundle["fitur"]
    rng = np.random.default_rng(42)

    # Untuk tiap fitur: ambil mean & std lalu sample dengan random walk ringan
    last_vals = daily.iloc[-1][fitur].to_dict()
    stds = daily[fitur].std().to_dict()
    means = daily[fitur].mean().to_dict()

    rows = []
    for i in range(1, n + 1):
        future_date = pd.Timestamp(ref_date) + pd.Timedelta(days=i)
        # Random walk: nilai bergerak menuju mean dengan noise
        new_vals = {}
        for f in fitur:
            momentum = 0.6 * last_vals[f] + 0.4 * means[f]
            noise = rng.normal(0, max(stds[f] * 0.3, 1))
            new_vals[f] = max(1.0, momentum + noise)

        # ISPU = max sub-index (proxy dari max polutan setelah konversi)
        # Simple proxy: ambil nilai max polutan sebagai ISPU estimate
        ispu_estimate = max(new_vals.values())

        # Klasifikasi pakai XGBoost
        pred = predict_xgb(new_vals, bundle)

        rows.append({
            "tanggal": future_date,
            "ispu": round(ispu_estimate),
            "kategori_model": pred["label"],
            "kategori": kategori_dari_ispu(ispu_estimate),
            **{f"val_{k}": round(v, 1) for k, v in new_vals.items()},
            "confidence": float(max(pred["probabilitas"].values())),
        })

        last_vals = new_vals

    return pd.DataFrame(rows)

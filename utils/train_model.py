"""
Training pipeline yang mereplikasi notebook CRISP-DM:
- Cleaning: hapus "TIDAK ADA DATA", standarisasi nama stasiun, konversi numerik
- Imputasi median
- Outlier removal IQR
- Stratified 80/20 split
- Train XGBoost dengan hyperparameter terbaik dari notebook
- Save model + encoder + metadata

Dijalankan hanya saat artifact .pkl belum ada (lazy training).
"""
from __future__ import annotations
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

FITUR_POLUTAN = [
    "pm_sepuluh",
    "pm_duakomalima",
    "sulfur_dioksida",
    "karbon_monoksida",
    "ozon",
    "nitrogen_dioksida",
]

KATEGORI_VALID = ["BAIK", "SEDANG", "TIDAK SEHAT"]

STASIUN_MAPPING = {
    "DKI1 Bundaran Hotel Indonesia (HI)": "DKI1 Bunderan HI",
    "DKI1 Bundaran Hotel Indonesia HI": "DKI1 Bunderan HI",
    "DKI5 Kebon Jeruk Jakarta Barat": "DKI5 Kebon Jeruk",
}

# Hyperparameter terbaik XGBoost (representatif dari GridSearchCV di notebook)
XGB_BEST_PARAMS = {
    "n_estimators": 300,
    "max_depth": 5,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "eval_metric": "mlogloss",
}


def load_and_clean(csv_path: Path) -> pd.DataFrame:
    """Load CSV ISPU dan terapkan cleaning persis seperti notebook BAB 3."""
    df = pd.read_csv(csv_path, sep=";")

    # Filter hanya tahun 2024
    df = df[df["periode_data"].astype(str).str.startswith("2024")].copy()

    # Hapus baris tanpa kategori valid
    df = df[df["kategori"].isin(KATEGORI_VALID)].copy()

    # Standarisasi nama stasiun
    df["stasiun"] = df["stasiun"].replace(STASIUN_MAPPING)

    # Konversi polutan ke numerik
    for col in FITUR_POLUTAN:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Imputasi median untuk missing values
    for col in FITUR_POLUTAN:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)

    # Outlier removal dengan IQR
    mask_inlier = pd.Series([True] * len(df), index=df.index)
    for col in FITUR_POLUTAN:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask_inlier &= (df[col] >= lower) & (df[col] <= upper)
    df_clean = df[mask_inlier].copy()

    return df_clean


def train_xgboost(df: pd.DataFrame) -> dict:
    """Latih XGBoost dengan stratified split + cross-validation."""
    X = df[FITUR_POLUTAN].copy()
    y_raw = df["kategori"].copy()

    le = LabelEncoder()
    y = le.fit_transform(y_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = XGBClassifier(**XGB_BEST_PARAMS)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    test_acc = accuracy_score(y_test, y_pred)
    test_f1 = f1_score(y_test, y_pred, average="macro")

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=skf, scoring="accuracy", n_jobs=-1)

    # Feature importance untuk halaman analisis
    feat_imp = dict(zip(FITUR_POLUTAN, model.feature_importances_.tolist()))

    return {
        "model": model,
        "encoder": le,
        "test_accuracy": float(test_acc),
        "test_f1_macro": float(test_f1),
        "cv_mean": float(cv_scores.mean()),
        "cv_std": float(cv_scores.std()),
        "feature_importance": feat_imp,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "kelas": le.classes_.tolist(),
    }


def run_training(csv_path: str | Path, output_dir: str | Path) -> dict:
    """Pipeline training end-to-end. Return metadata yang dipakai dashboard."""
    csv_path = Path(csv_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df_clean = load_and_clean(csv_path)
    result = train_xgboost(df_clean)

    # Persist artifacts
    joblib.dump(result["model"], output_dir / "model_xgboost.pkl")
    joblib.dump(result["encoder"], output_dir / "label_encoder.pkl")
    joblib.dump(FITUR_POLUTAN, output_dir / "fitur_polutan.pkl")
    df_clean.to_parquet(output_dir / "ispu_2024_clean.parquet", index=False)

    metadata = {
        "test_accuracy": result["test_accuracy"],
        "test_f1_macro": result["test_f1_macro"],
        "cv_mean": result["cv_mean"],
        "cv_std": result["cv_std"],
        "feature_importance": result["feature_importance"],
        "n_train": result["n_train"],
        "n_test": result["n_test"],
        "n_total_clean": len(df_clean),
        "kelas": result["kelas"],
        "fitur": FITUR_POLUTAN,
        "model_name": "XGBoost",
        "hyperparams": {k: v for k, v in XGB_BEST_PARAMS.items() if k != "random_state"},
    }
    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    return metadata


if __name__ == "__main__":
    import sys
    csv = sys.argv[1] if len(sys.argv) > 1 else "data/Data_ISPU.csv"
    out = sys.argv[2] if len(sys.argv) > 2 else "data"
    meta = run_training(csv, out)
    print("\n=== Training selesai ===")
    print(f"Test Accuracy   : {meta['test_accuracy']:.4f}")
    print(f"Test F1 (macro) : {meta['test_f1_macro']:.4f}")
    print(f"CV Mean         : {meta['cv_mean']:.4f} (+/- {meta['cv_std']:.4f})")
    print(f"Data clean      : {meta['n_total_clean']} baris")
    print(f"Train / Test    : {meta['n_train']} / {meta['n_test']}")
    print(f"Feature importance:")
    for k, v in sorted(meta["feature_importance"].items(), key=lambda x: -x[1]):
        print(f"  {k:25s}: {v:.4f}")

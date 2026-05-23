"""Halaman Detail Wilayah - info per wilayah administratif Jakarta."""
import streamlit as st

from utils.components import (
    build_chart_pola_harian, build_chart_tren, render_hero_ispu,
    render_page_header, render_polutan_grid,
)
from utils.data_loader import (
    TANGGAL_ACUAN, load_data_2024, load_model_bundle, pola_harian_synthetic,
    prediksi_n_hari, snapshot_per_wilayah, tren_7_hari,
)
from utils.ispu_helper import (
    WILAYAH_LIST, kategori_dari_ispu, warna_kategori,
)


def render():
    df = load_data_2024()
    bundle = load_model_bundle()
    snapshot = snapshot_per_wilayah(df, TANGGAL_ACUAN)

    render_page_header(
        "Detail Wilayah",
        "Pilih wilayah untuk melihat informasi kualitas udara lebih detail.",
        TANGGAL_ACUAN,
    )

    # Tabs untuk 6 wilayah
    tabs = st.tabs(WILAYAH_LIST)

    for tab, wilayah in zip(tabs, WILAYAH_LIST):
        with tab:
            if wilayah not in snapshot:
                st.warning(f"Data untuk {wilayah} tidak tersedia.")
                continue

            snap = snapshot[wilayah]

            if snap.get("data_terbatas"):
                st.info(
                    "ℹ️ **Kep. Seribu**: Stasiun pemantau ISPU resmi DKI hanya tersedia "
                    "di 5 wilayah Jakarta daratan. Nilai berikut adalah **estimasi** "
                    "berdasarkan karakteristik geografis pulau."
                )

            # ─── Row 1: Hero ISPU + Komposisi Polutan ───────────
            col1, col2 = st.columns([1, 1.1], gap="medium")
            with col1:
                render_hero_ispu(
                    ispu=snap["ispu"],
                    kategori=snap["kategori"],
                    judul=f"Kualitas Udara {wilayah}",
                    polutan_dominan=snap["polutan_dominan"],
                    polutan_value=snap["polutan_values"]["pm_duakomalima"],
                )
            with col2:
                render_polutan_grid(snap["polutan_values"])

            # ─── Row 2: Tren 7 hari + Pola harian ───────────────
            col3, col4 = st.columns(2, gap="medium")
            with col3:
                st.markdown(f"""
                <div class="card">
                    <h3 class="card-title">Tren ISPU {wilayah} (7 Hari Terakhir)</h3>
                """, unsafe_allow_html=True)

                # Untuk Kep. Seribu (data terbatas), skip tren historis
                if snap.get("data_terbatas"):
                    st.info("Data tren historis tidak tersedia untuk Kep. Seribu.")
                else:
                    df_tren = tren_7_hari(df, wilayah=wilayah, ref_date=TANGGAL_ACUAN)
                    if len(df_tren) > 0:
                        st.plotly_chart(
                            build_chart_tren(df_tren, "", height=280),
                            use_container_width=True,
                            config={"displayModeBar": False},
                            key=f"tren_{wilayah}",
                        )
                    else:
                        st.warning("Data tren tidak cukup.")
                st.markdown("</div>", unsafe_allow_html=True)

            with col4:
                st.markdown("""
                <div class="card">
                    <h3 class="card-title">Pola Harian (Rata-rata) <span class="info-icon">i</span></h3>
                """, unsafe_allow_html=True)
                df_pola = pola_harian_synthetic(snap["ispu"])
                st.plotly_chart(
                    build_chart_pola_harian(df_pola, height=280),
                    use_container_width=True,
                    config={"displayModeBar": False},
                    key=f"pola_{wilayah}",
                )
                st.markdown("</div>", unsafe_allow_html=True)

            # ─── Row 3: Prediksi singkat + Rekomendasi wilayah ──
            col5, col6 = st.columns([1.1, 1], gap="medium")
            with col5:
                st.markdown(f"""
                <div class="card">
                    <h3 class="card-title">Prediksi ISPU {wilayah} <span class="info-icon">i</span></h3>
                """, unsafe_allow_html=True)

                pred_wilayah = (None if snap.get("data_terbatas")
                                else wilayah)
                df_pred5 = prediksi_n_hari(df, pred_wilayah, 5, bundle, TANGGAL_ACUAN)

                if len(df_pred5) >= 5:
                    # Tampilkan card untuk Besok, 3 Hari, 5 Hari
                    pred_cols = st.columns(3)
                    pilihan = [(0, "Besok"), (2, "3 Hari ke Depan"), (4, "5 Hari ke Depan")]
                    for col, (idx, label) in zip(pred_cols, pilihan):
                        row = df_pred5.iloc[idx]
                        kat = kategori_dari_ispu(row["ispu"])
                        warna = warna_kategori(kat)
                        emoji_cuaca = "☀️" if row["ispu"] < 80 else "⛅" if row["ispu"] < 120 else "🌫️"
                        tgl_str = row["tanggal"].strftime("%d %b %Y")
                        with col:
                            st.markdown(f"""
                            <div style="padding:14px; background:#F8FAFC; border-radius:12px;">
                                <div style="font-size:11px; color:#64748B; font-weight:600;">{label}</div>
                                <div style="font-size:11px; color:#94A3B8; margin-bottom:8px;">{tgl_str}</div>
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <div>
                                        <div style="font-size:28px; font-weight:800; color:{warna};
                                            font-family:'Plus Jakarta Sans',sans-serif; line-height:1;">{int(row['ispu'])}</div>
                                        <div style="font-size:12px; color:{warna}; font-weight:600; margin-top:2px;">{kat}</div>
                                    </div>
                                    <div style="font-size:30px;">{emoji_cuaca}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    st.markdown("""
                    <div style="margin-top:14px; padding:10px 14px; background:#F0F9FF;
                        border-radius:10px; font-size:12px; color:#475569; border-left:3px solid #2563EB;">
                        💡 Prediksi ini dibuat menggunakan model machine learning <b>XGBoost</b>
                        berdasarkan data historis ISPU.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Data prediksi belum tersedia.")

                st.markdown("</div>", unsafe_allow_html=True)

            with col6:
                st.markdown("""
                <div class="card">
                    <h3 class="card-title">Rekomendasi untuk Wilayah Ini <span class="info-icon">i</span></h3>
                """, unsafe_allow_html=True)

                from utils.ispu_helper import rekomendasi_aktivitas
                rek = rekomendasi_aktivitas(snap["kategori"])
                items = [
                    ("masker", "😷", "Gunakan Masker", "#FEF3C7"),
                    ("olahraga", "🏃", "Batasi Aktivitas Berat", "#DBEAFE"),
                    ("jendela", "🪟", "Ventilasi Udara", "#DCFCE7"),
                ]
                rec_cols = st.columns(3)
                for col, (key, emoji, judul, bg) in zip(rec_cols, items):
                    status, warna, deskripsi = rek[key]
                    with col:
                        st.markdown(f"""
                        <div style="padding:14px; text-align:center; height:100%;">
                            <div style="width:48px; height:48px; background:{bg};
                                border-radius:10px; display:flex; align-items:center;
                                justify-content:center; font-size:24px; margin:0 auto 10px;">{emoji}</div>
                            <div style="font-size:13px; font-weight:700; color:#0F172A;
                                margin-bottom:6px;">{judul}</div>
                            <div style="font-size:11px; color:#64748B; line-height:1.5;">{deskripsi}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

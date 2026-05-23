"""Halaman Dashboard (Beranda) - ringkasan kualitas udara DKI Jakarta."""
from datetime import datetime
import streamlit as st

from utils.components import (
    build_chart_tren, render_hero_ispu, render_peta_jakarta,
    render_page_header, render_rekomendasi,
)
from utils.data_loader import (
    TANGGAL_ACUAN, hitung_jakarta_ratarata, load_data_2024,
    prediksi_n_hari, snapshot_per_wilayah, tren_7_hari, load_model_bundle,
)
from utils.ispu_helper import kategori_dari_ispu, warna_kategori


def render():
    df = load_data_2024()
    bundle = load_model_bundle()

    # Greeting dinamis
    jam = datetime.now().hour
    if jam < 11: salam = "Selamat Pagi"
    elif jam < 15: salam = "Selamat Siang"
    elif jam < 19: salam = "Selamat Sore"
    else: salam = "Selamat Malam"

    render_page_header(
        f"Halo, {salam}!",
        "Berikut ringkasan kualitas udara di Provinsi DKI Jakarta.",
        TANGGAL_ACUAN,
    )

    snapshot = snapshot_per_wilayah(df, TANGGAL_ACUAN)
    jakarta_avg = hitung_jakarta_ratarata(snapshot)

    # ─── Row 1: Hero ISPU rata-rata + Peta wilayah ──────────────
    col1, col2 = st.columns([1, 1.05], gap="medium")
    with col1:
        render_hero_ispu(
            ispu=jakarta_avg["ispu"],
            kategori=jakarta_avg["kategori"],
            judul="Kualitas Udara Jakarta (Rata-rata)",
            polutan_dominan=jakarta_avg["polutan_dominan"],
            polutan_value=jakarta_avg["polutan_values"]["pm_duakomalima"],
        )

    with col2:
        st.markdown("""
        <div class="card">
            <h3 class="card-title">Kualitas Udara per Wilayah <span class="info-icon">i</span></h3>
        """, unsafe_allow_html=True)
        render_peta_jakarta(snapshot)
        st.markdown("</div>", unsafe_allow_html=True)

    # ─── Row 2: Tren ISPU 7 hari + Prediksi ISPU ────────────────
    col3, col4 = st.columns([1.3, 1], gap="medium")
    with col3:
        st.markdown("""
        <div class="card">
            <h3 class="card-title">Tren ISPU Jakarta (7 Hari Terakhir)</h3>
        """, unsafe_allow_html=True)
        df_tren = tren_7_hari(df, ref_date=TANGGAL_ACUAN)
        st.plotly_chart(build_chart_tren(df_tren, "Tren 7 Hari", height=260),
                        use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="card">
            <h3 class="card-title">Prediksi ISPU Jakarta <span class="info-icon">i</span></h3>
        """, unsafe_allow_html=True)

        # Tabs prediksi (Besok / 3 Hari / 7 Hari)
        tab_besok, tab_3hari, tab_7hari = st.tabs(["Besok", "3 Hari", "7 Hari"])

        for tab, n_hari, label in [(tab_besok, 1, "Besok"),
                                     (tab_3hari, 3, "3 Hari ke Depan"),
                                     (tab_7hari, 7, "7 Hari ke Depan")]:
            with tab:
                df_pred = prediksi_n_hari(df, None, n_hari, bundle, TANGGAL_ACUAN)
                if len(df_pred) == 0:
                    st.warning("Data prediksi tidak tersedia.")
                    continue

                ispu_pred = int(df_pred["ispu"].iloc[-1] if n_hari > 1
                                 else df_pred["ispu"].iloc[0])
                kategori_pred = kategori_dari_ispu(ispu_pred)
                warna = warna_kategori(kategori_pred)
                tgl_pred = df_pred["tanggal"].iloc[-1 if n_hari > 1 else 0]

                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:24px; padding:8px 0 12px 0;">
                    <div>
                        <div style="font-size:48px; font-weight:800; color:{warna};
                            font-family:'Plus Jakarta Sans',sans-serif; line-height:1;">{ispu_pred}</div>
                        <div style="font-size:14px; color:{warna}; font-weight:700; margin-top:4px;">{kategori_pred}</div>
                        <div style="font-size:11px; color:#64748B; margin-top:6px;">{tgl_pred.strftime('%d %b %Y')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Mini chart kalau lebih dari 1 hari
                if n_hari > 1:
                    import plotly.graph_objects as go
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_pred["tanggal"].dt.strftime("%d %b"),
                        y=df_pred["ispu"],
                        mode="lines+markers",
                        line=dict(color="#2563EB", width=2.5, shape="spline"),
                        marker=dict(size=7, color="#2563EB"),
                        fill="tozeroy", fillcolor="rgba(37,99,235,0.08)",
                        hovertemplate="%{x}: ISPU %{y}<extra></extra>",
                    ))
                    fig.update_layout(
                        height=140, margin=dict(l=0, r=0, t=0, b=0),
                        plot_bgcolor="white", paper_bgcolor="white",
                        showlegend=False,
                        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
                        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=10)),
                    )
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
        <div style="margin-top:12px; padding:12px 14px; background:#F0F9FF;
            border-radius:10px; font-size:12px; color:#475569; border-left:3px solid #2563EB;">
            💡 Prediksi dibuat menggunakan model machine learning <b>XGBoost</b> berdasarkan data historis ISPU.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ─── Row 3: Rekomendasi Aktivitas ───────────────────────────
    st.markdown("""
    <div class="card">
        <h3 class="card-title">Rekomendasi Aktivitas</h3>
    """, unsafe_allow_html=True)
    render_rekomendasi(jakarta_avg["kategori"])
    st.markdown("</div>", unsafe_allow_html=True)

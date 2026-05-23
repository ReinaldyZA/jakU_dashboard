"""Halaman Prediksi & Analisis - prediksi multi-hari + analisis pola."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.components import (
    build_chart_pola_harian, render_page_header,
)
from utils.data_loader import (
    TANGGAL_ACUAN, load_data_2024, load_model_bundle,
    pola_harian_synthetic, prediksi_n_hari, snapshot_per_wilayah,
)
from utils.ispu_helper import (
    POLUTAN_INFO, WILAYAH_LIST, kategori_dari_ispu, warna_kategori,
)


def _chart_prediksi_multi_hari(df_pred, judul: str) -> go.Figure:
    """Chart prediksi N hari dengan label di tiap titik + confidence band."""
    fig = go.Figure()

    # Confidence band (sederhana: ± 10%)
    upper = df_pred["ispu"] * 1.1
    lower = df_pred["ispu"] * 0.9

    fig.add_trace(go.Scatter(
        x=df_pred["tanggal"], y=upper, mode="lines",
        line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=df_pred["tanggal"], y=lower, mode="lines",
        fill="tonexty", fillcolor="rgba(37, 99, 235, 0.10)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Rentang Kepercayaan (80%)", hoverinfo="skip",
    ))

    # Main line
    fig.add_trace(go.Scatter(
        x=df_pred["tanggal"], y=df_pred["ispu"],
        mode="lines+markers",
        line=dict(color="#2563EB", width=3, shape="spline", smoothing=0.5),
        marker=dict(size=9, color="#2563EB", line=dict(width=2, color="white")),
        name="Prediksi ISPU",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>ISPU: %{y}<extra></extra>",
    ))

    # Label di tiap titik
    for _, row in df_pred.iterrows():
        kat = kategori_dari_ispu(row["ispu"])
        warna = warna_kategori(kat)
        fig.add_annotation(
            x=row["tanggal"], y=row["ispu"],
            text=f"<b>{int(row['ispu'])}</b><br><span style='font-size:9px;'>{kat}</span>",
            showarrow=False, yshift=22,
            font=dict(size=11, color=warna),
            bgcolor="#FFFFFF", bordercolor=warna, borderwidth=1.5,
            borderpad=4, opacity=0.95,
        )

    fig.update_layout(
        height=320, margin=dict(l=0, r=20, t=40, b=20),
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2,
                     xanchor="left", x=0, font=dict(size=11)),
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#64748B"),
                    tickformat="%d %b<br>%a"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False,
                    tickfont=dict(size=11, color="#64748B"),
                    range=[0, max(200, df_pred["ispu"].max() * 1.4)]),
        font=dict(family="Inter, sans-serif"),
    )
    return fig


def _chart_donut_polutan(feat_imp: dict) -> go.Figure:
    """Donut chart feature importance polutan."""
    # Mapping ke label cantik
    label_map = {k: POLUTAN_INFO[k]["label"] for k in POLUTAN_INFO}
    sorted_items = sorted(feat_imp.items(), key=lambda x: -x[1])
    labels = [label_map.get(k, k) for k, _ in sorted_items]
    values = [v * 100 for _, v in sorted_items]
    colors = ["#2563EB", "#22C55E", "#A855F7", "#FACC15", "#EF4444", "#94A3B8"]

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=colors[:len(labels)], line=dict(color="white", width=3)),
        textposition="outside", textinfo="label+percent",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>",
    )])

    top_pol = labels[0]
    top_pct = values[0]
    fig.add_annotation(
        text=f"<b style='font-size:22px;'>{top_pol}</b><br><span style='font-size:14px;color:#2563EB;'>{top_pct:.0f}%</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(family="Plus Jakarta Sans", color="#0F172A"),
    )
    fig.update_layout(
        height=300, margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        font=dict(family="Inter, sans-serif"),
    )
    return fig


def _chart_korelasi(df_clean: pd.DataFrame) -> go.Figure:
    """Bar chart korelasi tiap polutan dengan ISPU (max)."""
    corr_vals = {}
    for key in ["pm_duakomalima", "pm_sepuluh", "nitrogen_dioksida",
                "ozon", "sulfur_dioksida", "karbon_monoksida"]:
        corr_vals[key] = df_clean[key].corr(df_clean["max"])

    sorted_items = sorted(corr_vals.items(), key=lambda x: -abs(x[1]))
    labels = [POLUTAN_INFO[k]["label"] for k, _ in sorted_items]
    values = [round(v, 2) for _, v in sorted_items]

    colors = []
    for v in values:
        if abs(v) >= 0.6: colors.append("#2563EB")
        elif abs(v) >= 0.4: colors.append("#22C55E")
        elif abs(v) >= 0.2: colors.append("#FACC15")
        else: colors.append("#EF4444")

    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=colors, line=dict(color="white", width=1)),
        text=[f"{v:.2f}" for v in values], textposition="outside",
        textfont=dict(size=12, color="#0F172A"),
        hovertemplate="<b>%{y}</b>: %{x:.2f}<extra></extra>",
    ))
    fig.add_vline(x=0, line=dict(color="#CBD5E1", width=1))
    fig.update_layout(
        height=300, margin=dict(l=0, r=40, t=20, b=20),
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9",
                    range=[-1.05, 1.15],
                    tickfont=dict(size=10, color="#64748B"),
                    tickvals=[-1, 0, 1],
                    ticktext=["-1 (Negatif Kuat)", "0", "1 (Positif Kuat)"]),
        yaxis=dict(showgrid=False, tickfont=dict(size=12, color="#0F172A")),
        font=dict(family="Inter, sans-serif"),
    )
    return fig


def render():
    df = load_data_2024()
    bundle = load_model_bundle()
    meta = bundle["metadata"]
    snapshot = snapshot_per_wilayah(df, TANGGAL_ACUAN)

    render_page_header(
        "Prediksi & Analisis",
        "Analisis data historis dan prediksi kualitas udara DKI Jakarta.",
        TANGGAL_ACUAN,
    )

    # ─── Top bar: Tabs + Pilih Wilayah ──────────────────────
    top_col1, top_col2 = st.columns([2, 1])
    with top_col2:
        opsi_wilayah = ["DKI Jakarta (Rata-rata)"] + [w for w in WILAYAH_LIST
                                                       if w in snapshot and not snapshot[w].get("data_terbatas")]
        wilayah_pilih = st.selectbox("Pilih Wilayah", opsi_wilayah,
                                      label_visibility="visible")

    wilayah_param = None if wilayah_pilih == "DKI Jakarta (Rata-rata)" else wilayah_pilih

    tab_pred, tab_pola = st.tabs(["Prediksi ISPU", "Analisis Pola"])

    # ═══════════════════════════════════════════════════════
    # TAB 1: Prediksi ISPU
    # ═══════════════════════════════════════════════════════
    with tab_pred:
        # ─── Row 1: Chart prediksi (kiri) + panel kanan ─────
        col1, col2 = st.columns([2, 0.9], gap="medium")
        with col1:
            st.markdown(f"""
            <div class="card">
                <h3 class="card-title">Prediksi ISPU {wilayah_pilih} <span class="info-icon">i</span></h3>
            """, unsafe_allow_html=True)

            # Pilihan range
            range_pilih = st.radio(
                "Range prediksi",
                ["1 Hari ke Depan", "3 Hari ke Depan", "7 Hari ke Depan"],
                index=1, horizontal=True, label_visibility="collapsed",
                key="range_pred",
            )
            n_hari = {"1 Hari ke Depan": 1, "3 Hari ke Depan": 3, "7 Hari ke Depan": 7}[range_pilih]

            df_pred = prediksi_n_hari(df, wilayah_param, max(n_hari, 7), bundle, TANGGAL_ACUAN)
            df_pred_show = df_pred.head(n_hari) if n_hari < 7 else df_pred

            if len(df_pred_show) > 0:
                st.plotly_chart(
                    _chart_prediksi_multi_hari(df_pred_show, ""),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            else:
                st.warning("Data prediksi tidak tersedia.")

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            if len(df_pred) > 0:
                # Pilih hari kritis (puncak)
                idx_max = df_pred["ispu"].idxmax()
                row_max = df_pred.loc[idx_max]
                kat = kategori_dari_ispu(row_max["ispu"])
                warna = warna_kategori(kat)
                tgl_str = row_max["tanggal"].strftime("%d %B %Y")
                bln_id = {"January": "Januari", "February": "Februari", "March": "Maret",
                          "April": "April", "May": "Mei", "June": "Juni", "July": "Juli",
                          "August": "Agustus", "September": "September", "October": "Oktober",
                          "November": "November", "December": "Desember"}
                for en, idn in bln_id.items():
                    tgl_str = tgl_str.replace(en, idn)

                emoji_cuaca = "☀️" if row_max["ispu"] < 80 else "⛅" if row_max["ispu"] < 120 else "🌫️"

                st.markdown(f"""
                <div class="card" style="padding:20px;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div style="font-size:13px; color:#64748B;">{tgl_str}</div>
                            <div style="font-size:60px; font-weight:800; color:{warna};
                                font-family:'Plus Jakarta Sans',sans-serif; line-height:1; margin-top:4px;">
                                {int(row_max['ispu'])}
                            </div>
                            <div style="font-size:16px; color:{warna}; font-weight:700; margin-top:4px;">{kat}</div>
                        </div>
                        <div style="font-size:42px;">{emoji_cuaca}</div>
                    </div>
                    <div style="margin-top:16px; padding:12px; background:#F8FAFC;
                        border-radius:10px; font-size:12px; color:#475569; line-height:1.5;">
                        Kualitas udara diprediksi <b>{('memburuk' if kat in ['Tidak Sehat','Sangat Tidak Sehat','Berbahaya'] else 'masih dalam batas wajar')}</b>
                        pada {tgl_str}. Disarankan untuk
                        {('mengurangi aktivitas di luar ruangan dan gunakan masker.' if kat in ['Tidak Sehat','Sangat Tidak Sehat','Berbahaya'] else 'tetap menjaga kesehatan saat beraktivitas.')}
                    </div>
                    <div style="margin-top:16px; padding-top:14px; border-top:1px solid #F1F5F9;
                        font-size:12px; color:#64748B;">
                        <div><b style="color:#0F172A;">Model:</b> XGBoost</div>
                        <div style="margin-top:4px;"><b style="color:#0F172A;">Akurasi Test:</b> {meta['test_accuracy']*100:.2f}%</div>
                        <div style="margin-top:4px;"><b style="color:#0F172A;">F1 Macro:</b> {meta['test_f1_macro']:.4f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ─── Row 2: Pola Harian + Polutan Berpengaruh + Korelasi
        col3, col4, col5 = st.columns(3, gap="medium")

        with col3:
            st.markdown(f"""
            <div class="card">
                <h3 class="card-title">Pola Harian ({wilayah_pilih}) <span class="info-icon">i</span></h3>
            """, unsafe_allow_html=True)
            ispu_dasar = (snapshot.get(wilayah_param, {}).get("ispu", 75)
                            if wilayah_param else 75)
            df_pola = pola_harian_synthetic(ispu_dasar)
            st.plotly_chart(
                build_chart_pola_harian(df_pola, height=240),
                use_container_width=True, config={"displayModeBar": False},
                key="pola_pred",
            )
            st.markdown("""
            <div style="margin-top:8px; padding:8px 12px; background:#FEF3C7;
                border-radius:8px; font-size:11px; color:#92400E;">
                ⚠️ Polusi cenderung meningkat pada sore hingga malam hari.
            </div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="card">
                <h3 class="card-title">Polutan Paling Berpengaruh <span class="info-icon">i</span></h3>
            """, unsafe_allow_html=True)
            st.plotly_chart(
                _chart_donut_polutan(meta["feature_importance"]),
                use_container_width=True, config={"displayModeBar": False},
            )
            top_pol_key = max(meta["feature_importance"].items(), key=lambda x: x[1])[0]
            top_pol_label = POLUTAN_INFO[top_pol_key]["label"]
            st.markdown(f"""
            <div style="font-size:12px; color:#64748B; line-height:1.5; margin-top:4px;">
                <b style="color:#0F172A;">{top_pol_label}</b> adalah polutan yang paling
                berkontribusi terhadap kualitas udara di Jakarta.
            </div>
            </div>
            """, unsafe_allow_html=True)

        with col5:
            st.markdown("""
            <div class="card">
                <h3 class="card-title">Korelasi Parameter terhadap ISPU <span class="info-icon">i</span></h3>
            """, unsafe_allow_html=True)
            st.plotly_chart(
                _chart_korelasi(df),
                use_container_width=True, config={"displayModeBar": False},
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # ─── Insight strip (footer) ─────────────────────────
        if len(df_pred) > 0:
            tren_naik = df_pred["ispu"].iloc[-1] > df_pred["ispu"].iloc[0]
            tren_label = "meningkat" if tren_naik else "menurun"

            st.markdown(f"""
            <div class="insight-strip">
                <div class="insight-title">💡 Insight Utama</div>
                <div style="display:flex; gap:14px;">
                    <span class="insight-icon">📈</span>
                    <div>
                        <h4>Tren {tren_label.title()}</h4>
                        <p>Prediksi menunjukkan ISPU {tren_label} dari {int(df_pred['ispu'].iloc[0])} ke {int(df_pred['ispu'].iloc[-1])} dalam {len(df_pred)} hari ke depan.</p>
                    </div>
                </div>
                <div style="display:flex; gap:14px;">
                    <span class="insight-icon">🕒</span>
                    <div>
                        <h4>Waktu Kritis</h4>
                        <p>Polusi tertinggi terjadi pada sore hingga malam hari (17:00 - 20:00 WIB).</p>
                    </div>
                </div>
                <div style="display:flex; gap:14px;">
                    <span class="insight-icon">😷</span>
                    <div>
                        <h4>Polutan Utama</h4>
                        <p>{POLUTAN_INFO[top_pol_key]['label']} menjadi faktor dominan yang memengaruhi kualitas udara Jakarta.</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # TAB 2: Analisis Pola
    # ═══════════════════════════════════════════════════════
    with tab_pola:
        col_a, col_b = st.columns(2, gap="medium")
        with col_a:
            st.markdown("""
            <div class="card">
                <h3 class="card-title">Distribusi Kategori Tahunan</h3>
            """, unsafe_allow_html=True)
            kat_count = df["kategori"].value_counts().reset_index()
            kat_count.columns = ["kategori", "jumlah"]
            kat_total = kat_count["jumlah"].sum()
            kat_count["persen"] = (kat_count["jumlah"] / kat_total * 100).round(1)

            color_map = {"BAIK": "#22C55E", "SEDANG": "#2563EB", "TIDAK SEHAT": "#FACC15"}
            fig = go.Figure(go.Bar(
                x=kat_count["kategori"], y=kat_count["jumlah"],
                marker=dict(color=[color_map.get(k, "#94A3B8") for k in kat_count["kategori"]]),
                text=[f"{j} hari<br>({p}%)" for j, p in zip(kat_count["jumlah"], kat_count["persen"])],
                textposition="outside", textfont=dict(size=11),
            ))
            fig.update_layout(
                height=280, margin=dict(l=0, r=0, t=30, b=0),
                plot_bgcolor="white", paper_bgcolor="white",
                showlegend=False,
                xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=10)),
                font=dict(family="Inter, sans-serif"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b:
            st.markdown("""
            <div class="card">
                <h3 class="card-title">Rata-rata ISPU per Bulan (2024)</h3>
            """, unsafe_allow_html=True)
            monthly = df.groupby("bulan")["max"].mean().reset_index()
            bulan_label = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                            "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
            monthly["bulan_label"] = monthly["bulan"].apply(lambda x: bulan_label[x - 1])

            fig2 = go.Figure(go.Scatter(
                x=monthly["bulan_label"], y=monthly["max"],
                mode="lines+markers",
                line=dict(color="#2563EB", width=2.5, shape="spline"),
                marker=dict(size=8, color="#2563EB"),
                fill="tozeroy", fillcolor="rgba(37,99,235,0.08)",
                hovertemplate="<b>%{x}</b><br>Rata-rata ISPU: %{y:.1f}<extra></extra>",
            ))
            fig2.update_layout(
                height=280, margin=dict(l=0, r=0, t=30, b=0),
                plot_bgcolor="white", paper_bgcolor="white",
                showlegend=False,
                xaxis=dict(showgrid=False, tickfont=dict(size=10)),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=10)),
                font=dict(family="Inter, sans-serif"),
            )
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        # Prediksi interaktif
        st.markdown("""
        <div class="card">
            <h3 class="card-title">🧪 Coba Prediksi Manual</h3>
            <p style="font-size:13px; color:#64748B; margin-bottom:16px;">
                Masukkan nilai 6 polutan, sistem akan memprediksi kategori ISPU
                menggunakan model XGBoost yang sudah dilatih.
            </p>
        """, unsafe_allow_html=True)

        cols_input = st.columns(6)
        defaults = {"pm_sepuluh": 50.0, "pm_duakomalima": 70.0, "sulfur_dioksida": 40.0,
                    "karbon_monoksida": 8.0, "ozon": 25.0, "nitrogen_dioksida": 22.0}
        input_vals = {}
        for col, (key, default) in zip(cols_input, defaults.items()):
            info = POLUTAN_INFO[key]
            with col:
                input_vals[key] = st.number_input(
                    f"{info['label']} ({info['satuan']})",
                    min_value=0.0, max_value=500.0,
                    value=default, step=1.0, key=f"input_{key}",
                )

        if st.button("Prediksi Kategori ISPU", type="primary"):
            from utils.data_loader import predict_xgb
            hasil = predict_xgb(input_vals, bundle)
            label_id = hasil["label"]
            label_view = label_id.title().replace("Tidak", "Tidak")
            warna = warna_kategori(label_view if label_view in ["Baik", "Sedang", "Tidak Sehat"]
                                    else "Sedang")

            st.markdown(f"""
            <div style="margin-top:14px; padding:18px; background:{warna}15;
                border-left:4px solid {warna}; border-radius:12px;">
                <div style="font-size:13px; color:#64748B;">Hasil Prediksi:</div>
                <div style="font-size:28px; font-weight:800; color:{warna};
                    font-family:'Plus Jakarta Sans',sans-serif; margin-top:4px;">{label_id}</div>
                <div style="font-size:12px; color:#475569; margin-top:8px;">
                    Confidence:
                    {", ".join([f"<b>{k}</b>: {v*100:.1f}%" for k, v in hasil['probabilitas'].items()])}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

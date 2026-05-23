"""
Komponen reusable: hero card, polutan grid, peta sederhana,
chart helpers, rekomendasi cards.
"""
from __future__ import annotations
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.ispu_helper import (
    KATEGORI_RANGE, POLUTAN_INFO, deskripsi_kategori,
    rekomendasi_aktivitas, warna_kategori, warna_kategori_bg,
)


# ────────────────────────────────────────────────────────────
# Page header
# ────────────────────────────────────────────────────────────
def render_page_header(title: str, subtitle: str, tanggal: date):
    """Header standar tiap page dengan badge tanggal update."""
    tgl_str = tanggal.strftime("%d %B %Y").replace(
        "January", "Januari").replace("February", "Februari").replace(
        "March", "Maret").replace("April", "April").replace(
        "May", "Mei").replace("June", "Juni").replace(
        "July", "Juli").replace("August", "Agustus").replace(
        "September", "September").replace("October", "Oktober").replace(
        "November", "November").replace("December", "Desember")

    st.markdown(f"""
    <div class="page-header">
        <div>
            <h1 class="page-title">{title}</h1>
            <p class="page-subtitle">{subtitle}</p>
        </div>
        <div class="header-meta">
            📅 Data terakhir diperbarui &nbsp;<b>{tgl_str}, 10:00 WIB</b>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────
# Hero ISPU card (Dashboard & Detail Wilayah)
# ────────────────────────────────────────────────────────────
def render_hero_ispu(ispu: int, kategori: str, judul: str,
                      polutan_dominan: str, polutan_value: float | None = None):
    """Card besar dengan angka ISPU & status."""
    warna = warna_kategori(kategori)
    desc = deskripsi_kategori(kategori)

    # Polutan dominan label
    pol_label = polutan_dominan
    pol_value_txt = ""
    pol_key_map = {
        "PM25": "pm_duakomalima", "PM10": "pm_sepuluh",
        "SO2": "sulfur_dioksida", "CO": "karbon_monoksida",
        "O3": "ozon", "NO2": "nitrogen_dioksida",
    }
    if polutan_dominan in pol_key_map:
        info = POLUTAN_INFO[pol_key_map[polutan_dominan]]
        pol_label = info["label"]
        if polutan_value is not None:
            pol_value_txt = f"({polutan_value} {info['satuan']})"

    st.markdown(f"""
    <div class="card">
        <h3 class="card-title">{judul} <span class="info-icon">i</span></h3>
        <div class="ispu-hero">
            <div>
                <div class="ispu-number" style="color: {warna};">{ispu}</div>
                <div class="ispu-label">ISPU</div>
            </div>
            <div style="flex: 1;">
                <div class="ispu-status" style="color: {warna};">{kategori}</div>
                <div class="ispu-subtext">{desc}</div>
            </div>
        </div>
        <div class="ispu-dominant">
            🌿 Polutan dominan: <b>{pol_label}</b> {pol_value_txt}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────
# Peta Jakarta sederhana (SVG inline) + legenda
# ────────────────────────────────────────────────────────────
def render_peta_jakarta(snapshot: dict):
    """Render peta sederhana dengan warna per wilayah berdasarkan ISPU."""
    # Posisi tetap untuk 6 wilayah dalam layout SVG 600×420
    wilayah_pos = {
        "Jakarta Barat":    {"cx": 175, "cy": 195, "rx": 110, "ry": 75, "rot": -8},
        "Jakarta Utara":    {"cx": 380, "cy": 110, "rx": 130, "ry": 60, "rot": -3},
        "Jakarta Pusat":    {"cx": 325, "cy": 215, "rx": 70,  "ry": 45, "rot": 0},
        "Jakarta Timur":    {"cx": 470, "cy": 245, "rx": 110, "ry": 80, "rot": 5},
        "Jakarta Selatan":  {"cx": 280, "cy": 320, "rx": 130, "ry": 70, "rot": 3},
        "Kep. Seribu":      {"cx": 90,  "cy": 70,  "rx": 36,  "ry": 26, "rot": 0},
    }

    shapes_svg = ""
    labels_svg = ""

    for wilayah, pos in wilayah_pos.items():
        if wilayah not in snapshot:
            continue
        snap = snapshot[wilayah]
        ispu = snap["ispu"]
        kategori = snap["kategori"]
        warna = warna_kategori(kategori)
        warna_bg = warna_kategori_bg(kategori)

        # Ellipse berwarna
        shapes_svg += f"""
            <ellipse cx="{pos['cx']}" cy="{pos['cy']}"
                rx="{pos['rx']}" ry="{pos['ry']}"
                transform="rotate({pos['rot']} {pos['cx']} {pos['cy']})"
                fill="{warna_bg}" stroke="{warna}" stroke-width="2" opacity="0.85"/>
        """

        # Label nama wilayah (di atas) + badge ISPU (di tengah)
        nama_short = "Kep. Seribu" if wilayah == "Kep. Seribu" else wilayah
        label_y_offset = -8
        labels_svg += f"""
            <text x="{pos['cx']}" y="{pos['cy']+label_y_offset}"
                text-anchor="middle" font-size="11" font-weight="600"
                fill="#334155" font-family="Inter,sans-serif">{nama_short}</text>
            <rect x="{pos['cx']-22}" y="{pos['cy']+4}" width="44" height="22"
                rx="6" fill="white" stroke="{warna}" stroke-width="1.5"/>
            <text x="{pos['cx']}" y="{pos['cy']+19}"
                text-anchor="middle" font-size="13" font-weight="800"
                fill="{warna}" font-family="Plus Jakarta Sans,Inter,sans-serif">{ispu}</text>
        """

    svg = f"""
    <svg viewBox="0 0 600 420" xmlns="http://www.w3.org/2000/svg"
        style="width:100%; height:auto; max-height:340px;">
        <defs>
            <pattern id="dots" x="0" y="0" width="14" height="14" patternUnits="userSpaceOnUse">
                <circle cx="2" cy="2" r="0.8" fill="#CBD5E1" opacity="0.4"/>
            </pattern>
        </defs>
        <rect width="600" height="420" fill="url(#dots)" opacity="0.5"/>
        {shapes_svg}
        {labels_svg}
    </svg>
    """

    # Legenda
    legenda_html = "<div style='display:flex; flex-direction:column; gap:10px; padding-top:8px;'>"
    for nama, lo, hi, _ in KATEGORI_RANGE:
        warna = warna_kategori(nama)
        range_label = f"{lo}-{hi}" if hi < 500 else f"≥{lo}"
        legenda_html += f"""
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:14px; height:14px; border-radius:50%; background:{warna};"></div>
            <span style="font-size:13px; color:#334155;">{nama} ({range_label})</span>
        </div>
        """
    legenda_html += "</div>"

    # Container card
    col1, col2 = st.columns([3, 1.2])
    with col1:
        st.markdown(svg, unsafe_allow_html=True)
    with col2:
        st.markdown(legenda_html, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────
# Polutan grid (6 polutan dengan progress bar)
# ────────────────────────────────────────────────────────────
def render_polutan_grid(polutan_values: dict):
    """Grid 6 polutan dengan nilai + bar relatif."""
    # Threshold untuk warna bar (% terhadap nilai 'tinggi')
    thresholds = {
        "pm_duakomalima": 75, "pm_sepuluh": 100,
        "nitrogen_dioksida": 80, "sulfur_dioksida": 80,
        "karbon_monoksida": 10, "ozon": 100,
    }

    chips_html = ""
    for key in ["pm_duakomalima", "pm_sepuluh", "nitrogen_dioksida",
                "sulfur_dioksida", "karbon_monoksida", "ozon"]:
        info = POLUTAN_INFO[key]
        val = polutan_values.get(key, 0)
        thr = thresholds[key]
        pct = min(100, (val / thr) * 100)

        if pct < 50: bar_color = "#22C55E"
        elif pct < 80: bar_color = "#2563EB"
        elif pct < 100: bar_color = "#FACC15"
        else: bar_color = "#EF4444"

        chips_html += f"""
        <div class="pol-chip">
            <div class="pol-name">{info['label']}</div>
            <div class="pol-val">{val}</div>
            <div class="pol-unit">{info['satuan']}</div>
            <div class="pol-bar"><div style="width:{pct}%; background:{bar_color};"></div></div>
        </div>
        """

    st.markdown(f"""
    <div class="card">
        <h3 class="card-title">Komposisi Polutan <span class="info-icon">i</span></h3>
        <div class="pol-grid">{chips_html}</div>
        <div style="margin-top:18px; font-size:12px; color:#64748B;">
            Tingkat konsentrasi setiap polutan terhadap baku mutu acuan.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────
# Chart: Tren ISPU 7 hari (line chart Plotly)
# ────────────────────────────────────────────────────────────
def build_chart_tren(df_tren: pd.DataFrame, judul: str, height: int = 280) -> go.Figure:
    """Line chart tren ISPU dengan threshold lines."""
    fig = go.Figure()

    # Threshold lines
    for nama, lo, hi, warna in KATEGORI_RANGE:
        if nama in ["Sangat Tidak Sehat", "Tidak Sehat", "Baik"] and hi < 250:
            fig.add_hline(
                y=hi, line=dict(color=warna, width=1, dash="dot"),
                annotation_text=nama, annotation_position="right",
                annotation_font_size=10, annotation_font_color=warna,
            )

    tanggal_labels = df_tren["tanggal_full"].dt.strftime("%d %b")
    fig.add_trace(go.Scatter(
        x=tanggal_labels, y=df_tren["ispu"],
        mode="lines+markers",
        line=dict(color="#2563EB", width=2.5, shape="spline", smoothing=0.6),
        marker=dict(size=8, color="#2563EB",
                    line=dict(width=2, color="white")),
        fill="tozeroy", fillcolor="rgba(37, 99, 235, 0.08)",
        hovertemplate="<b>%{x}</b><br>ISPU: %{y}<extra></extra>",
        name="ISPU",
    ))

    # Highlight last value
    last_idx = len(df_tren) - 1
    fig.add_annotation(
        x=tanggal_labels.iloc[last_idx], y=df_tren["ispu"].iloc[last_idx],
        text=f"<b>{df_tren['ispu'].iloc[last_idx]}</b>",
        showarrow=False, yshift=14,
        font=dict(size=12, color="#0F172A"),
        bgcolor="#FFFFFF", bordercolor="#E2E8F0", borderwidth=1,
        borderpad=4,
    )

    fig.update_layout(
        height=height, margin=dict(l=0, r=20, t=20, b=0),
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#64748B")),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False,
                   tickfont=dict(size=11, color="#64748B"),
                   range=[0, max(160, df_tren["ispu"].max() * 1.4)]),
        font=dict(family="Inter, sans-serif"),
    )
    return fig


# ────────────────────────────────────────────────────────────
# Chart: Pola Harian (24 jam)
# ────────────────────────────────────────────────────────────
def build_chart_pola_harian(df_pola: pd.DataFrame, height: int = 280) -> go.Figure:
    """Area chart pola 24 jam dengan annotation 'Puncak Polusi'."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_pola["jam"], y=df_pola["ispu"],
        mode="lines+markers",
        line=dict(color="#F97316", width=2.5, shape="spline", smoothing=0.5),
        marker=dict(size=6, color="#F97316"),
        fill="tozeroy", fillcolor="rgba(249, 115, 22, 0.15)",
        hovertemplate="<b>%{x}</b><br>ISPU: %{y}<extra></extra>",
    ))

    # Annotation puncak
    idx_max = df_pola["ispu"].idxmax()
    fig.add_annotation(
        x=df_pola["jam"].iloc[idx_max], y=df_pola["ispu"].iloc[idx_max],
        text="<b>Puncak Polusi</b><br>17:00 - 20:00",
        showarrow=True, arrowhead=0, arrowcolor="#F97316",
        arrowwidth=1.5, ax=0, ay=-40,
        font=dict(size=11, color="#0F172A"),
        bgcolor="#FFFFFF", bordercolor="#FED7AA", borderwidth=1,
        borderpad=8,
    )

    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#64748B"),
                   tickvals=df_pola["jam"][::4]),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False,
                   tickfont=dict(size=10, color="#64748B")),
        font=dict(family="Inter, sans-serif"),
    )
    return fig


# ────────────────────────────────────────────────────────────
# Rekomendasi aktivitas (4 cards)
# ────────────────────────────────────────────────────────────
def render_rekomendasi(kategori: str):
    rek = rekomendasi_aktivitas(kategori)
    items = [
        ("olahraga", "🏃", "Olahraga Luar Ruangan", "#DBEAFE"),
        ("masker", "😷", "Gunakan Masker", "#FEF3C7"),
        ("sensitif", "👴", "Kelompok Sensitif", "#FFEDD5"),
        ("jendela", "🪟", "Buka Jendela", "#DCFCE7"),
    ]
    cols = st.columns(4)
    for col, (key, emoji, judul, bg) in zip(cols, items):
        status, warna, deskripsi = rek[key]
        with col:
            st.markdown(f"""
            <div class="rec-card">
                <div class="rec-icon" style="background:{bg};">{emoji}</div>
                <div class="rec-content">
                    <h4>{judul}</h4>
                    <div class="rec-status" style="color:{warna};">{status}</div>
                    <p class="rec-desc">{deskripsi}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────
# Sidebar info card
# ────────────────────────────────────────────────────────────
def render_sidebar_info(tanggal_acuan: date):
    tgl_str = tanggal_acuan.strftime("%d %B %Y")
    bln = {"January": "Januari", "February": "Februari", "March": "Maret",
           "April": "April", "May": "Mei", "June": "Juni", "July": "Juli",
           "August": "Agustus", "September": "September", "October": "Oktober",
           "November": "November", "December": "Desember"}
    for en, idn in bln.items():
        tgl_str = tgl_str.replace(en, idn)

    st.sidebar.markdown(f"""
    <div class="sidebar-info-card">
        <h4>📌 Data tidak realtime</h4>
        <p>Data berasal dari sampel ISPU tahun 2024 dan diperbarui secara berkala.</p>
        <div class="updated">
            Data terakhir diperbarui
            <b>{tgl_str}, 10:00 WIB</b>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────
# Sidebar logo
# ────────────────────────────────────────────────────────────
def render_sidebar_logo():
    st.sidebar.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">U</div>
        <div class="sidebar-logo-text">
            <h1>JakU</h1>
            <p>Pantau Udara, Jaga Jakarta</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

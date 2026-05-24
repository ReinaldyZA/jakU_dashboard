"""
Komponen reusable: hero card, polutan grid, peta sederhana,
chart helpers, rekomendasi cards.

Semua HTML di-render via st.html() (Streamlit 1.33+) yang bypass
markdown parser, sehingga indentasi & newline tidak diparse sebagai
code block. SVG khusus pakai base64 img karena sanitizer Streamlit
strip <svg> mentah.
"""
from __future__ import annotations
import base64
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.ispu_helper import (
    KATEGORI_RANGE, POLUTAN_INFO, deskripsi_kategori,
    rekomendasi_aktivitas, warna_kategori, warna_kategori_bg,
)


# Fallback helper: pakai st.html jika ada, kalau tidak fallback ke markdown
def _render_html(html: str):
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


def _bulan_id(tanggal: date) -> str:
    bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
             "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    return f"{tanggal.day} {bulan[tanggal.month - 1]} {tanggal.year}"


# ────────────────────────────────────────────────────────────
# Page header
# ────────────────────────────────────────────────────────────
def render_page_header(title: str, subtitle: str, tanggal: date):
    tgl_str = _bulan_id(tanggal)
    html = (
        '<div class="page-header">'
        '<div>'
        f'<h1 class="page-title">{title}</h1>'
        f'<p class="page-subtitle">{subtitle}</p>'
        '</div>'
        '<div class="header-meta">'
        f'📅 Data terakhir diperbarui &nbsp;<b>{tgl_str}, 10:00 WIB</b>'
        '</div>'
        '</div>'
    )
    _render_html(html)


# ────────────────────────────────────────────────────────────
# Hero ISPU card (Dashboard & Detail Wilayah)
# ────────────────────────────────────────────────────────────
def render_hero_ispu(ispu: int, kategori: str, judul: str,
                      polutan_dominan: str, polutan_value: float | None = None):
    warna = warna_kategori(kategori)
    desc = deskripsi_kategori(kategori)

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

    html = (
        '<div class="card">'
        f'<h3 class="card-title">{judul} <span class="info-icon">i</span></h3>'
        '<div class="ispu-hero">'
        '<div>'
        f'<div class="ispu-number" style="color: {warna};">{ispu}</div>'
        '<div class="ispu-label">ISPU</div>'
        '</div>'
        '<div style="flex: 1;">'
        f'<div class="ispu-status" style="color: {warna};">{kategori}</div>'
        f'<div class="ispu-subtext">{desc}</div>'
        '</div>'
        '</div>'
        '<div class="ispu-dominant">'
        f'🌿 Polutan dominan: <b>{pol_label}</b> {pol_value_txt}'
        '</div>'
        '</div>'
    )
    _render_html(html)


# ────────────────────────────────────────────────────────────
# Peta Jakarta sederhana (SVG via base64 img) + legenda
# ────────────────────────────────────────────────────────────
def render_peta_jakarta(snapshot: dict):
    wilayah_pos = {
        "Jakarta Barat":    {"cx": 175, "cy": 195, "rx": 110, "ry": 75, "rot": -8},
        "Jakarta Utara":    {"cx": 380, "cy": 110, "rx": 130, "ry": 60, "rot": -3},
        "Jakarta Pusat":    {"cx": 325, "cy": 215, "rx": 70,  "ry": 45, "rot": 0},
        "Jakarta Timur":    {"cx": 470, "cy": 245, "rx": 110, "ry": 80, "rot": 5},
        "Jakarta Selatan":  {"cx": 280, "cy": 320, "rx": 130, "ry": 70, "rot": 3},
        "Kep. Seribu":      {"cx": 90,  "cy": 70,  "rx": 36,  "ry": 26, "rot": 0},
    }

    shapes = []
    labels = []
    for wilayah, pos in wilayah_pos.items():
        if wilayah not in snapshot:
            continue
        snap = snapshot[wilayah]
        ispu = snap["ispu"]
        kategori = snap["kategori"]
        warna = warna_kategori(kategori)
        warna_bg = warna_kategori_bg(kategori)

        shapes.append(
            f'<ellipse cx="{pos["cx"]}" cy="{pos["cy"]}" '
            f'rx="{pos["rx"]}" ry="{pos["ry"]}" '
            f'transform="rotate({pos["rot"]} {pos["cx"]} {pos["cy"]})" '
            f'fill="{warna_bg}" stroke="{warna}" stroke-width="2" opacity="0.85"/>'
        )

        labels.append(
            f'<text x="{pos["cx"]}" y="{pos["cy"]-8}" '
            f'text-anchor="middle" font-size="11" font-weight="600" '
            f'fill="#334155" font-family="Inter,sans-serif">{wilayah}</text>'
            f'<rect x="{pos["cx"]-22}" y="{pos["cy"]+4}" width="44" height="22" '
            f'rx="6" fill="white" stroke="{warna}" stroke-width="1.5"/>'
            f'<text x="{pos["cx"]}" y="{pos["cy"]+19}" '
            f'text-anchor="middle" font-size="13" font-weight="800" '
            f'fill="{warna}" font-family="Plus Jakarta Sans,Inter,sans-serif">{ispu}</text>'
        )

    svg = (
        '<svg viewBox="0 0 600 420" xmlns="http://www.w3.org/2000/svg" '
        'style="width:100%;height:auto;max-height:340px;">'
        '<defs>'
        '<pattern id="dots" x="0" y="0" width="14" height="14" patternUnits="userSpaceOnUse">'
        '<circle cx="2" cy="2" r="0.8" fill="#CBD5E1" opacity="0.4"/>'
        '</pattern>'
        '</defs>'
        '<rect width="600" height="420" fill="url(#dots)" opacity="0.5"/>'
        + "".join(shapes) + "".join(labels) +
        '</svg>'
    )

    # Encode ke base64 supaya lolos sanitizer Streamlit
    svg_b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    img_html = (
        f'<img src="data:image/svg+xml;base64,{svg_b64}" '
        f'style="width:100%;height:auto;max-height:340px;display:block;" '
        f'alt="Peta kualitas udara Jakarta">'
    )

    # Legenda: SINGLE-LINE HTML (no indentation, no newlines)
    legenda_items = []
    for nama, lo, hi, _ in KATEGORI_RANGE:
        warna = warna_kategori(nama)
        range_label = f"{lo}-{hi}" if hi < 500 else f"≥{lo}"
        legenda_items.append(
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">'
            f'<div style="width:14px;height:14px;border-radius:50%;background:{warna};flex-shrink:0;"></div>'
            f'<span style="font-size:13px;color:#334155;">{nama} ({range_label})</span>'
            f'</div>'
        )
    legenda_html = (
        '<div style="display:flex;flex-direction:column;padding-top:8px;">'
        + "".join(legenda_items)
        + '</div>'
    )

    col1, col2 = st.columns([3, 1.2])
    with col1:
        _render_html(img_html)
    with col2:
        _render_html(legenda_html)


# ────────────────────────────────────────────────────────────
# Polutan grid (6 polutan dengan progress bar)
# ────────────────────────────────────────────────────────────
def render_polutan_grid(polutan_values: dict):
    thresholds = {
        "pm_duakomalima": 75, "pm_sepuluh": 100,
        "nitrogen_dioksida": 80, "sulfur_dioksida": 80,
        "karbon_monoksida": 10, "ozon": 100,
    }

    chips = []
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

        chips.append(
            f'<div class="pol-chip">'
            f'<div class="pol-name">{info["label"]}</div>'
            f'<div class="pol-val">{val}</div>'
            f'<div class="pol-unit">{info["satuan"]}</div>'
            f'<div class="pol-bar"><div style="width:{pct}%;background:{bar_color};"></div></div>'
            f'</div>'
        )

    html = (
        '<div class="card">'
        '<h3 class="card-title">Komposisi Polutan <span class="info-icon">i</span></h3>'
        '<div class="pol-grid">' + "".join(chips) + '</div>'
        '<div style="margin-top:18px;font-size:12px;color:#64748B;">'
        'Tingkat konsentrasi setiap polutan terhadap baku mutu acuan.'
        '</div>'
        '</div>'
    )
    _render_html(html)


# ────────────────────────────────────────────────────────────
# Chart: Tren ISPU 7 hari (line chart Plotly) — TIDAK BERUBAH
# ────────────────────────────────────────────────────────────
def build_chart_tren(df_tren: pd.DataFrame, judul: str, height: int = 280) -> go.Figure:
    fig = go.Figure()

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
        marker=dict(size=8, color="#2563EB", line=dict(width=2, color="white")),
        fill="tozeroy", fillcolor="rgba(37, 99, 235, 0.08)",
        hovertemplate="<b>%{x}</b><br>ISPU: %{y}<extra></extra>",
        name="ISPU",
    ))

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
# Chart: Pola Harian (24 jam) — TIDAK BERUBAH
# ────────────────────────────────────────────────────────────
def build_chart_pola_harian(df_pola: pd.DataFrame, height: int = 280) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_pola["jam"], y=df_pola["ispu"],
        mode="lines+markers",
        line=dict(color="#F97316", width=2.5, shape="spline", smoothing=0.5),
        marker=dict(size=6, color="#F97316"),
        fill="tozeroy", fillcolor="rgba(249, 115, 22, 0.15)",
        hovertemplate="<b>%{x}</b><br>ISPU: %{y}<extra></extra>",
    ))

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
            html = (
                '<div class="rec-card">'
                f'<div class="rec-icon" style="background:{bg};">{emoji}</div>'
                '<div class="rec-content">'
                f'<h4>{judul}</h4>'
                f'<div class="rec-status" style="color:{warna};">{status}</div>'
                f'<p class="rec-desc">{deskripsi}</p>'
                '</div>'
                '</div>'
            )
            _render_html(html)


# ────────────────────────────────────────────────────────────
# Sidebar info card
# ────────────────────────────────────────────────────────────
def render_sidebar_info(tanggal_acuan: date):
    tgl_str = _bulan_id(tanggal_acuan)
    html = (
        '<div class="sidebar-info-card">'
        '<h4>📌 Data tidak realtime</h4>'
        '<p>Data berasal dari sampel ISPU tahun 2024 dan diperbarui secara berkala.</p>'
        '<div class="updated">'
        'Data terakhir diperbarui'
        f'<b>{tgl_str}, 10:00 WIB</b>'
        '</div>'
        '</div>'
    )
    with st.sidebar:
        _render_html(html)


# ────────────────────────────────────────────────────────────
# Sidebar logo
# ────────────────────────────────────────────────────────────
def render_sidebar_logo():
    html = (
        '<div class="sidebar-logo">'
        '<div class="sidebar-logo-icon">U</div>'
        '<div class="sidebar-logo-text">'
        '<h1>JakU</h1>'
        '<p>Pantau Udara, Jaga Jakarta</p>'
        '</div>'
        '</div>'
    )
    with st.sidebar:
        _render_html(html)

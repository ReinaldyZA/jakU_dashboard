"""Halaman Edukasi & Insight - penjelasan ISPU & dampak kesehatan."""
import plotly.graph_objects as go
import streamlit as st

from utils.components import _render_html, render_page_header
from utils.data_loader import TANGGAL_ACUAN
from utils.ispu_helper import KATEGORI_COLOR_BG, KATEGORI_RANGE


def _chart_sumber_polusi() -> go.Figure:
    labels = ["Transportasi", "Industri", "Aktivitas Rumah Tangga", "Konstruksi", "Lainnya"]
    values = [45, 20, 15, 10, 10]
    colors = ["#2563EB", "#22C55E", "#FACC15", "#EF4444", "#A855F7"]

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.58,
        marker=dict(colors=colors, line=dict(color="white", width=3)),
        textposition="outside", textinfo="label+percent",
        textfont=dict(size=11, family="Inter"),
        hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>",
    )])
    fig.add_annotation(
        text="<b>Kontribusi<br>Sumber Polusi</b>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(family="Plus Jakarta Sans", size=13, color="#0F172A"),
    )
    fig.update_layout(
        height=320, margin=dict(l=40, r=40, t=20, b=40),
        showlegend=False, font=dict(family="Inter, sans-serif"),
    )
    return fig


def _chart_puncak_polusi() -> go.Figure:
    hours = list(range(25))
    pola = [60, 50, 45, 40, 45, 55, 75, 90, 100, 95, 80, 75,
            70, 70, 75, 90, 110, 140, 155, 160, 145, 120, 95, 80, 75]
    jam_labels = [f"{h:02d}:00" for h in hours]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=jam_labels, y=pola, mode="lines+markers",
        line=dict(color="#F97316", width=2.5, shape="spline", smoothing=0.5),
        marker=dict(size=5, color="#F97316"),
        fill="tozeroy", fillcolor="rgba(249, 115, 22, 0.12)",
        hovertemplate="<b>%{x}</b><br>ISPU: %{y}<extra></extra>",
    ))
    idx_max = pola.index(max(pola))
    fig.add_annotation(
        x=jam_labels[idx_max], y=pola[idx_max],
        text="<b>Puncak Polusi</b><br>17:00 - 20:00",
        showarrow=True, arrowhead=0, arrowcolor="#F97316",
        arrowwidth=1.5, ax=-10, ay=-44,
        font=dict(size=10, color="#0F172A"),
        bgcolor="#FFFFFF", bordercolor="#FED7AA", borderwidth=1, borderpad=6,
    )
    fig.update_layout(
        height=270, margin=dict(l=0, r=10, t=30, b=20),
        plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#64748B"),
                    tickvals=[jam_labels[i] for i in range(0, 25, 4)]),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False,
                    tickfont=dict(size=10, color="#64748B"),
                    title=dict(text="ISPU", font=dict(size=10))),
        font=dict(family="Inter, sans-serif"),
    )
    return fig


def render():
    render_page_header(
        "Edukasi & Insight",
        "Pahami kualitas udara dan dampaknya bagi kesehatan Anda.",
        TANGGAL_ACUAN,
    )

    # ─── Section 1: Mengenal ISPU (5 kategori cards) ────────────
    # SATU HTML block lengkap - card + title + grid 5 kategori
    emoji_map = {
        "Baik": "😊", "Sedang": "😐", "Tidak Sehat": "😷",
        "Sangat Tidak Sehat": "😨", "Berbahaya": "😱",
    }
    desc_map = {
        "Baik": "Udara bersih, aman untuk beraktivitas sehari-hari.",
        "Sedang": "Masih dapat diterima untuk beraktivitas luar ruangan.",
        "Tidak Sehat": "Kurangi aktivitas luar ruangan, terutama bagi kelompok sensitif.",
        "Sangat Tidak Sehat": "Hindari aktivitas luar ruangan. Gunakan masker jika harus keluar.",
        "Berbahaya": "Hindari semua aktivitas luar ruangan. Tetap di dalam ruangan.",
    }

    cat_cards = []
    for nama, lo, hi, warna in KATEGORI_RANGE:
        bg = KATEGORI_COLOR_BG[nama]
        emoji = emoji_map[nama]
        desc = desc_map[nama]
        range_label = f"{lo} – {hi}" if hi < 500 else f"≥ {lo}"
        cat_cards.append(
            f'<div class="edu-cat-card" style="background:{bg};">'
            f'<div class="emoji">{emoji}</div>'
            f'<div class="range" style="color:{warna};">{range_label}</div>'
            f'<div class="nama" style="color:{warna};">{nama}</div>'
            f'<div class="desc">{desc}</div>'
            f'</div>'
        )

    section1_html = (
        '<div class="card">'
        '<h3 class="card-title">Mengenal ISPU (Indeks Standar Pencemar Udara)</h3>'
        '<p style="font-size:13px;color:#64748B;margin:-8px 0 18px 0;">'
        'ISPU digunakan untuk menggambarkan kualitas udara ambien di sekitar kita.'
        '</p>'
        '<div class="edu-cat-row">' + "".join(cat_cards) + '</div>'
        '</div>'
    )
    _render_html(section1_html)

    # ─── Section 2: Dampak | Sumber | Waktu Terburuk ────────────
    col1, col2, col3 = st.columns(3, gap="medium")

    # Kolom 1: Dampak Kesehatan - HTML murni, SATU block lengkap
    with col1:
        dampak_items = [
            ("🫁", "Sistem Pernapasan",
             "Polusi udara dapat menyebabkan iritasi, batuk, sesak napas, dan memperparah asma."),
            ("❤️", "Sistem Kardiovaskular",
             "Paparan jangka panjang meningkatkan risiko penyakit jantung dan tekanan darah tinggi."),
            ("👶", "Anak-anak",
             "Anak lebih rentan terhadap infeksi pernapasan dan gangguan perkembangan paru-paru."),
            ("👴", "Lansia",
             "Risiko penyakit kronis meningkat, terutama jika memiliki riwayat penyakit."),
        ]
        items_html = []
        for icon, judul, desc in dampak_items:
            items_html.append(
                '<div style="display:flex;gap:12px;align-items:flex-start;">'
                f'<div style="font-size:28px;flex-shrink:0;">{icon}</div>'
                '<div>'
                f'<div style="font-size:13px;font-weight:700;color:#0F172A;font-family:\'Plus Jakarta Sans\',sans-serif;">{judul}</div>'
                f'<div style="font-size:11px;color:#64748B;margin-top:2px;line-height:1.5;">{desc}</div>'
                '</div>'
                '</div>'
            )

        col1_html = (
            '<div class="card" style="height:100%;">'
            '<h3 class="card-title">Dampak Kualitas Udara terhadap Kesehatan <span class="info-icon">i</span></h3>'
            '<div style="display:flex;flex-direction:column;gap:14px;margin-top:8px;">'
            + "".join(items_html)
            + '</div>'
            '</div>'
        )
        _render_html(col1_html)

    # Kolom 2: Sumber Polusi - card pakai st.container(border) karena ada plotly chart
    with col2:
        with st.container(border=True):
            _render_html(
                '<h3 style="font-size:16px;font-weight:700;color:#0F172A;margin:0 0 8px 0;'
                'font-family:\'Plus Jakarta Sans\',sans-serif;">'
                'Sumber Polusi Udara di Jakarta <span class="info-icon">i</span>'
                '</h3>'
            )
            st.plotly_chart(_chart_sumber_polusi(), use_container_width=True,
                            config={"displayModeBar": False})
            _render_html(
                '<div style="font-size:11px;color:#64748B;line-height:1.5;">'
                '<b style="color:#0F172A;">Transportasi</b> menjadi penyumbang polusi udara terbesar di Jakarta. '
                'Sumber: estimasi referensi penelitian kualitas udara DKI.'
                '</div>'
            )

    # Kolom 3: Waktu Terburuk - card pakai st.container(border)
    with col3:
        with st.container(border=True):
            _render_html(
                '<h3 style="font-size:16px;font-weight:700;color:#0F172A;margin:0 0 8px 0;'
                'font-family:\'Plus Jakarta Sans\',sans-serif;">'
                'Waktu dengan Kualitas Udara Terburuk <span class="info-icon">i</span>'
                '</h3>'
            )
            st.plotly_chart(_chart_puncak_polusi(), use_container_width=True,
                            config={"displayModeBar": False})
            _render_html(
                '<div style="padding:10px 12px;background:#F0F9FF;border-radius:8px;'
                'font-size:11px;color:#1E40AF;line-height:1.5;">'
                '💡 Kualitas udara cenderung memburuk pada sore hingga malam hari. '
                'Sebaiknya batasi aktivitas luar ruangan pada waktu tersebut.'
                '</div>'
            )

    # ─── Section 3: Tips Kesehatan (5 cards) ────────────────────
    # SATU HTML block lengkap dengan CSS grid internal
    tips = [
        ("😷", "Gunakan Masker",
         "Gunakan masker berstandar yang dapat mengurangi paparan polusi udara."),
        ("🏃", "Batasi Aktivitas Luar",
         "Kurangi aktivitas fisik berat di luar ruangan, terutama saat sore hingga malam hari."),
        ("🪟", "Ventilasi yang Baik",
         "Tutup jendela saat polusi tinggi dan pastikan ventilasi rumah tetap berfungsi baik."),
        ("💧", "Perbanyak Minum Air",
         "Minum air putih yang cukup untuk menjaga kebersihan saluran pernapasan."),
        ("🌬️", "Gunakan Air Purifier",
         "Jika memungkinkan, gunakan alat penyaring udara di dalam ruangan untuk udara lebih bersih."),
    ]
    tip_cards = []
    for emoji, judul, desc in tips:
        tip_cards.append(
            '<div style="padding:18px 14px;text-align:left;">'
            f'<div style="font-size:36px;margin-bottom:10px;">{emoji}</div>'
            f'<div style="font-size:13px;font-weight:700;color:#0F172A;font-family:\'Plus Jakarta Sans\',sans-serif;margin-bottom:6px;">{judul}</div>'
            f'<div style="font-size:11px;color:#64748B;line-height:1.5;">{desc}</div>'
            '</div>'
        )

    section3_html = (
        '<div class="card">'
        '<h3 class="card-title">Tips Menjaga Kesehatan Saat Kualitas Udara Tidak Sehat <span class="info-icon">i</span></h3>'
        '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-top:4px;">'
        + "".join(tip_cards)
        + '</div>'
        '</div>'
    )
    _render_html(section3_html)

    # ─── Footer banner hijau ────────────────────────────────────
    banner_html = (
        '<div class="green-banner">'
        '<div class="green-banner-icon">🌿</div>'
        '<div>'
        '<h3>Jaga udara, jaga kesehatan, jaga Jakarta.</h3>'
        '<p>Langkah kecil hari ini untuk udara yang lebih baik di masa depan.</p>'
        '</div>'
        '</div>'
    )
    _render_html(banner_html)

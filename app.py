"""
JakU - Pantau Udara, Jaga Jakarta
=================================
Dashboard publik kualitas udara DKI Jakarta berdasarkan data ISPU 2024.
Dibangun dengan Streamlit + Plotly + XGBoost.

Skripsi: Implementasi Metodologi CRISP-DM Menggunakan Machine Learning
dengan Pendekatan User Centered Design sebagai Sistem Pendukung Keputusan
Kualitas Udara di Provinsi DKI Jakarta Berdasarkan Data ISPU.
"""
import streamlit as st

from utils.components import render_sidebar_info, render_sidebar_logo
from utils.data_loader import TANGGAL_ACUAN
from utils.styles import CSS
from views import dashboard, detail_wilayah, edukasi_insight, prediksi_analisis

# ─── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="JakU - Pantau Udara, Jaga Jakarta",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom CSS
st.markdown(CSS, unsafe_allow_html=True)

# ─── Sidebar navigation ─────────────────────────────────────
render_sidebar_logo()

# Inisialisasi page state
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

PAGES = [
    ("Dashboard", "🏠"),
    ("Detail Wilayah", "📍"),
    ("Prediksi & Analisis", "📈"),
    ("Edukasi & Insight", "📚"),
]

st.sidebar.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

for nama, icon in PAGES:
    is_active = st.session_state.current_page == nama
    if st.sidebar.button(
        f"{icon}   {nama}",
        key=f"nav_{nama}",
        type="primary" if is_active else "secondary",
        use_container_width=True,
    ):
        st.session_state.current_page = nama
        st.rerun()

# Sidebar info card (fixed di bawah)
render_sidebar_info(TANGGAL_ACUAN)

# ─── Render halaman terpilih ────────────────────────────────
page = st.session_state.current_page
if page == "Dashboard":
    dashboard.render()
elif page == "Detail Wilayah":
    detail_wilayah.render()
elif page == "Prediksi & Analisis":
    prediksi_analisis.render()
elif page == "Edukasi & Insight":
    edukasi_insight.render()

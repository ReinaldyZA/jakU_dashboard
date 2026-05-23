"""Custom CSS untuk dashboard JakU, di-inject di app.py."""

CSS = """
<style>
    /* ───────── Reset & font ───────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0F172A;
    }

    .stApp {
        background: #F8FAFC;
    }

    /* Hilangkan toolbar Streamlit default */
    header[data-testid="stHeader"] { background: transparent; }
    .stDeployButton { display: none; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }

    /* ───────── Main container ───────── */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* ───────── Sidebar ───────── */
    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 0.5rem;
    }

    .sidebar-logo {
        padding: 24px 24px 20px 24px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .sidebar-logo-icon {
        width: 44px; height: 44px;
        background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px; font-weight: 800; color: white;
        font-family: 'Plus Jakarta Sans', sans-serif;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }
    .sidebar-logo-text h1 {
        margin: 0; padding: 0;
        font-size: 22px; font-weight: 800;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #0F172A; line-height: 1;
    }
    .sidebar-logo-text p {
        margin: 4px 0 0 0;
        font-size: 11px; color: #64748B; font-weight: 500;
    }

    /* Sidebar nav buttons (overide Streamlit button) */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: transparent;
        border: none;
        color: #475569;
        font-size: 14px;
        font-weight: 500;
        text-align: left;
        padding: 12px 24px;
        border-radius: 0;
        margin: 2px 0;
        transition: all 0.15s ease;
        border-left: 3px solid transparent;
        justify-content: flex-start;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #F1F5F9;
        color: #0F172A;
    }
    section[data-testid="stSidebar"] .stButton > button:focus {
        box-shadow: none;
        outline: none;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #DCFCE7;
        color: #16A34A;
        font-weight: 600;
        border-left: 3px solid #22C55E;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: #BBF7D0;
        color: #15803D;
    }

    .sidebar-info-card {
        margin: 24px 16px;
        padding: 16px;
        background: #F0F9FF;
        border-radius: 12px;
        border-left: 3px solid #2563EB;
    }
    .sidebar-info-card h4 {
        margin: 0 0 6px 0;
        font-size: 13px;
        font-weight: 700;
        color: #1E40AF;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .sidebar-info-card p {
        margin: 0;
        font-size: 11px;
        color: #475569;
        line-height: 1.5;
    }
    .sidebar-info-card .updated {
        margin-top: 14px;
        padding-top: 12px;
        border-top: 1px solid #DBEAFE;
        font-size: 10px;
        color: #64748B;
    }
    .sidebar-info-card .updated b {
        display: block;
        color: #0F172A;
        font-size: 11px;
        margin-top: 2px;
    }

    /* ───────── Page header ───────── */
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 28px;
        flex-wrap: wrap;
        gap: 16px;
    }
    .page-title {
        margin: 0 0 6px 0;
        font-size: 32px;
        font-weight: 700;
        color: #0F172A;
        font-family: 'Plus Jakarta Sans', sans-serif;
        letter-spacing: -0.5px;
    }
    .page-subtitle {
        margin: 0;
        font-size: 14px;
        color: #64748B;
        font-weight: 400;
    }
    .header-meta {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 10px 16px;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        font-size: 12px;
        color: #64748B;
    }
    .header-meta b {
        color: #0F172A;
        font-weight: 600;
        font-size: 13px;
    }

    /* ───────── Cards ───────── */
    .card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 1px 2px rgba(15, 23, 42, 0.03);
        border: 1px solid #F1F5F9;
        margin-bottom: 16px;
    }
    .card-title {
        font-size: 16px;
        font-weight: 700;
        color: #0F172A;
        margin: 0 0 16px 0;
        font-family: 'Plus Jakarta Sans', sans-serif;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .info-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 16px; height: 16px;
        border-radius: 50%;
        background: #E2E8F0;
        color: #64748B;
        font-size: 10px;
        font-weight: 700;
    }

    /* ───────── ISPU big number ───────── */
    .ispu-hero {
        display: flex;
        align-items: center;
        gap: 24px;
        padding: 12px 0;
    }
    .ispu-number {
        font-size: 72px;
        font-weight: 800;
        line-height: 1;
        font-family: 'Plus Jakarta Sans', sans-serif;
        letter-spacing: -3px;
    }
    .ispu-status {
        font-size: 28px;
        font-weight: 700;
        font-family: 'Plus Jakarta Sans', sans-serif;
        margin-bottom: 4px;
    }
    .ispu-subtext {
        font-size: 13px;
        color: #64748B;
        max-width: 280px;
        line-height: 1.5;
    }
    .ispu-label {
        font-size: 12px;
        color: #64748B;
        font-weight: 600;
        margin-top: 4px;
        letter-spacing: 1px;
    }
    .ispu-dominant {
        margin-top: 12px;
        padding: 8px 12px;
        background: #F1F5F9;
        border-radius: 8px;
        font-size: 12px;
        color: #475569;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .ispu-dominant b { color: #0F172A; font-weight: 700; }

    /* ───────── Polutan chip grid ───────── */
    .pol-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 12px;
        margin-top: 4px;
    }
    .pol-chip {
        text-align: center;
    }
    .pol-chip .pol-name {
        font-size: 12px;
        color: #64748B;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .pol-chip .pol-val {
        font-size: 22px;
        font-weight: 800;
        color: #0F172A;
        font-family: 'Plus Jakarta Sans', sans-serif;
        line-height: 1;
    }
    .pol-chip .pol-unit {
        font-size: 11px;
        color: #94A3B8;
        margin-top: 2px;
    }
    .pol-chip .pol-bar {
        height: 4px;
        border-radius: 2px;
        margin-top: 8px;
        background: #E2E8F0;
        overflow: hidden;
    }
    .pol-chip .pol-bar > div {
        height: 100%;
        border-radius: 2px;
    }

    /* ───────── Wilayah list (map-side) ───────── */
    .wilayah-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 12px;
        border-radius: 10px;
        margin-bottom: 6px;
        transition: background 0.15s;
    }
    .wilayah-row:hover { background: #F8FAFC; }
    .wilayah-name {
        font-size: 13px;
        font-weight: 500;
        color: #334155;
    }
    .wilayah-badge {
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 700;
        color: white;
        font-family: 'Plus Jakarta Sans', sans-serif;
        min-width: 44px;
        text-align: center;
    }

    /* ───────── Tab area (wilayah / prediksi tabs) ───────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #FFFFFF;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #F1F5F9;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 8px 18px;
        font-size: 14px;
        font-weight: 500;
        color: #64748B;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: #EFF6FF !important;
        color: #2563EB !important;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-highlight"] { background: transparent !important; }
    .stTabs [data-baseweb="tab-border"] { background: transparent !important; }

    /* ───────── Rekomendasi card ───────── */
    .rec-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 18px;
        border: 1px solid #F1F5F9;
        display: flex;
        gap: 16px;
        align-items: flex-start;
        height: 100%;
    }
    .rec-icon {
        width: 56px; height: 56px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 28px;
        flex-shrink: 0;
    }
    .rec-content h4 {
        margin: 0 0 4px 0;
        font-size: 14px;
        font-weight: 600;
        color: #0F172A;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .rec-status {
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .rec-desc {
        font-size: 12px;
        color: #64748B;
        line-height: 1.5;
        margin: 0;
    }

    /* ───────── Edukasi kategori cards ───────── */
    .edu-cat-row {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 12px;
        margin-top: 4px;
    }
    .edu-cat-card {
        padding: 18px;
        border-radius: 14px;
        text-align: left;
        position: relative;
        min-height: 130px;
    }
    .edu-cat-card .range {
        font-size: 18px;
        font-weight: 800;
        font-family: 'Plus Jakarta Sans', sans-serif;
        margin-bottom: 2px;
    }
    .edu-cat-card .nama {
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 12px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .edu-cat-card .desc {
        font-size: 12px;
        color: #475569;
        line-height: 1.5;
    }
    .edu-cat-card .emoji {
        position: absolute;
        top: 18px; right: 18px;
        font-size: 32px;
    }

    /* ───────── Insight footer (Prediksi page) ───────── */
    .insight-strip {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 14px;
        padding: 16px 24px;
        margin-top: 16px;
        display: grid;
        grid-template-columns: auto 1fr 1fr 1fr;
        gap: 24px;
        align-items: center;
    }
    .insight-strip h4 {
        font-size: 13px;
        font-weight: 700;
        margin: 0 0 2px 0;
        color: #15803D;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .insight-strip p {
        font-size: 12px;
        color: #475569;
        margin: 0;
        line-height: 1.4;
    }
    .insight-icon {
        font-size: 26px;
    }
    .insight-title {
        font-size: 14px;
        font-weight: 700;
        color: #15803D;
        font-family: 'Plus Jakarta Sans', sans-serif;
        margin-right: 12px;
    }

    /* ───────── Footer pita hijau (Edukasi) ───────── */
    .green-banner {
        background: linear-gradient(90deg, #DCFCE7 0%, #F0FDF4 100%);
        border-radius: 16px;
        padding: 20px 28px;
        margin-top: 16px;
        display: flex; align-items: center; gap: 16px;
        border: 1px solid #BBF7D0;
    }
    .green-banner-icon {
        font-size: 32px;
    }
    .green-banner h3 {
        margin: 0 0 4px 0;
        font-size: 16px;
        font-weight: 700;
        color: #15803D;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .green-banner p {
        margin: 0;
        font-size: 13px;
        color: #475569;
    }

    /* ───────── Misc ───────── */
    .stRadio > div { gap: 6px; }
    .stRadio > div > label > div:first-child { display: none; }
    .stRadio > div > label {
        padding: 8px 16px;
        background: #F1F5F9;
        border-radius: 10px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 500;
        transition: all 0.15s;
    }
    .stRadio > div > label:has(input:checked) {
        background: #DBEAFE;
        color: #2563EB;
        font-weight: 600;
    }

    /* Hide checkbox label dots */
    label[data-baseweb="checkbox"] > div:first-child {
        margin-right: 8px;
    }

    /* Sembunyikan label radio asli */
    [role="radiogroup"] > label > div:first-child { display: none !important; }

    /* Select widget */
    .stSelectbox > div > div {
        border-radius: 10px;
        border-color: #E2E8F0;
    }

    /* Number input (untuk prediksi interaktif) */
    .stNumberInput > div > div > input {
        border-radius: 10px;
    }

    /* Hilangkan jarak div di columns */
    [data-testid="stHorizontalBlock"] > div {
        padding-right: 0;
    }
</style>
"""

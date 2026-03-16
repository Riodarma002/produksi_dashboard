"""
Dashboard Monitoring Rio — Main Entry Point
Sidebar = analysis pages. JO toggle at top of each page.
"""
import streamlit as st

from state import clear_cache
from ui.theme import inject_theme
from backend.sync_manager import sync_manager

# Start background sync thread (runs behind visual)
sync_manager.start_sync()

st.set_page_config(
    page_title="Dashboard Monitoring Production",
    page_icon="📊",
    layout="wide",
)

inject_theme()

# ── Navigation Setup ──────────────────────────────────────────
pg_summary = st.Page("pages/summary.py", title="Summary", icon="📊")
pg_production = st.Page("pages/production.py", title="Dashboard", icon="🎛️", default=True)

# Hide default sidebar nav so we can put our logo at the very top!
nav = st.navigation([pg_summary, pg_production], position="hidden")

# ── Custom Sidebar Layout ──────────────────────────────────────
with st.sidebar:
    # 1. Logo (Centered with columns)
    _l, _m, _r = st.columns([1, 2.5, 1])
    with _m:
        st.image("logo_mge.png", use_container_width=True)
    
    # Brand Name
    st.markdown(
        '<div style="font-size:13px;font-weight:700;color:#0f172a;letter-spacing:0.5px;text-align:center;margin-bottom:24px;margin-top:-8px;">'
        'PT. MEGA GLOBAL ENERGY'
        '</div>',
        unsafe_allow_html=True,
    )

    # 2. Section Header
    st.markdown(
        '<div style="padding:0 12px;margin-bottom:8px;">'
        '<div style="font-size:11px;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;">'
        'DASHBOARD PRODUKSI'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # 3. Navigation Links (Summary first, then Dashboard)
    st.page_link(pg_summary, label="Summary", icon="📊")
    st.page_link(pg_production, label="Produksi", icon="🎛️")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        clear_cache()
        st.rerun()

nav.run()

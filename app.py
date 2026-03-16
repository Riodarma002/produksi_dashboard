"""
Dashboard Monitoring Rio — Main Entry Point
Sidebar = analysis pages. JO toggle at top of each page.
"""
import streamlit as st

from state import clear_cache
from ui.theme import inject_theme
from backend.sync_manager import sync_manager
from streamlit_autorefresh import st_autorefresh

# Start background sync thread (runs behind visual)
sync_manager.start_sync()

st.set_page_config(
    page_title="Dashboard Monitoring Production",
    page_icon="logo_mge.png",
    layout="wide",
)

# Auto-refresh the entire application every 1 hour (3600000 ms) 
# to fetch the latest background sync data without manual refresh.
st_autorefresh(interval=3600000, key="global_hourly_refresh")

inject_theme()

# ── Navigation Setup ──────────────────────────────────────────
pg_summary = st.Page("pages/summary.py", title="Summary")
pg_production = st.Page("pages/production.py", title="Dashboard", default=True)

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
    # Convert PNGs to base64 for CSS injection
    import os
    import base64
    def get_base64_of_bin_file(bin_file):
        if os.path.exists(bin_file):
            with open(bin_file, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        return ""

    summary_icon_b64 = get_base64_of_bin_file("summary.png")
    prod_icon_b64 = get_base64_of_bin_file("mining-truck.png")

    st.markdown(f"""
    <style>
    /* Custom icons for page links */
    a[data-testid="stPageLink-NavLink"] {{
        position: relative !important;
        padding-left: 36px !important;
    }}
    a[data-testid="stPageLink-NavLink"] p {{
        margin-left: 0 !important;
    }}
    
    /* Target the Summary link by matching the 'Summary' in its href */
    a[data-testid="stPageLink-NavLink"][href*="ummary" i]::before {{
        content: ""; background-image: url("data:image/png;base64,{summary_icon_b64}");
        position: absolute; left: 16px; top: 50%; transform: translateY(-50%);
        width: 18px; height: 18px; background-size: contain; background-repeat: no-repeat;
    }}
    
    /* Target the Produksi link. Since it is default=True, its href might be "/" or "/Dashboard" */
    a[data-testid="stPageLink-NavLink"][href*="ashboard" i]::before,
    a[data-testid="stPageLink-NavLink"][href*="roduksi" i]::before,
    a[data-testid="stPageLink-NavLink"][href="/"]::before,
    a[data-testid="stPageLink-NavLink"][href=""]::before {{
        content: ""; background-image: url("data:image/png;base64,{prod_icon_b64}");
        position: absolute; left: 16px; top: 50%; transform: translateY(-50%);
        width: 18px; height: 18px; background-size: contain; background-repeat: no-repeat;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.page_link(pg_summary, label="Summary")
    st.page_link(pg_production, label="Produksi")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        clear_cache()
        st.rerun()

nav.run()

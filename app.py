"""
Dashboard Monitoring Rio — Main Entry Point
Sidebar = analysis pages. JO toggle at top of each page.
"""
import streamlit as st

from state import clear_cache
from ui.theme import inject_theme
from backend.sync_manager import sync_manager
from ui.sidebar_components import render_refresh_section, render_section_header
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
        padding-right: 12px !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
        margin: 4px 0 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
    }}

    /* Default state - subtle gray */
    a[data-testid="stPageLink-NavLink"] {{
        background-color: #f8fafc !important;
        color: #64748b !important;
    }}

    a[data-testid="stPageLink-NavLink"] p {{
        margin-left: 0 !important;
        color: inherit !important;
    }}

    /* HOVER state - green (for non-active pages) */
    a[data-testid="stPageLink-NavLink"]:not([data-testid="stPageLink-NavLink"][data-active="true"]):hover {{
        background-color: #dcfce7 !important;
        color: #16a34a !important;
        border-left: 3px solid #22c55e !important;
        transform: translateX(2px) !important;
    }}

    a[data-testid="stPageLink-NavLink"]:not([data-testid="stPageLink-NavLink"][data-active="true"]):hover p {{
        color: #16a34a !important;
    }}

    /* SELECTED/ACTIVE state - stronger green (PERMANENT) */
    [data-testid="stPageLink-NavLink"][data-active="true"],
    a[data-testid="stPageLink-NavLink"].active,
    .stPageLink-NavLink.active {{
        background-color: #bbf7d0 !important;
        color: #15803d !important;
        border-left: 3px solid #22c55e !important;
        font-weight: 600 !important;
    }}

    [data-testid="stPageLink-NavLink"][data-active="true"] p,
    a[data-testid="stPageLink-NavLink"].active p,
    .stPageLink-NavLink.active p {{
        color: #15803d !important;
        font-weight: 600 !important;
    }}

    /* Make sure active state overrides hover */
    [data-testid="stPageLink-NavLink"][data-active="true"]:hover,
    a[data-testid="stPageLink-NavLink"].active:hover {{
        background-color: #bbf7d0 !important;
        color: #15803d !important;
        border-left: 3px solid #22c55e !important;
        transform: none !important;
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

    /* Active page icons - slightly larger */
    [data-testid="stPageLink-NavLink"][data-active="true"]::before,
    a[data-testid="stPageLink-NavLink"].active::before {{
        transform: translateY(-50%) scale(1.1) !important;
    }}

    /* Hover icons for non-active pages */
    a[data-testid="stPageLink-NavLink"]:not([data-active="true"]):hover::before {{
        transform: translateY(-50%) scale(1.1) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.page_link(pg_summary, label="Summary")
    st.page_link(pg_production, label="Produksi")

    # Clean divider
    st.markdown(
        """
        <div style="
            height: 1px;
            background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
            margin: 20px 0;
        "></div>
        """,
        unsafe_allow_html=True
    )

    # Section header for refresh
    render_section_header("DATA CONTROL", "🔄")

    # Clean refresh section
    render_refresh_section()

    # Info section
    st.markdown(
        """
        <div style="
            padding: 12px;
            background: #f0f9ff;
            border-left: 3px solid #3b82f6;
            border-radius: 6px;
            margin: 12px 0;
        ">
            <div style="
                font-size: 11px;
                color: #0369a1;
                font-weight: 500;
                margin-bottom: 4px;
            ">💡 Info</div>
            <div style="
                font-size: 10px;
                color: #075985;
                line-height: 1.4;
            ">Data auto-sync setiap 1 jam. Klik refresh untuk update segera.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

nav.run()

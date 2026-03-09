"""
UI Theme — Global CSS injection for professional dashboard styling.
Modern minimalist design with clean cards, typography, and subtle shadows.
"""
import streamlit as st


def inject_theme():
    """Inject global CSS theme into the Streamlit app."""
    st.markdown("""
    <style>
    /* ── Google Font ──────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global Reset ────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Page Background & Layout ────────────────────── */
    .stApp {
        background: #f5f6f8;
    }
    .stMainBlockContainer {
        padding-top: 0.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* ── Hide default Streamlit chrome ────────────────── */
    #MainMenu, footer { visibility: hidden; }
    .stDeployButton { display: none !important; }
    div[data-testid="stStatusWidget"] { display: none !important; }
    header[data-testid="stHeader"] {
        background: transparent !important;
        backdrop-filter: none !important;
    }

    /* ── Sidebar ─────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #eef0f4;
        padding-top: 0 !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0.5rem !important;
    }

    /* Sidebar nav links (using st.page_link) */
    section[data-testid="stSidebar"] a {
        text-decoration: none !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"] {
        border-radius: 8px !important;
        margin: 2px 12px !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #64748b !important;
        transition: all 0.15s ease !important;
        background: transparent !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"] p {
        color: #64748b !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"]:hover {
        background: #f8fafc !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"]:hover p {
        color: #0f172a !important;
    }
    
    /* Active Link (AlphaLabs style) */
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"][data-test-active="true"] {
        background: #eff6ff !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"][data-test-active="true"] p {
        color: #2563eb !important;
        font-weight: 600 !important;
    }

    /* Sidebar section headers */
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        color: #94a3b8 !important;
        padding: 16px 12px 8px 16px !important;
        margin-top: 8px !important;
    }

    /* Sidebar toggle → burger ☰ */
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="collapsedControl"],
    button[data-testid="baseButton-headerNoPadding"],
    [data-testid="collapsedControl"],
    section[data-testid="stSidebar"] > div:first-child > button {
        background: #ffffff !important;
        border: 1px solid #eef0f4 !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        width: 36px !important;
        height: 36px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: hidden !important;
        font-size: 0 !important;
        color: transparent !important;
    }
    button[data-testid="stSidebarCollapseButton"] *,
    button[data-testid="collapsedControl"] *,
    button[data-testid="baseButton-headerNoPadding"] *,
    [data-testid="collapsedControl"] *,
    section[data-testid="stSidebar"] > div:first-child > button * {
        display: none !important;
    }
    button[data-testid="stSidebarCollapseButton"]::after,
    button[data-testid="collapsedControl"]::after,
    button[data-testid="baseButton-headerNoPadding"]::after,
    [data-testid="collapsedControl"]::after,
    section[data-testid="stSidebar"] > div:first-child > button::after {
        content: '☰' !important;
        font-size: 18px !important;
        color: #1a1f36 !important;
        font-weight: 600 !important;
        display: block !important;
        visibility: visible !important;
    }

    /* ── Header Layout ───────────────────────────────── */
    .header-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }
    .page-title {
        font-size: 20px;
        font-weight: 700;
        color: #1a1f36;
        margin-bottom: 0;
        line-height: 1.3;
    }
    .page-subtitle {
        font-size: 13px;
        color: #8b95a5;
        margin-bottom: 6px;
    }
    .clock-badge {
        font-size: 11px;
        font-weight: 500;
        color: #6b7280;
        background: #fff;
        border: 1px solid #eef0f4;
        border-radius: 8px;
        padding: 4px 10px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        white-space: nowrap;
    }

    .kpi-value { font-size: 32px; }
    .kpi-title { font-size: 13px; }
    .kpi-badge { font-size: 16px; padding: 4px 12px !important; }
    .stock-val { font-size: 20px; }
    .stock-label { font-size: 11px; }
    .stock-icon { font-size: 16px; }

    /* ── Segmented Control (JO Toggle) ───────────────── */
    div[data-testid="stSegmentedControl"] button {
        border-radius: 10px !important;
        font-weight: 500 !important;
        font-size: 13px !important;
    }

    /* ── Chart container ─────────────────────────────── */
    .stPlotlyChart {
        background: #ffffff;
        border: 1px solid #eef0f4;
        border-radius: 14px;
        padding: 12px 8px 4px 8px;
    }

    /* ══════════════════════════════════════════════════
       MOBILE RESPONSIVE  (≤ 768px)
       ══════════════════════════════════════════════════ */
    /* ══════════════════════════════════════════════════
       MOBILE RESPONSIVE  (≤ 768px)
       ══════════════════════════════════════════════════ */
    @media (max-width: 768px) {
        .stMainBlockContainer {
            padding-top: 0.25rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }

        /* Tighter gaps for stacked columns */
        div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }

        /* Force Streamlit columns to stack vertically */
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 0.5rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }

        /* ── Header ── */
        .header-row {
            flex-direction: column;
            align-items: flex-start;
            gap: 2px;
        }
        .page-title    { font-size: 14px !important; }
        .page-subtitle { font-size: 9px  !important; margin-bottom: 4px !important; }
        .clock-badge   { font-size: 8px  !important; padding: 2px 6px !important; }

        /* ── KPI cards ── */
        .kpi-value { font-size: 18px !important; }
        .kpi-title { font-size: 9px  !important; }
        .kpi-badge { font-size: 12px  !important; padding: 2px 8px !important; }

        /* ── Stock cards ── */
        .stock-val   { font-size: 15px !important; }
        .stock-label { font-size: 8px  !important; }
        .stock-icon  { font-size: 12px !important; width: 24px !important; height: 24px !important; min-width: 24px !important; }

        /* ── Production cards: 4-col → 2-col grid ── */
        .prod-cards-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 10px !important;
        }
        .prod-card { padding: 10px !important; }
        .prod-actual-value { font-size: 18px !important; }
        .prod-name { font-size: 10px !important; }

        /* ── Summary JO columns: stack to 1-col ── */
        .summary-jo-grid {
            grid-template-columns: 1fr !important;
            gap: 12px !important;
        }

        /* ── Plotly charts: reduce height ── */
        .stPlotlyChart {
            border-radius: 10px !important;
            padding: 4px !important;
        }
        .stPlotlyChart iframe {
            max-height: 280px !important;
        }

        /* ── Chart section title ── */
        .section-title { font-size: 12px !important; }

        /* ── Segmented control: horizontal scroll on mobile ── */
        div[data-testid="stSegmentedControl"] {
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            overflow-y: hidden !important;
            -webkit-overflow-scrolling: touch; /* smooth scrolling */
            gap: 4px !important;
            padding-bottom: 4px; /* for scrollbar */
        }
        div[data-testid="stSegmentedControl"]::-webkit-scrollbar {
            height: 2px;
        }
        div[data-testid="stSegmentedControl"]::-webkit-scrollbar-thumb {
            background-color: #cbd5e1;
            border-radius: 2px;
        }
        div[data-testid="stSegmentedControl"] button {
            font-size: 11px !important;
            padding: 6px 14px !important;
            flex: 0 0 auto !important; /* prevent shrinking */
            white-space: nowrap !important;
        }

        /* ── Aggressively Hide Streamlit Header & Toolbar ── */
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stAppDeployButton"],
        .stAppDeployButton,
        [data-testid="stStatusWidget"],
        #MainMenu, 
        header, 
        .stActionButton {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            width: 0 !important;
        }

        /* ── Fix alignment: compensate for sidebar arrow >> ── */
        .stAppViewBlockContainer {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }

        /* ── Tighter vertical spacing globally ── */
        .block-container {
            padding-top: 2rem !important;
        }

        /* ── Tables ── */
        .stDataFrame { font-size: 10px !important; }
    }

    </style>
    """, unsafe_allow_html=True)

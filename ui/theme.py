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
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700;800&display=swap');

    /* NUCLEAR RESET for absolute flush layout */
    html, body, .stApp, 
    [data-testid="stAppViewBlockContainer"], 
    [data-testid="stAppViewMain"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    .stMainBlockContainer, 
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        top: 0 !important;
        transform: none !important;
    }
    
    /* Force html and body to be exactly 0,0 */
    html, body {
        width: 100%;
        height: 100%;
        overflow-x: hidden;
    }
    
    /* SURGICAL HEADER FLUSH: Completely vanish native header content while keeping the container container interactive */
    header, 
    .stAppHeader,
    [data-testid="stAppHeader"] {
        background: none !important;
        background-color: transparent !important;
        background-image: none !important;
        border: none !important;
        box-shadow: none !important;
        height: 0 !important;
        min-height: 0 !important;
        overflow: visible !important;
        padding: 0 !important;
        margin: 0 !important;
        z-index: 100 !important; /* Low z-index for the container */
        pointer-events: none !important; /* Let clicks pass through */
    }
    
    /* Specifically target the native header bar to be invisible but NOT display:none as it contains the toggle */
    [data-testid="stHeader"] {
        background-color: transparent !important;
        background-image: none !important;
        height: 0 !important;
        overflow: visible !important;
        z-index: 100 !important;
        pointer-events: none !important;
    }
    
    /* Hide the decoration bar at the very top */
    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* Target the sidebar transition/collapse buttons specifically to STAY ON TOP and ACTIVE */
    [data-testid="stSidebarCollapseButton"], 
    [data-testid="collapsedControl"],
    button[aria-label="Expand sidebar"],
    button[aria-label="Collapse sidebar"],
    button[data-testid="stSidebarCollapse"],
    .st-emotion-cache-1qx64mb {
        background: #ffffff !important;
        color: #64748b !important;
        z-index: 9999999999 !important; /* Absolute top */
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 12px !important; /* Moved to top corner */
        left: 12px !important;
        pointer-events: auto !important; /* Force interactive */
        cursor: pointer !important;
        width: 36px !important;
        height: 36px !important;
        border-radius: 8px !important;
        border: 1px solid #eef2f6 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        align-items: center !important;
        justify-content: center !important;
    }
    /* Ensure the icon inside is also visible */
    [data-testid="stSidebarCollapseButton"] svg,
    .st-emotion-cache-1qx64mb svg,
    button[data-testid="stSidebarCollapse"] svg {
        display: block !important;
        fill: #64748b !important;
        color: #64748b !important;
        width: 20px !important;
        height: 20px !important;
    }
    .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-top: 0 !important; /* Content starts at absolute top */
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
        margin-top: 0 !important;
    }

    /* ── Hide default Streamlit chrome ────────────────── */
    #MainMenu, 
    [data-testid="stHeaderOptionsMenu"],
    footer { 
        display: none !important; 
        visibility: hidden !important; 
    }
    /* Hide Deploy button using various selectors found in Streamlit versions */
    .stDeployButton, 
    [data-testid="stAppHeader"] > div:last-child { 
        display: none !important; 
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    div[data-testid="stStatusWidget"] { display: none !important; }
    
    /* Hide the top decoration bar */
    [data-testid="stDecoration"] { 
        display: none !important; 
        height: 0 !important;
    } 
    
    /* Do NOT hide the entire header if it causes the toggle to disappear */
    /* Instead, make its components invisible */
    .stApp > header {
        background: transparent !important;
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
    /* ── Sidebar Active & Hover States (MGE Green Theme) ── */
    
    /* 1. Base link style */
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"] {
        border-radius: 8px !important;
        margin: 2px 12px !important;
        padding: 8px 12px !important;
        transition: all 0.2s ease !important;
        background-color: transparent !important;
    }

    /* 2. Hover state - Light Green */
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"]:hover {
        background-color: #f0fdf4 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"]:hover p {
        color: #16a34a !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"]:hover span[data-testid="stIcon"] {
        color: #16a34a !important;
    }

    /* 3. ACTIVE/SELECTED STATE - MGE Green */
    /* We target multiple possible selector patterns to ensure it works across Streamlit versions */
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"]:has(a[aria-current="page"]),
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"]:has(a[class*="active"]),
    section[data-testid="stSidebar"] a[aria-current="page"] div[data-testid="stPageLink-NavLink"],
    section[data-testid="stSidebar"] a[aria-current="page"] {
        background-color: #16a34a !important;
        background: #16a34a !important;
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.2) !important;
    }

    /* Active text & icon color */
    section[data-testid="stSidebar"] a[aria-current="page"] p,
    section[data-testid="stSidebar"] a[aria-current="page"] span[data-testid="stIcon"],
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"]:has(a[aria-current="page"]) p,
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"]:has(a[aria-current="page"]) span[data-testid="stIcon"] {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Handle images/icons if they are using img tags */
    section[data-testid="stSidebar"] a[aria-current="page"] img,
    section[data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"]:has(a[aria-current="page"]) img {
        filter: brightness(0) invert(1) !important;
    }

    /* Remove any default Streamlit active backgrounds that might leak */
    section[data-testid="stSidebar"] a:focus,
    section[data-testid="stSidebar"] a:active {
        outline: none !important;
        box-shadow: none !important;
    }

    /* Sidebar section headers */
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {
        font-size: clamp(10px, 0.8vw, 12px) !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        color: #94a3b8 !important;
        padding: 16px 12px 8px 16px !important;
        margin-top: 8px !important;
    }


    /* ── Dashboard Header (Fixed at the absolute top) ───────────────── */
    .white-header-bg {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100vw !important; /* Force full viewport width */
        z-index: 1000 !important; /* Lower than sidebar toggles */
        background: transparent !important; 
        backdrop-filter: none !important;
        border-bottom: none !important;
        padding: 0 2rem 0 60px !important; /* Increased left padding to clear arrow */
        margin: 0 !important;
        box-shadow: none !important;
        height: 60px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transform: translateZ(0) !important;
        pointer-events: none !important; /* Allows clicks to go through to elements behind/below this container */
    }
    
    /* Re-enable pointer events for the controls INSIDE the header */
    .white-header-bg > div,
    .white-header-bg button,
    .white-header-bg [data-testid="stSegmentedControl"] {
        pointer-events: auto !important;
    }
    
    /* Center all internal columns and blocks to exactly 60px height */
    .white-header-bg [data-testid="column"],
    .white-header-bg [data-testid="stHorizontalBlock"],
    .white-header-bg [data-testid="stVerticalBlock"],
    .white-header-bg [data-testid="stVerticalBlock"] > div {
        height: 60px !important;
        display: flex !important;
        align-items: center !important;
        margin: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
    }
    
    /* Specific overrides for widgets inside the header to remove padding/margins */
    .white-header-bg div[data-testid="stDateInput"],
    .white-header-bg div[data-testid="stSegmentedControl"],
    .white-header-bg div.stButton {
        margin: 0 !important;
        padding: 0 !important;
    }

    .white-header-bg [data-testid="stWidgetLabel"] {
        display: none !important; /* Hide labels if any exist to maintain vertical centering */
    }
    
    .dash-title {
        font-size: clamp(20px, 2.5vw, 32px) !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: normal !important;
        letter-spacing: -0.5px !important;
    }
    


    /* Force all widgets in header to have exact 40px content height for perfect alignment */
    .white-header-bg button,
    .white-header-bg div[data-testid="stDateInput"] input,
    .white-header-bg div[data-testid="stSegmentedControl"],
    .white-header-bg .stButton button {
        height: 40px !important;
        min-height: 40px !important;
        line-height: normal !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Target the wrapping div of widgets to prevent any offset */
    .white-header-bg [data-testid="stWidgetLabel"] {
        display: none !important;
    }
    
    .white-header-bg div[data-testid="stDateInput"] {
        margin-top: -8px !important; /* Increased nudge to force it up */
        transform: translateY(-2px) !important; /* Additional fine-tuning nudge */
        display: flex !important;
        align-items: center !important;
    }

    /* Align button text content properly */
    .white-header-bg button p {
        margin: 0 !important;
        line-height: 1 !important;
        display: flex !important;
        align-items: center !important;
    }
    /* ── MODERN UNDERLINE TABS: ABSOLUTE OVERRIDE ── */
    /* This block targets ALL segmented controls with extreme priority */
    /* ── MODERN UNDERLINE TABS: GLOBAL CLEAN DESIGN ── */
    div[data-testid="stSegmentedControl"],
    div[data-baseweb="segmented-control"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 46px !important;
    }

    div[data-testid="stSegmentedControl"] button,
    div[data-baseweb="segmented-control"] button {
        background: transparent !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        height: 44px !important;
        margin: 0 !important;
        padding: 4px 16px !important;
        color: #64748b !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
        flex: 1 !important;
    }

    /* Active State: Bold Green Text + Underline */
    div[data-testid="stSegmentedControl"] button[aria-checked="true"],
    div[data-baseweb="segmented-control"] button[aria-checked="true"] {
        background: transparent !important;
        border-bottom: 3px solid #16a34a !important;
        color: #16a34a !important;
    }

    div[data-testid="stSegmentedControl"] button[aria-checked="true"] p,
    div[data-baseweb="segmented-control"] button[aria-checked="true"] p {
        color: #16a34a !important;
        font-weight: 700 !important;
    }

    div[data-testid="stSegmentedControl"] button:hover:not([aria-checked="true"]) {
        background: rgba(22, 163, 74, 0.05) !important;
        color: #1e293b !important;
    }

    /* Kill standard boxes */
    div[data-testid="stSegmentedControl"] button div,
    div[data-baseweb="segmented-control"] button div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: inherit !important;
    }
    .header-title {
        color: #1e293b;
        font-size: clamp(22px, 3vw, 36px) !important;
        font-weight: 800 !important;
        letter-spacing: -0.8px !important;
        margin: 0 !important;
        line-height: 1.1 !important;
    }
    .header-subtitle {
        color: #3b82f6;
        font-size: clamp(9px, 0.8vw, 13px) !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        margin-bottom: 2px !important;
    }
    .header-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
    }
    .page-title {
        font-size: clamp(16px, 1.8vw, 24px);
        font-weight: 700;
        color: #1a1f36;
        margin-bottom: 0;
        line-height: 1.3;
    }
    .page-subtitle {
        font-size: clamp(11px, 1.2vw, 15px);
        color: #8b95a5;
        margin-bottom: 6px;
    }
    .clock-badge {
        font-size: clamp(9px, 1vw, 13px);
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

    /* KPI styling handled in components */
    .stock-val { font-size: 20px; }
    .stock-label { font-size: 11px; }
    .stock-icon { font-size: 16px; }

    /* ── Segmented Control (JO Toggle) ───────────────── */
    /* Handled by pill styles above */

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
            padding-top: 4rem !important;
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
        .page-title    { font-size: 18px !important; }
        .page-subtitle { font-size: 12px  !important; margin-bottom: 4px !important; }
        .clock-badge   { font-size: 11px  !important; padding: 2px 8px !important; }

        /* ── KPI cards ── */
        .kpi-value { font-size: 28px !important; }
        .kpi-title { font-size: 13px !important; }
        .kpi-badge { font-size: 14px !important; padding: 4px 10px !important; }

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
        [data-testid="stAppDeployButton"],
        .stAppDeployButton,
        [data-testid="stStatusWidget"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            width: 0 !important;
        }

        /* ── Force Header Visibility ── */
        [data-testid="stHeader"] {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            height: auto !important;
            z-index: 999999 !important;
            background: transparent !important;
        }

        /* ── Show Sidebar Toggle (Hamburger Menu) ── */
        [data-testid="collapsedControl"],
        [data-testid="collapsedControl"] button,
        [data-testid="collapsedControl"] svg {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            height: auto !important;
            width: auto !important;
            color: #0f172a !important; /* Ensure it's legible against light bg */
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

        /* ── Force Plotly Internal Text to Scale Down on Mobile ── */
        .js-plotly-plot .main-svg text,
        .js-plotly-plot .main-svg .annotation-text,
        .js-plotly-plot .main-svg .annotation-text b,
        .js-plotly-plot .main-svg .xtick text,
        .js-plotly-plot .main-svg .ytick text,
        .js-plotly-plot .main-svg .g-gtitle text,
        .js-plotly-plot .main-svg .g-xtitle text,
        .js-plotly-plot .main-svg .g-ytitle text {
            font-size: 10px !important;
        }
        /* Extra small for dense point labels */
        .js-plotly-plot .main-svg .textpoint text {
            font-size: 8px !important;
        }
        /* Summary text at the top of charts */
        .js-plotly-plot .main-svg .annotation-text span {
            font-size: 9px !important;
        }
    }

    </style>
    """, unsafe_allow_html=True)

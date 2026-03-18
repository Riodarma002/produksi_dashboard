"""
CSS Styles — Matching code.html Design
Rubik font, color palette, card styling, animations.
"""
import streamlit as st


def inject_css():
    """Inject custom CSS to transform Streamlit into a modern dashboard."""
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
    <style>
        /* ── Reset & Base ─────────────────────────────── */
        #MainMenu, footer { visibility: hidden; }
        
        .block-container {
            padding-top: 3.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 100% !important;
        }
        
        .stApp {
            background-color: #f6f7f8;
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
            -webkit-font-smoothing: antialiased;
            overflow-y: hidden;
        }
        
        /* Hide the main page scrollbar */
        section.main > div:first-child {
            overflow-y: hidden !important;
        }

        /* ── Sidebar ──────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #f0f0f0;
            width: 260px !important;
        }
        section[data-testid="stSidebar"] .block-container {
            padding: 1.5rem 1rem !important;
        }
        
        /* ── Main Content Area ────────────────────────── */
        .main .block-container {
            padding: 0.5rem 2rem 2rem 2rem !important;
        }

        /* ── Dashboard Header ─────────────────────────── */
        .dash-header {
            background: #ffffff;
            border-bottom: 1px solid #f0f0f0;
            padding: 1.25rem 2rem;
            margin: -0.5rem -2rem 1.5rem -2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .dash-header h1 {
            font-size: 1.25rem;
            font-weight: 700;
            color: #2D3748;
            margin: 0;
        }
        .dash-header .subtitle {
            font-size: 0.75rem;
            color: #718096;
            margin-top: 2px;
        }

        /* ── Stock Summary Cards (Top Row) ────────────── */
        .stock-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 1.75rem 2rem;
            border: 1px solid #f0f0f0;
            box-shadow: 0 2px 15px -3px rgba(0,0,0,0.03);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: box-shadow 0.3s ease;
        }
        .stock-card:hover {
            box-shadow: 0 8px 30px -4px rgba(0,0,0,0.05);
        }
        .stock-icon {
            width: 32px; height: 32px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 18px;
        }
        .stock-label {
            font-size: 0.8rem; font-weight: 600; color: #718096;
            text-transform: uppercase; letter-spacing: 0.05em;
        }
        .stock-value {
            font-size: 2.25rem; font-weight: 700; color: #2D3748;
            line-height: 1.2;
        }
        .stock-unit {
            font-size: 0.875rem; font-weight: 500; color: #718096;
            margin-left: 8px;
        }
        .stock-badge {
            display: inline-flex; align-items: center;
            padding: 4px 10px; border-radius: 9999px;
            font-size: 0.75rem; font-weight: 500;
        }
        .badge-green {
            background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0;
        }
        .badge-red {
            background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca;
        }

        /* ── Production Operation Cards ───────────────── */
        .prod-card {
            background: #ffffff;
            border-radius: 12px;
            border: 1px solid #f0f0f0;
            box-shadow: 0 2px 10px -3px rgba(0,0,0,0.02);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: all 0.3s ease;
            position: relative;
            height: 100%;
        }
        .prod-card:hover {
            box-shadow: 0 8px 30px -4px rgba(0,0,0,0.04);
        }
        .prod-body {
            padding: 1.5rem 1.5rem 0.75rem;
            flex: 1;
        }
        .prod-header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.25rem;
            padding-right: 48px;
        }
        .prod-dot {
            width: 8px; height: 8px; border-radius: 50%;
            display: inline-block; margin-right: 8px;
        }
        .prod-name {
            font-size: 0.875rem; font-weight: 600; color: #2D3748;
        }
        .prod-unit-badge {
            font-size: 0.7rem; font-weight: 500;
            padding: 3px 8px; background: #f8f9fa; color: #718096;
            border: 1px solid #f0f0f0; border-radius: 4px;
        }
        .prod-actual-label {
            font-size: 0.7rem; color: #718096;
            text-transform: uppercase; letter-spacing: 0.05em;
            font-weight: 500; margin-bottom: 4px;
        }
        .prod-actual-value {
            font-size: 1.75rem; font-weight: 700; color: #2D3748;
            letter-spacing: -0.02em;
        }
        .prod-plan-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #fafafa;
            padding-bottom: 4px;
            margin: 12px 0 4px;
        }
        .prod-plan-label {
            font-size: 0.7rem; color: #718096;
            text-transform: uppercase; letter-spacing: 0.05em;
            font-weight: 500;
        }
        .prod-plan-value {
            font-size: 1rem; font-weight: 700; color: #64748b; /* Increased size, weight and slightly darker color */
        }
        
        /* Progress Bar */
        .progress-track {
            width: 100%; background: #f0f0f0;
            border-radius: 9999px; height: 6px;
            margin-top: 8px; overflow: hidden;
        }
        .progress-fill {
            height: 100%; border-radius: 9999px;
            transition: width 0.6s ease;
        }
        
        /* Achievement Badge (absolute positioned) */
        .ach-badge {
            position: absolute; top: 16px; right: 16px;
        }
        .ach-ring {
            width: 48px; height: 48px; border-radius: 50%;
            border: 4px solid #f0f0f0; position: relative;
            display: flex; align-items: center; justify-content: center;
        }
        .ach-ring-text {
            font-size: 10px; font-weight: 700; color: #718096;
        }
        .ach-pill {
            display: inline-flex; align-items: center;
            padding: 5px 12px; border-radius: 9999px;
            font-size: 0.9rem; font-weight: 800; /* Increased font size & weight */
        }
        
        /* Card Footer */
        .prod-footer {
            border-top: 1px solid #fafafa;
            background: rgba(248,249,250,0.3);
            padding: 12px 1.5rem;
            display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
            margin-top: auto;
        }
        .footer-label {
            font-size: 10px; color: #718096;
            text-transform: uppercase; letter-spacing: 0.05em;
            font-weight: 600;
        }
        .footer-value {
            font-size: 0.875rem; font-weight: 600; color: #2D3748;
            margin-top: 2px;
        }
        .footer-delta {
            font-size: 10px; font-weight: 500;
            display: flex; align-items: center; gap: 2px;
            margin-top: 2px;
        }

        /* ── Bottom Info Cards ────────────────────────── */
        .info-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            border: 1px solid #f0f0f0;
            display: flex; align-items: center; gap: 16px;
        }
        .info-card-gradient {
            background: linear-gradient(135deg, rgba(19,127,236,0.05), #ffffff);
        }
        .info-icon {
            width: 48px; height: 48px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
        }

        /* ── Modern Date Picker Style ─────────────────── */
        /* Target the actual input field container inside the date widget */
        div[data-testid="stDateInput"] > div > div {
            background-color: #ffffff !important;
            border: 1px solid #e1e5e9 !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
        }

        /* Hover effect */
        div[data-testid="stDateInput"] > div > div:hover {
            border-color: #cbd5e1 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04) !important;
        }

        /* Focus effect */
        div[data-testid="stDateInput"] > div > div:focus-within {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
        }

        /* Styling the text/value inside the date picker */
        div[data-testid="stDateInput"] input {
            color: #334155 !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            padding: 0.5rem 0.75rem !important;
        }

        /* ── Utility ──────────────────────────────────── */
        .section-title {
            font-size: 1.1rem; font-weight: 700; color: #2D3748;
        }
        .hidden { display: none; }
        
        /* Hide Streamlit elements */
        div[data-testid="stDecoration"] { display: none; }
        div.stDeployButton { display: none; }
        
        /* ── Unified Plotly Chart Container ───────────────── */
        .stPlotlyChart {
            background: #ffffff !important;
            border-radius: 12px !important;
            border: 1px solid #f0f0f0 !important;
            box-shadow: 0 2px 10px -3px rgba(0,0,0,0.02) !important;
            padding: 8px !important;
            margin-bottom: 0.5rem !important;
        }
        
    </style>
    """, unsafe_allow_html=True)

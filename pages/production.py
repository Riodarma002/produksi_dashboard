"""
Production Page — OB + CH + CT with JO toggle at top.
Auto-rotates between JOs every 15 seconds. Pauses on user interaction.
"""
import datetime
import time
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

import sys
import os
from pathlib import Path

# Add project root to sys.path so Streamlit Cloud can find our modules
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from state import init_data, get_input_values, render_date_selector, get_valid_dates
from config import PIT_REGISTRY, OP_HOURS
from calculations.production import (
    filter_data, get_plan_values, calc_actuals,
    calc_achievements, calc_stripping_ratio, calc_global_stripping_ratio, calc_coal_stock,
)
from ui.kpi_cards import render_all_metrics
from ui.charts import render_production_charts
from ui.raw_tables import render_raw_tables, render_plan_tables

sheets = init_data()
input_values = get_input_values()

pit_names = list(PIT_REGISTRY.keys())
ROTATE_INTERVAL_MS = 15_000  # 15 seconds

# ── Session state init ────────────────────────────────────────
# ── Session state init ────────────────────────────────────────
if "jo_idx" not in st.session_state:
    st.session_state.jo_idx = 0
if "jo_toggle" not in st.session_state:
    st.session_state.jo_toggle = pit_names[0] if pit_names else "N/A"
if "prev_auto_count" not in st.session_state:
    st.session_state.prev_auto_count = 0
if "user_interact_time" not in st.session_state:
    st.session_state.user_interact_time = 0.0
if "auto_play" not in st.session_state:
    st.session_state.auto_play = True

# ── Auto-refresh timer (invisible, triggers every 15s) ────────
# If auto_play is False, we set interval to something very large or 0 to "stop" it.
# st_autorefresh doesn't support disabling easily, so we use a very large interval.
curr_interval = ROTATE_INTERVAL_MS if st.session_state.auto_play else 9999999
auto_count = st_autorefresh(interval=curr_interval, key="auto_rotate")

# Detect: was this rerun triggered by the auto-refresh timer?
is_auto = auto_count != st.session_state.prev_auto_count
st.session_state.prev_auto_count = auto_count

# If auto-refresh AND user has been idle for >10s (leave margin for lag) → advance JO
idle_seconds = time.time() - st.session_state.user_interact_time
if is_auto and idle_seconds > 10 and st.session_state.auto_play:
    st.session_state.jo_idx = (st.session_state.jo_idx + 1) % len(pit_names)
    st.session_state.jo_toggle = pit_names[st.session_state.jo_idx]
    st.session_state.jo_toggle_final_fix = st.session_state.jo_toggle
# ── Header Updates & Logic ──────────────────────────
# 1. State & Date Range Initialization


# 2. Logic for display
date_range = st.session_state.get("prod_date")
if not date_range or not isinstance(date_range, (list, tuple)) or len(date_range) < 2:
    # Use fallback calculated from data if session state is missing or incomplete
    valid_dates = get_valid_dates(sheets)
    default_date = valid_dates[-1].date() if valid_dates else datetime.date.today()
    date_range = (default_date, default_date)

start_date, end_date = date_range
display_jo = st.session_state.get("jo_toggle", pit_names[0])
formatted_date = datetime.date.today().strftime("%A, %d %B %Y")
formatted_time = time.strftime("%H:%M")

# 3. Filtering Logic (Must be before header to show freshness)
selected_pit = st.session_state.get("jo_toggle", pit_names[0])
filtered = filter_data(sheets, (start_date, end_date), selected_pit)

# Find freshness - Get last hour with actual data
actual_hours = set()
for df_key in ["ob_f", "ch_f", "ct_f"]:
    if not filtered[df_key].empty and "Hour LU" in filtered[df_key].columns:
        actual_hours.update(filtered[df_key]["Hour LU"].unique())

last_h = None
last_h_display = None
if actual_hours:
    # Filter only valid operational hours and find the last one
    valid_hours = [h for h in actual_hours if h in OP_HOURS]
    if valid_hours:
        # Get the index of last hour in OP_HOURS order
        indices = [OP_HOURS.index(h) for h in valid_hours]
        last_h = OP_HOURS[max(indices)]

        # Convert hour to readable format (e.g., "O5" -> "05:00", "11" -> "11:00")
        if last_h.startswith("O"):
            # After midnight hours (O0-O5)
            hour_num = last_h[1:]  # Remove "O" prefix
            last_h_display = f"{hour_num}:00"
        else:
            # Daytime hours (06-23)
            last_h_display = f"{last_h}:00"

# Calculate latest date from filtered data
latest_date_val = None
for df_key in ["ob_f", "ch_f", "ct_f"]:
    if not filtered[df_key].empty and "Date" in filtered[df_key].columns:
        df_latest = pd.to_datetime(filtered[df_key]["Date"]).max()
        if latest_date_val is None or df_latest > latest_date_val:
            latest_date_val = df_latest

# Format last update string with day, date, and time
if latest_date_val is not None:
    day_name = latest_date_val.strftime('%A')
    day_map = {
        'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
        'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
    }
    indo_day = day_map.get(day_name, day_name)
    date_str = latest_date_val.strftime('%d/%m/%Y')

    if last_h_display is not None:
        # Format: "Senin, 15 Maret 2026 • Jam 11:00"
        month_indo = latest_date_val.strftime('%m')
        month_map = {
            '01': 'Januari', '02': 'Februari', '03': 'Maret', '04': 'April',
            '05': 'Mei', '06': 'Juni', '07': 'Juli', '08': 'Agustus',
            '09': 'September', '10': 'Oktober', '11': 'November', '12': 'Desember'
        }
        month_name = month_map.get(month_indo, month_indo)
        date_str_readable = f"{latest_date_val.day} {month_name} {latest_date_val.year}"
        last_input_str = f"{indo_day}, {date_str_readable} • Jam {last_h_display}"
    else:
        # Only date, no hour data
        last_input_str = f"{indo_day}, {date_str} • Data belum lengkap"
else:
    # No date data at all
    last_input_str = "Belum ada data"

# 4. Dashboard Header Row (Fixed via CSS)
st.markdown('<div class="white-header-bg">', unsafe_allow_html=True)
# Ensure ALL columns are vertically aligned to the bottom
h_col1, h_col2, h_col3, h_col4 = st.columns([1.5, 2.2, 1.1, 0.4], vertical_alignment="bottom", gap="small")

with h_col1:
    st.markdown(f'''
    <div style="padding:4px 0;">
        <h1 class="dash-title" style="margin:0; font-size:22px; font-weight:700; color:#0f172a;">Dashboard Produksi</h1>
        <div style="font-size:12px; color:#64748b; margin-top:8px; font-weight:500; display:flex; align-items:center; gap:10px;">
            <span>Area: <strong style="color:#0f172a; font-size:13px;">{display_jo}</strong></span>
            <span style="background:linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); color:#0369a1; padding:6px 12px; border-radius:8px; border:1px solid #bae6fd; font-weight:600; font-size:11px; display:inline-flex; align-items:center; gap:6px; box-shadow:0 1px 3px rgba(14,165,233,0.1);">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                {last_input_str}
            </span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with h_col2:
    # THE MENU (CENTERED)
    selected_pit_new = st.segmented_control(
        "PIT", pit_names,
        label_visibility="collapsed",
        key="jo_toggle_final_fix"
    )
    
    # CSS: Aggressive Force Alignment and Underline Style
    st.markdown("""
    <style>
    /* 1. Global Column Alignment - Force vertical alignment to bottom */
    [data-testid="column"] {
        display: flex !important;
        align-items: flex-end !important; /* Changed from center to flex-end */
        height: 64px !important;
        padding-bottom: 4px !important; /* Small padding at bottom */
    }
    
    [data-testid="stHorizontalBlock"] > div:nth-child(1) { justify-content: flex-start !important; align-items: flex-start !important; }
    [data-testid="stHorizontalBlock"] > div:nth-child(2) { justify-content: center !important; }
    [data-testid="stHorizontalBlock"] > div:nth-child(3) { justify-content: flex-end !important; }
    [data-testid="stHorizontalBlock"] > div:nth-child(4) { justify-content: flex-end !important; }

    /* 2. COMPLETELY STRIP SEGMENTED CONTROL BOXES */
    div[data-testid="stSegmentedControl"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        margin: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
    }

    /* Target the actual buttons inside segmented control more specifically */
    div[data-testid="stSegmentedControl"] [data-testid="stBaseButton-secondary"],
    div[data-testid="stSegmentedControl"] button {
        background: transparent !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        border-radius: 0 !important;
        height: 36px !important; /* Reduced height to sit lower */
        margin: 0 !important;
        padding: 0 20px !important;
        color: #64748b !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
        width: auto !important;
        display: flex !important;
        align-items: flex-end !important; /* Text aligns to bottom */
        padding-bottom: 6px !important;
    }

    /* The Active state - Forced Underline */
    div[data-testid="stSegmentedControl"] [aria-checked="true"],
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background: transparent !important;
        border-bottom: 3px solid #16a34a !important; /* MGE Green Underline */
        color: #16a34a !important;
        font-weight: 700 !important;
    }

    /* 3. Date Input and Other Widgets Alignment */
    div[data-testid="stDateInput"] {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Target the container of the date input to push it down */
    div[data-testid="stDateInput"] > div {
        min-height: 36px !important;
    }
    
    /* Play/pause button adjustment */
    [data-testid="stButton"] button {
        height: 36px !important;
        min-height: 36px !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        display: flex !important;
        align-items: center !important;
        white-space: nowrap !important;
        min-width: 90px !important;
    }
    
    [data-testid="stButton"] button p {
        white-space: nowrap !important;
        margin: 0 !important;
    }

    /* Title specifically - remove gaps */
    .dash-title {
        margin: 0 !important;
        padding: 0 !important;
        line-height: normal !important;
    }
    </style>
    """, unsafe_allow_html=True)

with h_col3:
    date_range = render_date_selector(sheets, key="prod_date", show_label=False)

with h_col4:
    # Play/Pause Toggle with Text Labels
    if st.session_state.auto_play:
        label = "⏸️ Pause"
    else:
        label = "▶️ Play"
        
    if st.button(label, help="Klik untuk Jeda/Lanjut Rotasi Otomatis", use_container_width=False):
        st.session_state.auto_play = not st.session_state.auto_play
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ── Spacing ─────────────────────────────────────
st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

# ── Interaction Logic ──────────────────────────
if selected_pit_new and selected_pit_new != selected_pit:
    st.session_state.jo_idx = pit_names.index(selected_pit_new)
    st.session_state.jo_toggle = selected_pit_new
    st.session_state.user_interact_time = time.time()
    st.rerun()

if "prev_date" not in st.session_state:
    st.session_state.prev_date = date_range
if date_range != st.session_state.prev_date:
    st.session_state.user_interact_time = time.time()
    st.session_state.prev_date = date_range
    st.rerun()

# ── Calculations ──────────────────────────────────────────────
plans = get_plan_values(sheets, selected_pit)
actuals = calc_actuals(filtered)
achievements = calc_achievements(actuals, plans)
sr = calc_stripping_ratio(actuals)
stock = calc_coal_stock(sheets, date_range, input_values)

# ── KPI Metrics ───────────────────────────────────────────────
render_all_metrics(plans, actuals, achievements, plans["has_ct"], sr, stock)

# ── Charts ────────────────────────────────────────────────────
cumm_pit = sheets["cumm_plan"][sheets["cumm_plan"]["PIT"] == selected_pit].copy()
render_production_charts(
    filtered["ob_f"], filtered["ch_f"], cumm_pit,
    plans["plan_ob"], plans["plan_ch"],
    rain_f=filtered["rain_f"]
)



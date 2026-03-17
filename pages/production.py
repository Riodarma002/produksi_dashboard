"""
Production Page — Clean Simple Design
OB + CH + CT with JO toggle at top.
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

# Import logger for error tracking
from utils.logger import get_logger
logger = get_logger("production")

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
ROTATE_INTERVAL_MS = 25_000  # 25 seconds

# ── Session state init ────────────────────────────────────────
if "jo_idx" not in st.session_state:
    st.session_state.jo_idx = 0
if "jo_toggle" not in st.session_state:
    st.session_state.jo_toggle = pit_names[0] if pit_names else "N/A"
if "prev_auto_count" not in st.session_state:
    st.session_state.prev_auto_count = -1
if "user_interact_time" not in st.session_state:
    st.session_state.user_interact_time = 0.0
if "auto_play" not in st.session_state:
    st.session_state.auto_play = True

# ── Auto-refresh timer (invisible, triggers every 25s) ────────
curr_interval = ROTATE_INTERVAL_MS if st.session_state.auto_play else 9999999
auto_count = st_autorefresh(interval=curr_interval, key="auto_rotate")

# Detect: was this rerun triggered by the auto-refresh timer?
is_auto = auto_count != st.session_state.prev_auto_count
st.session_state.prev_auto_count = auto_count

# If auto-refresh AND user has been idle for >10s (leave margin for lag) → advance JO
idle_seconds = time.time() - st.session_state.user_interact_time
if is_auto and idle_seconds > 10 and st.session_state.auto_play and len(pit_names) > 0:
    st.session_state.jo_idx = (st.session_state.jo_idx + 1) % len(pit_names)
    st.session_state.jo_toggle = pit_names[st.session_state.jo_idx]
    st.session_state.jo_toggle_final_fix = st.session_state.jo_toggle
    logger.debug(f"Auto-rotated to PIT: {st.session_state.jo_toggle} (idle: {idle_seconds:.1f}s)")

# ── Header Updates & Logic ──────────────────────────
# 1. State & Date Range Initialization
date_range = st.session_state.get("prod_date")

# Get valid dates from fresh data
valid_dates = get_valid_dates(sheets)

# Error handling for empty data
if not valid_dates:
    st.error("❌ **Tidak ada data tersedia**")
    st.info("💡 Silakan klik tombol **Refresh Data** di sidebar untuk memuat data terbaru.")
    logger.error("No valid dates found in data sheets")
    st.stop()

# Get the latest available date
latest_available_date = valid_dates[-1].date()

# Smart date range selection:
# 1. If no date_range in session state → use latest
# 2. If date_range exists but is BEFORE latest available → auto-update to latest
# 3. If date_range exists and is valid → keep user's selection
if not date_range or not isinstance(date_range, (list, tuple)) or len(date_range) < 2:
    date_range = (latest_available_date, latest_available_date)
    logger.info(f"Using default date: {latest_available_date}")
else:
    # Check if current selection is outdated
    current_end = date_range[1] if isinstance(date_range[1], datetime.date) else date_range[0]
    if current_end < latest_available_date:
        # Auto-update to latest date if data is newer
        date_range = (latest_available_date, latest_available_date)
        st.session_state.prod_date = date_range
        logger.info(f"Auto-updated date from {current_end} to {latest_available_date}")
        st.toast(f"📅 Data baru tersedia! Tanggal diupdate ke {latest_available_date}", icon="ℹ️")

start_date, end_date = date_range
display_jo = st.session_state.get("jo_toggle", pit_names[0])

# 2. Logic for display
# 3. Filtering Logic (Must be before header to show freshness)
selected_pit = st.session_state.get("jo_toggle", pit_names[0])
filtered = filter_data(sheets, (start_date, end_date), selected_pit)

# Find freshness - Get last hour with actual data (>0 volume)
actual_hours = set()
for df_key in ["ob_f", "ch_f", "ct_f"]:
    df = filtered[df_key]
    if not df.empty and "Hour LU" in df.columns:
        # Check all possible value columns
        value_cols = ["Volume", "Netto", "Production"]
        has_val_mask = pd.Series(False, index=df.index)
        for c in value_cols:
            if c in df.columns:
                has_val_mask = has_val_mask | (pd.to_numeric(df[c], errors="coerce").fillna(0) > 0)

        valid_df = df[has_val_mask]
        if not valid_df.empty:
            actual_hours.update(valid_df["Hour LU"].unique())

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

# ── Simple Header Layout ────────────────────────────────────────
# Header with simple native Streamlit components
st.markdown("### Dashboard Produksi")

# Info row
col_info, col_pit, col_controls = st.columns([2, 3.5, 0.5], gap="small", vertical_alignment="center")

with col_info:
    st.markdown(f"""
    <div style="display: flex; gap: 0.75rem; align-items: center;">
        <div style="background: #f1f5f9; padding: 0.5rem 1rem; border-radius: 0.5rem; border: 1px solid #e2e8f0; font-size: 0.875rem; font-weight: 600; color: #475569;">
            Area: <strong>{display_jo}</strong>
        </div>
        <div style="background: #e0f2fe; padding: 0.5rem 1rem; border-radius: 0.5rem; border: 1px solid #bae6fd; font-size: 0.8125rem; font-weight: 600; color: #0369a1;">
            {last_input_str}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_pit:
    selected_pit_new = st.segmented_control(
        label="PIT",
        options=pit_names,
        label_visibility="collapsed",
        key="jo_toggle_final_fix"
    )

with col_controls:
    play_pause = st.button(
        "⏸️ Pause" if st.session_state.auto_play else "▶️ Play",
        help="Jeda/Lanjutkan rotasi otomatis",
        use_container_width=True
    )

# Minimal spacing
st.markdown("  ")  # Small spacing instead of divider

# ── Interaction Logic ──────────────────────────
if selected_pit_new and selected_pit_new != selected_pit:
    st.session_state.jo_idx = pit_names.index(selected_pit_new)
    st.session_state.jo_toggle = selected_pit_new
    st.session_state.user_interact_time = time.time()
    logger.info(f"User switched to PIT: {selected_pit_new}")
    st.rerun()

if play_pause:
    st.session_state.auto_play = not st.session_state.auto_play
    status = "PLAY" if st.session_state.auto_play else "PAUSE"
    logger.info(f"User clicked {status} button")
    st.rerun()

if "prev_date" not in st.session_state:
    st.session_state.prev_date = date_range
if date_range != st.session_state.prev_date:
    st.session_state.user_interact_time = time.time()
    st.session_state.prev_date = date_range
    logger.info(f"Date range changed to: {date_range[0]} - {date_range[1]}")
    st.rerun()

# ── Calculations ──────────────────────────────────────────────
try:
    plans = get_plan_values(sheets, selected_pit)
    actuals = calc_actuals(filtered)
    achievements = calc_achievements(actuals, plans)
    sr = calc_stripping_ratio(actuals)
    stock = calc_coal_stock(sheets, date_range, input_values)

    logger.info(f"Calculations completed for PIT: {selected_pit}")
except Exception as e:
    logger.error(f"Calculation error for PIT {selected_pit}: {e}", exc_info=True)
    st.error(f"❌ **Terjadi kesalahan dalam perhitungan:** {str(e)}")
    st.info("💡 Silakan coba refresh data atau pilih PIT yang lain.")
    st.stop()

# ── KPI Metrics ───────────────────────────────────────────────
render_all_metrics(plans, actuals, achievements, plans["has_ct"], sr, stock)

# ── Charts ────────────────────────────────────────────────────
cumm_pit = sheets["cumm_plan"][sheets["cumm_plan"]["PIT"] == selected_pit].copy()
render_production_charts(
    filtered["ob_f"], filtered["ch_f"], cumm_pit,
    plans["plan_ob"], plans["plan_ch"],
    rain_f=filtered["rain_f"]
)


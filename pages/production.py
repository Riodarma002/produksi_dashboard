"""
Production Page — OB + CH + CT with JO toggle at top.
Auto-rotates between JOs every 15 seconds. Pauses on user interaction.
"""
import time
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from state import init_data, get_input_values, render_date_selector
from config import PIT_REGISTRY
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
ROTATE_INTERVAL_MS = 30_000  # 30 seconds

# ── Session state init ────────────────────────────────────────
if "jo_idx" not in st.session_state:
    st.session_state.jo_idx = 0
    st.session_state.jo_toggle = pit_names[0]  # init widget value via session state
if "prev_auto_count" not in st.session_state:
    st.session_state.prev_auto_count = 0
if "user_interact_time" not in st.session_state:
    st.session_state.user_interact_time = 0.0

# ── Auto-refresh timer (invisible, triggers every 15s) ────────
auto_count = st_autorefresh(interval=ROTATE_INTERVAL_MS, key="auto_rotate")

# Detect: was this rerun triggered by the auto-refresh timer?
is_auto = auto_count != st.session_state.prev_auto_count
st.session_state.prev_auto_count = auto_count

# If auto-refresh AND user has been idle for >30s → advance JO
idle_seconds = time.time() - st.session_state.user_interact_time
if is_auto and idle_seconds > 30:
    st.session_state.jo_idx = (st.session_state.jo_idx + 1) % len(pit_names)
    st.session_state.jo_toggle = pit_names[st.session_state.jo_idx]

# ── Top Bar: JO toggle + Date selector ────────────────────────
top_left, top_right = st.columns([3, 1])
with top_left:
    selected_pit = st.segmented_control(
        "JO",
        pit_names,
        label_visibility="collapsed",
        key="jo_toggle",
    )
with top_right:
    date_range = render_date_selector(sheets, key="prod_date")
    start_date, end_date = date_range

if selected_pit is None:
    selected_pit = pit_names[0]

# Detect user manual click: if widget value differs from auto index
widget_idx = pit_names.index(selected_pit)
if not is_auto and widget_idx != st.session_state.jo_idx:
    # User clicked a different JO → mark interaction, pause auto-rotate
    st.session_state.jo_idx = widget_idx
    st.session_state.user_interact_time = time.time()

# Also detect any date change as user interaction
if "prev_date" not in st.session_state:
    st.session_state.prev_date = date_range
if date_range != st.session_state.prev_date:
    st.session_state.user_interact_time = time.time()
    st.session_state.prev_date = date_range

# ── Header with live time ─────────────────────────────────────
from datetime import datetime, timezone, timedelta
WITA = timezone(timedelta(hours=8))
now_wita = datetime.now(WITA)

HARI = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']
BULAN = ['','Januari','Februari','Maret','April','Mei','Juni',
         'Juli','Agustus','September','Oktober','November','Desember']
clock_str = f"{HARI[now_wita.weekday()]}, {now_wita.day} {BULAN[now_wita.month]} {now_wita.year} • {now_wita.strftime('%H:%M:%S')} WITA"

if start_date == end_date:
    date_str = pd.Timestamp(start_date).strftime('%d %B %Y')
else:
    date_str = f"{pd.Timestamp(start_date).strftime('%d %b')} – {pd.Timestamp(end_date).strftime('%d %b %Y')}"

st.markdown(
    f'<div class="header-row">'
    f'<div class="page-title">Production Dashboard — {selected_pit}</div>'
    f'<div class="clock-badge">'
    f'<span style="color:#10b981;">●</span> {clock_str}</div>'
    f'</div>'
    f'<div class="page-subtitle">📅 {date_str} &nbsp;•&nbsp; Real-time insights</div>',
    unsafe_allow_html=True,
)

# ── Calculations ──────────────────────────────────────────────
filtered = filter_data(sheets, date_range, selected_pit)
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
)



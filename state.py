"""
State Manager — Shared data loading & session state across pages.
Loads data once and caches it so page switches don't re-download.
"""
import pandas as pd
import streamlit as st

from backend.data_loader import load_data, extract_sheets, normalize_dataframes, parse_input_plan


import os
from config import CACHE_FILE

def init_data() -> dict:
    """
    Load, extract, normalize and cache all data.
    Automatically reloads if the background sync manager has updated the cache file.
    """
    mtime = 0
    if os.path.exists(CACHE_FILE):
        mtime = os.path.getmtime(CACHE_FILE)
        
    if "sheets" not in st.session_state or st.session_state.get("cache_mtime") != mtime:
        data = load_data()
        
        # Check if the returned data is already the processed 'cached' dict
        if isinstance(data, dict) and "sheets" in data:
            st.session_state["sheets"] = data["sheets"]
            st.session_state["input_values"] = data["input_values"]
        else:
            # Fallback for raw data (sync fetch)
            sheets = extract_sheets(data)
            normalize_dataframes(sheets)
            st.session_state["sheets"] = sheets
            st.session_state["input_values"] = parse_input_plan(sheets["input_plan"])
            
        st.session_state["cache_mtime"] = mtime
        
        # VERY IMPORTANT: If we just updated the data in the background, 
        # force a full rerun so the UI instantly draws the new numbers without manual refresh
        st.rerun()
            
    return st.session_state["sheets"]


def get_input_values() -> dict:
    """Get parsed input values (opening_rom, opening_port, plan_barging)."""
    if "input_values" not in st.session_state:
        init_data()
    return st.session_state["input_values"]


def get_valid_dates(sheets: dict):
    """Get sorted list of valid dates from prod_ob."""
    dates = sheets["prod_ob"]["Date"].dropna()
    dates = dates[dates.dt.year > 2000].unique()
    return sorted(dates)


def render_date_selector(sheets: dict, key: str, show_label: bool = True) -> tuple:
    """Render date selector at top of page. Returns (start_date, end_date) tuple."""
    valid_dates = get_valid_dates(sheets)
    
    # Style only - always injected to ensure icon and border consistency
    st.markdown(
        """
        <style>
        /* BROAD STROKE: Kill every possible default border/shadow/background in the hierarchy */
        div[data-testid="stDateInput"], 
        div[data-testid="stDateInput"] > div,
        div[data-testid="stDateInput"] div[data-baseweb="input"],
        div[data-testid="stDateInput"] div[data-baseweb="base-input"] {
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            background-color: transparent !important;
            background: none !important;
        }
        /* RE-APPLY: Style only the actual input box with our single professional border */
        div[data-testid="stDateInput"] input {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' height='16' viewBox='0 -960 960 960' width='16' fill='%2364748b'%3E%3Cpath d='M200-80q-33 0-56.5-23.5T120-160v-560q0-33 23.5-56.5T200-800h40v-80h80v80h320v-80h80v80h40q33 0 56.5 23.5T840-720v560q0-33-23.5-56.5T760-80H200Zm0-80h560v-400H200v400Zm0-480h560v-80H200v80Zm0 0v-80 80Z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: 12px center;
            padding-left: 36px !important;
            border-radius: 8px !important;
            border: 1px solid #eef0f4 !important; /* Matches pill borders */
            font-size: 13px !important;
            font-weight: 500 !important;
            color: #475569 !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
            transition: all 0.2s ease;
            height: 40px !important;
            background-color: #ffffff !important;
        }
        div[data-testid="stDateInput"] input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
        }
        /* Constrain width */
        div[data-testid="stDateInput"] {
            min-width: 200px !important;
            max-width: 220px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    if show_label:
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:6px; margin-bottom:6px;">
              <span style="font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:1px;">Date Range</span>
              <span title="Filter production by date" style="cursor:help; font-size:12px; color:#94a3b8;">ⓘ</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    today = pd.Timestamp.today().date()
    
    if not valid_dates:
        # Fallback if no dates found
        default_date = today
        min_allowed = today
        max_allowed = today
    else:
        # Default to LAST AVAILABLE DATE as requested by user to avoid empty charts
        default_date = valid_dates[-1].date()
        min_allowed = valid_dates[0].date()
        max_allowed = max(today, valid_dates[-1].date())

    # If key already in session state, use it as value to avoid "default value + session state" error
    current_val = st.session_state.get(key)

    # SMART DATE UPDATE: Check if session state date is outdated
    if current_val:
        # Extract the end date from current selection
        if isinstance(current_val, (list, tuple)) and len(current_val) >= 2:
            current_end_date = current_val[1]
        elif isinstance(current_val, (list, tuple)) and len(current_val) == 1:
            current_end_date = current_val[0]
        else:
            current_end_date = current_val

        # Check if current selection is BEFORE the latest available date
        # If yes, auto-update to latest (this fixes the "stuck on old date" issue)
        if current_end_date < default_date:
            widget_value = (default_date, default_date)
            # Update session state to new date
            st.session_state[key] = widget_value
        else:
            # Keep current selection
            if isinstance(current_val, (list, tuple)):
                widget_value = current_val
            else:
                widget_value = (current_val, current_val)
    else:
        # No session state yet, use default
        widget_value = (default_date, default_date)

    date_sel = st.date_input(
        "Date Input",
        value=widget_value,
        min_value=min_allowed,
        max_value=max_allowed,
        format="DD/MM/YYYY",
        key=key,
        label_visibility="collapsed",
    )

    # Handle if user hasn't selected an end date yet (tuple has 1 element)
    if isinstance(date_sel, tuple):
        start_date = date_sel[0]
        end_date = date_sel[1] if len(date_sel) > 1 else start_date
    else:
        start_date = date_sel
        end_date = date_sel

    # Convert to pandas Timestamps for filtering compatibility
    return pd.Timestamp(start_date), pd.Timestamp(end_date)


def clear_cache():
    """Clear all cached data and session state."""
    st.cache_data.clear()
    for key in ["sheets", "input_values"]:
        st.session_state.pop(key, None)

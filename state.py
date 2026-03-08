"""
State Manager — Shared data loading & session state across pages.
Loads data once and caches it so page switches don't re-download.
"""
import pandas as pd
import streamlit as st

from backend.data_loader import load_data, extract_sheets, normalize_dataframes, parse_input_plan


def init_data() -> dict:
    """
    Load, extract, normalize and cache all data.
    Returns the sheets dict. Call this at the top of every page.
    Data is cached via st.cache_data inside load_data().
    """
    if "sheets" not in st.session_state:
        data = load_data()
        sheets = extract_sheets(data)
        normalize_dataframes(sheets)
        st.session_state["sheets"] = sheets
        st.session_state["input_values"] = parse_input_plan(sheets["input_plan"])
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


def render_date_selector(sheets: dict, key: str = "date_select"):
    """Render date selector at top of page. Returns (start_date, end_date) tuple."""
    valid_dates = get_valid_dates(sheets)
    
    if not valid_dates:
        # Fallback if no dates found
        today = pd.Timestamp.today().date()
        date_sel = st.date_input("📅 Rentang Tanggal", value=(today, today), key=key)
    else:
        # Default to the most recent date available
        max_date = valid_dates[-1].date()
        
        # Determine min and max allowed dates based on data
        min_allowed = valid_dates[0].date()
        max_allowed = max_date

        date_sel = st.date_input(
            "📅 Rentang Tanggal",
            value=(max_date, max_date),
            min_value=min_allowed,
            max_value=max_allowed,
            format="DD/MM/YYYY",
            key=key,
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

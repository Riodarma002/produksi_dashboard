"""
Sidebar — Filter controls and input display
"""
import pandas as pd
import streamlit as st

from calculations.formatting import fmt


def render_sidebar(valid_dates, all_pits: list, input_values: dict) -> tuple:
    """
    Render the sidebar with date/PIT selectors and input values.
    Returns (selected_date, selected_pit, refresh_clicked).
    """
    st.sidebar.title("⛏️ Filter")

    # Date selector
    selected_date = st.sidebar.selectbox(
        "Tanggal",
        valid_dates,
        index=len(valid_dates) - 1,
        format_func=lambda x: pd.Timestamp(x).strftime("%d %b %Y"),
    )

    # PIT selector
    default_idx = all_pits.index("North JO IC") if "North JO IC" in all_pits else 0
    selected_pit = st.sidebar.selectbox("PIT", all_pits, index=default_idx)

    # Input values from Excel
    st.sidebar.markdown("---")
    st.sidebar.caption("📦 Input dari Excel (Input_plan)")
    st.sidebar.text(f"Opening ROM   : {fmt(input_values['opening_rom'])} MT")
    st.sidebar.text(f"Opening Port  : {fmt(input_values['opening_port'])} MT")
    st.sidebar.text(f"Plan Barging  : {fmt(input_values['plan_barging'])} MT")

    # Refresh button
    st.sidebar.markdown("---")
    refresh_clicked = st.sidebar.button("🔄 Refresh Data")

    return selected_date, selected_pit, refresh_clicked

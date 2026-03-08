"""
Data Manager — Caching, Loading & State Management
Central hub for data access with automatic caching.
"""
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime

from config import CACHE_TTL_SECONDS
from backend.onedrive import (
    download_excel_from_link,
    download_excel_all_sheets,
    read_local_excel,
)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Loading data from OneDrive...")
def load_data_from_link(share_link: str, sheet_name=0) -> pd.DataFrame | None:
    """Load Excel data from OneDrive link with caching (TTL=5min)."""
    return download_excel_from_link(share_link, sheet_name=sheet_name)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Loading all sheets...")
def load_all_sheets_from_link(share_link: str) -> dict | None:
    """Load ALL sheets from Excel link with caching."""
    return download_excel_all_sheets(share_link)


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_data_from_local(file_path: str, sheet_name=0) -> pd.DataFrame | None:
    """Load Excel from local OneDrive sync folder with caching."""
    return read_local_excel(file_path, sheet_name=sheet_name)


def load_from_upload(uploaded_file) -> pd.DataFrame | None:
    """Load Excel from Streamlit file uploader (no cache — unique per upload)."""
    if uploaded_file is None:
        return None
    try:
        return pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception as e:
        st.error(f"Upload parse error: {e}")
        return None


def generate_dummy_data() -> dict:
    """
    Generate realistic dummy data for dashboard preview.
    Returns dict with all production metrics.
    """
    np.random.seed(42)
    
    return {
        "ob": {
            "plan": 135_000,
            "actual": 124_500,
            "mtd": 2_450_000,
            "ytd": 18_200_000,
            "mtd_delta": 4.2,
            "color": "orange",
        },
        "coal_hauling": {
            "plan": 30_000,
            "actual": 32_800,
            "mtd": 850_400,
            "ytd": 7_120_000,
            "mtd_delta": 1.8,
            "color": "blue",
        },
        "coal_transit": {
            "plan": 30_000,
            "actual": 28_450,
            "mtd": 790_200,
            "ytd": 6_850_000,
            "mtd_delta": -0.5,
            "color": "purple",
        },
        "barging": {
            "plan": 34_000,
            "actual": 35_100,
            "mtd": 920_500,
            "ytd": 8_050_000,
            "mtd_delta": 3.5,
            "color": "teal",
        },
        "stock_rom": {
            "value": 45_200,
            "delta": 2.1,
        },
        "stockpile": {
            "value": 120_500,
            "delta": 1.5,
        },
        "timestamp": datetime.now().strftime("%d %b %Y — %H:%M"),
        "shift": "Shift 1",
    }


def get_data_source_info() -> str:
    """Returns a description of the current data source for UI display."""
    if st.session_state.get("data_source") == "link":
        return "OneDrive Link"
    elif st.session_state.get("data_source") == "local":
        return "Local OneDrive Sync"
    elif st.session_state.get("data_source") == "upload":
        return "Uploaded File"
    return "Demo Data"

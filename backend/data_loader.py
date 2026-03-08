"""
Data Loader — Download, Parse & Normalize Excel Data from OneDrive
"""
import io
import requests
import pandas as pd
import streamlit as st

from config import ONEDRIVE_LINKS, CACHE_TTL_SECONDS


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Downloading data...")
def load_data() -> dict:
    """Download all Excel files from OneDrive and return as dict of sheet dicts."""
    result = {}
    for name, url in ONEDRIVE_LINKS.items():
        dl = url.split("?")[0] + "?download=1"
        r = requests.get(dl, timeout=30, allow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0"})
        result[name] = pd.read_excel(
            io.BytesIO(r.content), sheet_name=None, engine="openpyxl"
        )
    return result


def extract_sheets(data: dict) -> dict:
    """
    Extract and return all individual DataFrames from the loaded data.
    Returns a dict with named keys for each production/plan sheet.
    """
    return {
        "prod_ob": data["db_hourly"]["prod ob"].copy(),
        "prod_ch": data["db_hourly"]["prod ch"].copy(),
        "prod_ct": data["db_hourly"]["prod ct"].copy(),
        "lt_ob": data["db_hourly"]["lt ob"].copy(),
        "lt_coal": data["db_hourly"]["lt coal"].copy(),
        "cumm_plan": data["plan_hourly"]["Cumm Plan Vol"].copy(),
        "plan_h_ob": data["plan_hourly"]["Plan Hourly OB"].copy(),
        "plan_h_ch": data["plan_hourly"]["Plan Hourly CH"].copy(),
        "plan_h_ct": data["plan_hourly"]["Plan Hourly CT"].copy(),
        "input_plan": data["plan_hourly"]["Input_plan"].copy(),
    }


def normalize_dataframes(sheets: dict) -> None:
    """
    Normalize all DataFrames in-place:
    - Parse Date columns to datetime
    - Convert Hour LU to zero-padded string
    - Convert object/time columns to string for Arrow compatibility
    """
    # Fix dates
    for key in ["prod_ob", "prod_ch", "prod_ct", "lt_ob", "lt_coal"]:
        df = sheets[key]
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Normalize Hour LU and object columns
    all_keys = [
        "prod_ob", "prod_ch", "prod_ct", "cumm_plan",
        "lt_ob", "lt_coal", "plan_h_ob", "plan_h_ch", "plan_h_ct",
    ]
    for key in all_keys:
        df = sheets[key]
        if "Hour LU" in df.columns:
            df["Hour LU"] = df["Hour LU"].astype(str).str.strip().str.zfill(2)
        for col in df.columns:
            if df[col].dtype == "object" or str(df[col].dtype).startswith("time"):
                try:
                    df[col] = df[col].astype(str)
                except Exception:
                    pass


def parse_input_plan(input_plan_df: pd.DataFrame) -> dict:
    """
    Parse the Input_plan sheet into a dict of named values.
    Returns dict with keys: opening_rom, opening_port, plan_barging
    """
    lookup = dict(
        zip(
            input_plan_df["NAME"].str.strip().str.upper(),
            input_plan_df["VALUE"],
        )
    )
    return {
        "opening_rom": lookup.get("ROM", 0),
        "opening_port": lookup.get("PORT", 0),
        "plan_barging": lookup.get("PLAN BARGING", 0),
    }

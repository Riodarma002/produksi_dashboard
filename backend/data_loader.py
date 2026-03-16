"""
Data Loader — Download, Parse & Normalize Excel Data from OneDrive
"""
import io
import requests
import pandas as pd
import streamlit as st
import os
import pickle
import logging

from config import ONEDRIVE_LINKS, CACHE_TTL_SECONDS, AZURE_CLIENT_SECRET, CACHE_FILE
from backend.azure_api import download_excel_from_graph

logger = logging.getLogger(__name__)


@st.cache_data(ttl=CACHE_TTL_SECONDS) # Removed show_spinner
def load_data() -> dict:
    """Read data from local cache if available, otherwise fetch synchronously."""
    # 1. Try to read from local cache file
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "rb") as f:
                cached = pickle.load(f)
                # Return the pre-processed sheets directly if they exist
                if "sheets" in cached:
                    return cached
                # Historical compatibility or raw data format
                return cached.get("raw_data", cached)
        except Exception as e:
            logger.error(f"Failed to read cache file: {e}")

    # 2. Fallback to synchronous fetch (first run or cache missing)
    result = {}
    for name, url in ONEDRIVE_LINKS.items():
        if AZURE_CLIENT_SECRET:
            try:
                sheets = download_excel_from_graph(url)
                if sheets:
                    result[name] = sheets
                    continue
            except Exception:
                pass

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

    Supports TWO file formats:
    1. OLD FORMAT: Single sheets (prod ob, prod ch, prod ct, lt ob, lt coal)
    2. NEW FORMAT (2026-03-15): Multiple sheets to combine
       - OB: 4 sheets (Vol OB BDE, Vol OB GPE Utara, Vol OB GPE Selatan, Vol OB MGE)
       - CH: 2 sheets (Vol Hauling North, Vol Hauling South)
       - CT: 1 sheet (Vol Transit North)
       - LT: 2 sheets (LT OB MGE, LT OB BDE)

    Also handles pre-processed data from cache (with 'sheets' key).
    """
    # Check if data is already processed (from cache)
    if "sheets" in data:
        # Return the pre-processed sheets directly
        return data["sheets"]

    # Otherwise, extract from raw Excel data
    db_hourly = data["db_hourly"]
    plan_hourly = data["plan_hourly"]

    # Detect file format by checking sheet names
    sheet_names = db_hourly.keys()
    is_new_format = "Vol OB BDE" in sheet_names or "Vol OB GPE Utara" in sheet_names

    if is_new_format:
        # ========================================================================
        # NEW FORMAT (2026-03-15): Combine multiple sheets
        # ========================================================================

        # 1. Combine all OB sheets (4 sheets)
        ob_sheets = []
        required_ob_cols = ["Date", "Hour LU", "PIT Fix", "Volume"]

        for sheet_name in ["Vol OB BDE", "Vol OB GPE Utara", "Vol OB GPE Selatan", "Vol OB MGE"]:
            if sheet_name in db_hourly:
                df = db_hourly[sheet_name].copy()
                # Keep only required columns + standardize
                if all(col in df.columns for col in required_ob_cols):
                    df_std = df[required_ob_cols].copy()
                    # Normalize PIT names to match PIT_REGISTRY format
                    df_std["PIT Fix"] = df_std["PIT Fix"].astype(str).str.strip().str.upper()
                    # Fix common inconsistencies
                    df_std["PIT Fix"] = df_std["PIT Fix"].replace({
                        "NORTH JO IC": "North JO IC",
                        "NORTH JO GAM": "North JO GAM",
                        "SOUTH JO IC": "South JO IC",
                        "SOUTH JO GAM": "South JO GAM",
                        "NORTH JO I": "North JO IC",  # Handle typo
                        "NORTH JO ICC": "North JO IC",  # Handle typo
                    })
                    ob_sheets.append(df_std)

        prod_ob = pd.concat(ob_sheets, ignore_index=True) if ob_sheets else pd.DataFrame()

        # 2. Combine CH sheets (2 sheets)
        ch_sheets = []
        required_ch_cols = ["Date", "Hour LU", "PIT Fix", "Seam"]

        for sheet_name in ["Vol Hauling North", "Vol Hauling South"]:
            if sheet_name in db_hourly:
                df = db_hourly[sheet_name].copy()

                # Remove spaces from column names to be safe, sometimes Excel has "Netto "
                df.columns = [str(c).strip() for c in df.columns]

                # Clean potential string spaces in value columns before checking them
                for col in ["Netto", "Volume"]:
                    if col in df.columns:
                        # Convert errant spaces to NaN, then 0, then float
                        df[col] = pd.to_numeric(df[col].astype(str).str.strip().replace("", "NaN"), errors="coerce").fillna(0)

                # Check which value column exists
                if "Netto" in df.columns and "Volume" in df.columns:
                    # Both columns exist (Vol Hauling South)
                    # Use Netto but convert it to Volume MT if Volume has empties
                    df["Volume"] = df["Netto"] / 1000
                    value_col = "Volume"
                elif "Netto" in df.columns:
                    # Only Netto exists (old format in kg)
                    df["Volume"] = df["Netto"] / 1000
                    value_col = "Volume"
                elif "Volume" in df.columns:
                    # Only Volume exists (new format in MT)
                    value_col = "Volume"
                else:
                    # No value column, skip this sheet
                    continue

                # Standardize column names
                if all(col in df.columns for col in required_ch_cols + [value_col]):
                    df_std = df[required_ch_cols + [value_col]].copy()

                    # Normalize PIT names - convert to string first if needed
                    df_std["PIT Fix"] = df_std["PIT Fix"].astype(str).str.strip().str.upper()
                    df_std["PIT Fix"] = df_std["PIT Fix"].replace({
                        "NORTH JO IC": "North JO IC",
                        "NORTH JO GAM": "North JO GAM",
                        "SOUTH JO IC": "South JO IC",
                        "SOUTH JO GAM": "South JO GAM",
                    })
                    ch_sheets.append(df_std)

        prod_ch = pd.concat(ch_sheets, ignore_index=True) if ch_sheets else pd.DataFrame()

        # Remove dirty data rows (PIT Fix='NAN', Date=NaT, etc.)
        if not prod_ch.empty:
            # Filter out rows with invalid PIT, Date, or Hour LU
            prod_ch = prod_ch[
                (prod_ch["PIT Fix"].notna()) &
                (prod_ch["PIT Fix"] != "NAN") &
                (prod_ch["PIT Fix"] != "") &
                (prod_ch["Date"].notna()) &
                (prod_ch["Hour LU"].notna())
            ].reset_index(drop=True)

        # 3. CT sheet (single sheet)
        required_ct_cols = ["Date", "Hour LU", "PIT Fix", "Volume"]
        if "Vol Transit North" in db_hourly:
            df = db_hourly["Vol Transit North"].copy()
            if all(col in df.columns for col in required_ct_cols):
                prod_ct = df[required_ct_cols].copy()
                # Normalize PIT names
                prod_ct["PIT Fix"] = prod_ct["PIT Fix"].astype(str).str.strip().str.upper()
                prod_ct["PIT Fix"] = prod_ct["PIT Fix"].replace({
                    "NORTH JO IC": "North JO IC",
                    "NORTH JO GAM": "North JO GAM",
                    "SOUTH JO IC": "South JO IC",
                    "SOUTH JO GAM": "South JO GAM",
                })
            else:
                prod_ct = pd.DataFrame()
        else:
            prod_ct = pd.DataFrame()

        # 4. Combine LT OB sheets (2 sheets)
        lt_sheets = []
        required_lt_cols = ["Date", "Hour LU", "PIT", "Losstime", "Duration"]

        for sheet_name in ["LT OB MGE", "LT OB BDE"]:
            if sheet_name in db_hourly:
                df = db_hourly[sheet_name].copy()
                if all(col in df.columns for col in required_lt_cols):
                    df_std = df[required_lt_cols].copy()
                    lt_sheets.append(df_std)

        lt_ob = pd.concat(lt_sheets, ignore_index=True) if lt_sheets else pd.DataFrame()

        # 5. LT Coal - Not available in new format, use empty DataFrame
        lt_coal = pd.DataFrame()

        # 6. Cumulative Volume
        cumm_plan = db_hourly["Cumm Vol"].copy() if "Cumm Vol" in db_hourly else pd.DataFrame()

        # 7. Coal ROM data (new sheet)
        coal_rom = db_hourly["Coal Hauling ROM"].copy() if "Coal Hauling ROM" in db_hourly else pd.DataFrame()

        # 8. Rain data (new sheet)
        rain = db_hourly["Rain"].copy() if "Rain" in db_hourly else pd.DataFrame()

        # 9. Master DB (new sheet)
        master_db = db_hourly["db"].copy() if "db" in db_hourly else pd.DataFrame()

    else:
        # ========================================================================
        # OLD FORMAT: Single sheets (backward compatibility)
        # ========================================================================
        prod_ob = db_hourly["prod ob"].copy()
        prod_ch = db_hourly["prod ch"].copy()
        prod_ct = db_hourly["prod ct"].copy()
        lt_ob = db_hourly["lt ob"].copy()
        lt_coal = db_hourly["lt coal"].copy()
        cumm_plan = plan_hourly["Cumm Plan Vol"].copy()
        coal_rom = pd.DataFrame()  # Not available in old format
        rain = pd.DataFrame()  # Not available in old format
        master_db = pd.DataFrame()  # Not available in old format

    # Plan files (same structure for both formats)
    plan_h_ob = plan_hourly["Plan Hourly OB"].copy()
    plan_h_ch = plan_hourly["Plan Hourly CH"].copy()
    plan_h_ct = plan_hourly["Plan Hourly CT"].copy()
    input_plan = plan_hourly["Input_plan"].copy()

    return {
        "prod_ob": prod_ob,
        "prod_ch": prod_ch,
        "prod_ct": prod_ct,
        "lt_ob": lt_ob,
        "lt_coal": lt_coal,
        "cumm_plan": cumm_plan,
        "plan_h_ob": plan_h_ob,
        "plan_h_ch": plan_h_ch,
        "plan_h_ct": plan_h_ct,
        "input_plan": input_plan,
        "coal_rom": coal_rom,  # NEW: Coal ROM data
        "rain": rain,  # NEW: Rain data
        "master_db": master_db,  # NEW: Master DB
    }


def normalize_dataframes(sheets: dict) -> None:
    """
    Normalize all DataFrames in-place:
    - Parse Date columns to datetime
    - Normalize Hour LU (handle both OLD string format and NEW integer format)
    - Convert object/time columns to string for Arrow compatibility

    NEW FORMAT (2026-03-15): Hour LU is INTEGER (6, 7, 8, ...)
    OLD FORMAT: Hour LU is STRING ("06", "07", "08", ...)
    """
    # Fix dates
    date_keys = ["prod_ob", "prod_ch", "prod_ct", "lt_ob", "lt_coal", "coal_rom", "rain", "cumm_plan"]
    for key in date_keys:
        if key in sheets and sheets[key] is not None and not sheets[key].empty:
            df = sheets[key]
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Normalize Hour LU - Handle both OLD (string) and NEW (integer) formats
    all_keys = [
        "prod_ob", "prod_ch", "prod_ct", "cumm_plan",
        "lt_ob", "lt_coal", "plan_h_ob", "plan_h_ch", "plan_h_ct",
        "coal_rom", "rain", "master_db", "input_plan"
    ]
    for key in all_keys:
        if key not in sheets or sheets[key] is None or sheets[key].empty:
            continue

        df = sheets[key]
        if "Hour LU" in df.columns:
            # Robust mapping for Hour LU (handles '6.0', '6', 6, '06', 0, 'O0')
            def _clean_hour(val):
                v_str = str(val).strip().upper()
                if v_str == "NAN" or v_str == "":
                    return "00"
                if v_str.endswith(".0"):
                    v_str = v_str[:-2]
                    
                if v_str.isdigit():
                    num = int(v_str)
                    if num < 6:
                        return f"O{num}"
                    else:
                        return f"{num:02d}"
                return v_str

            df["Hour LU"] = df["Hour LU"].apply(_clean_hour)

        # Force known numeric columns to be numeric
        numeric_cols = ["Volume", "Netto", "Production", "Plan_Daily", "VALUE", "Losstime", "Duration", "Rain", "Rainfall", "Minute"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Convert object/time columns to string for Arrow compatibility
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

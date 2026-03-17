"""
Centralized Configuration & Constants

Loads environment variables and validates required settings at startup.
"""
import os
import sys
import time
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

import streamlit as st

# ── Environment Variable Validation ───────────────────────────
def validate_environment():
    """
    Validate that all required environment variables are set.

    Raises:
        ValueError: If any required environment variable is missing
        SystemExit: If validation fails

    Returns:
        bool: True if all validations pass
    """
    required_vars = {
        "AZURE_TENANT_ID": "Azure AD Tenant ID",
        "AZURE_CLIENT_ID": "Azure AD Client ID (Application ID)",
        "AZURE_CLIENT_SECRET": "Azure AD Client Secret"
    }

    missing_vars = []

    for var_name, description in required_vars.items():
        # Specifically try to check Streamlit Secrets too if missing from os.getenv
        # This helps Streamlit Cloud users
        value = os.getenv(var_name)
        if not value:
            try:
                if var_name in st.secrets:
                    value = st.secrets[var_name]
                    os.environ[var_name] = value  # Sync it back to env for other libraries
            except:
                pass
                
        if not value or value.strip() == "":
            missing_vars.append(f"• {var_name}: {description}")

    if missing_vars:
        error_msg = (
            "🚨 **Missing Required Cloud Secrets/Environment Variables**\n\n"
            + "\n".join(missing_vars) +
            "\n\nIf you are on Streamlit Cloud, please add these to **Settings > Secrets**. "
            "If local, please ensure your `.env` file is loaded."
        )
        st.error(error_msg)
        st.stop()

    return True

# Validate environment on import
validate_environment()

# ── OneDrive Links ────────────────────────────────────────────
# Updated 2026-03-15: New db_hourly_report file with different structure
ONEDRIVE_LINKS = {
    "db_hourly": "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQCcW88khWRCTZFZE9PnZxdkAdVZbA3srdgAZbYUWf4lxNY?e=gABCsf",
    "plan_hourly": "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQBK3837O3nsR5AKLRsno8PGARDeJ9RzlLfjVdPLJLPykWk?e=wYAkLX",
}

# ── Cache Settings ────────────────────────────────────────────
CACHE_TTL_SECONDS = 900  # 15 minutes - Auto-refresh data
SYNC_INTERVAL = 900      # 15 minutes (background sync)
CACHE_FILE = "data/cache.pkl"

# ── Azure AD / Microsoft Graph API ─────────────────────────────
# All Azure credentials must be set in .env file or Streamlit Secrets (validated above)
AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")
AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID", "")
AZURE_CLIENT_SECRET: str = os.getenv("AZURE_CLIENT_SECRET", "")

# Optional: Specific file IDs for the Excel workbooks (if using Graph API with file IDs)
FILE_IDS = {
    "db_hourly": os.getenv("FILE_IDS_DB_HOURLY", ""),
    "plan_hourly": os.getenv("FILE_IDS_PLAN_HOURLY", ""),
}

# ── Retry Settings ────────────────────────────────────────────
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds, exponential

# ── Operational Hour Order ────────────────────────────────────
OP_HOURS = [f"{h:02d}" for h in range(6, 24)] + ["O0", "O1", "O2", "O3", "O4", "O5"]

# ── PIT Registry ─────────────────────────────────────────────
PIT_REGISTRY = {
    "North JO IC": {
        "icon": "🔵",
        "group": "North JO",
        "has_ct_plan": True,
        "label": "North JO IC",
    },
    "North JO GAM": {
        "icon": "🟢",
        "group": "North JO",
        "has_ct_plan": False,
        "label": "North JO GAM",
    },
    "South JO IC": {
        "icon": "🟠",
        "group": "South JO",
        "has_ct_plan": False,
        "label": "South JO IC",
    },
    "South JO GAM": {
        "icon": "🟣",
        "group": "South JO",
        "has_ct_plan": False,
        "label": "South JO GAM",
    },
}

# ── Color Palette ────────────────────────────────────────────
COLORS = {
    # Primary brand colors
    "primary": "#6366f1",      # Indigo 500
    "primary_light": "#818cf8",  # Indigo 400
    "primary_dark": "#4f46e5",   # Indigo 600

    # Semantic colors
    "success": "#10b981",      # Emerald 500
    "success_light": "#34d399", # Emerald 400
    "success_dark": "#059669",   # Emerald 600

    "danger": "#ef4444",       # Red 500
    "danger_light": "#f87171",  # Red 400
    "danger_dark": "#dc2626",    # Red 600

    "warning": "#f59e0b",      # Amber 500
    "warning_light": "#fbbf24", # Amber 400
    "warning_dark": "#d97706",   # Amber 600

    # Teal/Cyan variants (for charts)
    "teal": "#14b8a6",         # Teal 500
    "teal_light": "#5eead4",    # Teal 300
    "teal_dark": "#0f766e",      # Teal 700
    "teal_bg": "rgba(20, 184, 166, 0.1)",

    # Neutral grays
    "gray_50": "#f9fafb",
    "gray_100": "#f3f4f6",
    "gray_200": "#e5e7eb",
    "gray_300": "#d1d5db",
    "gray_400": "#9ca3af",
    "gray_500": "#6b7280",
    "gray_600": "#4b5563",
    "gray_700": "#374151",
    "gray_800": "#1f2937",
    "gray_900": "#111827",

    # Background colors
    "bg_primary": "#ffffff",
    "bg_secondary": "#f8fafc",
    "bg_tertiary": "#f1f5f9",
}

# ── Production Units ─────────────────────────────────────────
UNITS = {
    "ob": "BCM",
    "coal_hauling": "MT",
    "coal_transit": "MT",
    "stock": "MT",
}

"""
Centralized Configuration & Constants
"""
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── OneDrive Links ────────────────────────────────────────────
# Updated 2026-03-15: New db_hourly_report file with different structure
ONEDRIVE_LINKS = {
    "db_hourly": "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQCcW88khWRCTZFZE9PnZxdkAdVZbA3srdgAZbYUWf4lxNY?e=gABCsf",
    "plan_hourly": "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQBK3837O3nsR5AKLRsno8PGARDeJ9RzlLfjVdPLJLPykWk?e=wYAkLX",
}

# ── Cache Settings ────────────────────────────────────────────
CACHE_TTL_SECONDS = 3600  # 1 hour - Auto-refresh data setiap jam
SYNC_INTERVAL = 3600     # 1 hour (background sync)
CACHE_FILE = "data/cache.pkl"

# ── Azure AD / Microsoft Graph API ─────────────────────────────
# Read from environment variables with fallback to hardcoded values (for backward compatibility)
# WARNING: Hardcoded values are deprecated. Please use .env file in production.
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", "")

# Warn if using hardcoded credentials
if os.getenv("AZURE_TENANT_ID") is None:
    import warnings
    warnings.warn(
        "⚠️  Using hardcoded Azure credentials! Please create a .env file from .env.example "
        "and set your credentials there for better security.",
        DeprecationWarning,
        stacklevel=2
    )

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

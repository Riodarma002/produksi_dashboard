"""
Centralized Configuration & Constants
"""
import time

# ── OneDrive Links ────────────────────────────────────────────
ONEDRIVE_LINKS = {
    "db_hourly": "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQA6M4doUWthTb2Cqog-xC3gAY6XckTv72yVV3lnHZoQ3vc?e=R8mrCK",
    "plan_hourly": "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQBK3837O3nsR5AKLRsno8PGARDeJ9RzlLfjVdPLJLPykWk?e=wYAkLX",
}

# ── Cache Settings ────────────────────────────────────────────
CACHE_TTL_SECONDS = 300  # 5 minutes for production data

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
    "primary": "#137fec",
    "success": "#16a34a",
    "danger": "#ef4444",
    "warning": "#f59e0b",
    "teal": "#10b981",
    "teal_light": "#5eead4",
    "teal_dark": "#0f766e",
    "teal_bg": "rgba(240,253,250,0.9)",
}

# ── Production Units ─────────────────────────────────────────
UNITS = {
    "ob": "BCM",
    "coal_hauling": "MT",
    "coal_transit": "MT",
    "stock": "MT",
}

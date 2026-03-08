"""
Formatting & Display Utilities
Number formatting, color logic, icon selection.
"""
from config import ACH_THRESHOLD_GOOD, ACH_THRESHOLD_WARN


def format_number(num: float | int, decimals: int = 0) -> str:
    """Format number with comma separator. e.g. 124500 → '124,500'"""
    if num is None:
        return "-"
    if abs(num) >= 1_000_000:
        return f"{num / 1_000_000:,.1f} M"
    if abs(num) >= 1_000:
        return f"{num:,.{decimals}f}"
    return f"{num:,.{decimals}f}"


def format_compact(num: float | int) -> str:
    """Compact format: 2450000 → '2.45 M', 850400 → '850.4 K'"""
    if num is None:
        return "-"
    if abs(num) >= 1_000_000:
        return f"{num / 1_000_000:,.2f} M"
    if abs(num) >= 1_000:
        return f"{num / 1_000:,.1f} K"
    return f"{num:,.0f}"


def get_achievement_color(pct: float) -> str:
    """Return CSS color class based on achievement %."""
    if pct >= ACH_THRESHOLD_GOOD:
        return "green"
    if pct >= ACH_THRESHOLD_WARN:
        return "orange"
    return "red"


def get_achievement_bg(pct: float) -> tuple[str, str, str]:
    """Return (bg_color, text_color, border_color) for achievement badge."""
    if pct >= ACH_THRESHOLD_GOOD:
        return ("#f0fdf4", "#15803d", "#bbf7d0")  # green-50, green-700, green-200
    if pct >= ACH_THRESHOLD_WARN:
        return ("#fff7ed", "#c2410c", "#fed7aa")  # orange-50, orange-700, orange-200
    return ("#fef2f2", "#b91c1c", "#fecaca")  # red-50, red-700, red-200


def get_delta_icon(delta: float) -> tuple[str, str]:
    """Return (icon_name, color) for trend delta."""
    if delta > 0:
        return ("arrow_upward", "#16a34a")  # green
    elif delta < 0:
        return ("arrow_downward", "#dc2626")  # red
    return ("remove", "#718096")  # neutral gray


def get_progress_width(pct: float) -> str:
    """Return clamped width % for progress bar (0-100)."""
    return f"{min(max(pct, 0), 100):.0f}%"

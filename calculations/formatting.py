"""
Formatting Utilities — Number formatting, display helpers
"""
import pandas as pd


def fmt(val, decimals=0) -> str:
    """Format number: 1.234,56 (Indonesian locale — dot=thousands, comma=decimal)."""
    try:
        val_float = float(val)
    except (ValueError, TypeError):
        val_float = 0.0
    s = f"{val_float:,.{decimals}f}"
    return s.replace(",", "@").replace(".", ",").replace("@", ".")


def ach_color(val) -> str:
    """Return emoji indicator based on achievement percentage."""
    return "🟢" if val >= 100 else "🟡" if val >= 80 else "🔴"


def safe_df(df: pd.DataFrame) -> pd.DataFrame:
    """Convert all object/time columns to string for Arrow compatibility."""
    out = df.copy()
    for col in out.columns:
        if out[col].dtype == "object" or str(out[col].dtype).startswith("time"):
            out[col] = out[col].astype(str)
    return out

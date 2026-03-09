"""
Production Calculations — Filtering, Plan, Actual, Achievement, Stock
"""
import pandas as pd


def filter_data(sheets: dict, date_range: tuple, selected_pit: str) -> dict:
    """
    Filter production DataFrames by a date range and PIT.
    Returns dict with filtered DataFrames and visibility flags.
    """
    prod_ob = sheets["prod_ob"]
    prod_ch = sheets["prod_ch"]
    prod_ct = sheets["prod_ct"]
    
    start_date, end_date = date_range

    ob_f = prod_ob[
        (prod_ob["Date"] >= start_date) & 
        (prod_ob["Date"] <= end_date) & 
        (prod_ob["PIT"] == selected_pit)
    ]
    ch_f = prod_ch[
        (prod_ch["Date"] >= start_date) & 
        (prod_ch["Date"] <= end_date) & 
        (prod_ch["PIT Fix"] == selected_pit)
    ]

    # CT: prod ct uses PIT='LJO-A' which maps to Plan's 'North JO IC'
    # Filter by date only for actual; section visibility controlled by plan
    ct_f = prod_ct[
        (prod_ct["Date"] >= start_date) & 
        (prod_ct["Date"] <= end_date)
    ]

    return {"ob_f": ob_f, "ch_f": ch_f, "ct_f": ct_f}


def get_plan_values(sheets: dict, selected_pit: str) -> dict:
    """
    Extract Plan_Daily values for OB, CH, CT from Plan Hourly sheets.
    Returns dict with plan values and has_ct flag.
    Note: Currently returns the *daily* plan as the base target. 
    If spanning multiple days, this might need multiplying by date range length.
    """
    plan_h_ob = sheets["plan_h_ob"]
    plan_h_ch = sheets["plan_h_ch"]
    plan_h_ct = sheets["plan_h_ct"]

    def _get_daily(df, pit):
        match = df[df["PIT"] == pit]
        return match["Plan_Daily"].iloc[0] if len(match) > 0 else 0

    plan_ob = _get_daily(plan_h_ob, selected_pit)
    plan_ch = _get_daily(plan_h_ch, selected_pit)
    plan_ct = _get_daily(plan_h_ct, selected_pit)
    has_ct = plan_ct > 0

    return {
        "plan_ob": plan_ob,
        "plan_ch": plan_ch,
        "plan_ct": plan_ct,
        "has_ct": has_ct,
    }


def calc_actuals(filtered: dict) -> dict:
    """Calculate actual production volumes from filtered DataFrames."""
    actual_ob = filtered["ob_f"]["Volume"].sum()
    actual_ch = filtered["ch_f"]["Netto"].sum() / 1000  # kg -> MT
    actual_ct = filtered["ct_f"]["Production"].sum()

    return {"actual_ob": actual_ob, "actual_ch": actual_ch, "actual_ct": actual_ct}


def calc_achievements(actuals: dict, plans: dict) -> dict:
    """Calculate achievement percentages."""
    def _ach(actual, plan):
        return (actual / plan * 100) if plan > 0 else 0

    return {
        "ach_ob": _ach(actuals["actual_ob"], plans["plan_ob"]),
        "ach_ch": _ach(actuals["actual_ch"], plans["plan_ch"]),
        "ach_ct": _ach(actuals["actual_ct"], plans["plan_ct"]),
    }


def calc_stripping_ratio(actuals: dict) -> float:
    """Calculate actual stripping ratio (OB / CH)."""
    return actuals["actual_ob"] / actuals["actual_ch"] if actuals["actual_ch"] > 0 else 0


def calc_global_stripping_ratio(sheets: dict, date_range: tuple) -> float:
    """Calculate the global stripping ratio across all JOs."""
    prod_ob = sheets["prod_ob"]
    prod_ch = sheets["prod_ch"]
    start_date, end_date = date_range

    ob_range = prod_ob[
        (prod_ob["Date"] >= start_date) & 
        (prod_ob["Date"] <= end_date)
    ]
    ch_range = prod_ch[
        (prod_ch["Date"] >= start_date) & 
        (prod_ch["Date"] <= end_date)
    ]

    total_ob = ob_range["Volume"].sum()
    total_ch = ch_range["Netto"].sum() / 1000  # kg -> MT

    return total_ob / total_ch if total_ch > 0 else 0


def calc_coal_stock(
    sheets: dict, date_range: tuple, input_values: dict
) -> dict:
    """
    Calculate Coal Stock ROM and Port (GLOBAL — same value for all JOs).
    Stock ROM  = Opening ROM  + CH filtered by Seam in ('N-STOCK ROOM', 'N-STOCK ROOM 60')
    Stock Port = Opening Port + total CH (all JOs) - Plan Barging
    """
    prod_ch = sheets["prod_ch"]
    start_date, end_date = date_range
    
    ch_range = prod_ch[
        (prod_ch["Date"] >= start_date) & 
        (prod_ch["Date"] <= end_date)
    ]

    # Stock ROM: opening + CH where Seam = N-STOCK ROOM / N-STOCK ROOM 60
    ch_to_rom = ch_range[
        ch_range["Seam"].isin(["N-STOCK ROOM", "N-STOCK ROOM 60"])
    ]["Netto"].sum() / 1000  # kg -> MT

    # Total CH across ALL JOs for this date range (not filtered by PIT)
    total_ch = ch_range["Netto"].sum() / 1000  # kg -> MT

    coal_stock_rom = input_values["opening_rom"] + ch_to_rom
    coal_stock_port = (
        input_values["opening_port"]
        + total_ch
        - input_values["plan_barging"]
    )

    return {"coal_stock_rom": coal_stock_rom, "coal_stock_port": coal_stock_port}


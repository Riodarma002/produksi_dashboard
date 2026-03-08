"""
Summary Page — All JOs at a glance with quick insights.
"""
import pandas as pd
import streamlit as st

from state import init_data, get_input_values, render_date_selector
from config import PIT_REGISTRY
from calculations.production import (
    filter_data, get_plan_values, calc_actuals,
    calc_achievements, calc_stripping_ratio,
)
from calculations.formatting import fmt, ach_color


def _jo_color(pit):
    return {
        "North JO IC": "#0d9488",
        "North JO GAM": "#22c55e",
        "South JO IC": "#8b5cf6",
        "South JO GAM": "#c026d3",
    }.get(pit, "#3b82f6")


def _build_card(title, plan_lbl, plan_val, act_lbl, act_val, unit, ach, color):
    ach_display = min(ach, 100) if getattr(ach, 'real', None) is not None else 0
    
    if ach is not None:
        # Choose font size depending on digit count
        pct_font = "11px" if ach >= 100 else "13px"
        ring_html = f'''
<div style="position:relative;width:70px;height:70px;">
<svg viewBox="0 0 36 36" style="width:70px;height:70px;transform:rotate(-90deg);">
<path style="fill:none;stroke:#f1f5f9;stroke-width:3.5;" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
<path style="fill:none;stroke:{color};stroke-width:3.5;stroke-dasharray:{ach_display},100;stroke-linecap:round;" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
</svg>
<div style="position:absolute;top:0;left:0;width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:{pct_font};font-weight:800;color:{color};">
{fmt(ach, 1)}%
</div>
</div>
'''
        right_html = f'''
<div style="display:flex;flex-direction:column;align-items:flex-end;justify-content:center;">
{ring_html}
</div>
'''
    else:
        right_html = ''

    if plan_val != "":
        left_body = f'''
<div style="font-size:10px;color:#64748b;font-weight:600;margin-bottom:2px;">{plan_lbl}</div>
<div style="font-size:15px;font-weight:800;color:#0f172a;margin-bottom:8px;">{fmt(plan_val)} <span style="font-size:11px;font-weight:600;color:#64748b;">{unit}</span></div>
<div style="font-size:10px;color:#64748b;font-weight:600;margin-bottom:2px;">{act_lbl}</div>
<div style="font-size:15px;font-weight:800;color:#0f172a;">{fmt(act_val)} <span style="font-size:11px;font-weight:600;color:#64748b;">{unit}</span></div>
'''
    else:
        left_body = f'''
<div style="font-size:10px;color:#64748b;font-weight:600;margin-bottom:4px;">{act_lbl}</div>
<div style="font-size:18px;font-weight:800;color:#0f172a;line-height:1.2;">{fmt(act_val, 2)} <span style="font-size:11px;font-weight:600;color:#64748b;">{unit}</span></div>
'''

    return f'''
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:12px;margin-bottom:10px;box-shadow:0 1px 3px rgba(0,0,0,0.02);display:flex;justify-content:space-between;min-height:95px;">
<div style="flex:1;">{left_body}</div>
{right_html}
</div>
'''


def run():
    sheets = init_data()
    
    # Render header 
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">'
            '<span style="font-size:24px;">📊</span>'
            '<span style="font-size:20px;font-weight:700;color:#0f172a;">Summary - All JO</span>'
            '</div>', 
            unsafe_allow_html=True
        )
    with col2:
        date_range = render_date_selector(sheets, key="summary_date")
        start_date, end_date = date_range

    if start_date == end_date:
        date_str = pd.Timestamp(start_date).strftime('%A, %d %B %Y')
    else:
        date_str = f"{pd.Timestamp(start_date).strftime('%d %B')} – {pd.Timestamp(end_date).strftime('%d %B %Y')}"

    st.markdown(f'<div style="font-weight:600;color:#64748b;margin-bottom:24px;">{date_str}</div>', unsafe_allow_html=True)

    # Collect Data
    rows = []
    for pit_name, meta in PIT_REGISTRY.items():
        filtered = filter_data(sheets, date_range, pit_name)
        plans = get_plan_values(sheets, pit_name)
        actuals = calc_actuals(filtered)
        achievements = calc_achievements(actuals, plans)
        sr = calc_stripping_ratio(actuals)

        rows.append({
            "pit": pit_name,
            "color": _jo_color(pit_name),
            "plan_ob": plans["plan_ob"],
            "actual_ob": actuals["actual_ob"],
            "ach_ob": achievements["ach_ob"],
            "plan_ch": plans["plan_ch"],
            "actual_ch": actuals["actual_ch"],
            "ach_ch": achievements["ach_ch"],
            "plan_ct": plans["plan_ct"],
            "actual_ct": actuals["actual_ct"],
            "ach_ct": achievements["ach_ct"],
            "has_ct": plans["has_ct"],
            "sr": sr,
        })

    # Build 4 Columns HTML
    html_cols = ""
    for r in rows:
        color = r["color"]
        col_html = f'''
<div>
<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
<div style="width:14px;height:14px;border-radius:50%;background:{color};"></div>
<div style="font-size:15px;font-weight:700;color:#0f172a;">{r["pit"]}</div>
</div>
{_build_card("OB Plan", "OB Plan", r["plan_ob"], "OB Actual", r["actual_ob"], "BCM", r["ach_ob"], color)}
{_build_card("OB Plan", "Coal Hauling Plan", r["plan_ch"], "Coal Hauling Actual", r["actual_ch"], "MT", r["ach_ch"], color)}
'''
        if r["has_ct"]:
            col_html += _build_card("OB Plan", "Coal Transit Plan", r["plan_ct"], "Coal Transit Actual", r["actual_ct"], "MT", r["ach_ct"], color)
        
        col_html += _build_card("OB Plan", "", "", "Stripping Ratio", r["sr"], "Ratio", None, color)
        col_html += '</div>'
        html_cols += col_html

    grid_html = f'''
<div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:14px;margin-bottom:8px;">
{html_cols}
</div>
'''

    # Insights HTML
    best_ob = max(rows, key=lambda x: x["ach_ob"] if x["ach_ob"] is not None else 0)
    worst_ob = min(rows, key=lambda x: x["ach_ob"] if x["ach_ob"] is not None else 1000)
    best_ch = max(rows, key=lambda x: x["ach_ch"] if x["ach_ch"] is not None else 0)
    worst_ch = min(rows, key=lambda x: x["ach_ch"] if x["ach_ch"] is not None else 1000)

    insights_html = f'''
<div style="margin-bottom:12px;">
<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
<span style="font-size:16px;">💡</span>
<span style="font-size:14px;font-weight:700;color:#0f172a;">Quick Insights</span>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
<div style="display:flex;flex-direction:column;gap:6px;">
<div style="background:#dcfce7;color:#166534;padding:6px 12px;border-radius:6px;font-size:11px;font-weight:600;display:flex;align-items:center;gap:6px;">
<span style="font-size:12px;">🌲</span> Best OA: {best_ob['pit']} - {fmt(best_ob['ach_ob'], 1)}%
</div>
<div style="background:#dcfce7;color:#166534;padding:6px 12px;border-radius:6px;font-size:11px;font-weight:600;display:flex;align-items:center;gap:6px;">
<span style="font-size:12px;">🌲</span> Best CH: {best_ch['pit']} - {fmt(best_ch['ach_ch'], 1)}%
</div>
</div>
<div style="display:flex;flex-direction:column;gap:6px;">
<div style="background:#fee2e2;color:#991b1b;padding:6px 12px;border-radius:6px;font-size:11px;font-weight:600;display:flex;align-items:center;gap:6px;">
<span style="font-size:12px;">⚠️</span> Lowest OA: {worst_ob['pit']} - {fmt(worst_ob['ach_ob'], 1)}%
</div>
<div style="background:#fee2e2;color:#991b1b;padding:6px 12px;border-radius:6px;font-size:11px;font-weight:600;display:flex;align-items:center;gap:6px;">
<span style="font-size:12px;">⚠️</span> Lowest CH: {worst_ch['pit']} - {fmt(worst_ch['ach_ch'], 1)}%
</div>
</div>
</div>
</div>
'''

    # Total HTML
    total_ob = sum(r["actual_ob"] for r in rows)
    total_ch = sum(r["actual_ch"] for r in rows)
    total_plan_ob = sum(r["plan_ob"] for r in rows)
    total_plan_ch = sum(r["plan_ch"] for r in rows)

    def _total_card(label, val, unit):
        return f'''
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:12px 14px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 1px 2px rgba(0,0,0,0.02);">
<div>
<div style="font-size:11px;color:#0f172a;font-weight:600;margin-bottom:4px;">{label}</div>
<div style="font-size:20px;font-weight:800;color:#0f172a;">{fmt(val)} <span style="font-size:12px;font-weight:600;color:#64748b;">{unit}</span></div>
</div>
<svg width="32" height="16" viewBox="0 0 32 16">
<path d="M0 16 L 8 8 L 16 12 L 24 4 L 32 6" fill="none" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
</div>
'''

    totals_html = f'''
<div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:12px;padding-bottom:12px;">
{_total_card("Total OA Actual", total_ob, "BCM")}
{_total_card("Total OA Plan", total_plan_ob, "BCM")}
{_total_card("Total CH Actual", total_ch, "MT")}
{_total_card("Total CH Plan", total_plan_ch, "MT")}
</div>
'''

    st.markdown(grid_html + insights_html + totals_html, unsafe_allow_html=True)


run()

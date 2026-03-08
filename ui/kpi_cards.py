"""
KPI Cards — Matching reference design.
Row 1: Production cards (OB, CH, CT) with title+unit, badge, large value, sparkline, plan row
Row 2: Stock metrics with icon circles and horizontal layout
"""
import streamlit as st

from calculations.formatting import fmt


def _badge_style(ach):
    if ach >= 100:
        return "background:#dcfce7;color:#16a34a;"
    elif ach >= 80:
        return "background:#fef9c3;color:#d97706;"
    return "background:#fee2e2;color:#ef4444;"


def _badge_icon(ach):
    return "✓" if ach >= 100 else "✕"


def _bar_color(ach):
    if ach >= 100:
        return "#16a34a"
    elif ach >= 80:
        return "#f59e0b"
    return "#ef4444"


def _spark_color(ach):
    if ach >= 100:
        return "#16a34a"  # Green
    elif ach >= 80:
        return "#f59e0b"  # Yellow
    return "#ef4444"      # Red


def _spark_svg(ach):
    color = _spark_color(ach)
    
    # Generate an SVG path that looks like a stock chart
    # Shifted values down/up so the stroke width doesn't get cut off at the edges
    # Using explicit Cubic Bezier (C) to guarantee curve stays strictly within the bounding box
    if ach >= 100:
        # Trending Up
        path_line = "M 2 34 C 10 34, 15 24, 25 24 C 35 24, 40 30, 50 30 C 60 30, 65 14, 75 14 C 85 14, 90 4, 98 4"
        path_fill = f"{path_line} L 98 44 L 2 44 Z"
    elif ach >= 80:
        # Flat / Volatile
        path_line = "M 2 24 C 10 24, 15 16, 25 16 C 35 16, 40 28, 50 28 C 60 28, 65 20, 75 20 C 85 20, 90 26, 98 26"
        path_fill = f"{path_line} L 98 44 L 2 44 Z"
    else:
        # Trending Down
        path_line = "M 2 8 C 10 8, 15 18, 25 18 C 35 18, 40 10, 50 10 C 60 10, 65 26, 75 26 C 85 26, 90 36, 98 36"
        path_fill = f"{path_line} L 98 44 L 2 44 Z"

    # We use a linear gradient for the "filled area" effect
    gradient_id = f"sparkGrad_{int(ach)}"
    
    return f'''
    <svg width="100" height="44" viewBox="0 0 100 44" style="margin-bottom:4px;">
        <defs>
            <linearGradient id="{gradient_id}" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="{color}" stop-opacity="0.3" />
                <stop offset="100%" stop-color="{color}" stop-opacity="0.0" />
            </linearGradient>
        </defs>
        <path d="{path_fill}" fill="url(#{gradient_id})" />
        <path d="{path_line}" stroke="{color}" stroke-width="2.5" stroke-linecap="round" fill="none"/>
    </svg>
    '''


CARD = "background:#fff;border:1px solid #eef0f4;border-radius:14px;padding:20px 20px;min-height:130px;display:flex;flex-direction:column;justify-content:space-between;"


def _prod_card(name, unit, actual, plan, ach):
    """Production KPI card matching reference design."""
    pct = min(ach, 100)
    bstyle = _badge_style(ach)
    bicon = _badge_icon(ach)
    bcolor = _bar_color(ach)
    spark = _spark_svg(ach)

    return (
        f'<div style="{CARD}">'
        '<div>'
        # Row 1: Title + unit
        '<div style="margin-bottom:8px;">'
        f'<span class="kpi-title" style="font-weight:600;color:#374151;">{name}'
        f' <span style="color:#9ca3af;font-weight:400;">{unit}</span></span>'
        '</div>'
        # Row 2: Big value + ach badge (left) ... sparkline (right)
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
        '<div style="display:flex;align-items:center;gap:8px;">'
        f'<span class="kpi-value" style="font-weight:700;color:#111827;line-height:1;">{fmt(actual)}</span>'
        f'<span class="kpi-badge" style="font-weight:600;padding:3px 10px;border-radius:20px;{bstyle}">'
        f'{fmt(ach, 1)}% {bicon}</span>'
        '</div>'
        f'{spark}'
        '</div>'
        # Row 3: Progress bar
        '<div style="width:100%;height:5px;background:#f3f4f6;border-radius:3px;overflow:hidden;margin-bottom:12px;">'
        f'<div style="height:100%;width:{pct}%;background:{bcolor};border-radius:3px;"></div>'
        '</div>'
        '</div>'
        # Row 4: Progress label ... Plan value
        '<div style="display:flex;align-items:center;justify-content:space-between;">'
        f'<span style="font-size:13px;color:{bcolor};font-weight:500;">{"Achieved" if ach >= 100 else "Progress"}</span>'
        f'<span style="font-size:14px;font-weight:700;color:{bcolor};">Plan {fmt(plan)}</span>'
        '</div>'
        '</div>'
    )


def _stock_card(icon_svg, label, value, unit=""):
    """Stock metric card with icon — horizontal matching reference."""
    unit_html = f' <span style="font-size:14px;color:#0f172a;font-weight:700;">{unit}</span>' if unit else ""
    
    # Flatter, horizontal layout with distinct icon box
    card_style = (
        "background:#fff;border:1px solid #eef0f4;border-radius:12px;padding:16px;"
        "display:flex;align-items:center;gap:12px;min-height:72px;"
    )
    
    return (
        f'<div style="{card_style}">'
        # Icon box
        f'<div style="min-width:40px;height:40px;border-radius:10px;background:#f1f5f9;'
        f'display:flex;align-items:center;justify-content:center;">'
        f'{icon_svg}'
        '</div>'
        # Text grouping
        '<div style="display:flex;flex-direction:column;justify-content:center;">'
        f'<div style="font-size:12px;color:#475569;font-weight:500;margin-bottom:2px;">{label}</div>'
        f'<div style="font-size:18px;font-weight:700;color:#0f172a;line-height:1.2;">{value}{unit_html}</div>'
        '</div>'
        '</div>'
    )


def render_all_metrics(plans, actuals, achievements, has_ct, sr, stock):
    """Render all metrics in unified grid matching reference design."""
    # ── Row 1: Production cards ───────────────────────────────
    if has_ct:
        # 3 columns: OB, CH, CT
        c1, c2, c3 = st.columns(3, gap="small")
        with c1:
            st.markdown(
                _prod_card("Overburden", "BCM",
                           actuals["actual_ob"], plans["plan_ob"], achievements["ach_ob"]),
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                _prod_card("Coal Hauling", "MT",
                           actuals["actual_ch"], plans["plan_ch"], achievements["ach_ch"]),
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                _prod_card("Coal Transit", "MT",
                           actuals["actual_ct"], plans["plan_ct"], achievements["ach_ct"]),
                unsafe_allow_html=True,
            )
    else:
        # 2 columns: OB, CH (wider cards, no CT)
        c1, c2 = st.columns(2, gap="small")
        with c1:
            st.markdown(
                _prod_card("Overburden", "BCM",
                           actuals["actual_ob"], plans["plan_ob"], achievements["ach_ob"]),
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                _prod_card("Coal Hauling", "MT",
                           actuals["actual_ch"], plans["plan_ch"], achievements["ach_ch"]),
                unsafe_allow_html=True,
            )

    # ── Row 2: SR + Stock metrics (always 3 columns) ─────────
    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3, gap="small")

    # SVG Icons
    svg_sr = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 21V3m0 0L3 7m4-4l4 4M17 3v18m0 0l4-4m-4 4l-4-4"/></svg>'
    svg_rom = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/></svg>'
    svg_port = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>'

    with s1:
        st.markdown(_stock_card(svg_sr, "Stripping Ratio", fmt(sr, 2)), unsafe_allow_html=True)

    with s2:
        st.markdown(_stock_card(svg_rom, "Stock ROM", fmt(stock["coal_stock_rom"]), "MT"), unsafe_allow_html=True)

    with s3:
        st.markdown(_stock_card(svg_port, "Stock Port", fmt(stock["coal_stock_port"]), "MT"), unsafe_allow_html=True)


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
    # Triangle icons matching user request: Green Up Triangle / Red Down Triangle
    if ach >= 100:
        # Upward Triangle
        return '''<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="margin-right:6px;">
                    <path d="M12 4l9 16H3z"/>
                  </svg>'''
    # Downward Triangle
    return '''<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="margin-right:6px;">
                <path d="M12 20L3 4h18z"/>
              </svg>'''


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


CARD = (
    "background:linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);"
    "border:1px solid #e5e7eb;"
    "border-radius:20px;"
    "padding:28px 32px;"
    "min-width:300px; height:210px; display:flex; flex-direction:column; justify-content:space-between;"
    "transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);"
    "box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);"
    "position:relative; overflow:hidden;"
)

# Subtle gradient overlay for card depth
CARD_AFTER = (
    "content:''; position:absolute; top:0; left:0; right:0; height:4px;"
    "background:linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.1), transparent);"
)


def _prod_card(name, unit, actual, plan, ach):
    """Production KPI card with modern professional design."""
    pct = min(ach, 100)
    bstyle = _badge_style(ach)
    bicon = _badge_icon(ach)
    bcolor = _bar_color(ach)
    spark = _spark_svg(ach)

    return (
        f'<div style="{CARD}" class="kpi-card-hover">'
        '<div style="position:relative;z-index:1;">'
        # Row 1: Title + unit
        '<div style="margin-bottom:12px;">'
        f'<span class="kpi-title" style="font-size:clamp(16px, 1.3vw, 18px); font-weight:700; color:#1e293b; letter-spacing:-0.3px;">{name}'
        f' <span style="color:#94a3b8; font-weight:400; font-size:clamp(13px, 0.9vw, 15px); margin-left:4px;">{unit}</span></span>'
        '</div>'
        # Row 2: Big value (left) ... ach badge (right)
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'
        f'<span class="kpi-value" style="font-family:\'Inter\', sans-serif; font-size:clamp(42px, 4vw, 56px); font-weight:800; color:#0f172a; line-height:1; letter-spacing:-1px;">{fmt(actual)}</span>'
        f'<div class="kpi-badge ach-pill" style="font-weight:700; font-size:clamp(12px, 0.95vw, 14px); padding:4px 8px; border-radius:8px; display:flex; align-items:center; gap:4px; box-shadow:0 1px 2px rgba(0,0,0,0.05); {bstyle}">'
        f'{bicon}<span>{fmt(ach, 1)}%</span></div>'
        '</div>'
        # Row 3: Progress bar with gradient
        '<div style="width:100%;height:6px;background:#f1f5f9;border-radius:4px;overflow:hidden;margin-bottom:14px; position:relative;">'
        f'<div style="height:100%;width:{pct}%;background:linear-gradient(90deg, {bcolor} 0%, {bcolor}dd 100%);border-radius:4px;'
        f'transition:width 0.8s cubic-bezier(0.4, 0, 0.2, 1); box-shadow:0 2px 4px rgba(0,0,0,0.1);"></div>'
        '</div>'
        '</div>'
        # Row 4: Progress label ... Plan value
        '<div style="display:flex;align-items:center;justify-content:space-between; position:relative;z-index:1;">'
        f'<span style="font-size:clamp(11px, 0.85vw, 13px);color:{bcolor};font-weight:600; letter-spacing:0.3px;">{"Achieved" if ach >= 100 else "In Progress"}</span>'
        f'<span class="prod-plan-value" style="font-size:clamp(16px, 1.3vw, 18px);font-weight:800;color:#475569;">Target: <span style="font-weight:900;color:{bcolor};">{fmt(plan)}</span></span>'
        '</div>'
        '</div>'
        '<style>.kpi-card-hover:hover{transform:translateY(-2px); box-shadow:0 8px 16px rgba(0,0,0,0.08);}</style>'
    )


def _stock_card(icon_svg, label, value, unit="", bg_color="#f1f5f9", icon_color="#64748b"):
    """Stock metric card with modern professional styling."""
    unit_html = f' <span style="font-size:16px;color:#0f172a;font-weight:700;margin-left:2px;">{unit}</span>' if unit else ""

    # Modern card with subtle gradient and shadow
    card_style = (
        "background:linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);"
        "border:1px solid #e5e7eb;"
        "border-radius:16px;"
        "padding:24px;"
        "display:flex;align-items:center;gap:18px;min-height:96px;"
        "transition:all 0.3s cubic-bezier(0.4, 0, 0.2, 1);"
        "box-shadow:0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03);"
        "position:relative; overflow:hidden;"
    )

    # Icon container with gradient
    icon_style = (
        f"min-width:52px;height:52px;border-radius:14px;background:{bg_color};"
        f"display:flex;align-items:center;justify-content:center;color:{icon_color};"
        f"box-shadow:0 2px 8px rgba(0,0,0,0.08);"
        f"transition:all 0.3s ease;"
    )

    return (
        f'<div style="{card_style}" class="stock-card-hover">'
        # Icon box
        f'<div style="{icon_style}">'
        f'{icon_svg.replace("#64748b", icon_color)}'
        '</div>'
        # Text grouping
        '<div style="display:flex;flex-direction:column;justify-content:center;flex:1;">'
        f'<div style="font-size:clamp(11px, 0.85vw, 13px);color:#64748b;font-weight:600;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:6px;">{label}</div>'
        f'<div style="font-size:clamp(24px, 2vw, 32px);font-weight:800;color:#0f172a;line-height:1.1;letter-spacing:-0.8px;">{value}{unit_html}</div>'
        '</div>'
        # Subtle accent line
        f'<div style="position:absolute;left:0;top:50%;transform:translateY(-50%);width:4px;height:60%;background:{bg_color};border-radius:0 4px 4px 0;"></div>'
        '</div>'
        f'<style>.stock-card-hover:hover{{transform:translateY(-2px); box-shadow:0 8px 16px rgba(0,0,0,0.08);}} .stock-card-hover:hover div[style*="min-width"]{{transform:scale(1.05);}}</style>'
    )


def render_all_metrics(plans, actuals, achievements, has_ct, sr, stock):
    """Render all metrics in responsive CSS grid matching reference design."""
    
    # ── CSS Native Grid Configuration ──
    st.markdown("""
    <style>
    /* Responsive Grid for Production Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 16px;
        margin-bottom: 16px;
    }
    
    /* Responsive Grid for Stock Cards */
    .stock-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Row 1: Production cards ───────────────────────────────
    cards_html = []
    
    cards_html.append(_prod_card("Overburden", "BCM", actuals["actual_ob"], plans["plan_ob"], achievements["ach_ob"]))
    cards_html.append(_prod_card("Coal Hauling", "MT", actuals["actual_ch"], plans["plan_ch"], achievements["ach_ch"]))
    
    if has_ct:
        cards_html.append(_prod_card("Coal Transit", "MT", actuals["actual_ct"], plans["plan_ct"], achievements["ach_ct"]))

    # Wrap all production cards in our responsive grid
    st.markdown(f'<div class="kpi-grid">{"".join(cards_html)}</div>', unsafe_allow_html=True)

    # ── Row 2: SR + Stock metrics ───────────────────────────
    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

    # SVG Icons
    svg_sr = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7 21V3m0 0L3 7m4-4l4 4M17 3v18m0 0l4-4m-4 4l-4-4"/></svg>'
    svg_rom = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/></svg>'
    svg_port = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>'

    stock_html = [
        _stock_card(svg_sr, "Stripping Ratio", fmt(sr, 2), "Ratio", bg_color="rgba(59, 130, 246, 0.1)", icon_color="#3b82f6"),
        _stock_card(svg_rom, "Stock ROM", fmt(stock["coal_stock_rom"]), "MT", bg_color="rgba(34, 197, 94, 0.1)", icon_color="#22c55e"),
        _stock_card(svg_port, "Stock Port", fmt(stock["coal_stock_port"]), "MT", bg_color="rgba(99, 102, 241, 0.1)", icon_color="#6366f1")
    ]

    # Wrap all stock cards in our responsive grid
    st.markdown(f'<div class="stock-grid">{"".join(stock_html)}</div>', unsafe_allow_html=True)


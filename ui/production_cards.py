"""
Production Operation Cards — OB, Coal Hauling, Transit, Barging
4-column CSS grid with achievement badges, progress bars, MTD/YTD footers.
All rendered in a single st.markdown() call to avoid Streamlit HTML issues.
"""
import streamlit as st
from calculations.production import calculate_achievement
from calculations.utils import (
    format_number, format_compact,
    get_achievement_bg, get_delta_icon, get_progress_width,
)


CARD_COLORS = {
    "ob": "#fb923c",
    "coal_hauling": "#60a5fa",
    "coal_transit": "#c084fc",
    "barging": "#2dd4bf",
}

CARD_LABELS = {
    "ob": "Overburden",
    "coal_hauling": "Coal Hauling",
    "coal_transit": "Coal Transit",
    "barging": "Barging",
}

CARD_UNITS = {
    "ob": "BCM",
    "coal_hauling": "MT",
    "coal_transit": "MT",
    "barging": "MT",
}


def render_production_cards(data: dict):
    """Render the 4-column production operations as a single HTML block."""
    card_keys = ["ob", "coal_hauling", "coal_transit", "barging"]
    
    cards_html = ""
    for key in card_keys:
        card_data = data.get(key, {})
        cards_html += _build_card_html(
            key=key,
            actual=card_data.get("actual", 0),
            plan=card_data.get("plan", 0),
            mtd=card_data.get("mtd", 0),
            ytd=card_data.get("ytd", 0),
            mtd_delta=card_data.get("mtd_delta", 0),
        )
    
    full_html = f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin:24px 0 20px;">
        <span class="section-title">Production Operations</span>
        <div style="display:flex; align-items:center; gap:4px; color:#137fec;
            font-size:0.875rem; font-weight:500; cursor:pointer;">
            Download Report
            <span class="material-icons-outlined" style="font-size:16px;">download</span>
        </div>
    </div>
    <div class="prod-cards-grid" style="display:grid; grid-template-columns:repeat(4, 1fr); gap:20px;">
        {cards_html}
    </div>
    """
    
    st.markdown(full_html, unsafe_allow_html=True)


def _build_achievement_html(pct: float, color: str) -> str:
    """Build achievement donut chart HTML."""
    bg, text_color, border_color = get_achievement_bg(pct)
    visual_pct = min(pct, 100)

    # When 100%, fill the dasharray completely (100, 100) for a solid ring
    dash = f"{visual_pct:.1f},100"
    
    return f'''
    <div class="ach-badge">
        <div style="width: 52px; height: 52px; position: relative; display: flex; align-items: center; justify-content: center; background: #fff; border-radius: 50%;">
            <svg style="position:absolute;width:100%;height:100%;transform:rotate(-90deg);left:0;top:0;" viewBox="0 0 36 36">
                <!-- Background ring -->
                <path style="fill:none;stroke:#f1f5f9;stroke-width:3.5;" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                <!-- Foreground progress ring (no label, just the ring fill) -->
                <path style="fill:none;stroke:{text_color};stroke-width:3.5;stroke-dasharray:{dash};stroke-linecap:round;" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
            </svg>
        </div>
    </div>'''


def _build_card_html(
    key: str, actual: float, plan: float,
    mtd: float, ytd: float, mtd_delta: float
) -> str:
    """Build one production card as HTML string."""
    color = CARD_COLORS.get(key, "#718096")
    label = CARD_LABELS.get(key, key)
    unit = CARD_UNITS.get(key, "MT")
    pct = calculate_achievement(actual, plan)
    
    ach_html = _build_achievement_html(pct, color)
    delta_icon, delta_color = get_delta_icon(mtd_delta)
    
    return f'''
    <div class="prod-card">
        {ach_html}
        <div class="prod-body">
            <div class="prod-header-row">
                <div style="display:flex;align-items:center;">
                    <span class="prod-dot" style="background:{color};"></span>
                    <span class="prod-name">{label}</span>
                </div>
                <span class="prod-unit-badge">{unit}</span>
            </div>
            <div style="margin-bottom:12px;">
                <div class="prod-actual-label">Actual</div>
                <span class="prod-actual-value">{format_number(actual)}</span>
            </div>
            <div>
                <div class="prod-plan-row">
                    <span class="prod-plan-label">Plan</span>
                    <span class="prod-plan-value">{format_number(plan)}</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="background:{color};width:{get_progress_width(pct)};"></div>
                </div>
            </div>
        </div>
        <div class="prod-footer">
            <div>
                <div class="footer-label">MTD</div>
                <div class="footer-value">{format_compact(mtd)}</div>
                <div class="footer-delta" style="color:{delta_color};">
                    <span class="material-icons-outlined" style="font-size:10px;">{delta_icon}</span>
                    {abs(mtd_delta):.1f}%
                </div>
            </div>
            <div>
                <div class="footer-label">YTD</div>
                <div class="footer-value">{format_compact(ytd)}</div>
            </div>
        </div>
    </div>'''

"""
Header Bar Component
Title, shift info, date display.
"""
import streamlit as st
from datetime import datetime


def render_header(shift: str = "Shift 1", data_source: str = "Demo Data"):
    """Render the top header bar matching code.html design."""
    now = datetime.now()
    date_str = now.strftime("%b %d, %Y")
    time_str = now.strftime("%H:%M")
    
    st.markdown(f"""
        <div class="dash-header">
            <div>
                <h1>Production Summary Dashboard</h1>
                <div class="subtitle">Real-time insights for {shift} &bull; Source: {data_source}</div>
            </div>
            <div style="display:flex; align-items:center; gap:16px;">
                <div style="display:flex; align-items:center; gap:8px;
                    background:#fff; border:1px solid #e8e8e8; padding:8px 16px;
                    border-radius:8px; box-shadow:0 1px 2px rgba(0,0,0,0.04);
                    font-size:0.875rem; font-weight:500; color:#2D3748;">
                    <span class="material-icons-outlined" style="color:#a0aec0; font-size:18px;">calendar_today</span>
                    {date_str} — {shift}
                </div>
                <div style="display:flex; align-items:center; gap:4px;
                    background:#fff; border:1px solid #e8e8e8; padding:8px 12px;
                    border-radius:8px; font-size:0.875rem; color:#2D3748;">
                    <span class="material-icons-outlined" style="color:#a0aec0; font-size:18px;">schedule</span>
                    {time_str}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

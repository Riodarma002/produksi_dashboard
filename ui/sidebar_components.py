"""
Sidebar Components - Clean, organized layout for dashboard sidebar

Provides consistent styling and layout for all sidebar components.
"""
import streamlit as st
import time
import os
from datetime import datetime

from config import CACHE_FILE, SYNC_INTERVAL
from backend.sync_manager import sync_manager
from backend.data_loader import load_data, extract_sheets, normalize_dataframes, parse_input_plan
from utils.logger import get_logger

logger = get_logger("sidebar")


def get_sync_status_info() -> dict:
    """Get current sync status."""
    cache_path = CACHE_FILE

    if not os.path.exists(cache_path):
        return {
            "status": "never",
            "icon": "⏳",
            "color": "#6b7280",
            "bg_color": "rgba(107, 114, 128, 0.1)",
            "message": "Belum pernah sync",
            "last_sync": None
        }

    try:
        mtime = os.path.getmtime(cache_path)
        last_sync = datetime.fromtimestamp(mtime)
        time_ago = datetime.now() - last_sync

        if time_ago < timedelta(seconds=30):
            status = "syncing"
            icon = "🔄"
            color = "#3b82f6"
            bg_color = "rgba(59, 130, 246, 0.1)"
            message = "Sedang sync..."
        elif time_ago < timedelta(seconds=SYNC_INTERVAL):
            status = "synced"
            icon = "✅"
            color = "#10b981"
            bg_color = "rgba(16, 185, 129, 0.1)"
            minutes_ago = int(time_ago.total_seconds() / 60)
            if minutes_ago < 1:
                message = "Baru saja"
            else:
                message = f"{minutes_ago}m yang lalu"
        else:
            status = "stale"
            icon = "⚠️"
            color = "#f59e0b"
            bg_color = "rgba(245, 158, 11, 0.1)"
            minutes_late = int((time_ago.total_seconds() - SYNC_INTERVAL) / 60)
            message = f"Tertunda {minutes_late}m"

        return {
            "status": status,
            "icon": icon,
            "color": color,
            "bg_color": bg_color,
            "message": message,
            "last_sync": last_sync
        }

    except Exception as e:
        return {
            "status": "error",
            "icon": "❌",
            "color": "#ef4444",
            "bg_color": "rgba(239, 68, 68, 0.1)",
            "message": f"Error: {str(e)}",
            "last_sync": None
        }


def render_refresh_section():
    """
    Render clean, organized refresh section with button and status.

    Layout:
    ┌────────────────────────────────────┐
    │  🔄 Refresh Data            [✅]   │
    │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
    │  ✅ Sync 5m yang lalu             │
    └────────────────────────────────────┘
    """
    sync_info = get_sync_status_info()

    # Container with clean styling
    st.markdown(
        """
        <style>
        .refresh-section {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 12px;
            margin: 8px 0;
        }
        .refresh-button {
            width: 100%;
            padding: 10px 16px;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.2s;
        }
        .refresh-button:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
        .sync-status-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 12px;
            padding: 8px 12px;
            background: white;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        .sync-status-left {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .sync-status-icon {
            font-size: 16px;
        }
        .sync-status-text {
            font-size: 12px;
            font-weight: 500;
            color: #475569;
        }
        .sync-status-time {
            font-size: 11px;
            color: #94a3b8;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Refresh button
    if st.button("🔄 Refresh Data", key="refresh_btn", use_container_width=True):
        with st.spinner("🔄 Mengambil data terbaru..."):
            try:
                # CRITICAL FIX: Force fresh fetch by triggering immediate sync
                # This bypasses the old cache and fetches directly from OneDrive
                sync_result = sync_manager.trigger_immediate_sync()

                if not sync_result["success"]:
                    st.error(f"❌ {sync_result['message']}")
                else:
                    # Load the freshly cached data
                    data = load_data()

                    if not data:
                        st.error("❌ Gagal mengambil data dari cache")
                    else:
                        if isinstance(data, dict) and "sheets" in data:
                            sheets = data["sheets"]
                            input_values = data["input_values"]
                        else:
                            sheets = extract_sheets(data)
                            normalize_dataframes(sheets)
                            input_values = parse_input_plan(sheets["input_plan"])

                        # Update session state
                        st.session_state["sheets"] = sheets
                        st.session_state["input_values"] = input_values
                        st.session_state["cache_mtime"] = os.path.getmtime(CACHE_FILE)

                        # CRITICAL FIX: Clear prod_date from session state to force re-read latest date
                        if "prod_date" in st.session_state:
                            del st.session_state["prod_date"]

                        # Clear any Streamlit cached functions related to data loading
                        st.cache_data.clear()

                        # Success message
                        if not sheets["prod_ob"].empty:
                            latest_date = sheets["prod_ob"]["Date"].max().date()
                            st.success(f"✅ Data berhasil diupdate! Tanggal terbaru: {latest_date}")
                        else:
                            st.success("✅ Data berhasil diupdate!")
                        time.sleep(1)
                        st.rerun()

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Refresh failed: {e}", exc_info=True)

    # Sync status row
    st.markdown(
        f"""
        <div class="sync-status-row">
            <div class="sync-status-left">
                <span class="sync-status-icon">{sync_info['icon']}</span>
                <span class="sync-status-text">{sync_info['message']}</span>
            </div>
            <span class="sync-status-time">Interval: 1m | Refresh: 5m</span>
        </div>
        """,
        unsafe_allow_html=True
    )


from datetime import timedelta


def render_sidebar_divider():
    """Render a clean divider line."""
    st.markdown(
        """
        <div style="
            height: 1px;
            background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
            margin: 16px 0;
        "></div>
        """,
        unsafe_allow_html=True
    )


def render_section_header(title: str, icon: str = ""):
    """Render a section header with consistent styling."""
    if icon:
        st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                margin-bottom: 12px;
            ">
                <span style="font-size: 16px;">{icon}</span>
                <span style="
                    font-size: 11px;
                    font-weight: 700;
                    color: #64748b;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">{title}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="
                font-size: 11px;
                font-weight: 700;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                padding: 0 12px;
                margin-bottom: 12px;
            ">{title}</div>
            """,
            unsafe_allow_html=True
        )

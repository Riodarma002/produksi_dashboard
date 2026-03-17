"""
Sync Status Indicator Component

Displays real-time sync status with visual feedback and last update timestamp.
"""
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
import streamlit as st

from config import CACHE_FILE, SYNC_INTERVAL


def get_sync_status() -> dict:
    """
    Get current sync status from cache file.

    Returns:
        dict with keys:
        - status: "synced", "syncing", "error", "never"
        - last_sync: datetime or None
        - next_sync: datetime or None
        - message: str
    """
    cache_path = Path(CACHE_FILE)

    if not cache_path.exists():
        return {
            "status": "never",
            "last_sync": None,
            "next_sync": None,
            "message": "Belum pernah sync"
        }

    try:
        # Get file modification time as last sync time
        mtime = os.path.getmtime(cache_path)
        last_sync = datetime.fromtimestamp(mtime)
        next_sync = last_sync + timedelta(seconds=SYNC_INTERVAL)

        # Calculate time ago
        time_ago = datetime.now() - last_sync
        if time_ago < timedelta(seconds=30):
            status = "syncing"
            message = "Sedang sync..."
        elif time_ago < timedelta(seconds=SYNC_INTERVAL):
            status = "synced"
            minutes_ago = int(time_ago.total_seconds() / 60)
            if minutes_ago < 1:
                message = "Baru saja sync"
            else:
                message = f"Sync {minutes_ago} menit yang lalu"
        else:
            status = "stale"
            minutes_late = int((time_ago.total_seconds() - SYNC_INTERVAL) / 60)
            message = f"Data tertunda {minutes_late} menit"

        return {
            "status": status,
            "last_sync": last_sync,
            "next_sync": next_sync,
            "message": message
        }

    except Exception as e:
        return {
            "status": "error",
            "last_sync": None,
            "next_sync": None,
            "message": f"Error: {str(e)}"
        }


def render_sync_status(show_next_sync: bool = False):
    """
    Render sync status indicator in UI.

    Args:
        show_next_sync: Whether to show next sync time

    Example:
        render_sync_status(show_next_sync=True)
    """
    sync_info = get_sync_status()

    # Status colors and icons
    status_config = {
        "synced": {
            "icon": "✅",
            "color": "#10b981",  # Green
            "bg_color": "rgba(16, 185, 129, 0.1)"
        },
        "syncing": {
            "icon": "🔄",
            "color": "#3b82f6",  # Blue
            "bg_color": "rgba(59, 130, 246, 0.1)"
        },
        "stale": {
            "icon": "⚠️",
            "color": "#f59e0b",  # Amber
            "bg_color": "rgba(245, 158, 11, 0.1)"
        },
        "error": {
            "icon": "❌",
            "color": "#ef4444",  # Red
            "bg_color": "rgba(239, 68, 68, 0.1)"
        },
        "never": {
            "icon": "⏳",
            "color": "#6b7280",  # Gray
            "bg_color": "rgba(107, 114, 128, 0.1)"
        }
    }

    config = status_config.get(sync_info["status"], status_config["never"])

    # Format next sync time if requested
    next_sync_text = ""
    if show_next_sync and sync_info["next_sync"]:
        next_sync_text = f" • Next: {sync_info['next_sync'].strftime('%H:%M')}"

    # Render status badge
    st.markdown(
        f"""
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            background: {config['bg_color']};
            border: 1px solid {config['color']};
            border-radius: 8px;
            font-size: 12px;
            font-weight: 500;
            color: {config['color']};
        ">
            <span style="font-size: 14px;">{config['icon']}</span>
            <span>{sync_info['message']}{next_sync_text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    return sync_info


def render_last_update_footer():
    """
    Render last update info in footer style.

    Example:
        render_last_update_footer()
    """
    sync_info = get_sync_status()

    if sync_info["last_sync"]:
        time_str = sync_info["last_sync"].strftime("%d/%m/%Y • %H:%M")
        st.markdown(
            f"""
            <div style="
                text-align: center;
                font-size: 11px;
                color: #6b7280;
                padding: 8px 0;
                border-top: 1px solid #e5e7eb;
                margin-top: 20px;
            ">
                📅 Last Update: {time_str}
                <br>
                <span style="color: #9ca3af;">{sync_info['message']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="
                text-align: center;
                font-size: 11px;
                color: #ef4444;
                padding: 8px 0;
                border-top: 1px solid #e5e7eb;
                margin-top: 20px;
            ">
                ⚠️ Data belum tersedia. Silakan refresh.
            </div>
            """,
            unsafe_allow_html=True
        )

"""
Refresh Manager - Enhanced manual refresh with immediate sync

Provides manual refresh functionality that triggers immediate sync
from OneDrive with proper error handling and user feedback.
"""
import time
import os
import pickle
import streamlit as st
from datetime import datetime

from config import ONEDRIVE_LINKS, CACHE_FILE, SYNC_INTERVAL
from backend.data_loader import load_data, extract_sheets, normalize_dataframes, parse_input_plan
from utils.logger import get_logger

logger = get_logger("refresh_manager")


def trigger_immediate_sync() -> dict:
    """
    Trigger immediate sync from OneDrive (bypasses background sync).

    This is called when user clicks manual refresh button.
    Fetches fresh data from OneDrive and updates cache file.

    Returns:
        dict with keys:
        - success: bool
        - message: str
        - duration: float (seconds)
        - timestamp: datetime
    """
    start_time = time.time()

    try:
        logger.info("Manual sync triggered by user")

        # Show loading spinner
        with st.spinner("🔄 Mengambil data terbaru dari OneDrive..."):
            # 1. Fetch data from OneDrive
            data = load_data()

            if not data:
                return {
                    "success": False,
                    "message": "Gagal mengambil data dari OneDrive. Silakan cek koneksi internet.",
                    "duration": time.time() - start_time,
                    "timestamp": datetime.now()
                }

            # 2. Process data
            if isinstance(data, dict) and "sheets" in data:
                sheets = data["sheets"]
                input_values = data["input_values"]
            else:
                sheets = extract_sheets(data)
                normalize_dataframes(sheets)
                input_values = parse_input_plan(sheets["input_plan"])

            # 3. Save to cache atomically
            cache_data = {
                "sheets": sheets,
                "input_values": input_values,
                "timestamp": time.time()
            }

            # Ensure directory exists
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

            # Atomic write
            temp_file = CACHE_FILE + ".tmp"
            with open(temp_file, "wb") as f:
                pickle.dump(cache_data, f)
            os.replace(temp_file, CACHE_FILE)

            duration = time.time() - start_time

            logger.info(f"Manual sync completed successfully in {duration:.2f}s")

            return {
                "success": True,
                "message": f"Data berhasil diupdate! ({duration:.1f}s)",
                "duration": duration,
                "timestamp": datetime.now(),
                "sheets": sheets,
                "input_values": input_values
            }

    except Exception as e:
        logger.error(f"Manual sync failed: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "duration": time.time() - start_time,
            "timestamp": datetime.now()
        }


def render_refresh_button(
    label: str = "🔄 Refresh Data",
    help_text: str = "Update data dari OneDrive",
    key: str = "manual_refresh"
) -> bool:
    """
    Render enhanced refresh button with immediate sync.

    Args:
        label: Button label text
        help_text: Tooltip text
        key: Unique key for the button

    Returns:
        bool: True if refresh was clicked

    Example:
        if render_refresh_button():
            st.success("Data berhasil diupdate!")
    """
    # Container for button and status
    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            clicked = st.button(
                label,
                help=help_text,
                use_container_width=True,
                key=key
            )

        with col2:
            # Show current sync status
            from ui.sync_status import get_sync_status
            sync_info = get_sync_status()

            status_icons = {
                "synced": "✅",
                "syncing": "🔄",
                "stale": "⚠️",
                "error": "❌",
                "never": "⏳"
            }

            icon = status_icons.get(sync_info["status"], "❓")
            st.markdown(
                f"""
                <div style="
                    text-align: center;
                    padding: 8px;
                    font-size: 20px;
                ">
                    {icon}
                </div>
                """,
                unsafe_allow_html=True
            )

            # Show status message on hover
            st.caption(sync_info["message"])

        return clicked


def handle_manual_refresh():
    """
    Handle manual refresh with full flow:
    1. Trigger sync
    2. Show progress/error
    3. Update session state
    4. Rerun app

    Call this from your main app or page.

    Example:
        if handle_manual_refresh():
            st.rerun()
    """
    if render_refresh_button():
        # Trigger immediate sync
        result = trigger_immediate_sync()

        if result["success"]:
            # Update session state with fresh data
            st.session_state["sheets"] = result["sheets"]
            st.session_state["input_values"] = result["input_values"]
            st.session_state["cache_mtime"] = os.path.getmtime(CACHE_FILE)

            # Show success message
            st.success(f"✅ {result['message']}")
            st.balloons()

            logger.info("Session state updated with fresh data")

            # Auto rerun after short delay
            time.sleep(1)
            st.rerun()

        else:
            # Show error message
            st.error(f"❌ {result['message']}")
            st.info("💡 Tips: Pastikan koneksi internet stabil dan OneDrive link valid.")

            return False

    return False

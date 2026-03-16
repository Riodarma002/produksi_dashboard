"""
Sync Manager — Background data synchronization for the dashboard.
Runs a daemon thread that fetches data every hour and saves it to a local pickle cache.
"""
import threading
import time
import os
import pickle
import logging
from pathlib import Path

from config import SYNC_INTERVAL, CACHE_FILE

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncManager:
    _instance = None
    _lock = threading.Lock()
    _thread = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SyncManager, cls).__new__(cls)
                cls._instance.initialized = False
        return cls._instance

    def start_sync(self):
        """Start the background sync thread if not already running."""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return

            self._thread = threading.Thread(target=self._sync_worker, daemon=True)
            self._thread.start()
            logger.info("Background sync thread started.")

    def _sync_worker(self):
        """Infinite loop to fetch data periodically."""
        # Delayed import to avoid circular dependency
        from backend.data_loader import load_data, extract_sheets, normalize_dataframes, parse_input_plan

        while True:
            try:
                logger.info("Starting background data sync...")
                
                # 1. Fetch data (runs synchronously in this thread)
                # Note: We bypass st.cache_data here by calling the underlying logic
                # or we just rely on the fact that this is a separate thread.
                # Since st.cache_data is bound to the streamlit session, we need
                # a way to fetch data without requiring a streamlit context if possible.
                
                # For now, let's use a non-cached version of loading for the worker
                data = self._fetch_raw_data()
                if data:
                    sheets = extract_sheets(data)
                    normalize_dataframes(sheets)
                    input_values = parse_input_plan(sheets["input_plan"])
                    
                    # 2. Save to local pickle file atomically
                    cache_data = {
                        "sheets": sheets,
                        "input_values": input_values,
                        "timestamp": time.time()
                    }
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
                    
                    # Write to temp file first then rename for atomicity
                    temp_file = CACHE_FILE + ".tmp"
                    with open(temp_file, "wb") as f:
                        pickle.dump(cache_data, f)
                    os.replace(temp_file, CACHE_FILE)
                    
                    logger.info(f"Sync complete. Data saved to {CACHE_FILE}")
                else:
                    logger.warning("Sync failed: No data fetched.")

            except Exception as e:
                logger.error(f"Error in background sync worker: {e}")

            # Wait for the next interval
            time.sleep(SYNC_INTERVAL)

    def _fetch_raw_data(self):
        """Bypass Streamlit cache to fetch raw data directly."""
        import requests
        import pandas as pd
        import io
        from config import ONEDRIVE_LINKS, AZURE_CLIENT_SECRET
        from backend.azure_api import download_excel_from_graph

        result = {}
        for name, url in ONEDRIVE_LINKS.items():
            try:
                # Try Azure API
                if AZURE_CLIENT_SECRET:
                    sheets = download_excel_from_graph(url)
                    if sheets:
                        result[name] = sheets
                        continue

                # Fallback to direct download
                dl = url.split("?")[0] + "?download=1"
                r = requests.get(dl, timeout=60, allow_redirects=True,
                                 headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
                result[name] = pd.read_excel(
                    io.BytesIO(r.content), sheet_name=None, engine="openpyxl"
                )
            except Exception as e:
                logger.error(f"Failed to fetch {name}: {e}")
        
        return result if len(result) == len(ONEDRIVE_LINKS) else None

# Singleton accessor
sync_manager = SyncManager()

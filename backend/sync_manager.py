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
    _is_syncing = False
    _last_sync_status = {"success": False, "message": "", "timestamp": None}

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

    def is_syncing(self) -> bool:
        """Check if sync is currently in progress."""
        return self._is_syncing

    def get_last_sync_status(self) -> dict:
        """Get last sync status."""
        return self._last_sync_status.copy()

    def trigger_immediate_sync(self) -> dict:
        """
        Trigger immediate sync (can be called manually).
        This runs synchronously and returns the result.
        """
        self._is_syncing = True
        try:
            result = self._sync_once()
            self._last_sync_status = result
            return result
        finally:
            self._is_syncing = False

    def _sync_once(self) -> dict:
        """
        Perform a single sync operation.

        Returns:
            dict with keys: success (bool), message (str), duration (float)
        """
        from backend.data_loader import load_data, extract_sheets, normalize_dataframes, parse_input_plan

        start_time = time.time()
        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                logger.info(f"Starting sync attempt {retry_count + 1}/{max_retries}")

                # 1. Fetch data
                data = self._fetch_raw_data()
                if not data:
                    raise Exception("Failed to fetch data from OneDrive")

                # 2. Process data
                sheets = extract_sheets(data)
                normalize_dataframes(sheets)
                input_values = parse_input_plan(sheets["input_plan"])

                # 3. Save to cache atomically
                cache_data = {
                    "sheets": sheets,
                    "input_values": input_values,
                    "timestamp": time.time()
                }

                os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
                temp_file = CACHE_FILE + ".tmp"
                with open(temp_file, "wb") as f:
                    pickle.dump(cache_data, f)
                os.replace(temp_file, CACHE_FILE)

                duration = time.time() - start_time
                logger.info(f"Sync completed successfully in {duration:.2f}s")

                return {
                    "success": True,
                    "message": f"Sync berhasil ({duration:.1f}s)",
                    "duration": duration,
                    "timestamp": datetime.now()
                }

            except Exception as e:
                retry_count += 1
                logger.error(f"Sync attempt {retry_count} failed: {e}")

                if retry_count >= max_retries:
                    duration = time.time() - start_time
                    logger.error(f"All sync attempts failed after {duration:.2f}s")

                    return {
                        "success": False,
                        "message": f"Sync gagal setelah {max_retries} percobaan: {str(e)}",
                        "duration": duration,
                        "timestamp": datetime.now()
                    }
                else:
                    # Exponential backoff: 2^retry_count seconds
                    backoff_time = 2 ** retry_count
                    logger.warning(f"Retrying in {backoff_time}s...")
                    time.sleep(backoff_time)

        return {
            "success": False,
            "message": "Unknown error",
            "duration": time.time() - start_time,
            "timestamp": datetime.now()
        }

    def _sync_worker(self):
        """Infinite loop to fetch data periodically."""
        while True:
            try:
                self._is_syncing = True
                result = self._sync_once()
                self._last_sync_status = result
                self._is_syncing = False

                if not result["success"]:
                    logger.warning(f"Background sync failed: {result['message']}")

            except Exception as e:
                logger.error(f"Error in background sync worker: {e}", exc_info=True)
                self._is_syncing = False

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

"""
Sync Manager — Background data synchronization for the dashboard.
Runs a daemon thread that fetches data every hour and saves it to a local pickle cache.
"""
import threading
import time
import os
import pickle
import logging
from datetime import datetime, timedelta
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
        consecutive_failures = 0
        max_consecutive_failures = 5

        while True:
            try:
                self._is_syncing = True
                result = self._sync_once()
                self._last_sync_status = result
                self._is_syncing = False

                if result["success"]:
                    consecutive_failures = 0
                    logger.info(f"Background sync completed: {result['message']}")
                else:
                    consecutive_failures += 1
                    logger.warning(f"Background sync failed ({consecutive_failures}/{max_consecutive_failures}): {result['message']}")

                    # If too many consecutive failures, increase wait time to avoid spam
                    if consecutive_failures >= max_consecutive_failures:
                        logger.error(f"Too many consecutive failures ({consecutive_failures}), waiting 5 minutes before retry")
                        time.sleep(300)  # Wait 5 minutes
                        consecutive_failures = 0  # Reset counter after long wait

            except Exception as e:
                consecutive_failures += 1
                logger.error(f"Error in background sync worker ({consecutive_failures}/{max_consecutive_failures}): {e}", exc_info=True)
                self._is_syncing = False

                # If too many consecutive failures, increase wait time
                if consecutive_failures >= max_consecutive_failures:
                    logger.error(f"Too many consecutive exceptions ({consecutive_failures}), waiting 5 minutes before retry")
                    time.sleep(300)  # Wait 5 minutes
                    consecutive_failures = 0  # Reset counter after long wait

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
                # Try Azure API first
                if AZURE_CLIENT_SECRET:
                    try:
                        logger.info(f"Attempting Azure Graph API download for {name}...")
                        sheets = download_excel_from_graph(url)
                        if sheets:
                            result[name] = sheets
                            logger.info(f"✅ Successfully downloaded {name} via Azure Graph API")
                            continue
                        else:
                            logger.warning(f"Azure Graph API returned None for {name}")
                    except Exception as azure_err:
                        logger.warning(f"Azure Graph API failed for {name}: {azure_err}")

                # Fallback to direct download
                logger.info(f"Attempting direct download for {name}...")
                dl = url.split("?")[0] + "?download=1"
                r = requests.get(dl, timeout=60, allow_redirects=True,
                                 headers={"User-Agent": "Mozilla/5.0"})

                # Log response info for debugging
                logger.info(f"Response status: {r.status_code}")
                logger.info(f"Response content-type: {r.headers.get('content-type', 'unknown')}")
                logger.info(f"Response size: {len(r.content)} bytes")

                # Check if we got HTML instead of Excel file
                content_type = r.headers.get('content-type', '').lower()
                if 'text/html' in content_type or b'<html' in r.content[:100]:
                    logger.error(f"Got HTML page instead of Excel file for {name}")
                    logger.error(f"First 200 chars: {r.content[:200]}")
                    raise Exception(f"Download returned HTML page instead of Excel file. Check if OneDrive link requires authentication.")

                r.raise_for_status()

                # Validate that we got a valid Excel file by checking magic bytes
                # Excel files (XLSX) are ZIP files starting with PK
                if len(r.content) < 4 or r.content[:2] != b'PK':
                    logger.error(f"Downloaded content for {name} is not a valid Excel/ZIP file")
                    logger.error(f"First 20 bytes (hex): {r.content[:20].hex()}")
                    raise Exception(f"Downloaded file is not a valid Excel format")

                # Try to parse the Excel file
                try:
                    result[name] = pd.read_excel(
                        io.BytesIO(r.content), sheet_name=None, engine="openpyxl"
                    )
                    logger.info(f"✅ Successfully downloaded and parsed {name} via direct download")
                except Exception as parse_err:
                    logger.error(f"Failed to parse Excel file for {name}: {parse_err}")
                    raise

            except Exception as e:
                logger.error(f"Failed to fetch {name}: {e}")
                import traceback
                logger.error(f"Full traceback:\n{traceback.format_exc()}")

        # Only return result if we successfully fetched all files
        if len(result) == len(ONEDRIVE_LINKS):
            logger.info(f"✅ Successfully fetched all {len(result)} files")
            return result
        else:
            logger.error(f"Only fetched {len(result)}/{len(ONEDRIVE_LINKS)} files")
            return None

# Singleton accessor
sync_manager = SyncManager()

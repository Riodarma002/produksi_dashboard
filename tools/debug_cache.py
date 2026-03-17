"""
Debug Cache Tool - Check cache data and available dates
"""
import pickle
import os
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import CACHE_FILE

def check_cache():
    print("=" * 60)
    print("CACHE DEBUG TOOL")
    print("=" * 60)

    if not os.path.exists(CACHE_FILE):
        print(f"Cache file tidak ada: {CACHE_FILE}")
        return

    mtime = os.path.getmtime(CACHE_FILE)
    size = os.path.getsize(CACHE_FILE)
    mtime_dt = datetime.fromtimestamp(mtime)

    print(f"\nCache File: {CACHE_FILE}")
    print(f"Last Modified: {mtime_dt}")
    print(f"Size: {size:,} bytes")

    try:
        with open(CACHE_FILE, 'rb') as f:
            cache_data = pickle.load(f)

        print(f"\nCache loaded successfully!")

        if isinstance(cache_data, dict):
            print(f"\nCache keys: {list(cache_data.keys())}")

            if 'sheets' in cache_data:
                sheets = cache_data['sheets']
                print(f"\nSheets available: {list(sheets.keys())}")

                if 'prod_ob' in sheets:
                    prod_ob = sheets['prod_ob']
                    if not prod_ob.empty and 'Date' in prod_ob.columns:
                        dates = prod_ob['Date'].dropna().unique()
                        dates = sorted(dates)

                        print(f"\nTanggal yang tersedia ({len(dates)} dates):")
                        for i, date in enumerate(dates[-10:], 1):
                            date_str = str(date.date())
                            print(f"   {i}. {date_str}")

                        print(f"\nTanggal terbaru: {dates[-1].date()}")

                        today = datetime.now().date()
                        if dates[-1].date() == today:
                            print(f"Data hari ini SUDAH TERSEDIA!")
                        else:
                            print(f"Data terbaru: {dates[-1].date()}")
                            print(f"Hari ini: {today}")
                            print(f"SELISIH: {(today - dates[-1].date()).days} hari")

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_cache()

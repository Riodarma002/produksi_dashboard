import pandas as pd
import pickle
import os

CACHE_FILE = "data/cache.pkl"

def raw_check():
    if not os.path.exists(CACHE_FILE):
        print("No cache")
        return
    with open(CACHE_FILE, "rb") as f:
        data = pickle.load(f)
    
    # Check "db_hourly" which is the raw dict of sheets
    db_hourly = data.get("raw_data", {}).get("db_hourly", {})
    if not db_hourly:
        # Try if it's in a different format
        db_hourly = data.get("db_hourly", {})
        
    rain_raw = db_hourly.get("Rain")
    if rain_raw is not None:
        print("Raw Rain Columns:", rain_raw.columns.tolist())
        print("\nRaw Rain Head:")
        print(rain_raw.head(10))
        
        # Check if there are any non-dash values
        for col in rain_raw.columns:
            non_dash = rain_raw[rain_raw[col].astype(str).str.strip() != "-"]
            if not non_dash.empty:
                print(f"\nCol '{col}' has non-dash values:")
                print(non_dash[col].unique()[:10])
    else:
        print("Raw Rain sheet not found in db_hourly")

if __name__ == "__main__":
    raw_check()

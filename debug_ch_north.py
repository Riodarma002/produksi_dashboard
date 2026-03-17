import pandas as pd
import pickle
import os

CACHE_FILE = "data/cache.pkl"

def check_north_jo_ic_ch():
    if not os.path.exists(CACHE_FILE):
        print("No cache file found")
        return

    with open(CACHE_FILE, "rb") as f:
        data = pickle.load(f)
    
    # Check Hourly Database
    db_hourly = data.get("db_hourly")
    if db_hourly is not None and not db_hourly.empty:
        # Filter for recent data & North JO IC
        recent = db_hourly.sort_values("Date", ascending=False).head(500)
        north_ic = recent[recent["PIT"].astype(str).str.contains("IC", case=False, na=False)]
        print(f"--- db_hourly records for North JO IC ---")
        print(north_ic[["Date", "PIT", "Hour LU", "Volume OB", "Volume CH"]].head(15))
        print("Data types:")
        print(north_ic[["Volume OB", "Volume CH"]].dtypes)
    else:
        print("db_hourly empty or missing")

if __name__ == "__main__":
    check_north_jo_ic_ch()

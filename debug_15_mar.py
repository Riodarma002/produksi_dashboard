import pandas as pd
import pickle
import os

CACHE_FILE = "data/cache.pkl"

def print_15_mar():
    if not os.path.exists(CACHE_FILE):
        return
    with open(CACHE_FILE, "rb") as f:
        data = pickle.load(f)
    
    sheets = data.get("sheets", {})
    rain = sheets.get("rain")
    
    if rain is None or rain.empty:
        return
        
    match = rain[rain["Date"].astype(str).str.contains("2026-03-15")]
    if match.empty:
        print("No data for 15-Mar-26 in Rain sheet")
        print("Available dates:", rain["Date"].unique().tolist())
    else:
        print(f"Data for 15-Mar-26 ({len(match)} rows):")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(match)

if __name__ == "__main__":
    print_15_mar()

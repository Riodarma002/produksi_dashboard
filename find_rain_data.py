import pandas as pd
import pickle
import os

CACHE_FILE = "data/cache.pkl"

def find_data_column():
    if not os.path.exists(CACHE_FILE):
        print("No cache")
        return
    with open(CACHE_FILE, "rb") as f:
        data = pickle.load(f)
    
    sheets = data.get("sheets", {})
    rain = sheets.get("rain")
    
    if rain is None or rain.empty:
        print("Rain sheet missing")
        return
        
    print(f"Checking {len(rain)} rows in Rain sheet...")
    for col in rain.columns:
        # Try to convert to numeric, ignore strings like "-"
        vals = pd.to_numeric(rain[col], errors="coerce").fillna(0)
        non_zero = rain[vals > 0]
        if not non_zero.empty:
            print(f"FOUND DATA in '{col}': {len(non_zero)} rows > 0.")
            print(non_zero[["Date", "PIT Fix", "Hour LU", col]].head(10))
            
if __name__ == "__main__":
    find_data_column()

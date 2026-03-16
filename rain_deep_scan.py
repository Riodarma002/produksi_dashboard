import pandas as pd
import pickle
import os

CACHE_FILE = "data/cache.pkl"

def rain_sheet_deep_scan():
    if not os.path.exists(CACHE_FILE):
        return
    with open(CACHE_FILE, "rb") as f:
        data = pickle.load(f)
    
    sheets = data.get("sheets", {})
    rain = sheets.get("rain")
    
    if rain is None:
        print("Rain sheet not in processed sheets")
        return
        
    print("Rain Sheet Columns:", rain.columns.tolist())
    print("\nRain Sheet Summary:")
    print(rain.describe(include='all'))
    
    # Check for non-zero in ANY column
    for col in rain.columns:
        if rain[col].dtype in ['float64', 'int64', 'int32']:
            nz = rain[rain[col] > 0]
            if not nz.empty:
                print(f"Column '{col}' HAS {len(nz)} non-zero numeric values.")
        else:
            # Check if it has non-dash strings
            nz_s = rain[(rain[col].astype(str).str.strip() != "-") & (rain[col].astype(str).str.strip() != "0") & (rain[col].astype(str).str.strip() != "")]
            # Filter out known categorical cols
            if col not in ["Date", "Shift", "Hour", "PIT", "Hour LU", "Shift Fix", "PIT Fix", "Hour Fix"]:
                if not nz_s.empty:
                    print(f"Column '{col}' HAS {len(nz_s)} non-dash string values.")
                    print(nz_s[col].unique()[:5])

if __name__ == "__main__":
    rain_sheet_deep_scan()

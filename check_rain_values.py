import pandas as pd
import pickle
import os

CACHE_FILE = "data/cache.pkl"

def check_rain_data():
    if not os.path.exists(CACHE_FILE):
        print("Cache not found")
        return

    with open(CACHE_FILE, "rb") as f:
        data = pickle.load(f)
    
    sheets = data.get("sheets", {})
    rain = sheets.get("rain")
    
    if rain is None or rain.empty:
        print("Rain sheet missing or empty")
        return
        
    print("Rain Columns:", rain.columns.tolist())
    
    # Check for non-zero values in potential columns
    cols = ["Minute", "Duration", "Rain", "Rainfall", "VALUE"]
    for col in cols:
        if col in rain.columns:
            # Convert to numeric to be sure
            vals = pd.to_numeric(rain[col], errors="coerce").fillna(0)
            non_zero = rain[vals > 0]
            if not non_zero.empty:
                print(f"Column '{col}' HAS {len(non_zero)} non-zero rows.")
                print(non_zero[["Date", "PIT Fix", "Hour LU", col]].head(5))
            else:
                print(f"Column '{col}' is all zero/empty")
        else:
            print(f"Column '{col}' NOT FOUND")

if __name__ == "__main__":
    check_rain_data()

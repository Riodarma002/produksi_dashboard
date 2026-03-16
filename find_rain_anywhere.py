import pandas as pd
import pickle
import os

CACHE_FILE = "data/cache.pkl"

def find_rain_column_anywhere():
    if not os.path.exists(CACHE_FILE):
        return
    with open(CACHE_FILE, "rb") as f:
        data = pickle.load(f)
    
    sheets = data.get("sheets", {})
    for s_name, df in sheets.items():
        if df is not None and not df.empty:
            rain_cols = [c for c in df.columns if "rain" in c.lower()]
            if rain_cols:
                print(f"Sheet '{s_name}' has rain-related columns: {rain_cols}")
                # Check for values
                for rc in rain_cols:
                    try:
                        vals = pd.to_numeric(df[rc], errors="coerce").fillna(0)
                        if (vals > 0).any():
                            print(f"  -> Column '{rc}' HAS DATA!")
                    except:
                        pass
                        
if __name__ == "__main__":
    find_rain_column_anywhere()

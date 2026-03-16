import pandas as pd
import pickle
import os

CACHE_FILE = "data/cache.pkl"

def string_check():
    if not os.path.exists(CACHE_FILE):
        return
    with open(CACHE_FILE, "rb") as f:
        data = pickle.load(f)
    
    sheets = data.get("sheets", {})
    rain = sheets.get("rain")
    
    if rain is None or rain.empty:
        return
        
    for col in ["Duration", "Minute"]:
        if col in rain.columns:
            # Filter rows where value is not "-" and not "0" and not null
            content = rain[
                (rain[col].astype(str).str.strip() != "-") & 
                (rain[col].astype(str).str.strip() != "0") &
                (rain[col].astype(str).str.strip() != "0.0") &
                (rain[col].notna())
            ]
            if not content.empty:
                print(f"Content found in '{col}':")
                print(content[["Date", "PIT Fix", "Hour LU", col]].head(20))
            else:
                print(f"Column '{col}' is ONLY dashes or zeros.")
                
if __name__ == "__main__":
    string_check()

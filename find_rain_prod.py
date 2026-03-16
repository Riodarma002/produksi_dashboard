import pandas as pd
import pickle
import os

CACHE_FILE = "data/cache.pkl"

def search_production_sheets():
    if not os.path.exists(CACHE_FILE):
        return
    with open(CACHE_FILE, "rb") as f:
        data = pickle.load(f)
    
    sheets = data.get("sheets", {})
    for name in ["prod_ob", "prod_ch"]:
        df = sheets.get(name)
        if df is not None and not df.empty:
            cols = [c for c in df.columns if "rain" in c.lower()]
            if cols:
                print(f"Sheet '{name}' has columns: {cols}")
                # Check for non-zero
                for c in cols:
                    vals = pd.to_numeric(df[c], errors="coerce").fillna(0)
                    if (vals > 0).any():
                        print(f"  -> Column '{c}' HAS DATA in '{name}'!")
            
if __name__ == "__main__":
    search_production_sheets()

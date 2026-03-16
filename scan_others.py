import pandas as pd
import pickle
import os

CACHE_FILE = "data/cache.pkl"

def scan_other_potential_sheets():
    if not os.path.exists(CACHE_FILE):
        return
    with open(CACHE_FILE, "rb") as f:
        data = pickle.load(f)
    
    sheets = data.get("sheets", {})
    for name in ["coal_rom", "master_db"]:
        df = sheets.get(name)
        if df is not None and not df.empty:
            print(f"\nSheet '{name}' Columns: {df.columns.tolist()[:20]}")
            # Search for any rain, delay, or duration
            targets = [c for c in df.columns if any(x in str(c).lower() for x in ["rain", "hujan", "delay", "dur"])]
            for t in targets:
                print(f"  -> Found potential column '{t}' in '{name}'")
                vals = pd.to_numeric(df[t], errors="coerce").fillna(0)
                if (vals > 0).any():
                    print(f"     *** Column '{t}' HAS DATA! ***")
                    print(df[vals > 0][["Date", "Hour LU", t]].head(5))

if __name__ == "__main__":
    scan_other_potential_sheets()

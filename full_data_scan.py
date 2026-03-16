import pandas as pd
import pickle
import os

CACHE_FILE = "data/cache.pkl"

def full_columns_check():
    if not os.path.exists(CACHE_FILE):
        return
    with open(CACHE_FILE, "rb") as f:
        data = pickle.load(f)
    
    # Check "db_hourly" if it's there
    # Wait, data_loader.py load_data returns the whole cached dict if "sheets" in it.
    sheets = data.get("sheets", {})
    if not sheets:
        sheets = data
        
    for s_name, df in sheets.items():
        if df is not None:
            print(f"Sheet '{s_name}' Columns: {df.columns.tolist()[:10]} ...")
            # Search for any non-zero numeric data in columns with "rain", "dur", "min"
            target_cols = [c for c in df.columns if any(x in str(c).lower() for x in ["rain", "dur", "min"])]
            for tc in target_cols:
                try:
                    vals = pd.to_numeric(df[tc], errors="coerce").fillna(0)
                    if (vals > 0).any():
                        print(f"  -> FOUND DATA in '{s_name}.{tc}'! Sample non-zero:")
                        print(df[vals > 0][[tc, "Date"]].head(3))
                except:
                    pass

if __name__ == "__main__":
    full_columns_check()

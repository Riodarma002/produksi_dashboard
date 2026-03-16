import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__name__)))
from backend.data_loader import load_data, extract_sheets, normalize_dataframes
from config import OP_HOURS

def debug_hours():
    try:
        data = load_data()
        sheets = extract_sheets(data)
        normalize_dataframes(sheets)
        
        prod_ch = sheets.get("prod_ch")
        if prod_ch is not None and not prod_ch.empty:
            print("--- prod_ch 'Hour LU' values ---")
            unique_hours = prod_ch["Hour LU"].unique()
            print("Unique Hour LU:", unique_hours)
            print("DType:", prod_ch["Hour LU"].dtype)
            
            # OP_HOURS comparison
            print("\nOP_HOURS from config:", OP_HOURS)
            
            # simulate merge
            import pandas as pd
            hourly = prod_ch.groupby("Hour LU")["Volume"].sum().reset_index()
            hourly.columns = ["Hour", "Actual"]
            
            hourly_full = pd.DataFrame({"Hour": OP_HOURS})
            merged = hourly_full.merge(hourly, on="Hour", how="left")
            
            print("\nMerged sample (first 10):")
            print(merged.head(10))
            
            print("\nNon-null matches after merge:")
            print(merged.dropna())
            
        else:
            print("prod_ch missing or empty")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    debug_hours()

import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__name__)))
from backend.data_loader import load_data, extract_sheets, normalize_dataframes

def check_dates():
    try:
        data = load_data()
        sheets = extract_sheets(data)
        normalize_dataframes(sheets)  # Apply the exact app formatting
        
        prod_ch = sheets.get("prod_ch")
        if prod_ch is not None and not prod_ch.empty:
            print("--- Date Info for prod_ch ---")
            print(f"DType of Date column: {prod_ch['Date'].dtype}")
            print(f"Min Date: {prod_ch['Date'].min()}")
            print(f"Max Date: {prod_ch['Date'].max()}")
            
            # Check for the specific date from the user screenshot (15 March 2026)
            target_date = pd.Timestamp("2026-03-15")
            mask = (prod_ch["Date"] == target_date) & (prod_ch["PIT Fix"] == "South JO IC")
            
            filtered = prod_ch[mask]
            print(f"\nRows for South JO IC on 2026-03-15: {len(filtered)}")
            if len(filtered) > 0:
                print(f"Volume for that day: {filtered['Volume'].sum()}")
                
                # Further check if volume might be stored as string somehow after normalization
                print(f"Volume DType: {filtered['Volume'].dtype}")
                if filtered['Volume'].dtype == object:
                    print("Sample values (first 5):", filtered['Volume'].head().tolist())
            else:
                print("No rows found for 2026-03-15!")
                # Show available dates for South JO IC
                sjo = prod_ch[prod_ch["PIT Fix"] == "South JO IC"]
                print("Available dates for South JO IC:")
                print(sjo["Date"].value_counts())
                
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check_dates()

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__name__)))
from backend.data_loader import load_data

def check_raw():
    try:
        # Load fresh data (bypassing cache if necessary by deleting cache first)
        data = load_data()
        db_hourly = data.get("db_hourly", {})
        
        print("--- RAW PIT FIX VALUES ---")
        for sheet in ["Vol Hauling North", "Vol Hauling South", "Vol OB GPE Selatan", "Vol OB MGE"]:
            if sheet in db_hourly:
                df = db_hourly[sheet]
                if "PIT Fix" in df.columns:
                    print(f"\nSheet {sheet} - 'PIT Fix' raw values:")
                    print(df["PIT Fix"].dropna().unique())
                else:
                    print(f"\nSheet {sheet} has no 'PIT Fix' column.")
            else:
                print(f"\nSheet {sheet} not found.")
                
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check_raw()

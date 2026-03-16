import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__name__)))
from backend.data_loader import load_data

def investigate_pits():
    try:
        data = load_data()
        db_hourly = data.get("db_hourly", {})
        
        sheet_name = "Vol Hauling South"
        if sheet_name in db_hourly:
            df = db_hourly[sheet_name]
            print(f"--- RAW COLUMNS IN {sheet_name} ---")
            print(df.columns.tolist())
            
            # Check PIT column
            if "PIT" in df.columns:
                print("\nUnique raw values in 'PIT':")
                print(df["PIT"].value_counts())
            
            if "PIT Fix" in df.columns:
                print("\nUnique raw values in 'PIT Fix':")
                print(df["PIT Fix"].value_counts())
                
            if "SubKontraktor" in df.columns:
                print("\nUnique raw values in 'SubKontraktor':")
                print(df["SubKontraktor"].value_counts())
                
            if "Kontraktor" in df.columns:
                print("\nUnique raw values in 'Kontraktor':")
                print(df["Kontraktor"].value_counts())
        else:
            print(f"Sheet {sheet_name} not found.")
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    investigate_pits()

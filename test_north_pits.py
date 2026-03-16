import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__name__)))
from backend.data_loader import load_data, extract_sheets

def investigate_north():
    try:
        data = load_data()
        db_hourly = data.get("db_hourly", {})
        
        # Look at Vol Hauling North
        if "Vol Hauling North" in db_hourly:
            df_n = db_hourly["Vol Hauling North"]
            print("--- Vol Hauling North ---")
            if "PIT Fix" in df_n.columns:
                print("North PIT Fix:", df_n["PIT Fix"].unique())
            if "Kontraktor" in df_n.columns:
                print("North Kontraktor:", df_n["Kontraktor"].unique())
            if "SubKontraktor" in df_n.columns:
                print("North SubKontraktor:", df_n["SubKontraktor"].unique())
        
        # Look at Vol Hauling South
        if "Vol Hauling South" in db_hourly:
            df_s = db_hourly["Vol Hauling South"]
            print("\n--- Vol Hauling South ---")
            for col in ["PIT", "PIT Fix", "Kontraktor", "SubKontraktor"]:
                if col in df_s.columns:
                    print(f"South {col}:", df_s[col].unique())
                    
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    investigate_north()

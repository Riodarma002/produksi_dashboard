import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__name__)))
from backend.data_loader import load_data, extract_sheets

def analyze_raw_data():
    try:
        data = load_data()
        db_hourly = data.get("db_hourly", {})
        
        with open("analysis_output.txt", "w", encoding="utf-8") as f:
            f.write("=== Data Successfully Fetched ===\n")
            f.write(f"Keys present: {list(data.keys())}\n\n")

            for sname in ["Vol Hauling North", "Vol Hauling South"]:
                if sname in db_hourly:
                    df = db_hourly[sname]
                    f.write(f"+++ RAW SHEET: {sname} +++\n")
                    f.write(f"Columns: {df.columns.tolist()}\n")
                    
                    target_cols = [c for c in df.columns if "netto" in str(c).lower() or "volume" in str(c).lower()]
                    f.write(f"Target Value Columns: {target_cols}\n\n")
                    
                    if target_cols:
                        for c in target_cols:
                            f.write(f"Sample raw data for '{c}':\n")
                            f.write(f"{df[c].dropna().head(10)}\n")
                            f.write(f"DType of '{c}': {df[c].dtype}\n\n")
                else:
                    f.write(f"\nRAW SHEET '{sname}' NOT FOUND\n")

            f.write("=== EXTRACT SHEETS BEHAVIOR ===\n")
            sheets = extract_sheets(data)
            prod_ch = sheets.get("prod_ch")
            
            if prod_ch is not None and not prod_ch.empty:
                f.write(f"prod_ch extracted successfully. Shape: {prod_ch.shape}\n")
                f.write(f"prod_ch columns: {prod_ch.columns.tolist()}\n")
                if "Volume" in prod_ch.columns:
                    f.write(f"Sum of Volume: {prod_ch['Volume'].sum()}\n")
                if "Netto" in prod_ch.columns:
                    f.write(f"Sum of Netto: {prod_ch['Netto'].sum()}\n")
            else:
                f.write("prod_ch is EMPTY after extraction\n")
                
    except Exception as e:
        with open("analysis_output.txt", "a", encoding="utf-8") as f:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    analyze_raw_data()

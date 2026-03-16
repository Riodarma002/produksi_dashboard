import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__name__)))
from backend.data_loader import load_data, extract_sheets

def check_plans():
    try:
        data = load_data()
        sheets = extract_sheets(data)
        plan_h_ch = sheets.get("plan_h_ch")
        
        if plan_h_ch is not None and not plan_h_ch.empty:
            print("--- CH Plans ---")
            print(plan_h_ch[["PIT", "Plan_Daily"]].drop_duplicates())
        
        # Also let's check OB DB to see what PIT Fix corresponds to MGE
        prod_ob = sheets.get("prod_ob")
        if prod_ob is not None:
            db_hourly = data.get("db_hourly", {})
            for name in ["Vol OB MGE", "Vol OB GPE Utara", "Vol OB GPE Selatan", "Vol OB BDE"]:
                if name in db_hourly:
                    print(f"\n--- OB Sheet: {name} ---")
                    df = db_hourly[name]
                    if "PIT Fix" in df.columns:
                        vals = df["PIT Fix"].unique()
                        print("Raw PIT Fix:", vals)
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check_plans()

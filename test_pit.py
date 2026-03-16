import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__name__)))
from backend.data_loader import load_data, extract_sheets

def check_pits():
    try:
        data = load_data()
        sheets = extract_sheets(data)
        
        prod_ch = sheets.get("prod_ch")
        if prod_ch is not None and not prod_ch.empty:
            print("Unique PIT Fix values in prod_ch:")
            print(prod_ch["PIT Fix"].unique())
            
            # Simulate what the UI does for South JO IC
            selected_pit = "South JO IC"
            test_f = prod_ch[prod_ch["PIT Fix"] == selected_pit]
            print(f"\nRows matching '{selected_pit}': {len(test_f)}")
            if len(test_f) > 0:
                print(f"Volume for '{selected_pit}': {test_f['Volume'].sum()}")
            else:
                # Print raw pit names without formatting to see hidden characters
                print("\nRaw representation of PIT Fix values:")
                for p in prod_ch["PIT Fix"].unique():
                    print(f"'{p}' (Length: {len(str(p))})")
        else:
            print("prod_ch is empty.")
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check_pits()

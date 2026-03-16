import pandas as pd
import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.data_loader import load_data, extract_sheets, normalize_dataframes

def check_new_data():
    print("Loading data from Excel...")
    data = load_data()
    sheets = extract_sheets(data)
    normalize_dataframes(sheets)
    
    rain = sheets.get("rain")
    if rain is None or rain.empty:
        print("Rain sheet still empty!")
        return
        
    print(f"Rain sheet columns: {rain.columns.tolist()}")
    # Focus on Duration
    if "Duration" in rain.columns:
        # Check raw values before numeric conversion if possible, 
        # but normalize_dataframes already converted them.
        nz = rain[rain["Duration"] > 0]
        if not nz.empty:
            print("\nFound non-zero Duration values:")
            print(nz[["Date", "PIT Fix", "Hour LU", "Duration"]])
        else:
            print("\nDuration is still all zeros in the processed DataFrame.")
    else:
        print("\n'Duration' column not found in processed Rain sheet.")

if __name__ == "__main__":
    check_new_data()

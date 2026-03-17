import pandas as pd
import pickle
import os

CACHE_FILE = "data/cache.pkl"

def check_cached_ch():
    if not os.path.exists(CACHE_FILE):
        print("No cache file found")
        return

    with open(CACHE_FILE, "rb") as f:
        data = pickle.load(f)
    
    if "sheets" in data:
        prod_ch = data["sheets"].get("prod_ch")
        if prod_ch is not None and not prod_ch.empty:
            north_ic = prod_ch[prod_ch["PIT Fix"] == "NORTH JO IC"]
            print("--- CACHED prod_ch records for NORTH JO IC ---")
            if not north_ic.empty:
                print(north_ic.head(15))
                print(f"Total rows for North JO IC: {len(north_ic)}")
                print(f"Total Volume: {north_ic['Volume'].sum()}")
            else:
                print("No rows found for NORTH JO IC in prod_ch")
        else:
            print("prod_ch is empty or missing in sheets")

if __name__ == "__main__":
    check_cached_ch()

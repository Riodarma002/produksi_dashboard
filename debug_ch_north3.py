import requests, io, pandas as pd
from config import ONEDRIVE_LINKS

dl = ONEDRIVE_LINKS['db_hourly'].split('?')[0] + '?download=1'
r = requests.get(dl)
db_hourly = pd.read_excel(io.BytesIO(r.content), sheet_name=None, engine='openpyxl')

for sheet_name in ["Vol Hauling North"]:
    if sheet_name in db_hourly:
        df = db_hourly[sheet_name].copy()
        for col in ["Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.strip().replace("", "NaN"), errors="coerce").fillna(0)
        
        print("BEFORE FALLBACK:")
        print(f"PIT Fix NaNs: {df['PIT Fix'].isna().sum()} | Hour LU NaNs: {df['Hour LU'].isna().sum()}")
        
        if "Hour LU" in df.columns and df["Hour LU"].isna().mean() > 0.5:
            if "Hour Fix" in df.columns:
                df["Hour LU"] = df["Hour LU"].fillna(
                        pd.to_datetime(df["Hour Fix"].astype(str), errors='coerce').dt.hour.apply(
                            lambda x: f"{int(x):02d}" if pd.notna(x) else None
                        )
                    )

        if "PIT Fix" in df.columns and df["PIT Fix"].isna().mean() > 0.5:
            if "Product" in df.columns and "db" in db_hourly:
                db_sheet = db_hourly["db"]
                if "Product" in db_sheet.columns and "PIT" in db_sheet.columns:
                    prod_to_pit = dict(zip(db_sheet["Product"].dropna().astype(str).str.strip(), db_sheet["PIT"].dropna().astype(str).str.strip()))
                    df["PIT Fix"] = "TEST" # just to see if it executes
                    df["PIT Fix"] = df["PIT Fix"].fillna(df["Product"].astype(str).str.strip().map(prod_to_pit))

        print("AFTER FALLBACK:")
        print(f"PIT Fix NaNs: {df['PIT Fix'].isna().sum()} | Hour LU NaNs: {df['Hour LU'].isna().sum()}")
        print(df[["Product", "PIT Fix", "Hour LU", "Volume"]].head())

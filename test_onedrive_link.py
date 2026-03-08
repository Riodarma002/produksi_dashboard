"""Quick test: confirm Excel download and print clean results"""
import sys, os, io, base64
os.environ["PYTHONIOENCODING"] = "utf-8"
import requests, pandas as pd

LINKS = {
    "db_hourly": "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQA6M4doUWthTb2Cqog-xC3gAY6XckTv72yVV3lnHZoQ3vc?e=R8mrCK",
    "plan_hourly": "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQBK3837O3nsR5AKLRsno8PGARDeJ9RzlLfjVdPLJLPykWk?e=wYAkLX",
}

def download(url):
    dl = url.split("?")[0] + "?download=1"
    r = requests.get(dl, timeout=15, allow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code == 200 and len(r.content) > 500:
        return pd.read_excel(io.BytesIO(r.content), engine="openpyxl", sheet_name=None)
    return None

for name, url in LINKS.items():
    print(f"\n=== {name} ===", flush=True)
    sheets = download(url)
    if sheets:
        for sn, df in sheets.items():
            print(f"Sheet: {sn}", flush=True)
            print(f"  Shape: {df.shape}", flush=True)
            cols = list(df.columns)
            print(f"  Cols: {cols[:10]}", flush=True)
            if len(df) > 0:
                print(f"  Row0: {dict(list(df.iloc[0].items())[:6])}", flush=True)
    else:
        print("  FAILED", flush=True)

print("\nDONE", flush=True)

"""Preview data from OneDrive links — output to data_preview.txt"""
import io, requests, pandas as pd

LINKS = {
    "db_hourly": "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQA6M4doUWthTb2Cqog-xC3gAY6XckTv72yVV3lnHZoQ3vc?e=R8mrCK",
    "plan_hourly": "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQBK3837O3nsR5AKLRsno8PGARDeJ9RzlLfjVdPLJLPykWk?e=wYAkLX",
}

with open("data_preview.txt", "w", encoding="utf-8") as f:
    for name, url in LINKS.items():
        f.write(f"\n{'='*80}\n")
        f.write(f"FILE: {name}\n")
        f.write(f"{'='*80}\n")
        
        dl = url.split("?")[0] + "?download=1"
        r = requests.get(dl, timeout=30, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        sheets = pd.read_excel(io.BytesIO(r.content), sheet_name=None, engine="openpyxl")
        
        for sn, df in sheets.items():
            f.write(f"\n--- Sheet: {sn} | Shape: {df.shape} ---\n")
            f.write(f"Columns: {list(df.columns)}\n\n")
            f.write(df.head(5).to_string())
            f.write("\n\n")
    
    f.write("DONE\n")

print("Output written to data_preview.txt", flush=True)

"""
Analisis Data Produksi Coal Mining
Logika perhitungan: Plan, Actual, Achievement, SR, Cumulative Trend
"""

# === CELL 1: Import & Download ===
import io, requests
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
pd.set_option('display.float_format', '{:,.2f}'.format)

LINKS = {
    "db_hourly": "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQA6M4doUWthTb2Cqog-xC3gAY6XckTv72yVV3lnHZoQ3vc?e=R8mrCK",
    "plan_hourly": "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQBK3837O3nsR5AKLRsno8PGARDeJ9RzlLfjVdPLJLPykWk?e=wYAkLX",
}

def download(url):
    dl = url.split("?")[0] + "?download=1"
    r = requests.get(dl, timeout=30, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
    return pd.read_excel(io.BytesIO(r.content), sheet_name=None, engine="openpyxl")

db_hourly = download(LINKS["db_hourly"])
plan_hourly = download(LINKS["plan_hourly"])

# Extract sheets
prod_ob   = db_hourly["prod ob"]
prod_ch   = db_hourly["prod ch"]
prod_ct   = db_hourly["prod ct"]
lt_ob     = db_hourly["lt ob"]
lt_coal   = db_hourly["lt coal"]
cumm_plan = plan_hourly["Cumm Plan Vol"]

# Plan hourly per operation
plan_h_ob = plan_hourly["Plan Hourly OB"]
plan_h_ch = plan_hourly["Plan Hourly CH"]
plan_h_ct = plan_hourly["Plan Hourly CT"]

# Fix Date columns
for df in [prod_ob, prod_ch, prod_ct, lt_ob, lt_coal]:
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Normalize Hour LU to string for consistent sorting
for df in [prod_ob, prod_ch, prod_ct, cumm_plan]:
    if "Hour LU" in df.columns:
        df["Hour LU"] = df["Hour LU"].astype(str).str.zfill(2)

print("Data loaded OK")


# === CELL 2: Settings ===

# Ambil tanggal yang ada datanya (biasanya hari ini / terbaru)
valid_dates = prod_ob["Date"].dropna()
valid_dates = valid_dates[valid_dates.dt.year > 2000]  # filter out 1970-01-01
TARGET_DATE = valid_dates.max()
TARGET_PIT  = "North JO IC"

print(f"\nTARGET DATE: {TARGET_DATE.strftime('%A, %d %B %Y')}")
print(f"TARGET PIT : {TARGET_PIT}")


# === CELL 3: Daily Plan per PIT ===
# Plan_Daily ada di plan_hourly sheets (per User/PIT/Shift)
# Plan ini FIXED (tidak berubah per tanggal), jadi langsung ambil

# OB Plan
plan_ob_pit = plan_h_ob[plan_h_ob["PIT"] == TARGET_PIT]
daily_plan_ob = plan_ob_pit["Plan_Daily"].iloc[0] if len(plan_ob_pit) > 0 else 0

# Coal Hauling Plan
plan_ch_pit = plan_h_ch[plan_h_ch["PIT"] == TARGET_PIT]
daily_plan_ch = plan_ch_pit["Plan_Daily"].iloc[0] if len(plan_ch_pit) > 0 else 0

# Coal Transit Plan
plan_ct_pit = plan_h_ct[plan_h_ct["PIT"] == TARGET_PIT]
daily_plan_ct = plan_ct_pit["Plan_Daily"].iloc[0] if len(plan_ct_pit) > 0 else 0

print(f"\n--- Daily Plan [{TARGET_PIT}] ---")
print(f"  Plan OB      : {daily_plan_ob:>12,.0f} BCM")
print(f"  Plan Coal H  : {daily_plan_ch:>12,.0f} MT")
print(f"  Plan Coal T  : {daily_plan_ct:>12,.0f} MT")


# === CELL 4: Actual Volume per PIT (filter Date + PIT) ===

# OB Actual = sum of Volume (BCM)
ob_filt = prod_ob[(prod_ob["Date"] == TARGET_DATE) & (prod_ob["PIT"] == TARGET_PIT)]
actual_ob = ob_filt["Volume"].sum()

# Coal Hauling Actual = sum of Netto (kg -> MT)
ch_filt = prod_ch[(prod_ch["Date"] == TARGET_DATE) & (prod_ch["PIT Fix"] == TARGET_PIT)]
actual_ch = ch_filt["Netto"].sum() / 1000  # kg to MT

# Coal Transit Actual = sum of Production (MT)
ct_filt = prod_ct[(prod_ct["Date"] == TARGET_DATE) & (prod_ct["PIT"] == TARGET_PIT)]
actual_ct = ct_filt["Production"].sum()

print(f"\n--- Actual Volume [{TARGET_PIT}] [{TARGET_DATE.strftime('%Y-%m-%d')}] ---")
print(f"  Actual OB    : {actual_ob:>12,.0f} BCM  ({ob_filt.shape[0]} records)")
print(f"  Actual Coal H: {actual_ch:>12,.0f} MT   ({ch_filt.shape[0]} records)")
print(f"  Actual Coal T: {actual_ct:>12,.0f} MT   ({ct_filt.shape[0]} records)")


# === CELL 5: Achievement % ===
# Achievement = (Actual / Plan) * 100

ach_ob = (actual_ob / daily_plan_ob * 100) if daily_plan_ob > 0 else 0
ach_ch = (actual_ch / daily_plan_ch * 100) if daily_plan_ch > 0 else 0
ach_ct = (actual_ct / daily_plan_ct * 100) if daily_plan_ct > 0 else 0

print(f"\n--- Achievement ---")
print(f"  OB      : {ach_ob:>8.1f}%  {'HIJAU' if ach_ob >= 100 else 'MERAH'}")
print(f"  Coal H  : {ach_ch:>8.1f}%  {'HIJAU' if ach_ch >= 100 else 'MERAH'}")
print(f"  Coal T  : {ach_ct:>8.1f}%  {'HIJAU' if ach_ct >= 100 else 'MERAH'}")


# === CELL 6: Stripping Ratio ===
# SR = OB Volume (BCM) / Coal Hauling (MT)

sr = actual_ob / actual_ch if actual_ch > 0 else 0

print(f"\n--- Stripping Ratio ---")
print(f"  SR = {actual_ob:,.0f} BCM / {actual_ch:,.0f} MT = {sr:.2f}")


# === CELL 7: Cumulative Plan vs Actual per Hour (untuk grafik trend) ===

# --- Cumulative Plan (dari cumm_plan sheet) ---
cumm_pit = cumm_plan[cumm_plan["PIT"] == TARGET_PIT].copy()
cumm_pit = cumm_pit.sort_values("Hour LU")

# --- Cumulative Actual OB per Hour ---
ob_per_hour = ob_filt.groupby("Hour LU")["Volume"].sum().reset_index()
ob_per_hour.columns = ["Hour", "Actual_OB"]
ob_per_hour = ob_per_hour.sort_values("Hour")
ob_per_hour["Cumm_Actual_OB"] = ob_per_hour["Actual_OB"].cumsum()

# Merge plan + actual OB
ob_trend = cumm_pit[["Hour LU", "Plan OB", "Cumm OB"]].merge(
    ob_per_hour, left_on="Hour LU", right_on="Hour", how="left"
).fillna(0)

print(f"\n--- Cumulative OB per Hour [{TARGET_PIT}] ---")
print(ob_trend[["Hour LU", "Plan OB", "Cumm OB", "Actual_OB", "Cumm_Actual_OB"]].to_string(index=False))

# --- Cumulative Actual Coal Hauling per Hour ---
ch_per_hour = ch_filt.groupby("Hour LU")["Netto"].sum().reset_index()
ch_per_hour.columns = ["Hour", "Actual_CH_kg"]
ch_per_hour["Actual_CH"] = ch_per_hour["Actual_CH_kg"] / 1000
ch_per_hour = ch_per_hour.sort_values("Hour")
ch_per_hour["Cumm_Actual_CH"] = ch_per_hour["Actual_CH"].cumsum()

ch_trend = cumm_pit[["Hour LU", "Plan CH", "Cumm CH"]].merge(
    ch_per_hour[["Hour", "Actual_CH", "Cumm_Actual_CH"]], 
    left_on="Hour LU", right_on="Hour", how="left"
).fillna(0)

print(f"\n--- Cumulative Coal Hauling per Hour [{TARGET_PIT}] ---")
print(ch_trend[["Hour LU", "Plan CH", "Cumm CH", "Actual_CH", "Cumm_Actual_CH"]].to_string(index=False))


# === CELL 8: Summary Dashboard ===

print(f"\n{'='*65}")
print(f"  Estimated Hourly Production {TARGET_PIT}")
print(f"  {TARGET_DATE.strftime('%A, %d %b %Y')}")
print(f"{'='*65}")
print(f"  Daily Plan OB    : {daily_plan_ob:>10,.0f} BCM")
print(f"  Actual Volume OB : {actual_ob:>10,.0f} BCM")
print(f"  Achievement OB   : {ach_ob:>10.0f}%")
print(f"  ---")
print(f"  Daily Plan CH    : {daily_plan_ch:>10,.0f} MT")
print(f"  Actual Volume CH : {actual_ch:>10,.0f} MT")
print(f"  Achievement CH   : {ach_ch:>10.0f}%")
print(f"  ---")
print(f"  Daily Plan CT    : {daily_plan_ct:>10,.0f} MT")
print(f"  Actual Volume CT : {actual_ct:>10,.0f} MT")
print(f"  Achievement CT   : {ach_ct:>10.0f}%")
print(f"  ---")
print(f"  Stripping Ratio  : {sr:>10.2f}")
print(f"{'='*65}")

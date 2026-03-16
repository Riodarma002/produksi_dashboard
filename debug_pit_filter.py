# -*- coding: utf-8 -*-
"""
Debug PIT Filter - Cek apa yang terjadi dengan filter PIT
"""
import sys
from pathlib import Path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

import pandas as pd
from backend.data_loader import load_data, extract_sheets, normalize_dataframes
from calculations.production import filter_data

print("="*80)
print("DEBUG: PIT FILTER")
print("="*80)

# Load data
data = load_data()
sheets = extract_sheets(data)
normalize_dataframes(sheets)

# Cek PIT yang tersedia di data
print("\n[INFO] PIT names di prod_ob:")
if "PIT Fix" in sheets["prod_ob"].columns:
    pit_list = sheets["prod_ob"]["PIT Fix"].dropna().unique()
    print(f"  Unique PITs ({len(pit_list)}): {pit_list}")
else:
    print("  ERROR: Kolom 'PIT Fix' tidak ditemukan!")
    print(f"  Columns: {sheets['prod_ob'].columns.tolist()}")

print("\n[INFO] PIT names di prod_ch:")
if "PIT Fix" in sheets["prod_ch"].columns:
    pit_list = sheets["prod_ch"]["PIT Fix"].dropna().unique()
    print(f"  Unique PITs ({len(pit_list)}): {pit_list}")
else:
    print("  ERROR: Kolom 'PIT Fix' tidak ditemukan!")
    print(f"  Columns: {sheets['prod_ch'].columns.tolist()}")

# Cek tanggal yang tersedia
print("\n[INFO] Tanggal yang tersedia:")
if "Date" in sheets["prod_ob"].columns:
    dates = sheets["prod_ob"]["Date"].dropna().unique()
    valid_dates = [d for d in dates if pd.notna(d) and d.year > 2000]
    print(f"  Total tanggal: {len(valid_dates)}")
    print(f"  Date range: {min(valid_dates)} s/d {max(valid_dates)}")
    print(f"  Latest dates: {sorted(valid_dates, reverse=True)[:5]}")

# Test filter untuk setiap PIT
print("\n" + "="*80)
print("TEST FILTER PER PIT")
print("="*80)

test_date = (pd.Timestamp("2026-03-13"), pd.Timestamp("2026-03-13"))  # Gunakan tanggal latest

for pit_name in ["North JO IC", "North JO GAM", "South JO IC", "South JO GAM"]:
    filtered = filter_data(sheets, test_date, pit_name)

    print(f"\n{pit_name}:")
    print(f"  OB: {filtered['ob_f'].shape[0]} rows")
    print(f"  CH: {filtered['ch_f'].shape[0]} rows")
    print(f"  CT: {filtered['ct_f'].shape[0]} rows")

    if filtered["ob_f"].shape[0] > 0:
        print(f"  Sample OB PIT values: {filtered['ob_f']['PIT Fix'].unique()[:5]}")
    if filtered["ch_f"].shape[0] > 0:
        print(f"  Sample CH PIT values: {filtered['ch_f']['PIT Fix'].unique()[:5]}")

# Cek raw data sebelum filter
print("\n" + "="*80)
print("RAW DATA SAMPLE")
print("="*80)

print("\n[prod_ob] First 5 rows:")
print(sheets["prod_ob"][["Date", "Hour LU", "PIT Fix", "Volume"]].head())

print("\n[prod_ch] First 5 rows:")
print(sheets["prod_ch"][["Date", "Hour LU", "PIT Fix", "Volume", "Seam"]].head())

print("\n" + "="*80)
print("DEBUG COMPLETE")
print("="*80)

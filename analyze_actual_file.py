# -*- coding: utf-8 -*-
"""
Analisa File Baru - Actual structure from OneDrive
Download dan cek struktur sheet yang sebenarnya
"""
import requests
import pandas as pd
import io

# Link baru dari user
NEW_ONEDRIVE_LINK = "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQCcW88khWRCTZFZE9PnZxdkAdVZbA3srdgAZbYUWf4lxNY?e=zCRAO4"

print("="*80)
print("DOWNLOAD FILE BARU (ACTUAL)")
print("="*80)

try:
    # Download file
    dl = NEW_ONEDRIVE_LINK.split("?")[0] + "?download=1"
    print(f"\n[*] Downloading from: {NEW_ONEDRIVE_LINK[:60]}...")

    r = requests.get(dl, timeout=60, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()

    print(f"[+] Download success! Size: {len(r.content):,} bytes")

    # Baca semua sheet
    print("\n" + "="*80)
    print("MEMBACA STRUKTUR FILE")
    print("="*80)

    excel_file = io.BytesIO(r.content)
    xl_file = pd.ExcelFile(excel_file)

    print(f"\n[INFO] Total Sheets: {len(xl_file.sheet_names)}")
    print(f"\nSheet Names:")
    for i, sheet in enumerate(xl_file.sheet_names, 1):
        print(f"  {i}. {sheet}")

    # Analisa setiap sheet
    print("\n" + "="*80)
    print("DETAIL SHEET & KOLOM")
    print("="*80)

    for sheet_name in xl_file.sheet_names:
        print(f"\n{'='*80}")
        print(f"SHEET: {sheet_name}")
        print(f"{'='*80}")

        df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=10)

        print(f"\n[INFO] Dimensions (first 10 rows): {df.shape[0]} rows x {df.shape[1]} columns")

        print(f"\n[INFO] Columns ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            dtype = str(df[col].dtype)
            sample_vals = df[col].dropna().head(3).tolist()
            sample_str = ", ".join([str(v)[:20] for v in sample_vals])
            print(f"  {i:2}. {col:40} | {dtype:12} | Sample: {sample_str}")

    print("\n" + "="*80)
    print("ANALISA SELESAI")
    print("="*80)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

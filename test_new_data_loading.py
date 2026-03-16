# -*- coding: utf-8 -*-
"""
Test Script - New Data Loading
Verify that the new file format loads correctly
"""
import sys
from pathlib import Path

# Add project root to sys.path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

import pandas as pd
from backend.data_loader import load_data, extract_sheets, normalize_dataframes, parse_input_plan

print("="*80)
print("TEST: Load Data dari File Baru")
print("="*80)

try:
    # Step 1: Load data
    print("\n[STEP 1] Loading data from OneDrive...")
    data = load_data()
    print(f"[SUCCESS] Loaded {len(data)} files")

    # Step 2: Extract sheets
    print("\n[STEP 2] Extracting sheets...")
    sheets = extract_sheets(data)

    print(f"\n[INFO] Sheets extracted:")
    for key, df in sheets.items():
        if df is not None and not df.empty:
            print(f"  - {key:20} : {df.shape[0]:5} rows x {df.shape[1]:2} cols")
        else:
            print(f"  - {key:20} : EMPTY")

    # Step 3: Normalize
    print("\n[STEP 3] Normalizing dataframes...")
    normalize_dataframes(sheets)
    print("[SUCCESS] Normalization complete")

    # Step 4: Check sample data
    print("\n[STEP 4] Checking sample data...")

    if not sheets["prod_ob"].empty:
        print(f"\n[PROD OB] First 3 rows:")
        print(sheets["prod_ob"][["Date", "Hour LU", "PIT Fix", "Volume"]].head(3).to_string())
        print(f"[INFO] Hour LU dtype: {sheets['prod_ob']['Hour LU'].dtype}")
        print(f"[INFO] Hour LU unique values: {sorted(sheets['prod_ob']['Hour LU'].unique())[:10]}")

    if not sheets["prod_ch"].empty:
        print(f"\n[PROD CH] First 3 rows:")
        print(sheets["prod_ch"][["Date", "Hour LU", "PIT Fix", "Volume", "Seam"]].head(3).to_string())
        print(f"[INFO] Volume sample: {sheets['prod_ch']['Volume'].head(5).tolist()}")

    if not sheets["prod_ct"].empty:
        print(f"\n[PROD CT] First 3 rows:")
        print(sheets["prod_ct"][["Date", "Hour LU", "PIT Fix", "Volume"]].head(3).to_string())

    # Step 5: Parse input plan
    print("\n[STEP 5] Parsing input plan...")
    input_values = parse_input_plan(sheets["input_plan"])
    print(f"[INFO] Input values:")
    for key, val in input_values.items():
        print(f"  - {key:15} : {val}")

    # Step 6: Test PIT filtering
    print("\n[STEP 6] Testing PIT filtering...")
    from calculations.production import filter_data, get_plan_values, calc_actuals

    test_date = (pd.Timestamp("2026-03-12"), pd.Timestamp("2026-03-12"))
    test_pit = "North JO IC"

    filtered = filter_data(sheets, test_date, test_pit)
    print(f"[INFO] Filtered data for {test_pit} on 2026-03-12:")
    print(f"  - OB: {filtered['ob_f'].shape[0]} rows")
    print(f"  - CH: {filtered['ch_f'].shape[0]} rows")
    print(f"  - CT: {filtered['ct_f'].shape[0]} rows")

    # Step 7: Test calculations
    print("\n[STEP 7] Testing calculations...")
    plans = get_plan_values(sheets, test_pit)
    actuals = calc_actuals(filtered)

    print(f"[INFO] Plans for {test_pit}:")
    print(f"  - Plan OB  : {plans['plan_ob']:,.2f} BCM")
    print(f"  - Plan CH  : {plans['plan_ch']:,.2f} MT")
    print(f"  - Plan CT  : {plans['plan_ct']:,.2f} MT")
    print(f"  - Has CT   : {plans['has_ct']}")

    print(f"\n[INFO] Actuals for {test_pit}:")
    print(f"  - Actual OB  : {actuals['actual_ob']:,.2f} BCM")
    print(f"  - Actual CH  : {actuals['actual_ch']:,.2f} MT")
    print(f"  - Actual CT  : {actuals['actual_ct']:,.2f} MT")

    print("\n" + "="*80)
    print("[SUCCESS] All tests passed!")
    print("="*80)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

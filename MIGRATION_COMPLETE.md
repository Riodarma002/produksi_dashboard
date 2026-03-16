# Data Source Migration - COMPLETE ✅

## Ringkasan

Berhasil migrasi dari file `db_hourly` format LAMA ke file `db_hourly_report` format BARU.
Logika bisnis tetap sama, hanya struktur data yang berbeda.

---

## Perubahan yang Dilakukan

### 1. Files Modified

#### [config.py](config.py)
- ✅ Update `ONEDRIVE_LINKS["db_hourly"]` dengan link baru
- Link: `https://mgeid-my.sharepoint.com/...IQCcW88khWRCTZFZE9PnZxdkAdVZbA3srdgAZbYUWf4lxNY`

#### [backend/data_loader.py](backend/data_loader.py)
- ✅ **extract_sheets()**: Combine multiple sheets untuk OB, CH, LT
- ✅ **normalize_dataframes()**: Handle Hour LU integer vs string
- ✅ **PIT Normalization**: Fix case inconsistency (North JO IC vs NORTH JO IC)
- ✅ Backward compatible dengan format lama

#### [calculations/production.py](calculations/production.py)
- ✅ **calc_actuals()**: CH Volume sudah dalam MT (tidak perlu /1000)
- ✅ **filter_data()**: Handle "PIT Fix" vs "PIT" column
- ✅ Backward compatible dengan kedua format

---

## Hasil Testing

### Data Load Success
```
✅ prod_ob    :   734 rows ×  4 cols
✅ prod_ch    :   293 rows ×  5 cols
✅ prod_ct    :    66 rows ×  4 cols
✅ lt_ob      :    42 rows ×  5 cols
✅ cumm_plan  :   100 rows ×  8 cols
✅ coal_rom   :    23 rows × 13 cols (NEW)
✅ rain       :    96 rows ×  9 cols (NEW)
✅ master_db  :    26 rows × 18 cols (NEW)
```

### PIT Normalization Success
```
✅ North JO IC (consistent)
✅ Hour LU: "06", "07", "08" (string format untuk compatibility)
```

### Filter & Calculation Success
```
✅ Filter by PIT: 465 OB rows, 170 CH rows, 66 CT rows
✅ Plan OB  : 56,709.57 BCM
✅ Actual OB: 21,296.00 BCM
✅ Plan CH  : 21,572.53 MT
✅ Actual CH: 7,773.97 MT (sudah dalam MT, bukan kg!)
✅ Plan CT  : 6,449.73 MT
✅ Actual CT: 1,828.48 MT
```

---

## Struktur File Baru

### Sheet Mapping

| Data | Sheet Baru | Rows | Columns |
|------|-----------|------|---------|
| **OB Production** | | | |
| - BDE | `Vol OB BDE` | ~200 | 23 cols |
| - GPE Utara | `Vol OB GPE Utara` | ~180 | 9 cols |
| - GPE Selatan | `Vol OB GPE Selatan` | ~180 | 9 cols |
| - MGE | `Vol OB MGE` | ~174 | 16 cols |
| **CH Production** | | | |
| - North | `Vol Hauling North` | ~150 | 17 cols |
| - South | `Vol Hauling South` | ~143 | 17 cols |
| **CT Production** | `Vol Transit North` | ~66 | 17 cols |
| **Loss Time OB** | `LT OB MGE`, `LT OB BDE` | ~42 | 13/5 cols |
| **Cumulative** | `Cumm Vol` | ~100 | 8 cols |
| **Coal ROM** | `Coal Hauling ROM` | ~23 | 13 cols |
| **Rain** | `Rain` | ~96 | 9 cols |
| **Master DB** | `db` | ~26 | 18 cols |

---

## Key Differences from Old Format

### 1. Hour LU Format
- **OLD**: String "06", "07", "08"
- **NEW**: Integer 6, 7, 8
- **Solution**: normalize_dataframes() converts both to string "06", "07", "08"

### 2. PIT Names
- **OLD**: "North JO IC" (consistent)
- **NEW**: "NORTH JO IC", "North Jo Ic" (inconsistent)
- **Solution**: extract_sheets() normalizes to "North JO IC"

### 3. Volume Units
- **OLD CH**: Netto in kg (÷1000 → MT)
- **NEW CH**: Volume in MT (direct use)
- **Solution**: calc_actuals() detects column name

### 4. Column Names
- **OLD**: `PIT` for OB
- **NEW**: `PIT Fix` for all (OB, CH, CT)
- **Solution**: filter_data() checks both columns

---

## Backward Compatibility

✅ Code masih bisa handle file LAMA jika dibutuhkan:
```python
# Auto-detect format
if "Vol OB BDE" in sheets:
    # NEW FORMAT: Combine 4 OB sheets
else:
    # OLD FORMAT: Single sheet
```

---

## Next Steps

### Done ✅
- [x] Update link OneDrive
- [x] Rewrite extract_sheets() untuk combine sheets
- [x] Fix normalize_dataframes() untuk Hour LU
- [x] Fix calc_actuals() untuk CH dalam MT
- [x] Fix filter_data() untuk PIT Fix column
- [x] Normalize PIT names
- [x] Test data loading
- [x] Test PIT filtering
- [x] Test calculations

### Recommended 📋
- [ ] Test di Streamlit: `streamlit run app.py`
- [ ] Verify semua PIT works (South JO GAM dll)
- [ ] Test di production date range
- [ ] Monitor untuk data inconsistency
- [ ] Update plan_hourly file jika berubah juga
- [ ] Dokumentasikan perubahan ke team

---

## Files untuk Review

1. **[config.py](config.py)** - Link update
2. **[backend/data_loader.py](backend/data_loader.py)** - Extract & normalize
3. **[calculations/production.py](calculations/production.py)** - Filter & calculate
4. **[FILE_MIGRATION_GUIDE.md](FILE_MIGRATION_GUIDE.md)** - Detailed mapping
5. **[test_new_data_loading.py](test_new_data_loading.py)** - Test script

---
**Migration Date**: 2026-03-15
**Status**: ✅ COMPLETE & TESTED
**File Size**: 2.4 MB
**Total Sheets**: 15

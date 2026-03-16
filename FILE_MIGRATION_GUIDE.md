# File Migration Guide - db_hourly_report.xlsx

## Ringkasan

File Excel sumber data telah berubah dari format lama ke format baru. Struktur data berbeda tetapi logika bisnis tetap sama.

---

## Perbandingan Struktur File

### File LAMA vs File BARU

| Data | File LAMA (db_hourly) | File BARU (db_hourly_report) | Sheet Baru |
|------|----------------------|------------------------------|------------|
| **OB Production** | `prod ob` sheet | Tersebar di 4 sheet terpisah: | |
| - North JO IC (BDE) | - | `Vol OB BDE` | ✅ |
| - North JO GAM (GPE) | - | `Vol OB GPE Utara` | ✅ |
| - North JO MGE | - | `Vol OB MGE` | ✅ |
| - South JO IC (GPE) | - | `Vol OB GPE Selatan` | ✅ |
| **CH Production** | `prod ch` sheet | 2 sheet terpisah: | |
| - North JO | - | `Vol Hauling North` | ✅ |
| - South JO | - | `Vol Hauling South` | ✅ |
| **CT Production** | `prod ct` sheet | `Vol Transit North` | ✅ |
| **LT OB** | `lt ob` sheet | 2 sheet terpisah: | |
| - LT OB MGE | - | `LT OB MGE` | ✅ |
| - LT OB BDE | - | `LT OB BDE` | ✅ |
| **LT Coal** | `lt coal` sheet | Tidak ada di file baru | ⚠️ |
| **Cumulative Plan** | `Cumm Plan Vol` | `Cumm Vol` | ✅ |
| **Master DB** | Tidak ada | `db` | ✅ (NEW) |
| **Hour Lookup** | Tidak ada | `LU Hour`, `LU PIT` | ✅ (NEW) |
| **Rain Data** | Tidak ada | `Rain` | ✅ (NEW) |
| **ROM Data** | Tidak ada | `Coal Hauling ROM` | ✅ (NEW) |

---

## Mapping Kolom

### 1. Overburden (OB)

#### Vol OB BDE / Vol OB GPE Utara / Vol OB GPE Selatan / Vol OB MGE

| Kolom Lama | Kolom Baru | Tipe Data |
|------------|-----------|-----------|
| `Date` | `Date` | datetime64 |
| `Hour LU` | `Hour LU` | int64 |
| `PIT` / `PIT Fix` | `PIT Fix` | object |
| `Volume` | `Volume` | float64/int64 |

**Catatan:**
- `Hour LU` sekarang integer (6, 7, 8, ...) bukan string ("06", "07", "08")
- `PIT Fix` lebih konsisten digunakan daripada `PIT`
- Semua sheet OB memiliki struktur kolom yang sama

#### Vol OB MGE (Extra Columns)

Kolom tambahan:
- `Loader`, `Hauler`, `RIT`, `Distance`, `Owner`, `Status`, `Material`

#### Vol OB BDE (Extra Columns)

Kolom tambahan:
- `M'LY`, `DWO`, `Loader`, `EGI Loader`, `Hauler`, `EGI Hauler`
- `OPT Loader`, `OPT Hauler`, `SITE`, `LOKASI`, `SUB MATERIAL`, `LU`

---

### 2. Coal Hauling (CH)

#### Vol Hauling North / Vol Hauling South

| Kolom Lama | Kolom Baru | Tipe Data |
|------------|-----------|-----------|
| `Date` | `Date` | datetime64 |
| `Hour LU` | `Hour LU` | int64 |
| `PIT Fix` | `PIT Fix` | object |
| `Netto` | `Volume` | float64 (dalam MT) |
| `Seam` | `Seam` | object |

**Catatan:**
- `Netto` lama dalam kg → `Volume` baru sudah dalam MT
- Tidak perlu bagi 1000 lagi!

---

### 3. Coal Transit (CT)

#### Vol Transit North

| Kolom Lama | Kolom Baru | Tipe Data |
|------------|-----------|-----------|
| `Date` | `Date` | datetime64 |
| `Hour LU` | `Hour LU` | int64 |
| `PIT Fix` | `PIT Fix` | object |
| `Production` | `Volume` | float64 (dalam MT) |
| `Product` | `Product` / `Product Fix` | object |

**Catatan:**
- `Production` lama → `Volume` baru
- `Product Fix` lebih konsisten

---

### 4. Cumulative Volume

#### Cumm Vol

| Kolom Lama | Kolom Baru | Tipe Data |
|------------|-----------|-----------|
| `Hour LU` | `Hour LU` | int64 |
| `PIT` | `PIT` | object |
| `Cumm OB` | `Cumm OB` | int64 |
| `Cumm CH` | `Cumm CH` | float64 |
| `Cumm CT` | `Cumm CT` | float64 |

**Catatan:**
- Sama persis dengan file lama
- Ada juga kolom `Volume OB/CH/CT` untuk hourly

---

## PIT Mapping

### PIT Names di File Baru

| PIT Lama | PIT Baru | Sheet Source |
|----------|----------|--------------|
| North JO IC | `North JO IC` / `NORTH JO IC` | Vol OB BDE, Vol Hauling North, Vol Transit North |
| North JO GAM | `North JO GAM` | Vol OB GPE Utara, Vol Hauling North |
| South JO IC | `South JO IC` | Vol OB GPE Selatan, Vol Hauling South |
| South JO GAM | `South JO GAM` | (Belum ada data di file baru) |

**Catatan:** Ada inconsistency dalam naming:
- `North JO IC` vs `NORTH JO IC` (case sensitivity)
- Perlu normalization di code

---

## Perubahan yang Diperlukan di Code

### 1. config.py
✅ Update link OneDrive:
```python
ONEDRIVE_LINKS = {
    "db_hourly": "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQCcW88khWRCTZFZE9PnZxdkAdVZbA3srdgAZbYUWf4lxNY?e=gABCsf",
    "plan_hourly": "https://mgeid-my.sharepoint.com/:x:/g/personal/planning_department_mgeid_onmicrosoft_com/IQBK3837O3nsR5AKLRsno8PGARDeJ9RzlLfjVdPLJLPykWk?e=wYAkLX",
}
```

### 2. data_loader.py - extract_sheets()
✅ Combine data dari 4 sheet OB:

```python
def extract_sheets(data: dict) -> dict:
    # File BARU: Combine 4 OB sheets
    ob_bde = data["Vol OB BDE"].copy()
    ob_gpe_u = data["Vol OB GPE Utara"].copy()
    ob_gpe_s = data["Vol OB GPE Selatan"].copy()
    ob_mge = data["Vol OB MGE"].copy()

    # Standardize columns
    required_cols = ["Date", "Hour LU", "PIT Fix", "Volume"]
    for df in [ob_bde, ob_gpe_u, ob_gpe_s, ob_mge]:
        # Keep only required columns
        # (ada extra columns yang tidak perlu)

    # Concat semua OB sheets
    prod_ob = pd.concat([ob_bde, ob_gpe_u, ob_gpe_s, ob_mge], ignore_index=True)

    # CH: Combine 2 sheets
    ch_north = data["Vol Hauling North"].copy()
    ch_south = data["Vol Hauling South"].copy()
    prod_ch = pd.concat([ch_north, ch_south], ignore_index=True)

    # CT: Single sheet
    prod_ct = data["Vol Transit North"].copy()

    # LT: Combine 2 sheets
    lt_ob_mge = data["LT OB MGE"].copy()
    lt_ob_bde = data["LT OB BDE"].copy()
    lt_ob = pd.concat([lt_ob_mge, lt_ob_bde], ignore_index=True)

    # ... rest of sheets
```

### 3. data_loader.py - normalize_dataframes()
⚠️ **CRITICAL**: Hour LU sekarang integer, bukan string!

```python
def normalize_dataframes(sheets: dict) -> None:
    # Fix dates
    for key in ["prod_ob", "prod_ch", "prod_ct", "lt_ob"]:
        df = sheets[key]
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # FIX: Hour LU sekarang INTEGER, bukan string!
    # Tidak perlu .str.zfill(2) lagi
    for key in ["prod_ob", "prod_ch", "prod_ct", "cumm_vol", "lt_ob"]:
        df = sheets[key]
        if "Hour LU" in df.columns:
            # Konversi ke int, pastikan tidak ada NaN
            df["Hour LU"] = pd.to_numeric(df["Hour LU"], errors="coerce").fillna(0).astype(int)
```

### 4. calculations/production.py - calc_actuals()
⚠️ **CRITICAL**: CH Volume sudah dalam MT, bukan kg!

```python
def calc_actuals(filtered: dict) -> dict:
    actual_ob = filtered["ob_f"]["Volume"].sum()
    # TIDAK PERLU bagi 1000 lagi! Volume sudah dalam MT
    actual_ch = filtered["ch_f"]["Volume"].sum()  # dalam MT langsung
    actual_ct = filtered["ct_f"]["Volume"].sum()  # dalam MT langsung

    return {"actual_ob": actual_ob, "actual_ch": actual_ch, "actual_ct": actual_ct}
```

---

## Testing Checklist

- [ ] Test load data dari file baru
- [ ] Test normalisasi Hour LU (integer)
- [ ] Test perhitungan CH (tanpa /1000)
- [ ] Test PIT filtering (case insensitive)
- [ ] Test cumulative chart (Cumm Vol sheet)
- [ ] Test coal ROM calculation (Coal Hauling ROM sheet)
- [ ] Test rain data (Rain sheet)
- [ ] Verify semua 4 PIT ter-representasi

---

## Next Steps

1. Update config.py dengan link baru
2. Rewrite extract_sheets() untuk combine multiple sheets
3. Fix normalize_dataframes() untuk Hour LU integer
4. Fix calc_actuals() untuk CH dalam MT
5. Test dan verify data flow
6. Update PIT_REGISTRY untuk handle case inconsistency
7. Deploy dan monitor

---
Generated: 2026-03-15
File Size: 2.4 MB
Total Sheets: 15

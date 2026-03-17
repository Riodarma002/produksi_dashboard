# 🚀 Quick Start - Dashboard Produksi

## ✅ Dashboard Berjalan!

Dashboard sudah berjalan di: **http://localhost:8501**

---

## 🌐 URL Akses

| Tipe | URL |
|------|-----|
| Local | http://localhost:8501 |
| Network | http://192.168.114.123:8501 |
| External | http://116.254.97.80:8501 |

---

## 🎯 Cara Menggunakan

### 1. Buka Dashboard
```
1. Buka browser (Chrome/Firefox/Edge)
2. Ketik: http://localhost:8501
3. Enter
```

### 2. Navigasi
- **Summary**: Halaman ringkasan
- **Produksi**: Dashboard utama dengan KPI & Charts

### 3. Kontrol Dashboard

#### **PIT Selector**
```
[North JO IC | North JO GAM | South JO IC | South JO GAM]
```
Klik untuk ganti area PIT

#### **Play/Pause Auto-Rotation**
```
[⏸️ Pause] - Jeda rotasi otomatis
[▶️ Play]  - Lanjut rotasi otomatis
```
Default: Rotate setiap 25 detik

#### **Date Range Picker**
```
[📅 Date Range]
```
Pilih tanggal untuk filter data

---

## 🔄 Fitur Refresh

### Enhanced Refresh Button (BARU!)

**Klik:** 🔄 Refresh Data

**Yang Akan Terjadi:**
1. Spinner: "🔄 Mengambil data terbaru..."
2. Fetch dari OneDrive (2-5 detik)
3. Success message: "✅ Data berhasil diupdate! (2.3s)"
4. Balloons celebration 🎈
5. Dashboard auto-rerun dengan data baru

### Sync Status Indicator

**Icons:**
- ✅ Green = Data up-to-date
- 🔄 Blue = Sedang sync
- ⚠️ Amber = Data tertunda (>1 jam)
- ❌ Red = Sync gagal
- ⏳ Gray = Belum pernah sync

**Display:**
```
Sync 5 menit yang lalu
• Next: 14:35
```

---

## 📊 Komponen Dashboard

### KPI Cards
- **Overburden (BCM)**: Volume OB hari ini
- **Coal Hauling (MT)**: Volume batubara diangkut
- **Coal Transit (MT)**: Volume batubara transit
- **Stripping Ratio**: Rasio OB/Coal (BCM/MT)
- **Stock ROM (MT)**: Stock di ROM
- **Stock Port (MT)**: Stock di port

### Charts
- **Cumulative OB Production**: Grafik produksi OB
- **Cumulative Coal Hauling**: Grafik pengangkutan batubara
- **Rainfall Overlay**: Curah hujan

### Tables
- **Raw Data Tables**: Data mentah per jam
- **Plan Tables**: Rencana produksi

---

## 🛠️ Troubleshooting

### Dashboard tidak muncul?

**1. Check apakah server jalan:**
```bash
# Cek health
curl http://localhost:8501/_stcore/health

# Harus return: "ok"
```

**2. Cek port:**
```bash
netstat -ano | findstr :8501
```

**3. Restart server:**
```bash
# Stop current: Ctrl + C
# Start ulang:
cd "D:\Rio Disk\rio\dashboard_produksi\produksi_dashboard"
python -m streamlit run app.py --server.port 8501
```

### Data tidak muncul?

**1. Manual refresh:**
- Klik tombol "🔄 Refresh Data"

**2. Check .env file:**
```bash
cat .env
```

**3. Check logs:**
```bash
# Windows
Get-Content logs\dashboard_*.log -Tail 50

# Linux/Mac
tail -50 logs/dashboard_*.log
```

**4. Clear cache (last resort):**
```bash
# Delete cache
rm data/cache.pkl

# Restart app
```

---

## 📱 Commands

### Start Dashboard
```bash
cd "D:\Rio Disk\rio\dashboard_produksi\produksi_dashboard"
python -m streamlit run app.py
```

### Stop Dashboard
```
Tekan: Ctrl + C
```

### Start dengan Port Berbeda
```bash
python -m streamlit run app.py --server.port 8502
```

### Start dengan Debug Mode
```bash
python -m streamlit run app.py --logger.level=debug
```

---

## 🎉 Selamat Menggunakan!

Dashboard produksi Anda sudah siap digunakan!

**URL:** http://localhost:8501

**Features:**
- ✅ Real-time KPI & Charts
- ✅ Auto-rotation antar PIT
- ✅ Enhanced refresh system
- ✅ Sync status indicator
- ✅ Manual & automatic refresh
- ✅ Responsive design

---

## 📞 Support

Jika ada masalah:
1. Check logs di `logs/` directory
2. Check sync status di sidebar
3. Manual refresh jika perlu
4. Restart dashboard

---

**Status:** ✅ **RUNNING**
**URL:** http://localhost:8501
**Version:** 2.0 (Enhanced)

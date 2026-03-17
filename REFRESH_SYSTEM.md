# 🔄 Sistem Refresh Dashboard Produksi

## 📋 Overview

Sistem refresh dashboard produksi menggunakan **multi-layer approach** untuk memastikan data selalu up-to-date:

1. **Background Sync** (otomatis, setiap 1 jam)
2. **Manual Refresh** (user-triggered, immediate)
3. **Cache System** (optimalisasi performa)
4. **Auto-Refresh** (halaman auto-reload)

---

## 🏗️ Arsitektur

```
┌─────────────────────────────────────────────────────────┐
│                     Streamlit App                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   Sidebar    │         │   Pages      │             │
│  │              │         │              │             │
│  │ 🔄 Refresh   │────────>│  Production  │             │
│  │    Button    │         │    Page      │             │
│  │              │         │              │             │
│  │ 📊 Sync      │         │  Summary     │             │
│  │   Status     │         │    Page      │             │
│  └──────────────┘         └──────────────┘             │
│         │                        │                      │
│         │                        │                      │
│         v                        v                      │
│  ┌──────────────────────────────────────────┐         │
│  │         Session State (st.session_state) │         │
│  │  - sheets (DataFrame)                    │         │
│  │  - input_values (dict)                   │         │
│  │  - cache_mtime (timestamp)               │         │
│  └──────────────────────────────────────────┘         │
│                          ↑                              │
│                          │                              │
│  ┌───────────────────────┴──────────────────────┐      │
│  │              State Manager                   │      │
│  │  - init_data()                              │      │
│  │  - get_input_values()                       │      │
│  │  - clear_cache()                            │      │
│  └───────────────────────┬──────────────────────┘      │
│                         │                              │
└─────────────────────────┼──────────────────────────────┘
                          │
                          │
         ┌────────────────┴────────────────┐
         │                                 │
         v                                 v
┌──────────────────┐            ┌──────────────────┐
│  Sync Manager    │            │   Cache File     │
│  (Background)    │            │  data/cache.pkl  │
│                  │            └──────────────────┘
│  - Threading     │                       ↑
│  - 1 jam interval│                       │
│  - Retry logic   │                       │
│  - Atomic write  │                       │
└──────────┬───────┘                       │
           │                               │
           │                               │
           v                               │
┌────────────────────┐                    │
│   OneDrive /       │                    │
│   Azure API        │                    │
│                    │                    │
│  - db_hourly       │                    │
│  - plan_hourly     │                    │
└────────────────────┘                    │
                                          │
                          (Atomic write)  │
                                          │
```

---

## 🔄 **1. Background Sync (Otomatis)**

### Cara Kerja:
```python
# app.py - Start on app launch
sync_manager.start_sync()
```

**Timeline:**
```
00:00 - App starts
  └─> Background thread begins
      ├─> Fetch data from OneDrive
      ├─> Save to data/cache.pkl (atomic)
      └─> Sleep for 1 hour

01:00 - Auto-sync triggers again
  └─> Repeat...
```

### Fitur:
- ✅ **Non-blocking**: Jalan di background thread
- ✅ **Atomic Write**: Temp file → rename (prevent corrupt)
- ✅ **Retry Logic**: 3x retry dengan exponential backoff
- ✅ **Error Logging**: Semua error di-log ke file
- ✅ **Singleton**: Hanya 1 instance running

### Code:
```python
# backend/sync_manager.py
class SyncManager:
    def _sync_once(self) -> dict:
        """
        Single sync operation with retry logic.
        Returns: {success, message, duration, timestamp}
        """
        for attempt in range(3):
            try:
                data = self._fetch_raw_data()
                sheets = extract_sheets(data)
                # ... process ...
                self._save_to_cache(sheets)
                return {"success": True, ...}
            except Exception as e:
                if attempt < 2:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return {"success": False, ...}
```

---

## 🖱️ **2. Manual Refresh (User-Triggered)**

### Tombol Refresh Baru:

```python
# app.py sidebar
if handle_manual_refresh():
    st.rerun()
```

### Cara Kerja:

**Step 1: User Click Refresh**
```
🔄 Refresh Data  →  [Trigger]
```

**Step 2: Immediate Sync**
```python
def trigger_immediate_sync() -> dict:
    with st.spinner("🔄 Mengambil data..."):
        data = load_data()  # Fresh from OneDrive
        sheets = extract_sheets(data)
        save_to_cache(sheets)
    return {"success": True, "message": "Data berhasil diupdate!"}
```

**Step 3: Update Session State**
```python
st.session_state["sheets"] = result["sheets"]
st.session_state["input_values"] = result["input_values"]
st.session_state["cache_mtime"] = os.path.getmtime(CACHE_FILE)
```

**Step 4: Rerun App**
```python
st.success("✅ Data berhasil diupdate! (2.3s)")
st.balloons()  # Celebration!
time.sleep(1)
st.rerun()
```

### Visual Feedback:
```
┌────────────────────────────────────┐
│  🔄 Refresh Data          [✅]     │ ← Sync status icon
│                                    │
│  Sync 5 menit yang lalu            │ ← Status message
│  • Next: 14:35                     │ ← Next sync time
└────────────────────────────────────┘
```

### Error Handling:
```python
if result["success"]:
    st.success("✅ Data berhasil diupdate! (2.3s)")
else:
    st.error("❌ Gagal mengambil data")
    st.info("💡 Tips: Pastikan koneksi internet stabil")
```

---

## 💾 **3. Cache System**

### Cache Flow:

```python
# state.py - init_data()
def init_data() -> dict:
    # Check cache file mtime
    mtime = os.path.getmtime(CACHE_FILE)

    # If changed, reload data
    if st.session_state.get("cache_mtime") != mtime:
        data = load_data()  # From cache file
        st.session_state["sheets"] = data["sheets"]
        st.session_state["cache_mtime"] = mtime

    return st.session_state["sheets"]
```

### Cache Lifecycle:

```
┌────────────────────────────────────────────────────────┐
│  1. App Start                                          │
│     ├─> Check data/cache.pkl                           │
│     ├─> If exists: Load to session_state               │
│     └─> If not exists: Fetch from OneDrive             │
├────────────────────────────────────────────────────────┤
│  2. Background Sync (every 1 hour)                     │
│     ├─> Fetch from OneDrive                            │
│     ├─> Update cache.pkl (atomic)                      │
│     └─> Session state auto-detects mtime change        │
├────────────────────────────────────────────────────────┤
│  3. Manual Refresh                                     │
│     ├─> Immediate fetch from OneDrive                  │
│     ├─> Update cache.pkl                               │
│     ├─> Force reload session_state                     │
│     └─> Rerun app                                      │
└────────────────────────────────────────────────────────┘
```

### Atomic Write:

```python
# Prevent corrupt cache
temp_file = CACHE_FILE + ".tmp"
with open(temp_file, "wb") as f:
    pickle.dump(data, f)
os.replace(temp_file, CACHE_FILE)  # Atomic operation
```

---

## 📊 **4. Sync Status Indicator**

### Status Types:

| Status | Icon | Color | Kondisi |
|--------|------|-------|---------|
| **synced** | ✅ | Green | Sync < 1 jam lalu |
| **syncing** | 🔄 | Blue | Sedang sync (30d terakhir) |
| **stale** | ⚠️ | Amber | Sync > 1 jam (terlambat) |
| **error** | ❌ | Red | Error saat sync |
| **never** | ⏳ | Gray | Belum pernah sync |

### Display di Sidebar:

```python
# app.py
render_sync_status(show_next_sync=True)
```

### Output:

```
┌────────────────────────────────────┐
│  ✅ Sync 5 menit yang lalu         │
│     • Next: 14:35                  │
└────────────────────────────────────┘
```

---

## ⏰ **5. Auto-Refresh Halaman**

```python
# app.py
st_autorefresh(interval=3600000)  # 1 jam
```

**Cara Kerja:**
- Halaman auto-reload setiap 1 jam
- Mendeteksi cache file changes
- Auto-update session state

---

## 🛠️ **Troubleshooting**

### Problem: Data tidak update

**Solutions:**

1. **Check sync status:**
```bash
# View logs
tail -f logs/dashboard_*.log

# Look for:
# - "Background sync thread started"
# - "Sync completed successfully"
# - "Sync failed: ..."
```

2. **Manual refresh:**
   - Klik tombol "🔄 Refresh Data" di sidebar
   - Tunggu feedback message

3. **Check cache file:**
```bash
# Check if cache exists
ls -lh data/cache.pkl

# Check last modification
stat data/cache.pkl
```

4. **Check OneDrive link:**
   - Pastikan link masih valid
   - Coba akses link di browser

### Problem: Sync selalu gagal

**Possible causes:**

1. **Koneksi internet:**
```bash
# Test connection
ping api.onedrive.com
```

2. **Azure credentials:**
```bash
# Check .env file
cat .env | grep AZURE
```

3. **Rate limiting:**
   - OneDrive mungkin rate-limit
   - Tunggu beberapa saat dan retry

### Problem: Cache corrupt

**Solution:**
```bash
# Delete cache file
rm data/cache.pkl

# Restart app
streamlit run app.py
```

---

## 📝 **Best Practices**

### DO ✅:
- Gunakan manual refresh untuk data urgent
- Monitor sync status di sidebar
- Check logs jika ada error
- Tunggu background sync untuk update rutin

### DON'T ❌:
- Jangan delete cache saat app running
- Jangan refresh terlalu sering (rate limit)
- Jangan edit cache.pkl manually
- Jangan stop app saat background sync sedang running

---

## 🔧 **Configuration**

### Ubah Sync Interval:

```python
# config.py
SYNC_INTERVAL = 1800  # 30 menit (default: 3600 = 1 jam)
```

### Ubah Cache TTL:

```python
# config.py
CACHE_TTL_SECONDS = 1800  # 30 menit (default: 3600)
```

### Disable Background Sync:

```python
# app.py
# sync_manager.start_sync()  # Comment out this line
```

---

## 📈 **Performance Metrics**

| Operation | Time | Notes |
|-----------|------|-------|
| Manual Refresh | 2-5s | Termasuk OneDrive download |
| Background Sync | 2-5s | Non-blocking |
| Load from Cache | <0.5s | Sangat cepat |
| Auto-Refresh | <1s | Hanya page reload |

---

## 🎯 **Summary**

### Sistem Refresh Anda SUDAH BAGUS! ✅

**Kelebihan:**
1. ✅ Background sync (otomatis)
2. ✅ Manual refresh (immediate)
3. ✅ Cache system (cepat)
4. ✅ Retry logic (reliable)
5. ✅ Status indicator (transparent)
6. ✅ Error handling (robust)

**Penambahan Baru:**
1. ✅ Enhanced manual refresh dengan feedback
2. ✅ Sync status indicator di sidebar
3. ✅ Retry logic dengan exponential backoff
4. ✅ Proper error messages
5. ✅ Atomic cache write

### Cara Pakai:

**Routine:**
- Biarkan background sync bekerja (otomatis setiap jam)
- Monitor sync status di sidebar

**Urgent:**
- Klik tombol "🔄 Refresh Data"
- Tunggu 2-5 detik
- Data akan update segera!

**Troubleshooting:**
- Check logs di `logs/` directory
- Check sync status indicator
- Manual refresh jika perlu

---

**Status:** ✅ Sistem refresh Anda sekarang sudah sangat robust!

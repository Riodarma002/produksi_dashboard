# Azure Credentials Migration Guide

## 📋 Summary

Azure credentials telah dipindahkan dari hardcoded di `config.py` ke environment variables via file `.env` untuk keamanan yang lebih baik.

## 🔄 Perubahan yang Dilakukan

### 1. **File Baru yang Dibuat**

#### `.env.example` (Safe to commit)
Template file untuk team members. Copy file ini dan rename menjadi `.env`:
```bash
cp .env.example .env
```

#### `.env` (Ignored by git - Sensitive!)
File ini berisi credentials aktual dan sudah di-add ke `.gitignore`, sehingga tidak akan di-commit ke git.

### 2. **config.py Modifications**

**Before:**
```python
AZURE_TENANT_ID = "<your-tenant-id>"
AZURE_CLIENT_ID = "<your-client-id>"
AZURE_CLIENT_SECRET = "<your-client-secret>"
```

**After:**
```python
from dotenv import load_dotenv
load_dotenv()

AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", "")

# Warning jika menggunakan hardcoded credentials
if os.getenv("AZURE_TENANT_ID") is None:
    warnings.warn("⚠️  Using hardcoded Azure credentials!...")
```

## ✅ Keuntungan

1. **Security**: Credentials tidak ter-expose di codebase
2. **Flexibility**: Berbeda untuk setiap environment (dev/staging/prod)
3. **Team Collaboration**: Setiap developer punya credentials sendiri via `.env`
4. **Deployment-Friendly**: Streamlit Cloud & deployment platforms bisa inject environment variables

## 🚀 Cara Penggunaan

### **Local Development**

1. Install dependencies (jika belum):
```bash
pip install -r requirements.txt
```

2. File `.env` sudah dibuat dengan credentials dari config.py yang lama

3. Run aplikasi:
```bash
streamlit run app.py
```

### **Untuk Team Members Baru**

1. Copy template:
```bash
cp .env.example .env
```

2. Edit `.env` dan isi dengan Azure credentials masing-masing

3. Run aplikasi

### **Deployment (Streamlit Cloud / Production)**

Di Streamlit Cloud, masukkan environment variables di:
**Settings > Secrets** atau **Environment Variables**

```toml
# .streamlit/secrets.toml (untuk Streamlit Cloud)
AZURE_TENANT_ID = "your-tenant-id-here"
AZURE_CLIENT_ID = "your-client-id-here"
AZURE_CLIENT_SECRET = "your-client-secret-here"
```

## 🔒 Keamanan

- ✅ `.env` sudah di .gitignore (tidak akan di-commit)
- ✅ `.env.example` aman di-commit (hanya template)
- ✅ Fallback values tetap ada untuk backward compatibility
- ✅ Warning muncul jika environment variables tidak di-set

## 📝 Checklist

- [x] Backup commit dibuat (edfa590)
- [x] .env.example dibuat
- [x] config.py di-update dengan load_dotenv()
- [x] .env dibuat dengan credentials aktual
- [x] .gitignore sudah mem-blok .env
- [x] Warning message ditambahkan
- [x] Backward compatibility maintained

## ⚠️ Penting

**JANGAN** commit file `.env` ke git! Jika tidak sengaja ter-commit:
```bash
git remove --cached .env
git commit -m "Remove sensitive .env file"
```

---
Generated: 2026-03-15
Author: Claude Sonnet 4.6

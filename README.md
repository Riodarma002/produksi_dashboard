# 📊 Dashboard Monitoring Rio

Dashboard monitoring berbasis **Streamlit** untuk visualisasi dan analisis data operasional.

## 🚀 Quick Start

### 1. Aktivasi Virtual Environment

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Jalankan Dashboard

```bash
streamlit run app.py
```

Dashboard akan terbuka di browser pada `http://localhost:8501`

## 📁 Struktur Project

```
Dashboard_monitoring_rio/
├── app.py                 # Entry point aplikasi
├── pages/                 # Halaman tambahan (multi-page)
├── components/            # Komponen UI reusable
├── utils/                 # Fungsi utilitas
├── data/                  # Data files
├── .streamlit/
│   └── config.toml        # Konfigurasi Streamlit
├── requirements.txt       # Dependencies
├── .gitignore
└── README.md
```

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** — Framework dashboard
- **Pandas** — Data manipulation
- **Plotly** — Interactive charts
- **OpenPyXL** — Excel file handling

## 📝 License

Internal use only.

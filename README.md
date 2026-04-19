# 💧 AquaGuard — IoT Water Leakage Detection System [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://waterleakagedetection-waterconservation.streamlit.app/)

### Simulation-Based · Python · Streamlit · SQLite

---

## 📁 Project Structure
```
water_leakage_system/
├── main.py          # Streamlit dashboard (UI + logic)
├── database.py      # SQLite data layer
├── requirements.txt # Python dependencies
└── README.md        # This file
```
`water_leakage.db` is auto-created on first run.

---

## 🚀 Quick Start

### 1. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run main.py
```
Open `http://localhost:8501` in your browser.

---

## 🎮 How to Use

| Action | How |
|--------|-----|
| Start monitoring | Click **▶ Start** in the sidebar |
| Pause            | Click **⏸ Pause** |
| Simulate a leak  | Toggle **🚨 Simulate Leak Manually** |
| Reset session    | Click **🔄 Reset** |
| Change speed     | Adjust the **Refresh rate** slider |
| View raw data    | Check **Show raw data table** |

---

## ⚙️ Detection Logic

| Rule | Condition | Trigger label |
|------|-----------|---------------|
| Flow drop | Current flow drops ≥ 45 % vs previous reading | `flow_drop` |
| High moisture | Moisture sensor ≥ 70 % | `moisture_high` |
| Manual | Toggle switch in sidebar | `manual` |

---

## 🗄 Database Schema

**sensor_readings** — every simulated tick  
`id · timestamp · flow_rate · moisture · leak_status`

**leak_events** — only when a leak is detected  
`id · timestamp · trigger · flow_rate · moisture`

---

## 🛠 Tech Stack
- **Frontend / UI** — Streamlit
- **Charts** — Plotly (gauges, area, line charts)
- **Database** — SQLite via Python `sqlite3`
- **Language** — Python 3.10+
## 🚀 Live Demo
Try the app here: [Water Leakage Detection Streamlit App](https://waterleakagedetection-waterconservation.streamlit.app)



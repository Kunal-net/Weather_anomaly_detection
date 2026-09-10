# Weather Anomaly Detection System — Memory Bank

> **Project Identity:** AI/ML-Powered Weather Anomaly Detection, Monitoring, and Explainability Platform  
> **Target:** Smart India Hackathon (SIH) Prototype  
> **Last Updated:** 2026-09-10  
> **Active Workspace:** `/Users/kunalsuryanshi/Documents/Projectsnew/Innovate X`

---

## 1. Project Overview & North Star

Traditional weather apps answer: *"What is the weather?"*  
Our system answers: **"Is the current weather behaving abnormally compared to what is historically expected for this location and time of year?"**

The core pipeline:
$$\text{Weather Observation} \longrightarrow \text{Historical Baseline Lookup} \longrightarrow \text{Statistical + ML Engine} \longrightarrow \text{Score [0-1]} \longrightarrow \text{Severity} \longrightarrow \text{Explainability} \longrightarrow \text{FastAPI} \longrightarrow \text{Dashboard}$$

---

## 2. Team Member Allocation (5 Members)

| Member | Role | Primary Directory | Key Responsibilities |
| :--- | :--- | :--- | :--- |
| **Member 1** | ML/AI Lead | `ml/` | Baseline calculation, Isolation Forest, Anomaly scoring, Model evaluation, Serialization. |
| **Member 2** | Data Engineer | `data/`, `ml/preprocessing.py` | Data cleaning, METAR parsing, feature engineering, physical bounds validation. |
| **Member 3** | Backend Developer | `backend/` | FastAPI routes, Pydantic schemas, database models, prediction service. |
| **Member 4** | Frontend Developer | `frontend/` | React dashboard, Leaflet India map, Recharts, Prediction studio, responsive UI. |
| **Member 5** | Integration & SIH Lead | `docs/`, `tests/` | End-to-end integration, evaluation metrics, presentation demo script, explainability validation. |

---

## 3. Dataset Status (`output.csv`)

- **File:** `output.csv` (12.8 MB) in workspace root.
- **Source:** Authentic NOAA ISD / ICAO METAR station reports for **Bangalore / Hindustan Airport (VOBG)**.
- **Timeframe:** Full year 2024 (Jan 1, 2024 to Dec 31, 2024) at 30-minute intervals (**16,236 rows**).
- **Profile:**
  - `temperature`: 100% complete (16.0°C – 39.0°C).
  - `relative_humidity`: 100% complete (20% – 100%).
  - `altimeter` (Atmospheric Pressure): 99.7% complete (1005 hPa – 1024 hPa).
  - `wind_speed`: 100% complete (0 – 17.5 m/s).
  - `pres_wx_MW1` / `REM`: Captures rain, drizzle, thunderstorms, mist, haze events.
- **Strategy Decision:**
  - **Hybrid Foundation**: We use this real Bengaluru dataset as the empirical real-world anchor for Bangalore.
  - For the SIH presentation requirement of multi-city national monitoring (Mumbai, Delhi, Chennai, etc.), we complement it with calibrated Indian city profiles matching the exact same schema.

---

## 4. Current Architecture Decisions

1. **Dual Anomaly Engine**:
   - **Layer 1 (Statistical)**: Standardized seasonal Z-score per variable ($Z = (X - \mu)/\sigma$).
   - **Layer 2 (Machine Learning)**: Scikit-learn Isolation Forest trained on multivariable feature vectors (scaled deviations + cyclical time features + rolling averages).
   - **Output Score**: Calibrated float between `0.00` and `1.00`.
2. **Four Severity Classes**:
   - `NORMAL` ($< 0.40$), `WATCH` ($0.40 - 0.69$), `HIGH` ($0.70 - 0.89$), `CRITICAL` ($\ge 0.90$).
3. **Transparent Explainability**:
   - Ranked list of primary contributor variables with their observed value, seasonal expected normal, and deviation percentage.
4. **Backend Stack**:
   - FastAPI + Uvicorn + Pydantic v2 + SQLAlchemy (SQLite for instant zero-config demo, PostgreSQL-compatible).
5. **Frontend Stack**:
   - React + Vite + Tailwind CSS + Lucide Icons + Recharts + React-Leaflet.

---

## 5. Directory Structure Blueprint

```
Innovate X/
├── rules.md                         # Vibe coding & development guidelines
├── memory.md                        # Project state & memory bank
├── GEMINI.md                        # Antigravity project context
├── .cursorrules                     # Cursor / Agent editor configuration
├── architecture.md                  # Detailed system architecture
├── output.csv                       # Raw uploaded METAR dataset (16k rows)
├── data/
│   ├── raw/
│   │   └── bangalore_2024_metar.csv # Relocated copy of output.csv
│   └── processed/
│       ├── weather_cleaned.csv      # Cleaned, standardized observations
│       └── baseline_stats.json      # Precomputed location-monthly normals
├── ml/
│   ├── preprocessing.py             # METAR parser, cleaning & features
│   ├── baseline.py                  # Mean, std, IQR calculator
│   ├── anomaly_engine.py            # Statistical Z-score + Isolation Forest
│   ├── explainability.py            # Contributor ranking & natural language
│   ├── train.py                     # Pipeline training & artifact saver
│   └── models/                      # Saved .joblib model files
├── backend/
│   ├── main.py                      # FastAPI entrypoint
│   ├── config.py                    # App configuration
│   ├── database/                    # SQLAlchemy models & connection
│   ├── schemas/                     # Pydantic request/response schemas
│   ├── routes/                      # /health, /locations, /weather, /anomalies, /predict, /history
│   └── services/                    # Prediction & explainability services
├── frontend/                        # React + Vite dashboard
├── tests/                           # Pytest unit & integration tests
└── docs/                            # SIH presentation guide & documentation
```

---

## 6. Execution Roadmap & Progress

- [x] **Phase 1: Project Blueprint & PRD Analysis** (Completed)
- [x] **Phase 2: Dataset Profiling & Verification** (`output.csv` verified)
- [x] **Phase 3: Vibe Coding Setup** (`rules.md`, `memory.md`, `GEMINI.md`, `.cursorrules`)
- [x] **Phase 4: ML Baseline Engine & Statistical Layer** (Prompts 1.1 - 1.8: `ml/baseline.py`, `ml/anomaly_engine.py`, `data/processed/baseline_statistics.json`)
- [x] **Phase 5: ML Layer & Dual-Engine Fusion** (Prompts 1.9 - 1.15: `MLAnomalyEngine`, `DualAnomalyEngine`, 4-tier severity, anomaly type classifier)
- [x] **Phase 6: Explainability Engine & Training Pipeline** (Prompts 1.16 - 1.20: `ml/explainability.py`, `ml/train.py`, self-validation, `ml/models/isolation_forest.joblib`, `scaler.joblib`)
- [ ] **Phase 7: FastAPI REST Backend** (Endpoints `/predict`, `/locations`, `/weather`, `/history`)
- [ ] **Phase 8: Interactive React Dashboard** (Map, Weather Gauges, Prediction Studio, Charts)
- [ ] **Phase 9: SIH Presentation Script & Demo Polish**

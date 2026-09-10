# 🌦️ Weather Anomaly Detection System (SIH Prototype)

> **AI/ML-Powered Weather Anomaly Detection, Monitoring, and Explainability Platform**  
> **Target:** Smart India Hackathon (SIH)  
> **Core Concept:** Context-aware deviation from historical expected baselines (Statistical Z-scores + Isolation Forest).

---

## 📌 Executive Summary

Traditional weather apps answer: *"What is the weather?"*  
Our system answers: **"Is the current weather behaving abnormally compared to what is historically expected for this location and time?"**

Instead of using naive static thresholds (`temp > 35`), our platform evaluates multivariable observations (temperature, relative humidity, atmospheric pressure, wind speed, precipitation) against historical location- and season-specific baselines using a dual **Statistical + Isolation Forest** architecture.

Every detection provides:
1. **Calibrated Anomaly Score** ($0.00 - 1.00$)
2. **Four-Tier Severity Classification**: `NORMAL`, `WATCH`, `HIGH`, `CRITICAL`
3. **Transparent Explainability**: Contributing factor rankings and deviation percentage from seasonal normal
4. **Interactive Dashboard**: National India map with status pins, location deep-dive, and "What-If" prediction studio.

---

## 🏛️ System Architecture

```text
Weather Observation
        ↓
Data Preprocessing & Bounds Validation
        ↓
Feature Engineering (Cyclic Temporal + Rolling Averages)
        ↓
Historical Baseline Lookup (Location + Month)
        ↓
Dual Engine Detection:
  ├── Layer 1: Statistical Z-Score Deviation
  └── Layer 2: Scikit-learn Isolation Forest
        ↓
Calibrated Anomaly Score [0.00 - 1.00]
        ↓
Severity Classifier (Normal / Watch / High / Critical)
        ↓
Explainability Engine (Contributor Rankings & Rationale)
        ↓
FastAPI Backend (REST API)
        ↓
React Dashboard (Geographic Map + Gauges + Prediction Studio)
```

---

## 👥 Team Responsibilities (5 Members)

| Member | Focus Area | Directory | Responsibilities |
| :--- | :--- | :--- | :--- |
| **Member 1** | **ML / AI Lead** | `ml/` | Baseline calculation, Isolation Forest, Anomaly scoring, Model evaluation & serialization. |
| **Member 2** | **Data Engineer** | `data/`, `ml/preprocessing.py` | Data cleaning, METAR parsing, feature engineering, physical range validation. |
| **Member 3** | **Backend Developer** | `backend/` | FastAPI REST API, Pydantic schemas, database models, prediction service. |
| **Member 4** | **Frontend Developer** | `frontend/` | React dashboard, Leaflet India map, Recharts, Prediction studio, responsive UI. |
| **Member 5** | **Integration & Evaluation** | `docs/`, `tests/` | End-to-end integration, evaluation metrics, SIH demo script, explainability validation. |

---

## 🌳 Git Branching Strategy

Each team member works on a dedicated feature branch:

```bash
# Branch naming convention:
git checkout -b feature/data-engineering     # Member 2
git checkout -b feature/ml-model             # Member 1
git checkout -b feature/fastapi-backend      # Member 3
git checkout -b feature/react-dashboard      # Member 4
git checkout -b feature/evaluation-docs      # Member 5
```

Always create pull requests into `main` after local verification.

---

## 🚀 Quickstart Guide

### 1. Clone & Environment Setup

```bash
git clone <your-github-repo-url>
cd "Innovate X"

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Backend API

```bash
cd backend
uvicorn main:app --reload --port 8000
```
- API Docs (Swagger UI): `http://localhost:8000/docs`

### 3. Run the Frontend Dashboard

```bash
cd frontend
npm install
npm run dev
```
- Dashboard: `http://localhost:5173`

---

## 📂 Project Structure

```
.
├── rules.md                         # Core domain rules & vibe coding guidelines
├── memory.md                        # Living project memory & roadmap
├── GEMINI.md                        # AI pair programmer context
├── .cursorrules                     # Cursor / Agent editor configuration
├── architecture.md                  # Detailed architectural diagrams
├── requirements.txt                 # Global Python dependencies
├── .gitignore                       # Git ignore configuration
├── data/
│   ├── raw/                         # Raw datasets (e.g. Bangalore 2024 METAR)
│   └── processed/                   # Cleaned datasets & precomputed baselines
├── ml/
│   ├── preprocessing.py             # METAR cleaner & feature engineering
│   ├── baseline.py                  # Location-month historical baseline calculator
│   ├── anomaly_engine.py            # Dual statistical + Isolation Forest engine
│   ├── explainability.py            # Contributor ranking & natural language rationale
│   ├── train.py                     # Training & evaluation pipeline
│   └── models/                      # Serialized .joblib models
├── backend/
│   ├── main.py                      # FastAPI application entrypoint
│   ├── routes/                      # API endpoints (/predict, /locations, /weather, etc.)
│   ├── schemas/                     # Pydantic data schemas
│   ├── services/                    # Business logic & inference services
│   └── database/                    # SQLAlchemy database models
├── frontend/                        # React + Vite + Tailwind dashboard
├── docs/                            # Presentation guide & evaluation notes
└── tests/                           # Unit and integration test suite
```

---

## 📜 Key References
- [Architecture Details](architecture.md)
- [Development Rules & Domain Constraints](rules.md)
- [Project Memory Bank](memory.md)

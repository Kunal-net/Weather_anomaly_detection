# Weather Anomaly Detection System — Rules & Development Guidelines

> **Project Identity:** AI/ML-Powered Weather Anomaly Detection, Monitoring, and Explainability Platform  
> **Target:** Smart India Hackathon (SIH) Prototype  
> **Core Concept:** Deviation from Historical Expected Normal (Context-Aware Intelligence)

---

## 1. Core Domain Invariants (NEVER VIOLATE)

1. **Anomaly ≠ Raw Thresholding**:
   - Never use static thresholds like `if temperature > 35: anomaly = True`.
   - 35°C in Delhi in May is normal; 35°C in Shimla or Bengaluru in January is an extreme anomaly.
   - Always evaluate weather relative to **Location + Month/Season + Time of Day + Historical Baseline**.

2. **Anomaly Engine Architecture (Dual-Engine)**:
   - **Statistical Layer**: Computes location-month standardized Z-scores ($Z = \frac{X - \mu}{\sigma}$) for baseline deviations.
   - **ML Layer**: Isolation Forest on multi-variable feature vectors to catch non-linear compound patterns.
   - **Final Score**: Always normalize to calibrated $[0.00, 1.00]$.

3. **Severity Mapping**:
   - `0.00 - 0.39`: **NORMAL** (Within seasonal variation)
   - `0.40 - 0.69`: **WATCH** (Noticeable departure, needs monitoring)
   - `0.70 - 0.89`: **HIGH** (Significant anomaly, potential advisory)
   - `0.90 - 1.00`: **CRITICAL** (Extreme event or severe compound anomaly)

4. **Mandatory Explainability**:
   - Never output just a score. Every prediction MUST provide:
     1. Primary contributor variables ranked by influence.
     2. Observed value vs. Expected seasonal baseline.
     3. Human-readable diagnostic rationale (e.g. *"Rainfall is 650% above September baseline accompanied by severe pressure drop"*).

5. **Clarification on Warnings**:
   - The platform is an **intelligent anomaly monitoring and decision-support layer**.
   - Always display disclaimers distinguishing prototype anomaly detections from official government meteorological warnings (IMD).

---

## 2. Tech Stack & Library Standards

| Layer | Technology | Guidelines |
| :--- | :--- | :--- |
| **Python** | Python 3.9+ | Clean type hints (`typing`), modular functions, PEP 8 style. |
| **ML/Data** | `scikit-learn`, `pandas`, `numpy`, `joblib` | Deterministic random states (`random_state=42`), persistent model artifacts in `ml/models/`. |
| **Backend** | `FastAPI`, `Pydantic v2`, `Uvicorn` | Fully typed schemas, standard HTTP status codes, structured JSON error handling. |
| **Database** | `SQLAlchemy` (SQLite default, Postgres-ready) | Zero-setup local SQLite by default, configurable via `DATABASE_URL`. |
| **Frontend** | `React` + `Vite` + `Tailwind CSS` + `Lucide Icons` | Dark mode / modern sleek UI, responsive grid, live charts (`Recharts`), interactive maps (`Leaflet`). |

---

## 3. Machine Learning Code Guidelines (`ml/`)

- **Separation of Concerns**:
  - `preprocessing.py`: Imputation, physical bounds verification, cyclic feature encoding (`sin`/`cos` day-of-year), rolling statistics.
  - `baseline.py`: Location & monthly historical means, std deviations, percentiles (exported as lookup JSON for $<1$ms API latency).
  - `anomaly_engine.py`: Scikit-learn Isolation Forest inference + statistical Z-score combiner.
  - `explainability.py`: Feature importance, deviation calculation, natural language generator.
  - `train.py`: Training pipeline with validation metrics and model serialization.
- **Physical Bounds Safeguard**:
  - Temperature: $[-50°C, 65°C]$
  - Relative Humidity: $[0\%, 100\%]$
  - Atmospheric Pressure: $[870\text{ hPa}, 1085\text{ hPa}]$
  - Wind Speed: $[0\text{ m/s}, 120\text{ m/s}]$
  - Rainfall: $[0\text{ mm}, 1500\text{ mm}]$
  - Values outside these bounds must be flagged as sensor errors/invalid data, not legitimate anomalies.

---

## 4. Backend & API Conventions (`backend/`)

- **Response Format**:
  All prediction responses must follow the strict Pydantic schema:
  ```json
  {
    "location": "Bengaluru",
    "timestamp": "2024-09-10T12:00:00",
    "is_anomaly": true,
    "anomaly_score": 0.94,
    "severity": "CRITICAL",
    "anomaly_type": "Compound Weather Anomaly",
    "contributors": [
      {
        "feature": "rainfall",
        "contribution_pct": 52.4,
        "observed": 145.0,
        "expected": 18.2,
        "unit": "mm",
        "direction": "HIGH"
      }
    ],
    "explanation": "Observed rainfall is 696% above seasonal baseline..."
  }
  ```
- **Error Handling**: Return clean HTTP 400 with actionable messages for invalid input coordinates, unknown cities, or out-of-bounds metrics.
- **CORS**: Always allow local frontend origins (`http://localhost:5173`, `http://localhost:3000`).

---

## 5. Frontend & UI Conventions (`frontend/`)

- **Design Aesthetic**:
  - Premium dashboard styling: Slate / Dark navy color palette (`#0f172a`, `#1e293b`), crisp typography, smooth transitions.
  - Color-coded severities:
    - 🟢 Normal: Emerald (`#10b981`)
    - 🟡 Watch: Amber / Yellow (`#f59e0b`)
    - 🟠 High: Orange (`#f97316`)
    - 🔴 Critical: Crimson / Rose (`#ef4444`)
- **Key Screens**:
  1. **National Map Overview**: Interactive India map with station pins color-coded by current anomaly status.
  2. **Location Deep Dive**: City weather gauges + Observed vs Historical Expected baseline charts.
  3. **Interactive "What-If" Prediction Studio**: Sliders and presets to test extreme scenarios live.
  4. **Historical Analysis & Trends**: Multi-year timeline and seasonal anomaly frequency charts.

---

## 6. Vibe Coding Workflow Rules

- **Think Modular**: Never dump everything in one monolithic script. Keep ML, API, and Frontend separated.
- **Fail Fast & Verify**: Always test with sample inputs before committing.
- **Update Memory**: Whenever an architectural decision or feature is completed, update `memory.md`.

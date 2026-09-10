# 👥 Team Collaboration Plan & Vibe Coding Prompts

> **Project:** Weather Anomaly Detection System (AeroSense-AI) — SIH Prototype  
> **Team:** ILLUMINATI (Team ID: 27113, PS: SIH1642)  
> **Strategy:** 100% decoupled simultaneous execution. Each member has an independent module, mock fallbacks, and a ready-to-use master prompt for AI pair programming (Cursor / Antigravity / Claude / ChatGPT).

---

## 🤝 The Shared Interface Contract (The Law)

To ensure all 5 parts connect seamlessly on Day 1, everyone adheres to this exact data contract:

### 1. The 4 Severity Tiers:
- `0.00 - 0.39`: **NORMAL** (Emerald Green `#10b981`)
- `0.40 - 0.69`: **WATCH** (Amber Yellow `#f59e0b`)
- `0.70 - 0.89`: **HIGH** (Vibrant Orange `#f97316`)
- `0.90 - 1.00`: **CRITICAL** (Crimson Red `#ef4444`)

### 2. Core Weather Variables:
`temperature` (°C), `relative_humidity` (%), `pressure` (hPa), `wind_speed` (m/s), `rainfall` (mm).

### 3. Prediction API Request & Response JSON:
```json
// POST /predict
// Request Body:
{
  "location": "Bengaluru",
  "month": 9,
  "temperature": 37.0,
  "relative_humidity": 92.0,
  "pressure": 994.0,
  "wind_speed": 14.5,
  "rainfall": 145.0
}

// Response Body:
{
  "location": "Bengaluru",
  "timestamp": "2024-09-10T12:00:00",
  "is_anomaly": true,
  "anomaly_score": 0.94,
  "severity": "CRITICAL",
  "anomaly_type": "Compound Weather Anomaly",
  "contributors": [
    {"feature": "rainfall", "contribution_pct": 52.4, "observed": 145.0, "expected": 18.2, "unit": "mm", "direction": "HIGH"},
    {"feature": "temperature", "contribution_pct": 28.1, "observed": 37.0, "expected": 27.1, "unit": "°C", "direction": "HIGH"},
    {"feature": "pressure", "contribution_pct": 19.5, "observed": 994.0, "expected": 1008.0, "unit": "hPa", "direction": "LOW"}
  ],
  "explanation": "CRITICAL: Observed rainfall is 696% above seasonal baseline with significant temperature surge (+9.9°C) and barometric plunge (-14 hPa)."
}
```

---

## 👤 Member 1: ML / AI Lead
- **Branch:** `feature/ml-model`
- **Ownership Directory:** `ml/`
- **Deliverables:** `ml/baseline.py`, `ml/anomaly_engine.py`, `ml/explainability.py`, `ml/train.py`, `ml/models/isolation_forest.joblib`

### 📋 Vibe Coding Prompt for Member 1:
```text
You are the ML/AI Lead for the SIH Weather Anomaly Detection Platform (AeroSense-AI).
Repository: Innovate X
Read rules.md, memory.md, and PROJECT_EXPLANATION.md for project context.

Your task is to build the core Anomaly Detection & Explainability Engine in the ml/ directory:

1. ml/baseline.py:
   - Create a BaselineCalculator class that reads clean observations and computes monthly historical parameters for each location and weather variable: mean (mu), std dev (sigma), median, IQR, 5th percentile, and 95th percentile.
   - Save the precomputed baselines to data/processed/baseline_statistics.json so lookups take <1ms.

2. ml/anomaly_engine.py:
   - Implement the Dual-Engine Architecture:
     a) Statistical Layer: Computes standardized Z-scores: Z = (X - mu) / sigma.
     b) Machine Learning Layer: Scikit-learn IsolationForest(n_estimators=150, contamination=0.03, random_state=42) trained on multivariable feature vectors (scaled deviations, cyclic temporal sin/cos features, rolling averages).
     c) Score Calibrator: Maps Isolation Forest decision function & statistical departures to a smooth [0.00, 1.00] anomaly score.
     d) Severity Classifier: Normal (<0.40), Watch (0.40-0.69), High (0.70-0.89), Critical (0.90-1.00).
     e) Anomaly Type Classifier: Heat Wave, Cold Wave, Extreme Rainfall, Severe Drought, Low Pressure Depression, or Compound Weather Anomaly.

3. ml/explainability.py:
   - Calculate relative feature contribution: Contrib_i = (|Z_i| / sum(|Z_j|)) * 100.
   - Rank contributors by importance and format observed vs expected delta.
   - Generate natural language diagnostic rationale for decision-makers.

4. ml/train.py:
   - Load processed data, train the Isolation Forest model and standard scaler, evaluate on known extreme benchmarks, and serialize artifacts to ml/models/isolation_forest.joblib and ml/models/scaler.joblib.

Ensure all functions have type hints, docstrings, and zero static thresholding.
```

---

## 👤 Member 2: Data Engineer
- **Branch:** `feature/data-engineering`
- **Ownership Directory:** `data/`, `ml/preprocessing.py`, `ml/data_generator.py`
- **Deliverables:** `ml/preprocessing.py`, `ml/data_generator.py`, `data/processed/weather_cleaned.csv`

### 📋 Vibe Coding Prompt for Member 2:
```text
You are the Data Engineer for the SIH Weather Anomaly Detection Platform (AeroSense-AI).
Repository: Innovate X
Read rules.md, memory.md, and PROJECT_EXPLANATION.md for project context.

Your task is to build the data ingestion, cleaning, and multi-city expansion pipeline in ml/ and data/:

1. ml/preprocessing.py:
   - Ingest the raw NOAA METAR dataset from data/raw/bangalore_2024_metar.csv (16,236 rows).
   - Extract and standardize columns:
     • timestamp: Parse DATE into datetime
     • temperature: Numeric in °C
     • relative_humidity: Numeric in %
     • pressure: Extract from 'altimeter' field in hPa
     • wind_speed: Numeric in m/s
     • visibility: Numeric in km
     • rainfall: Derive continuous estimates from weather phenomena codes ('pres_wx_MW1' like RA, TS, DZ) and precipitation fields.
   - Physical Bounds Filter: Reject impossible values (Humidity 0-100%, Pressure 870-1085 hPa, Temp -50 to 60°C).
   - Feature Engineering:
     • Cyclical temporal features: sin(2pi * day/365), cos(2pi * day/365)
     • Rolling statistics: 7-day and 30-day rolling averages and rainfall accumulations.
   - Save clean dataset to data/processed/weather_cleaned.csv.

2. ml/data_generator.py:
   - To support the national India map and multi-year historical trends during the SIH demo, create a calibrated weather profile synthesizer for 10 key Indian cities (Bengaluru, Mumbai, Delhi, Chennai, Kolkata, Hyderabad, Ahmedabad, Jaipur, Shimla, Bhubaneswar) across 2015–2025.
   - Calibrate each city's distributions to real IMD climate normals (e.g. Mumbai monsoon spikes in July, Delhi 45°C summer peaks in May, Shimla sub-zero winter).
   - Inject labeled historical extreme benchmark events (e.g. 2015 Chennai deluge, 2022 Northern heatwave).
   - Append to data/processed/weather_cleaned.csv so the full system has national coverage.

Provide a command-line entrypoint so running `python ml/preprocessing.py` and `python ml/data_generator.py` executes reproducibly.
```

---

## 👤 Member 3: Backend Developer
- **Branch:** `feature/fastapi-backend`
- **Ownership Directory:** `backend/`
- **Deliverables:** `backend/main.py`, `backend/routes/`, `backend/schemas/`, `backend/services/`, `backend/database/`

### 📋 Vibe Coding Prompt for Member 3:
```text
You are the Backend Developer for the SIH Weather Anomaly Detection Platform (AeroSense-AI).
Repository: Innovate X
Read rules.md, memory.md, and PROJECT_EXPLANATION.md for project context.

Your task is to build the high-performance FastAPI microservice in backend/:

1. backend/schemas/weather.py:
   - Define strict Pydantic v2 schemas for PredictionRequest, PredictionResponse, LocationInfo, WeatherObservation, AnomalyEvent, ContributorItem, and HistoricalTrendResponse matching the shared contract in rules.md.

2. backend/database/:
   - connection.py: SQLAlchemy async/sync database engine (SQLite default for zero-config demo, PostgreSQL-ready via DATABASE_URL).
   - models.py: WeatherObservation table (station, timestamp, metrics) and AnomalyEvent table (score, severity, contributors, explanation).

3. backend/services/:
   - model_loader.py: Singleton service to load Isolation Forest and baseline JSON. If models are not yet trained by Member 1, provide a graceful rule-based/mock fallback so the API works immediately!
   - prediction_service.py: Evaluates incoming requests against baselines, runs model, and computes score and severity.
   - explanation_service.py: Generates contributor percentage rankings and human-readable diagnostic text.

4. backend/routes/:
   - health.py: GET /health (status, loaded model version, database status)
   - locations.py: GET /locations (list of 10 Indian cities, coordinates, active alert level)
   - weather.py: GET /weather/{location} (current observation, baseline comparison)
   - anomalies.py: GET /anomalies (recent anomalies) and GET /anomalies/{location} (history)
   - history.py: GET /history/{location} (time-series observed vs expected values for charts)
   - predictions.py: POST /predict (live prediction endpoint with <15ms response time)

5. backend/main.py:
   - Initialize FastAPI app with CORS middleware (allow localhost:5173 and localhost:3000), register all routers, and include Swagger docs at /docs.

Ensure running `uvicorn backend.main:app --reload --port 8000` starts cleanly with zero warnings.
```

---

## 👤 Member 4: Frontend Developer
- **Branch:** `feature/react-dashboard`
- **Ownership Directory:** `frontend/`
- **Deliverables:** React + Vite + Tailwind CSS dashboard with Leaflet India map, Recharts, and Prediction Studio.

### 📋 Vibe Coding Prompt for Member 4:
```text
You are the Frontend Developer for the SIH Weather Anomaly Detection Platform (AeroSense-AI).
Repository: Innovate X
Read rules.md, memory.md, and PROJECT_EXPLANATION.md for project context.

CRITICAL INSTRUCTION - LEVERAGE INSTALLED SKILLS:
Before writing code, inspect and actively utilize all available agent skills downloaded on this Mac (including `generative_ui`, UI design skills, web development skills, and any custom skills installed in ~/.gemini/ or your AI coding environment). Use them to render rich interactive visual widgets, live component previews, animated dials, and high-fidelity command-center interfaces.

Your task is to build a modern, high-impact monitoring dashboard in frontend/:
Tech Stack: React 18, Vite, Tailwind CSS, Lucide Icons, Leaflet / React-Leaflet, Recharts, Axios.

1. Theme & Design System:
   - Dark command-center theme: Slate/Navy (#0f172a, #1e293b), crisp typography, clean borders.
   - Standardized Severity Colors:
     • NORMAL: #10b981 (Emerald)
     • WATCH: #f59e0b (Amber)
     • HIGH: #f97316 (Orange)
     • CRITICAL: #ef4444 (Crimson)

2. Core Components to Build:
   - Navbar: AeroSense-AI branding, team ILLUMINATI badge, system health indicator, live time.
   - ExecutiveSummaryCards: Metric counters (Total Stations Monitored, Critical Alerts, High, Normal).
   - IndiaAnomalyMap: Interactive Leaflet map of India with custom pulsing SVG pins for Bengaluru, Mumbai, Delhi, Chennai, etc., color-coded by current severity. Clicking a pin opens station details.
   - StationDeepDive: Selected city view with visual dial gauges comparing current reading to the shaded green "Historical Normal Corridor" (mu ± 2*sigma).
   - PredictionStudio (Interactive What-If Tester): Live sliders for Temperature (10-50°C), Rainfall (0-200mm), Humidity (10-100%), Pressure (970-1040 hPa), and Wind Speed (0-40 m/s). As the user moves sliders, trigger POST /predict and update the score, severity badge, and explainability breakdown in real-time.
   - ExplainabilityCard: Horizontal bar chart showing the % contribution of each variable and displaying the natural-language diagnostic text.
   - HistoricalTrends: Recharts time-series comparing observed vs baseline corridor and anomaly frequency bar charts.
   - api.js: Axios service pointing to http://localhost:8000 with mock fallback data so the UI can be developed and previewed independently.

Initialize with `npm create vite@latest frontend -- --template react`, install tailwindcss, lucide-react, recharts, leaflet, react-leaflet, and axios.
```

---

## 👤 Member 5: Integration, Evaluation & SIH Lead
- **Branch:** `feature/integration-docs`
- **Ownership Directory:** `tests/`, `docs/`
- **Deliverables:** `tests/test_ml_pipeline.py`, `tests/test_backend_api.py`, `docs/evaluation_results.md`, Demo script rehearsal.

### 📋 Vibe Coding Prompt for Member 5:
```text
You are the Integration, Evaluation & SIH Lead for the Weather Anomaly Detection Platform (AeroSense-AI).
Repository: Innovate X
Read rules.md, memory.md, PROJECT_EXPLANATION.md, and docs/presentation_content.md for project context.

Your task is to build automated tests, evaluate model accuracy, and orchestrate the SIH demo:

1. tests/test_ml_pipeline.py:
   - Test that baseline calculations compute valid non-null means and standard deviations.
   - Test that Isolation Forest predicts calibrated scores strictly bounded in [0.00, 1.00].
   - Test that the physical bounds filter correctly rejects impossible sensor readings (e.g. 500% humidity).
   - Test that extreme simulated observations (e.g. 37°C + 145mm rain + 994 hPa in Bengaluru) trigger CRITICAL severity (score >= 0.90).
   - Test that typical seasonal values trigger NORMAL severity (score < 0.40).

2. tests/test_backend_api.py:
   - Use FastAPI TestClient (httpx) to test:
     • GET /health returns 200 OK
     • GET /locations returns list of Indian cities
     • POST /predict returns valid response schema with contributor ranking
     • POST /predict rejects invalid out-of-range payloads with 400 Bad Request.

3. docs/evaluation_results.md:
   - Run an evaluation benchmark comparing the Dual-Engine model against baseline methods (static thresholding, standalone Z-score, standalone Isolation Forest) on simulated extreme ground truth events.
   - Report evaluation metrics: Precision, Recall, F1-Score, ROC-AUC, and Inference Latency (<15ms).

4. SIH Demo Script:
   - Rehearse the exact 6-step presentation scenario matching docs/presentation_content.md:
     1. Open Dashboard & show India Map
     2. Select Bengaluru & show normal September baselines
     3. Slide inputs in What-If Studio to extreme (37°C, 145mm rain, 994 hPa)
     4. Show 0.94 CRITICAL score and explainability driver ranking (Rainfall 52%, Temp 28%, Pressure 20%)
     5. Show historical trend comparison
     6. Deliver the winning closing pitch to judges.
```

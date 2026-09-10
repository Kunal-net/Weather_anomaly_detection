# 🎯 20-Step Vibe Coding Prompts for Each Team Member

> **Project:** Weather Anomaly Detection System (AeroSense-AI) — SIH Prototype  
> **Team:** ILLUMINATI (Team ID: 27113, PS: SIH1642)  
> **Instructions:** Each member should open their code editor (Cursor / Antigravity / Claude / ChatGPT) and paste their prompts **one by one (from Prompt 1 to Prompt 20)**. Review the AI's generated code after each prompt, test it, and move to the next.

---

# 👤 MEMBER 1: ML / AI LEAD
**Branch:** `feature/ml-model` | **Primary Directory:** `ml/`

### Phase 1: Historical Baseline Engine (`ml/baseline.py`)
- **Prompt 1.1:** "Create `ml/baseline.py`. Define a `BaselineCalculator` class with an `__init__` method. It should take a Pandas DataFrame of clean weather records with columns `['location', 'month', 'temperature', 'relative_humidity', 'pressure', 'wind_speed', 'rainfall']`. Add docstrings and type hints."
- **Prompt 1.2:** "In `BaselineCalculator`, add a method `compute_baselines()`. Group the data by `['location', 'month']`. For each of the 5 weather variables, compute the mean ($\mu$), standard deviation ($\sigma$), median, 25th percentile, 75th percentile, IQR, 5th percentile, and 95th percentile."
- **Prompt 1.3:** "In `BaselineCalculator`, handle edge cases where a standard deviation is zero or very small: set a minimum variance threshold ($\sigma_{\min} = 0.1$) to prevent division by zero during Z-score calculations."
- **Prompt 1.4:** "In `BaselineCalculator`, implement `save_to_json(filepath)` and `load_from_json(filepath)`. Ensure the precomputed baseline dictionary serializes cleanly into `data/processed/baseline_statistics.json` so that live lookups take $O(1)$ time ($<1\text{ms}$)."
- **Prompt 1.5:** "Add a lookup helper `get_baseline(location: str, month: int) -> dict` in `ml/baseline.py` that returns the baseline parameters for a given location and month, raising a clear ValueError if the location is unknown."

### Phase 2: Statistical Anomaly Layer (`ml/anomaly_engine.py`)
- **Prompt 1.6:** "Create `ml/anomaly_engine.py`. Define a `StatisticalEngine` class that takes baseline statistics from `BaselineCalculator`. Implement `calculate_z_scores(observation: dict, baseline: dict) -> dict` that computes $Z_i = (X_i - \mu_i) / \sigma_i$ for each metric."
- **Prompt 1.7:** "In `StatisticalEngine`, implement `compute_statistical_anomaly_score(z_scores: dict) -> float`. Use a normalized Euclidean / Mahalanobis-style norm of the Z-scores mapped via a sigmoid or tanh function to scale between $[0.00, 1.00]$."
- **Prompt 1.8:** "Add individual variable flags in `StatisticalEngine`: flag any variable as a primary departure if its absolute Z-score $|Z_i| \ge 2.5$ ($p < 0.01$ significance)."

### Phase 3: Machine Learning Layer (Isolation Forest)
- **Prompt 1.9:** "In `ml/anomaly_engine.py`, create a class `MLAnomalyEngine`. Initialize it with Scikit-learn's `IsolationForest(n_estimators=150, contamination=0.03, random_state=42, n_jobs=-1)`."
- **Prompt 1.10:** "In `MLAnomalyEngine`, implement `prepare_features(df: pd.DataFrame) -> np.ndarray`. Standardize the feature vector combining raw metrics, Z-score deviations from monthly baselines, cyclical temporal features (`sin_doy`, `cos_doy`), and rolling statistics using `StandardScaler`."
- **Prompt 1.11:** "In `MLAnomalyEngine`, implement `fit(X: np.ndarray)`. Fit the `StandardScaler` and `IsolationForest`. Ensure random seeds are fixed for 100% reproducible training results."
- **Prompt 1.12:** "In `MLAnomalyEngine`, implement `predict_raw_score(X: np.ndarray) -> float`. Use `decision_function()` from Isolation Forest. Transform the negative decision function output into a continuous calibrated score $[0.00, 1.00]$, where higher values indicate stronger anomalies."

### Phase 4: Dual-Engine Fusion & Severity Mapping
- **Prompt 1.13:** "In `ml/anomaly_engine.py`, create `DualAnomalyEngine` that fuses `StatisticalEngine` and `MLAnomalyEngine`. Define a weighting formula: $\text{FinalScore} = 0.4 \times \text{StatScore} + 0.6 \times \text{MLScore}$. Ensure the output is strictly bounded in $[0.00, 1.00]$."
- **Prompt 1.14:** "In `DualAnomalyEngine`, implement `classify_severity(score: float) -> str`. Map `0.00 - 0.39` to `'NORMAL'`, `0.40 - 0.69` to `'WATCH'`, `0.70 - 0.89` to `'HIGH'`, and `0.90 - 1.00` to `'CRITICAL'`."
- **Prompt 1.15:** "In `DualAnomalyEngine`, implement `classify_anomaly_type(observation, baseline, z_scores) -> str`. Identify specific types: `'Heat Wave'` (high temp), `'Cold Wave'` (low temp), `'Extreme Rainfall'` (high rain), `'Severe Drought'` (low rain & humidity), `'Deep Depression'` (low pressure + wind), or `'Compound Weather Anomaly'` (multiple simultaneous deviations)."

### Phase 5: Explainability & Serialization (`ml/explainability.py` & `ml/train.py`)
- **Prompt 1.16:** "Create `ml/explainability.py`. Define `ExplainabilityEngine`. Implement `compute_feature_contributions(z_scores: dict) -> list[dict]`. Calculate the relative percentage: $\text{Contrib}_i = (|Z_i| / \sum_j |Z_j|) \times 100\%$. Rank features in descending order."
- **Prompt 1.17:** "In `ExplainabilityEngine`, format each contributor object to include: `feature`, `contribution_pct` (rounded to 1 decimal), `observed`, `expected`, `unit`, and `direction` (`'HIGH'` or `'LOW'`)."
- **Prompt 1.18:** "In `ExplainabilityEngine`, implement `generate_natural_language_summary(severity, anomaly_type, contributors) -> str`. Generate clear, actionable diagnostic sentences (e.g. *'CRITICAL: Observed rainfall is 696% above seasonal baseline accompanied by an anomalous +9.9°C heat spike'*)."
- **Prompt 1.19:** "Create `ml/train.py`. Write an end-to-end training script that loads `data/processed/weather_cleaned.csv`, computes baselines, trains the Isolation Forest, tests on known extreme scenarios, and saves artifacts to `ml/models/isolation_forest.joblib` and `ml/models/scaler.joblib`."
- **Prompt 1.20:** "In `ml/train.py`, add a self-validation check: run a simulated normal observation (verify score $< 0.40$) and a simulated cloudburst (verify score $> 0.90$). Print validation status and inference latency (must be $<15\text{ms}$)."

---

# 👤 MEMBER 2: DATA ENGINEER
**Branch:** `feature/data-engineering` | **Primary Directory:** `data/`, `ml/preprocessing.py`, `ml/data_generator.py`

### Phase 1: Ingestion & METAR Parsing (`ml/preprocessing.py`)
- **Prompt 2.1:** "Create `ml/preprocessing.py`. Write a function `load_raw_metar(filepath: str) -> pd.DataFrame` that reads `data/raw/bangalore_2024_metar.csv` efficiently, handling potential mixed types with `low_memory=False`."
- **Prompt 2.2:** "In `ml/preprocessing.py`, extract and clean core columns from the raw dataset: map `DATE` to `timestamp`, `temperature` to float, `dew_point_temperature` to float, `relative_humidity` to float, `wind_speed` to float, and `wind_direction` to float."
- **Prompt 2.3:** "In `ml/preprocessing.py`, extract atmospheric pressure: parse the `altimeter` column (which stores QNH station pressure in hPa/mb). If missing, fallback to `sea_level_pressure` or `station_level_pressure`."
- **Prompt 2.4:** "In `ml/preprocessing.py`, extract precipitation: parse `precipitation_24_hour`, `precipitation_3_hour`, and weather phenomena codes (`pres_wx_MW1` and `REM`). Extract rain event indicators (e.g. `RA`, `DZ`, `TSRA`) and derive a continuous `rainfall` estimate in mm."
- **Prompt 2.5:** "In `ml/preprocessing.py`, parse timestamps into a proper datetime index. Extract `year`, `month`, `day`, `hour`, and `day_of_year` columns."

### Phase 2: Physical Bounds & Sanity Cleaning
- **Prompt 2.6:** "In `ml/preprocessing.py`, implement `validate_physical_bounds(df: pd.DataFrame) -> pd.DataFrame`. Flag or filter physically impossible sensor readings: Temperature $[-50, 60]^\circ\text{C}$, Humidity $[0, 100]\%$, Pressure $[870, 1085]\text{ hPa}$, Wind Speed $[0, 120]\text{ m/s}$, Rainfall $\ge 0\text{ mm}$."
- **Prompt 2.7:** "In `ml/preprocessing.py`, implement missing value imputation: for short gaps ($\le 3$ hours), use forward-fill (`ffill`); for larger gaps, impute using the monthly hourly median. Ensure zero NaN values remain in core columns."
- **Prompt 2.8:** "In `ml/preprocessing.py`, deduplicate records matching the same `(location, timestamp)`. Sort all observations chronologically."

### Phase 3: Feature Engineering
- **Prompt 2.9:** "In `ml/preprocessing.py`, implement cyclical temporal encoding: compute `sin_day = sin(2 * pi * day_of_year / 365.25)` and `cos_day = cos(2 * pi * day_of_year / 365.25)` to represent seamless seasonal transitions."
- **Prompt 2.10:** "In `ml/preprocessing.py`, compute diurnal cyclical encoding: `sin_hour = sin(2 * pi * hour / 24)` and `cos_hour = cos(2 * pi * hour / 24)`."
- **Prompt 2.11:** "In `ml/preprocessing.py`, compute rolling statistics for persistent weather behavior: 7-day rolling mean for `temperature`, `pressure`, and `relative_humidity`, and 7-day cumulative sum for `rainfall`."
- **Prompt 2.12:** "In `ml/preprocessing.py`, compute 30-day seasonal moving averages to capture broader climate trends."
- **Prompt 2.13:** "In `ml/preprocessing.py`, save the cleaned, feature-rich Bengaluru dataset to `data/processed/bangalore_cleaned.csv`."

### Phase 4: Multi-City Indian Meteorological Synthesizer (`ml/data_generator.py`)
- **Prompt 2.14:** "Create `ml/data_generator.py`. Define coordinate, elevation, and climatic zone dictionaries for 10 major Indian cities: Bengaluru (Deccan Plateau), Mumbai (Coastal Tropical), Delhi (Northern Subtropical), Chennai (Coromandel Coast), Kolkata (Gangetic Delta), Hyderabad (Semiarid), Ahmedabad (Hot Semiarid), Jaipur (Arid Desert), Shimla (Himalayan Alpine), and Bhubaneswar (Eastern Coastal)."
- **Prompt 2.15:** "In `ml/data_generator.py`, implement a synthetic observation generator calibrated to genuine IMD monthly normals (1991–2020) for each city across 10 years (2015–2025). Ensure realistic seasonal cycles (e.g. Mumbai monsoon rainfall peaks in July, Delhi summer heat peaks in May, Shimla sub-zero winter temperatures in January)."
- **Prompt 2.16:** "In `ml/data_generator.py`, add realistic diurnal temperature variations (daily highs around 14:00, daily lows around 05:00) and correlated humidity drops."
- **Prompt 2.17:** "In `ml/data_generator.py`, inject known historical extreme weather benchmarks: 2015 Chennai Cloudburst (Dec 1, 2015), 2022 Northern India Heatwave (May 2022 in Delhi/Jaipur), 2020 Cyclone Amphan pressure drop (May 2020 in Kolkata), and 2024 Bengaluru record heatwave."
- **Prompt 2.18:** "In `ml/data_generator.py`, tag injected extreme events with an `is_ground_truth_anomaly` boolean column for Member 5 to use in model evaluation."
- **Prompt 2.19:** "In `ml/data_generator.py`, combine the real Bengaluru observations with the 10-city calibrated historical dataset and save to `data/processed/weather_cleaned.csv`."
- **Prompt 2.20:** "Write a CLI entrypoint in `ml/preprocessing.py` and `ml/data_generator.py` so running `python ml/preprocessing.py && python ml/data_generator.py` completely rebuilds `data/processed/` with progress logs."

---

# 👤 MEMBER 3: BACKEND DEVELOPER
**Branch:** `feature/fastapi-backend` | **Primary Directory:** `backend/`

### Phase 1: FastAPI Core & Pydantic Schemas (`backend/schemas/` & `backend/main.py`)
- **Prompt 3.1:** "Create `backend/config.py` using `pydantic-settings`. Define `Settings` class with `PROJECT_NAME='AeroSense-AI'`, `API_V1_STR='/api/v1'`, `CORS_ORIGINS=['http://localhost:5173', 'http://localhost:3000']`, and `DATABASE_URL='sqlite:///./weather_anomaly.db'`."
- **Prompt 3.2:** "Create `backend/schemas/weather.py`. Define Pydantic v2 model `PredictionRequest` with fields: `location: str`, `month: Optional[int]`, `temperature: float`, `relative_humidity: float`, `pressure: float`, `wind_speed: float`, `rainfall: float`. Add field validators ensuring inputs are within physical bounds."
- **Prompt 3.3:** "In `backend/schemas/weather.py`, define `ContributorItem` schema (`feature`, `contribution_pct`, `observed`, `expected`, `unit`, `direction`)."
- **Prompt 3.4:** "In `backend/schemas/weather.py`, define `PredictionResponse` schema (`location`, `timestamp`, `is_anomaly`, `anomaly_score`, `severity`, `anomaly_type`, `contributors`, `explanation`)."
- **Prompt 3.5:** "In `backend/schemas/weather.py`, define schemas for `LocationInfo` (city, lat, lon, state, current_severity, current_score) and `HistoricalDataPoint` (timestamp, observed, expected_normal, upper_bound, lower_bound)."
- **Prompt 3.6:** "Create `backend/main.py`. Initialize the FastAPI application with title 'AeroSense-AI Weather Anomaly Platform', add CORS middleware with `allow_origins=['*']`, `allow_methods=['*']`, `allow_headers=['*']`, and add a root welcome endpoint."

### Phase 2: Database Layer (`backend/database/`)
- **Prompt 3.7:** "Create `backend/database/connection.py`. Set up SQLAlchemy engine, `sessionmaker`, and `Base = declarative_base()`. Use SQLite by default for zero-setup local development, with PostgreSQL support enabled via `DATABASE_URL`."
- **Prompt 3.8:** "Create `backend/database/models.py`. Define `WeatherObservationModel` table (`id`, `location`, `timestamp`, `temperature`, `relative_humidity`, `pressure`, `wind_speed`, `rainfall`, `created_at`)."
- **Prompt 3.9:** "In `backend/database/models.py`, define `AnomalyEventModel` table (`id`, `location`, `timestamp`, `anomaly_score`, `severity`, `anomaly_type`, `contributors_json`, `explanation`)."
- **Prompt 3.10:** "In `backend/database/connection.py`, add a function `init_db()` that creates all tables on application startup."

### Phase 3: Service Layer & Mock Fallbacks (`backend/services/`)
- **Prompt 3.11:** "Create `backend/services/model_loader.py`. Implement a singleton loader that loads `ml/models/isolation_forest.joblib`, `scaler.joblib`, and `data/processed/baseline_statistics.json`. If files do not exist yet, log a warning and initialize a graceful rule-based mock engine so the API is fully functional for frontend testing immediately."
- **Prompt 3.12:** "Create `backend/services/prediction_service.py`. Implement `predict_weather_anomaly(request: PredictionRequest) -> PredictionResponse`. Look up seasonal baselines, compute deviations, call `model_loader`, and format the response."
- **Prompt 3.13:** "Create `backend/services/explanation_service.py`. Implement logic to calculate feature percentage contributions and construct a human-readable diagnostic sentence."

### Phase 4: API Routes (`backend/routes/`)
- **Prompt 3.14:** "Create `backend/routes/health.py` with endpoint `GET /health`. Return system status (`'ok'`), model loaded status, database connectivity, and version."
- **Prompt 3.15:** "Create `backend/routes/locations.py` with endpoint `GET /locations`. Return the list of all 10 monitored Indian cities with latitude, longitude, elevation, current anomaly score, and active severity level."
- **Prompt 3.16:** "Create `backend/routes/weather.py` with endpoint `GET /weather/{location}`. Return the latest weather observation for the given city along with its expected monthly normals."
- **Prompt 3.17:** "Create `backend/routes/anomalies.py` with endpoints `GET /anomalies` (returns the 20 most recent anomaly events across India) and `GET /anomalies/{location}` (returns anomaly events for a specific city)."
- **Prompt 3.18:** "Create `backend/routes/history.py` with endpoint `GET /history/{location}`. Accept query parameters `variable` (default: `'temperature'`) and `days` (default: 30). Return observed vs expected baseline corridors for charts."
- **Prompt 3.19:** "Create `backend/routes/predictions.py` with endpoint `POST /predict`. Validate input payload with `PredictionRequest`, invoke `prediction_service`, log the event to `AnomalyEventModel` if `is_anomaly=True`, and return `PredictionResponse`."
- **Prompt 3.20:** "In `backend/main.py`, include all routers under `/api/v1`. Add custom exception handlers for 400 Bad Request and 404 Not Found returning clean JSON error responses. Verify running `uvicorn backend.main:app --reload --port 8000` loads Swagger docs cleanly at `http://localhost:8000/docs`."

---

# 👤 MEMBER 4: FRONTEND DEVELOPER
**Branch:** `feature/react-dashboard` | **Primary Directory:** `frontend/`  
> 💡 **CRITICAL AI SKILL DIRECTIVE:** Before executing frontend prompts, instruct your AI coding assistant to inspect, activate, and utilize all local agent skills downloaded on this Mac (including `generative_ui`, UI design skills, and any custom web/prototyping skills located in `~/.gemini/` or your AI environment). Use them to render live interactive widgets, animated dials, and rich command-center interfaces.

### Phase 1: Setup & Design System
- **Prompt 4.1:** "CRITICAL: Inspect and leverage all available local agent skills downloaded on this Mac (including `generative_ui` and UI design skills in ~/.gemini/ or environment). Initialize Vite + React in frontend/. Install Tailwind CSS, lucide-react, recharts, leaflet, react-leaflet, and axios. Configure tailwind.config.js with dark slate theme and severity colors: Normal (#10b981), Watch (#f59e0b), High (#f97316), Critical (#ef4444)."
- **Prompt 4.2:** "Create `frontend/src/services/api.js`. Create an Axios client configured to `http://localhost:8000/api/v1`. Include local mock fallback responses for every endpoint so the entire frontend can be built and previewed without running the backend."
- **Prompt 4.3:** "Create `frontend/src/components/Navbar.jsx`. Include the AeroSense-AI brand logo, Team ILLUMINATI badge, live ticking clock, API status indicator, and tab navigation (`National Map`, `Station Deep-Dive`, `What-If Studio`, `Historical Trends`)."
- **Prompt 4.4:** "Create `frontend/src/components/ExecutiveSummaryCards.jsx`. Display 4 responsive metric summary cards: Total Stations Monitored, Critical Alerts, High Alerts, and Stations Normal, with pulsing status indicators."

### Phase 2: Interactive India Map (`frontend/src/components/IndiaAnomalyMap.jsx`)
- **Prompt 4.5:** "Create `frontend/src/components/IndiaAnomalyMap.jsx` using `react-leaflet`. Center the map on India (`lat: 20.5937, lon: 78.9629`, zoom: 5). Use a dark-mode tile layer (CartoDB Dark Matter)."
- **Prompt 4.6:** "In `IndiaAnomalyMap.jsx`, create custom SVG marker icons that pulse with glowing borders matching station severity: Green (Normal), Yellow (Watch), Orange (High), Red (Critical)."
- **Prompt 4.7:** "In `IndiaAnomalyMap.jsx`, bind Leaflet Popups to each station pin showing city name, current temperature, rainfall, anomaly score %, and severity badge."
- **Prompt 4.8:** "In `IndiaAnomalyMap.jsx`, add an `onSelectLocation(locationName)` callback when a user clicks a station marker, smoothly switching the deep-dive panel to that city."

### Phase 3: Station Deep-Dive & Baseline Gauges
- **Prompt 4.9:** "Create `frontend/src/components/StationDeepDive.jsx`. Display the selected city name, coordinates, elevation, and overall anomaly status banner."
- **Prompt 4.10:** "In `StationDeepDive.jsx`, create 5 metric gauge cards: Temperature, Rainfall, Humidity, Pressure, Wind Speed. Show Observed Value, Expected Seasonal Normal, and Deviation Delta ($\Delta$). Color-code the delta (e.g. red for $+9.9^\circ\text{C}$)."
- **Prompt 4.11:** "In `StationDeepDive.jsx`, add a visual progress bar or mini-corridor for each metric showing where the current observation sits relative to the normal $\mu \pm 2\sigma$ corridor."

### Phase 4: Interactive "What-If" Prediction Studio (The SIH Demo Feature)
- **Prompt 4.12:** "Create `frontend/src/components/PredictionStudio.jsx`. Include a city selector (default: Bengaluru) and a month selector."
- **Prompt 4.13:** "In `PredictionStudio.jsx`, create 5 interactive sliders with numeric input fields: Temperature ($10-50^\circ\text{C}$), Rainfall ($0-200\text{ mm}$), Relative Humidity ($10-100\%$), Pressure ($970-1040\text{ hPa}$), Wind Speed ($0-40\text{ m/s}$)."
- **Prompt 4.14:** "In `PredictionStudio.jsx`, add quick-preset buttons for SIH demo scenarios: 'Normal September Day', 'Extreme Heatwave', 'Bengaluru Cloudburst (145mm Rain + 994 hPa)', 'Cyclone Depression'. Clicking a preset populates all sliders immediately."
- **Prompt 4.15:** "In `PredictionStudio.jsx`, trigger a debounced `POST /predict` API call whenever sliders change. Display a large gauge showing the Anomaly Score (0–100%), animated severity badge (`CRITICAL`, `HIGH`, `WATCH`, `NORMAL`), and the anomaly type tag."

### Phase 5: Explainability & Historical Trends
- **Prompt 4.16:** "Create `frontend/src/components/ExplainabilityCard.jsx`. Display the natural-language diagnostic alert string in a high-contrast banner."
- **Prompt 4.17:** "In `ExplainabilityCard.jsx`, use Recharts `BarChart` to render a horizontal bar chart ranking the contributor variables by their contribution percentage (e.g. Rainfall 52.4%, Temp 28.1%, Pressure 19.5%)."
- **Prompt 4.18:** "Create `frontend/src/components/HistoricalTrends.jsx`. Use Recharts `AreaChart` and `LineChart` to plot the 30-day time-series: shaded green area for Normal Corridor ($\mu \pm 2\sigma$), blue line for observed readings, and red alert dots for anomaly breaches."
- **Prompt 4.19:** "In `HistoricalTrends.jsx`, add a seasonal anomaly frequency bar chart showing how many anomalies occurred in Winter, Summer, Monsoon, and Post-Monsoon."
- **Prompt 4.20:** "In `frontend/src/App.jsx`, wire all components into a sleek, responsive dark layout. Add a toast notification when an anomaly escalates to Critical. Ensure layout works seamlessly on laptops and projectors."

---

# 👤 MEMBER 5: INTEGRATION, EVALUATION & SIH LEAD
**Branch:** `feature/integration-docs` | **Primary Directory:** `tests/`, `docs/`, `eval/`

### Phase 1: ML Unit Tests (`tests/test_ml_pipeline.py`)
- **Prompt 5.1:** "Create `tests/test_ml_pipeline.py`. Write a test `test_baseline_calculation()` that loads clean weather data, computes monthly baselines, and asserts that $\mu$, $\sigma$, and $IQR$ are non-null and valid for all 10 cities."
- **Prompt 5.2:** "In `tests/test_ml_pipeline.py`, write `test_physical_bounds_validator()`. Feed impossible inputs (e.g. Humidity = 500%, Temp = -999°C) and assert that the preprocessing pipeline correctly filters them out."
- **Prompt 5.3:** "In `tests/test_ml_pipeline.py`, write `test_isolation_forest_score_bounds()`. Run 100 diverse random weather vectors and assert that all predicted anomaly scores lie strictly within $[0.00, 1.00]$."
- **Prompt 5.4:** "In `tests/test_ml_pipeline.py`, write `test_normal_weather_scenario()`. Provide typical September Bengaluru weather (26°C, 10mm rain, 70% humidity, 1014 hPa) and assert that the severity is `'NORMAL'` and anomaly score $< 0.40$."
- **Prompt 5.5:** "In `tests/test_ml_pipeline.py`, write `test_extreme_cloudburst_scenario()`. Provide extreme values (37°C, 145mm rain, 92% humidity, 994 hPa) and assert that severity is `'CRITICAL'` (score $\ge 0.90$) and that rainfall is ranked as the #1 contributor."
- **Prompt 5.6:** "In `tests/test_ml_pipeline.py`, write `test_explainability_percentages()`. Assert that the sum of all contributor percentages equals $100.0\% \pm 0.5\%$."

### Phase 2: Backend API Integration Tests (`tests/test_backend_api.py`)
- **Prompt 5.7:** "Create `tests/test_backend_api.py` using `fastapi.testclient.TestClient`. Write `test_health_endpoint()` asserting `GET /health` returns status code 200 and `'status': 'ok'`."
- **Prompt 5.8:** "In `tests/test_backend_api.py`, write `test_locations_endpoint()` asserting `GET /locations` returns a list of 10 cities with latitude, longitude, and active severity."
- **Prompt 5.9:** "In `tests/test_backend_api.py`, write `test_predict_endpoint_valid()` asserting `POST /predict` returns a valid schema with score, severity, contributors, and explanation."
- **Prompt 5.10:** "In `tests/test_backend_api.py`, write `test_predict_endpoint_invalid()` sending out-of-bounds metrics (e.g. humidity = -20%) and asserting HTTP 400 or 422 with actionable error messages."
- **Prompt 5.11:** "In `tests/test_backend_api.py`, write `test_history_endpoint()` asserting `GET /history/Bengaluru` returns time-series points with observed and expected normal values."

### Phase 3: Benchmark Model Evaluation (`eval/evaluate_models.py`)
- **Prompt 5.12:** "Create `eval/evaluate_models.py`. Ingest the test dataset with labeled ground-truth extreme events from Member 2."
- **Prompt 5.13:** "In `eval/evaluate_models.py`, implement baseline comparison models:
  1. Static Threshold Model (`temp > 35` or `rain > 50`)
  2. Standalone Z-Score Model
  3. Standalone Isolation Forest
  4. Our Proposed Dual-Engine Model."
- **Prompt 5.14:** "In `eval/evaluate_models.py`, compute standard classification metrics for all 4 models: Precision, Recall, F1-Score, and ROC-AUC."
- **Prompt 5.15:** "In `eval/evaluate_models.py`, measure inference latency across 1,000 predictions and calculate 95th percentile latency (target: $<15\text{ms}$)."
- **Prompt 5.16:** "Generate a formatted Markdown evaluation report and save to `docs/evaluation_results.md` containing comparison tables and metric graphs."

### Phase 4: SIH Presentation Drill & Demo Runbook
- **Prompt 5.17:** "Create `docs/demo_runbook.md`. Write a minute-by-minute live demonstration checklist matching our 6-slide presentation ([`docs/presentation_content.md`](docs/presentation_content.md))."
- **Prompt 5.18:** "In `docs/demo_runbook.md`, detail the exact click sequence for the demo:
  1. Show National Anomaly Map (All green except 1 alert).
  2. Click Bengaluru pin to reveal the deep-dive dials.
  3. Switch to Prediction Studio and load the 'Bengaluru Cloudburst' preset.
  4. Point out the instant jump to 0.94 CRITICAL and explainability breakdown.
  5. Show the historical trend chart with the red alert breach marker."
- **Prompt 5.19:** "In `docs/demo_runbook.md`, add a 30-second speaking script for each member during the live judging demo so all 5 members speak."
- **Prompt 5.20:** "Conduct an end-to-end integration dry run: verify that starting the backend (`uvicorn backend.main:app`) and frontend (`npm run dev`) runs the full demo with zero console errors. Log final sign-off in `memory.md`."

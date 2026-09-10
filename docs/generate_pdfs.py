import os
import zlib
import textwrap

class SimplePDFBuilder:
    def __init__(self):
        self.page_width = 595.28
        self.page_height = 841.89
        self.margin_x = 36.0
        self.margin_top = 40.0
        self.margin_bottom = 40.0

    def generate(self, filename, title, subtitle, role_info, prompts_by_phase):
        pages_streams = []
        current_stream = []
        current_page = 1
        y = self.page_height

        def start_page():
            nonlocal y, current_stream
            current_stream = []
            # Background
            current_stream.append("0.98 0.98 0.99 rg 0 0 595.28 841.89 re f")
            
            # Header banner
            current_stream.append("0.06 0.09 0.16 rg 0 760 595.28 81.89 re f")
            current_stream.append("0.06 0.72 0.51 rg 0 757 595.28 3 re f")
            
            # Title text
            current_stream.append(f"1 1 1 rg BT /F2 16 Tf 36 805 Td ({self.escape_pdf(title)}) Tj ET")
            current_stream.append(f"0.58 0.64 0.72 rg BT /F1 9 Tf 36 788 Td ({self.escape_pdf(subtitle)}) Tj ET")
            current_stream.append(f"0.23 0.75 0.62 rg BT /F2 9 Tf 36 768 Td ({self.escape_pdf(role_info)}) Tj ET")
            
            y = 735.0

        def check_page_space(needed_height):
            nonlocal current_page, y, current_stream
            if y - needed_height < self.margin_bottom + 25:
                # Add footer before closing
                current_stream.append(f"0.6 0.6 0.6 rg BT /F1 8 Tf 36 25 Td (AeroSense-AI - Smart India Hackathon 2026 | Team ILLUMINATI - PS: SIH1642) Tj ET")
                current_stream.append(f"0.6 0.6 0.6 rg BT /F1 8 Tf 500 25 Td (Page {current_page}) Tj ET")
                pages_streams.append("\n".join(current_stream))
                current_page += 1
                start_page()

        start_page()

        phase_colors = [
            (0.06, 0.72, 0.51), # Emerald
            (0.15, 0.55, 0.85), # Blue
            (0.95, 0.60, 0.05), # Amber
            (0.55, 0.35, 0.95), # Purple
            (0.92, 0.25, 0.35)  # Rose
        ]

        color_idx = 0
        for phase_name, prompts in prompts_by_phase.items():
            # Phase Header
            check_page_space(35)
            r, g, b = phase_colors[color_idx % len(phase_colors)]
            color_idx += 1
            
            # Phase section bar
            current_stream.append(f"{r} {g} {b} rg {self.margin_x} {y-18} 523 20 re f")
            current_stream.append(f"1 1 1 rg BT /F2 10 Tf {self.margin_x + 10} {y-13} Td ({self.escape_pdf(phase_name.upper())}) Tj ET")
            y -= 28

            for p_num, p_text in prompts:
                # Wrap text to fit in card
                wrapped_lines = textwrap.wrap(p_text, width=85)
                card_height = 24 + len(wrapped_lines) * 12 + 6
                
                check_page_space(card_height + 8)
                
                # Draw Card
                card_y = y - card_height
                # Card background
                current_stream.append(f"1 1 1 rg {self.margin_x} {card_y} 523 {card_height} re f")
                # Card border
                current_stream.append(f"0.88 0.90 0.93 RG 0.5 w {self.margin_x} {card_y} 523 {card_height} re S")
                # Left accent pill
                current_stream.append(f"{r} {g} {b} rg {self.margin_x} {card_y} 4 {card_height} re f")
                
                # Prompt Number / Badge
                current_stream.append(f"0.15 0.20 0.30 rg BT /F2 9 Tf {self.margin_x + 12} {card_y + card_height - 15} Td ({self.escape_pdf(p_num)}) Tj ET")
                
                # Prompt text lines
                line_y = card_y + card_height - 28
                for line in wrapped_lines:
                    current_stream.append(f"0.25 0.28 0.33 rg BT /F1 8.5 Tf {self.margin_x + 12} {line_y} Td ({self.escape_pdf(line)}) Tj ET")
                    line_y -= 12
                
                y = card_y - 7

        # Final footer
        current_stream.append(f"0.6 0.6 0.6 rg BT /F1 8 Tf 36 25 Td (AeroSense-AI - Smart India Hackathon 2026 | Team ILLUMINATI - PS: SIH1642) Tj ET")
        current_stream.append(f"0.6 0.6 0.6 rg BT /F1 8 Tf 500 25 Td (Page {current_page}) Tj ET")
        pages_streams.append("\n".join(current_stream))

        # Build PDF structure
        self.compile_pdf(filename, pages_streams)

    def escape_pdf(self, text):
        # Replace non-latin1 unicode characters with ASCII equivalents
        replacements = {
            '\u2014': ' - ',
            '\u2013': ' - ',
            '\u2018': "'",
            '\u2019': "'",
            '\u201c': '"',
            '\u201d': '"',
            '\u2022': '*',
            '\u00b0': ' deg ',
            '\u2265': '>=',
            '\u2264': '<=',
            '\u03bc': 'mu',
            '\u03c3': 'sigma',
            '\u00b1': '+/-',
            '\u2192': '->'
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        # Encode to ascii/latin1 safely
        text = text.encode('latin-1', 'replace').decode('latin-1')
        return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

    def compile_pdf(self, filename, pages_streams):
        objects = ['', '']
        # Fonts
        f1 = len(objects) + 1
        objects.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
        f2 = len(objects) + 1
        objects.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>')

        page_ids = []
        for stream in pages_streams:
            comp_stream = zlib.compress(stream.encode('latin1'))
            stream_id = len(objects) + 1
            objects.append(f'<< /Length {len(comp_stream)} /Filter /FlateDecode >>\nstream\n'.encode('latin1') + comp_stream + b'\nendstream')
            page_id = len(objects) + 1
            objects.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] /Resources << /Font << /F1 {f1} 0 R /F2 {f2} 0 R >> >> /Contents {stream_id} 0 R >>')
            page_ids.append(page_id)

        objects[0] = '<< /Type /Catalog /Pages 2 0 R >>'
        kids_str = ' '.join(f'{pid} 0 R' for pid in page_ids)
        objects[1] = f'<< /Type /Pages /Kids [{kids_str}] /Count {len(page_ids)} >>'

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as f:
            f.write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
            offsets = []
            for i, obj in enumerate(objects, 1):
                offsets.append(f.tell())
                f.write(f'{i} 0 obj\n'.encode('latin1'))
                if isinstance(obj, str):
                    f.write(obj.encode('latin1'))
                else:
                    f.write(obj)
                f.write(b'\nendobj\n')

            xref_pos = f.tell()
            f.write(b'xref\n')
            f.write(f'0 {len(objects) + 1}\n'.encode('latin1'))
            f.write(b'0000000000 65535 f \n')
            for off in offsets:
                f.write(f'{off:010d} 00000 n \n'.encode('latin1'))

            f.write(b'trailer\n')
            f.write(f'<< /Size {len(objects) + 1} /Root 1 0 R >>\n'.encode('latin1'))
            f.write(b'startxref\n')
            f.write(f'{xref_pos}\n'.encode('latin1'))
            f.write(b'%%EOF\n')

# Prompts Data Definition
builder = SimplePDFBuilder()

# ----------------- MEMBER 1 -----------------
m1_prompts = {
    "Phase 1: Historical Baseline Engine": [
        ("Prompt 1.1", "Create ml/baseline.py. Define a BaselineCalculator class with an __init__ method taking a Pandas DataFrame of clean observations (location, month, temperature, relative_humidity, pressure, wind_speed, rainfall). Add docstrings and type hints."),
        ("Prompt 1.2", "In BaselineCalculator, add compute_baselines(). Group data by [location, month]. For each of the 5 weather variables, compute mean (mu), std dev (sigma), median, 25th percentile, 75th percentile, IQR, 5th percentile, and 95th percentile."),
        ("Prompt 1.3", "In BaselineCalculator, handle zero standard deviations: set a minimum variance threshold (sigma_min = 0.1) to prevent division by zero during Z-score calculations."),
        ("Prompt 1.4", "In BaselineCalculator, implement save_to_json(filepath) and load_from_json(filepath). Save precomputed baselines to data/processed/baseline_statistics.json for O(1) in-memory lookup (<1ms)."),
        ("Prompt 1.5", "Add a helper get_baseline(location: str, month: int) -> dict in ml/baseline.py that returns baseline stats for a given location and month, raising a clean ValueError if location is unknown.")
    ],
    "Phase 2: Statistical Anomaly Layer": [
        ("Prompt 1.6", "Create ml/anomaly_engine.py. Define StatisticalEngine class that takes baseline statistics from BaselineCalculator. Implement calculate_z_scores(obs: dict, base: dict) -> dict computing Z = (X - mu) / sigma."),
        ("Prompt 1.7", "In StatisticalEngine, implement compute_statistical_anomaly_score(z_scores: dict) -> float. Use a normalized Euclidean/Mahalanobis-style norm of Z-scores mapped via a sigmoid/tanh function to scale [0.00, 1.00]."),
        ("Prompt 1.8", "Add individual variable departure flags in StatisticalEngine: flag any variable as primary departure if absolute Z-score |Z| >= 2.5 (p < 0.01 significance).")
    ],
    "Phase 3: Machine Learning Layer (Isolation Forest)": [
        ("Prompt 1.9", "In ml/anomaly_engine.py, create MLAnomalyEngine class. Initialize with Scikit-learn's IsolationForest(n_estimators=150, contamination=0.03, random_state=42, n_jobs=-1)."),
        ("Prompt 1.10", "In MLAnomalyEngine, implement prepare_features(df: pd.DataFrame) -> np.ndarray. Standardize feature vector combining raw metrics, baseline Z-deviations, cyclical temporal sin/cos features, and rolling statistics using StandardScaler."),
        ("Prompt 1.11", "In MLAnomalyEngine, implement fit(X: np.ndarray). Fit the StandardScaler and IsolationForest. Ensure random seeds are fixed for 100% reproducible training."),
        ("Prompt 1.12", "In MLAnomalyEngine, implement predict_raw_score(X: np.ndarray) -> float using decision_function(). Transform negative decision values into a continuous calibrated score [0.00, 1.00] where higher values indicate stronger anomalies.")
    ],
    "Phase 4: Dual-Engine Fusion & Severity Mapping": [
        ("Prompt 1.13", "In ml/anomaly_engine.py, create DualAnomalyEngine fusing StatisticalEngine and MLAnomalyEngine: FinalScore = 0.4 * StatScore + 0.6 * MLScore. Ensure output is strictly bounded in [0.00, 1.00]."),
        ("Prompt 1.14", "In DualAnomalyEngine, implement classify_severity(score: float) -> str: map 0.00-0.39 to NORMAL, 0.40-0.69 to WATCH, 0.70-0.89 to HIGH, and 0.90-1.00 to CRITICAL."),
        ("Prompt 1.15", "In DualAnomalyEngine, implement classify_anomaly_type(obs, base, z_scores) -> str: identify Heat Wave, Cold Wave, Extreme Rainfall, Severe Drought, Deep Depression, or Compound Weather Anomaly.")
    ],
    "Phase 5: Explainability & Serialization": [
        ("Prompt 1.16", "Create ml/explainability.py. Define ExplainabilityEngine. Implement compute_feature_contributions(z_scores: dict) -> list[dict] calculating relative percentage: Contrib_i = (|Z_i| / sum(|Z_j|)) * 100. Rank features in descending order."),
        ("Prompt 1.17", "In ExplainabilityEngine, format each contributor object to include: feature, contribution_pct, observed, expected, unit, and direction ('HIGH' or 'LOW')."),
        ("Prompt 1.18", "In ExplainabilityEngine, implement generate_natural_language_summary(severity, anomaly_type, contributors) -> str producing clear diagnostic rationale sentences for disaster managers."),
        ("Prompt 1.19", "Create ml/train.py. Write an end-to-end training pipeline loading data/processed/weather_cleaned.csv, computing baselines, training Isolation Forest, evaluating extreme scenarios, and saving artifacts to ml/models/isolation_forest.joblib and scaler.joblib."),
        ("Prompt 1.20", "In ml/train.py, add self-validation: test a normal observation (assert score < 0.40) and cloudburst (assert score > 0.90). Print validation status and inference latency (must be <15ms).")
    ]
}

builder.generate(
    "docs/prompts/Member_1_ML_AI_Lead_Prompts.pdf",
    "MEMBER 1: ML & AI LEAD — VIBE CODING ROADMAP",
    "Smart India Hackathon 2026 | Team ILLUMINATI (ID: 27113) | PS: SIH1642",
    "Primary Folder: ml/ | Dedicated Branch: feature/ml-model | Deliverables: 5 Files",
    m1_prompts
)

# ----------------- MEMBER 2 -----------------
m2_prompts = {
    "Phase 1: Ingestion & METAR Parsing": [
        ("Prompt 2.1", "Create ml/preprocessing.py. Write load_raw_metar(filepath: str) -> pd.DataFrame that efficiently reads data/raw/bangalore_2024_metar.csv handling potential mixed types with low_memory=False."),
        ("Prompt 2.2", "In ml/preprocessing.py, extract and clean core columns: map DATE to timestamp, temperature to float, dew_point_temperature to float, relative_humidity to float, wind_speed to float, and wind_direction to float."),
        ("Prompt 2.3", "In ml/preprocessing.py, extract atmospheric pressure: parse the altimeter column (QNH station pressure in hPa). If missing, fallback to sea_level_pressure or station_level_pressure."),
        ("Prompt 2.4", "In ml/preprocessing.py, extract precipitation: parse precipitation_24_hour, precipitation_3_hour, and weather phenomena codes (pres_wx_MW1 and REM for RA, TS, DZ) and derive continuous rainfall in mm."),
        ("Prompt 2.5", "In ml/preprocessing.py, parse timestamps into datetime index. Extract year, month, day, hour, and day_of_year columns.")
    ],
    "Phase 2: Sanity Cleaning & Physical Bounds Filter": [
        ("Prompt 2.6", "In ml/preprocessing.py, implement validate_physical_bounds(df) -> df. Reject sensor glitches: Temperature [-50, 60] deg C, Humidity [0, 100]%, Pressure [870, 1085] hPa, Wind Speed [0, 120] m/s, Rainfall >= 0 mm."),
        ("Prompt 2.7", "In ml/preprocessing.py, implement missing value imputation: for gaps <= 3 hours use forward-fill (ffill); for larger gaps, impute using monthly hourly median. Ensure zero NaN values remain."),
        ("Prompt 2.8", "In ml/preprocessing.py, deduplicate records matching the same (location, timestamp). Sort all observations chronologically.")
    ],
    "Phase 3: Temporal & Rolling Feature Engineering": [
        ("Prompt 2.9", "In ml/preprocessing.py, implement cyclical temporal encoding: sin_day = sin(2*pi*day_of_year/365.25) and cos_day = cos(2*pi*day_of_year/365.25) to represent continuous seasonal cycles."),
        ("Prompt 2.10", "In ml/preprocessing.py, compute diurnal cyclical encoding: sin_hour = sin(2*pi*hour/24) and cos_hour = cos(2*pi*hour/24)."),
        ("Prompt 2.11", "In ml/preprocessing.py, compute rolling statistics for persistent weather: 7-day rolling mean for temperature, pressure, relative_humidity, and 7-day cumulative sum for rainfall."),
        ("Prompt 2.12", "In ml/preprocessing.py, compute 30-day seasonal moving averages to capture broader climatic shifts."),
        ("Prompt 2.13", "In ml/preprocessing.py, save the cleaned, feature-rich Bengaluru dataset to data/processed/bangalore_cleaned.csv.")
    ],
    "Phase 4: Multi-City Indian Meteorological Synthesizer": [
        ("Prompt 2.14", "Create ml/data_generator.py. Define coordinates, elevation, and climatic zones for 10 Indian cities: Bengaluru, Mumbai, Delhi, Chennai, Kolkata, Hyderabad, Ahmedabad, Jaipur, Shimla, and Bhubaneswar."),
        ("Prompt 2.15", "In ml/data_generator.py, generate 10-year historical observations (2015-2025) calibrated to genuine IMD monthly normals (1991-2020) for each city (e.g. Mumbai monsoon peaks in July, Delhi heat in May, Shimla sub-zero winter)."),
        ("Prompt 2.16", "In ml/data_generator.py, add realistic diurnal temperature swings (highs at 14:00, lows at 05:00) with inversely correlated relative humidity."),
        ("Prompt 2.17", "In ml/data_generator.py, inject known historical extreme weather benchmarks: 2015 Chennai Cloudburst (Dec 1, 2015), 2022 Northern Heatwave (May 2022 in Delhi), 2020 Cyclone Amphan (May 2020 in Kolkata), 2024 Bengaluru heat record."),
        ("Prompt 2.18", "In ml/data_generator.py, tag injected extreme events with an is_ground_truth_anomaly boolean flag for Member 5 to evaluate model accuracy."),
        ("Prompt 2.19", "In ml/data_generator.py, combine real Bengaluru observations with the 10-city calibrated historical dataset and save to data/processed/weather_cleaned.csv."),
        ("Prompt 2.20", "Add CLI entrypoints so running python ml/preprocessing.py && python ml/data_generator.py completely rebuilds data/processed/ with clean progress logs.")
    ]
}

builder.generate(
    "docs/prompts/Member_2_Data_Engineer_Prompts.pdf",
    "MEMBER 2: DATA ENGINEER — VIBE CODING ROADMAP",
    "Smart India Hackathon 2026 | Team ILLUMINATI (ID: 27113) | PS: SIH1642",
    "Primary Folder: data/, ml/ | Dedicated Branch: feature/data-engineering | Deliverables: 3 Files",
    m2_prompts
)

# ----------------- MEMBER 3 -----------------
m3_prompts = {
    "Phase 1: FastAPI Core & Pydantic v2 Schemas": [
        ("Prompt 3.1", "Create backend/config.py using pydantic-settings. Define Settings class with PROJECT_NAME='AeroSense-AI', API_V1_STR='/api/v1', CORS_ORIGINS=['http://localhost:5173', 'http://localhost:3000'], and DATABASE_URL='sqlite:///./weather_anomaly.db'."),
        ("Prompt 3.2", "Create backend/schemas/weather.py. Define Pydantic v2 PredictionRequest schema with fields: location: str, month: Optional[int], temperature: float, relative_humidity: float, pressure: float, wind_speed: float, rainfall: float with physical bounds validators."),
        ("Prompt 3.3", "In backend/schemas/weather.py, define ContributorItem schema (feature, contribution_pct, observed, expected, unit, direction)."),
        ("Prompt 3.4", "In backend/schemas/weather.py, define PredictionResponse schema (location, timestamp, is_anomaly, anomaly_score, severity, anomaly_type, contributors, explanation)."),
        ("Prompt 3.5", "In backend/schemas/weather.py, define schemas for LocationInfo (city, lat, lon, state, current_severity, current_score) and HistoricalDataPoint (timestamp, observed, expected_normal, upper_bound, lower_bound)."),
        ("Prompt 3.6", "Create backend/main.py. Initialize FastAPI application with title 'AeroSense-AI Weather Anomaly Platform', CORS middleware with allow_origins=['*'], allow_methods=['*'], and a root welcome endpoint.")
    ],
    "Phase 2: Database Layer (SQLAlchemy)": [
        ("Prompt 3.7", "Create backend/database/connection.py. Set up SQLAlchemy engine, sessionmaker, and Base = declarative_base(). Use SQLite by default for zero-setup local dev with PostgreSQL support via DATABASE_URL."),
        ("Prompt 3.8", "Create backend/database/models.py. Define WeatherObservationModel table (id, location, timestamp, temperature, relative_humidity, pressure, wind_speed, rainfall, created_at)."),
        ("Prompt 3.9", "In backend/database/models.py, define AnomalyEventModel table (id, location, timestamp, anomaly_score, severity, anomaly_type, contributors_json, explanation)."),
        ("Prompt 3.10", "In backend/database/connection.py, add an init_db() function creating all tables on application startup.")
    ],
    "Phase 3: Service Layer & Graceful Mock Fallbacks": [
        ("Prompt 3.11", "Create backend/services/model_loader.py. Implement a singleton loader that loads ml/models/isolation_forest.joblib, scaler.joblib, and data/processed/baseline_statistics.json. If files don't exist yet, provide a graceful rule-based mock fallback so API works immediately for frontend testing!"),
        ("Prompt 3.12", "Create backend/services/prediction_service.py. Implement predict_weather_anomaly(request: PredictionRequest) -> PredictionResponse. Look up baselines, compute deviations, call model_loader, and format response."),
        ("Prompt 3.13", "Create backend/services/explanation_service.py. Implement logic to calculate feature percentage contributions and construct a human-readable diagnostic sentence.")
    ],
    "Phase 4: REST API Endpoints": [
        ("Prompt 3.14", "Create backend/routes/health.py with GET /health returning status 'ok', model loaded status, database connectivity, and version."),
        ("Prompt 3.15", "Create backend/routes/locations.py with GET /locations returning all 10 monitored Indian cities with lat, lon, elevation, current anomaly score, and active severity level."),
        ("Prompt 3.16", "Create backend/routes/weather.py with GET /weather/{location} returning latest weather observation for given city alongside expected monthly normals."),
        ("Prompt 3.17", "Create backend/routes/anomalies.py with GET /anomalies (20 most recent national anomalies) and GET /anomalies/{location} (city history)."),
        ("Prompt 3.18", "Create backend/routes/history.py with GET /history/{location} taking query params variable ('temperature') and days (30). Return observed vs expected baseline corridors for charts."),
        ("Prompt 3.19", "Create backend/routes/predictions.py with POST /predict. Validate payload, invoke prediction_service, log to AnomalyEventModel if anomalous, and return PredictionResponse in <15ms."),
        ("Prompt 3.20", "In backend/main.py, include all routers under /api/v1. Add custom exception handlers for 400 Bad Request and 404 Not Found. Verify uvicorn backend.main:app --reload loads Swagger at http://localhost:8000/docs.")
    ]
}

builder.generate(
    "docs/prompts/Member_3_Backend_Developer_Prompts.pdf",
    "MEMBER 3: BACKEND DEVELOPER — VIBE CODING ROADMAP",
    "Smart India Hackathon 2026 | Team ILLUMINATI (ID: 27113) | PS: SIH1642",
    "Primary Folder: backend/ | Dedicated Branch: feature/fastapi-backend | Deliverables: 8 Files",
    m3_prompts
)

# ----------------- MEMBER 4 -----------------
m4_prompts = {
    "Phase 1: Setup & Command-Center Design System": [
        ("Prompt 4.1", "Initialize Vite + React in frontend/. Install Tailwind CSS, lucide-react, recharts, leaflet, react-leaflet, and axios. Configure tailwind.config.js with dark slate theme and severity colors: Normal (#10b981), Watch (#f59e0b), High (#f97316), Critical (#ef4444)."),
        ("Prompt 4.2", "Create frontend/src/services/api.js with Axios pointing to http://localhost:8000/api/v1. Include local mock fallback responses for every endpoint so frontend can be developed completely without running backend."),
        ("Prompt 4.3", "Create frontend/src/components/Navbar.jsx with AeroSense-AI brand logo, Team ILLUMINATI badge, live ticking clock, API status pill, and navigation tabs (National Map, Station Deep-Dive, What-If Studio, Historical Trends)."),
        ("Prompt 4.4", "Create frontend/src/components/ExecutiveSummaryCards.jsx displaying 4 metric counters: Total Stations Monitored, Critical Alerts, High Alerts, and Stations Normal with glowing status indicators.")
    ],
    "Phase 2: Interactive India Leaflet Map": [
        ("Prompt 4.5", "Create frontend/src/components/IndiaAnomalyMap.jsx using react-leaflet centered on India (lat: 20.59, lon: 78.96, zoom: 5) with dark CartoDB tiles."),
        ("Prompt 4.6", "In IndiaAnomalyMap.jsx, create custom pulsating SVG marker icons matching station severity: Green (Normal), Yellow (Watch), Orange (High), Red (Critical)."),
        ("Prompt 4.7", "In IndiaAnomalyMap.jsx, bind Leaflet Popups to pins showing city name, current temperature, rainfall, anomaly score %, and severity badge."),
        ("Prompt 4.8", "In IndiaAnomalyMap.jsx, add onSelectLocation(cityName) callback when a user clicks a pin, switching the active deep-dive panel to that city.")
    ],
    "Phase 3: Station Deep-Dive & Baseline Gauges": [
        ("Prompt 4.9", "Create frontend/src/components/StationDeepDive.jsx showing selected city name, coordinates, elevation, and overall anomaly status banner."),
        ("Prompt 4.10", "In StationDeepDive.jsx, create 5 metric gauge cards: Temperature, Rainfall, Humidity, Pressure, Wind Speed. Show Observed Value, Expected Seasonal Normal, and Deviation Delta (color-coded red for +9.9 deg C)."),
        ("Prompt 4.11", "In StationDeepDive.jsx, add a visual progress bar or mini-corridor for each metric showing where observed reading sits relative to normal mu +/- 2*sigma corridor.")
    ],
    "Phase 4: What-If Prediction Studio (SIH Demo Feature)": [
        ("Prompt 4.12", "Create frontend/src/components/PredictionStudio.jsx with city selector (default: Bengaluru) and month selector."),
        ("Prompt 4.13", "In PredictionStudio.jsx, create 5 interactive sliders with numeric inputs: Temperature (10-50 deg C), Rainfall (0-200 mm), Humidity (10-100%), Pressure (970-1040 hPa), Wind Speed (0-40 m/s)."),
        ("Prompt 4.14", "In PredictionStudio.jsx, add quick-preset buttons for SIH demo: 'Normal September Day', 'Extreme Heatwave', 'Bengaluru Cloudburst (145mm Rain + 994 hPa)', 'Cyclone Depression'. Clicking populates sliders instantly."),
        ("Prompt 4.15", "In PredictionStudio.jsx, trigger debounced POST /predict on slider changes. Show a large gauge with Anomaly Score (0-100%), animated severity badge (CRITICAL/HIGH/WATCH/NORMAL), and anomaly type tag.")
    ],
    "Phase 5: Explainability & Historical Trends": [
        ("Prompt 4.16", "Create frontend/src/components/ExplainabilityCard.jsx displaying natural-language diagnostic alert string in a high-contrast banner."),
        ("Prompt 4.17", "In ExplainabilityCard.jsx, use Recharts BarChart to render a horizontal bar chart ranking contributor variables by contribution percentage (e.g. Rainfall 52.4%, Temp 28.1%, Pressure 19.5%)."),
        ("Prompt 4.18", "Create frontend/src/components/HistoricalTrends.jsx. Use Recharts AreaChart & LineChart to plot 30-day time-series: shaded green area for Normal Corridor (mu +/- 2*sigma), blue line for observed readings, red dots for breaches."),
        ("Prompt 4.19", "In HistoricalTrends.jsx, add seasonal anomaly frequency bar chart showing occurrences in Winter, Summer, Monsoon, and Post-Monsoon."),
        ("Prompt 4.20", "In frontend/src/App.jsx, wire all components into a sleek, responsive dark layout. Add toast notification when anomaly escalates to Critical. Ensure layout works seamlessly on laptops and projectors.")
    ]
}

builder.generate(
    "docs/prompts/Member_4_Frontend_Developer_Prompts.pdf",
    "MEMBER 4: FRONTEND DEVELOPER — VIBE CODING ROADMAP",
    "Smart India Hackathon 2026 | Team ILLUMINATI (ID: 27113) | PS: SIH1642",
    "Primary Folder: frontend/ | Dedicated Branch: feature/react-dashboard | Deliverables: 8 Components",
    m4_prompts
)

# ----------------- MEMBER 5 -----------------
m5_prompts = {
    "Phase 1: ML Pipeline Automated Tests": [
        ("Prompt 5.1", "Create tests/test_ml_pipeline.py. Write test_baseline_calculation() asserting that mu, sigma, and IQR are non-null and valid for all 10 cities across all months."),
        ("Prompt 5.2", "In tests/test_ml_pipeline.py, write test_physical_bounds_validator() feeding impossible inputs (Humidity=500%, Temp=-999 deg C) and asserting they are correctly filtered out."),
        ("Prompt 5.3", "In tests/test_ml_pipeline.py, write test_isolation_forest_score_bounds() running 100 random weather vectors and asserting all anomaly scores lie strictly within [0.00, 1.00]."),
        ("Prompt 5.4", "In tests/test_ml_pipeline.py, write test_normal_weather_scenario() providing typical September Bengaluru weather (26 deg C, 10mm rain, 70% humidity) and asserting severity is NORMAL and score < 0.40."),
        ("Prompt 5.5", "In tests/test_ml_pipeline.py, write test_extreme_cloudburst_scenario() providing 37 deg C, 145mm rain, 92% humidity, 994 hPa and asserting severity is CRITICAL (score >= 0.90) with rainfall as #1 contributor."),
        ("Prompt 5.6", "In tests/test_ml_pipeline.py, write test_explainability_percentages() asserting the sum of all contributor percentages equals 100.0% +/- 0.5%.")
    ],
    "Phase 2: Backend API Integration Tests": [
        ("Prompt 5.7", "Create tests/test_backend_api.py using FastAPI TestClient (httpx). Write test_health_endpoint() asserting GET /health returns 200 OK and status 'ok'."),
        ("Prompt 5.8", "In tests/test_backend_api.py, write test_locations_endpoint() asserting GET /locations returns 10 cities with lat, lon, and active severity."),
        ("Prompt 5.9", "In tests/test_backend_api.py, write test_predict_endpoint_valid() asserting POST /predict returns valid schema with score, severity, contributors, and explanation."),
        ("Prompt 5.10", "In tests/test_backend_api.py, write test_predict_endpoint_invalid() sending negative humidity (-20%) and asserting HTTP 400 or 422 with actionable error message."),
        ("Prompt 5.11", "In tests/test_backend_api.py, write test_history_endpoint() asserting GET /history/Bengaluru returns time-series data points with observed and expected values.")
    ],
    "Phase 3: Benchmark Model Evaluation & Metrics": [
        ("Prompt 5.12", "Create eval/evaluate_models.py ingesting test dataset with labeled ground-truth extreme events from Member 2."),
        ("Prompt 5.13", "In eval/evaluate_models.py, implement baseline comparison models: 1. Static Threshold Model (temp > 35 or rain > 50), 2. Standalone Z-Score Model, 3. Standalone Isolation Forest, 4. Proposed Dual-Engine Model."),
        ("Prompt 5.14", "In eval/evaluate_models.py, compute standard classification metrics for all 4 models: Precision, Recall, F1-Score, and ROC-AUC."),
        ("Prompt 5.15", "In eval/evaluate_models.py, measure inference latency across 1,000 predictions and calculate 95th percentile latency (target: <15ms)."),
        ("Prompt 5.16", "Generate formatted Markdown evaluation report and save to docs/evaluation_results.md containing comparison tables and metric graphs.")
    ],
    "Phase 4: SIH Presentation Drill & Demo Runbook": [
        ("Prompt 5.17", "Create docs/demo_runbook.md writing a minute-by-minute live demonstration checklist matching our 6-slide presentation (docs/presentation_content.md)."),
        ("Prompt 5.18", "In docs/demo_runbook.md, detail exact click sequence: 1. Show National Anomaly Map, 2. Click Bengaluru pin to reveal deep-dive dials, 3. Load Bengaluru Cloudburst preset in What-If Studio, 4. Point out 0.94 CRITICAL score and explainability breakdown, 5. Show historical trend chart."),
        ("Prompt 5.19", "In docs/demo_runbook.md, add 30-second speaking scripts for each member during the live judging demo so all 5 members speak."),
        ("Prompt 5.20", "Conduct end-to-end integration dry run: verify uvicorn backend.main:app and npm run dev run with zero console errors. Log final sign-off in memory.md.")
    ]
}

builder.generate(
    "docs/prompts/Member_5_Integration_SIH_Lead_Prompts.pdf",
    "MEMBER 5: INTEGRATION & SIH LEAD — VIBE CODING ROADMAP",
    "Smart India Hackathon 2026 | Team ILLUMINATI (ID: 27113) | PS: SIH1642",
    "Primary Folder: tests/, docs/ | Dedicated Branch: feature/integration-docs | Deliverables: 4 Files",
    m5_prompts
)

print("All 5 PDFs generated successfully!")

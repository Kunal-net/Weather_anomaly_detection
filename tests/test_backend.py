"""
Comprehensive Backend Test Suite for AeroSense-AI Weather Anomaly Platform.

Validates all 20 Member 3 prompts (Prompts 3.1 to 3.20):
- Phase 1: Config, Pydantic schemas, physical bounds validators, FastAPI app & CORS
- Phase 2: SQLAlchemy connection, models, and table initialization
- Phase 3: Model loader, singleton instance, fallback resilience, prediction & explanation services
- Phase 4: REST API endpoints (/health, /locations, /weather, /anomalies, /history, /predict)
- Latency check: Live inference under 15ms
- Custom error handlers: 400, 404, 422
"""

import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.config import Settings, settings
from backend.database.connection import SessionLocal, get_db, init_db
from backend.database.models import AnomalyEventModel, Base, WeatherObservationModel
from backend.main import app
from backend.schemas.weather import (
    ContributorItem,
    HealthResponse,
    HistoricalDataPoint,
    HistoricalSeriesResponse,
    LocationInfo,
    PredictionRequest,
    PredictionResponse,
    WeatherSummaryResponse,
)
from backend.services.explanation_service import explanation_service
from backend.services.model_loader import INDIAN_CITIES_METADATA, model_loader
from backend.services.prediction_service import prediction_service

client = TestClient(app)


# ==============================================================================
# Phase 1 Tests: Config & Pydantic v2 Schemas (Prompts 3.1 - 3.6)
# ==============================================================================

def test_prompt_3_1_config_settings():
    """Prompt 3.1: Verify Settings configuration and default values."""
    assert settings.PROJECT_NAME == "AeroSense-AI"
    assert settings.API_V1_STR == "/api/v1"
    assert "http://localhost:5173" in settings.CORS_ORIGINS or "*" in settings.CORS_ORIGINS
    assert "sqlite" in settings.DATABASE_URL.lower()


def test_prompt_3_2_prediction_request_validation():
    """Prompt 3.2: Verify PredictionRequest physical bounds validators."""
    # Valid observation
    valid_req = PredictionRequest(
        location="Bengaluru",
        month=9,
        temperature=27.5,
        relative_humidity=75.0,
        pressure=1008.5,
        wind_speed=4.2,
        rainfall=12.0,
    )
    assert valid_req.location == "Bengaluru"
    assert valid_req.temperature == 27.5

    # Out of bounds temperature (> 65°C)
    with pytest.raises(ValidationError):
        PredictionRequest(
            location="Bengaluru",
            temperature=85.0,
            relative_humidity=50.0,
            pressure=1010.0,
            wind_speed=3.0,
            rainfall=0.0,
        )

    # Out of bounds relative humidity (> 100%)
    with pytest.raises(ValidationError):
        PredictionRequest(
            location="Bengaluru",
            temperature=25.0,
            relative_humidity=120.0,
            pressure=1010.0,
            wind_speed=3.0,
            rainfall=0.0,
        )

    # Out of bounds pressure (< 870 hPa)
    with pytest.raises(ValidationError):
        PredictionRequest(
            location="Bengaluru",
            temperature=25.0,
            relative_humidity=50.0,
            pressure=800.0,
            wind_speed=3.0,
            rainfall=0.0,
        )

    # Out of bounds wind speed (< 0 m/s)
    with pytest.raises(ValidationError):
        PredictionRequest(
            location="Bengaluru",
            temperature=25.0,
            relative_humidity=50.0,
            pressure=1010.0,
            wind_speed=-5.0,
            rainfall=0.0,
        )

    # Out of bounds rainfall (< 0 mm)
    with pytest.raises(ValidationError):
        PredictionRequest(
            location="Bengaluru",
            temperature=25.0,
            relative_humidity=50.0,
            pressure=1010.0,
            wind_speed=3.0,
            rainfall=-10.0,
        )

    # Out of bounds month (13)
    with pytest.raises(ValidationError):
        PredictionRequest(
            location="Bengaluru",
            month=13,
            temperature=25.0,
            relative_humidity=50.0,
            pressure=1010.0,
            wind_speed=3.0,
            rainfall=0.0,
        )


def test_prompt_3_3_contributor_item_schema():
    """Prompt 3.3: Verify ContributorItem schema."""
    item = ContributorItem(
        feature="rainfall",
        contribution_pct=55.4,
        observed=145.0,
        expected=18.0,
        unit="mm",
        direction="HIGH",
        departure=127.0,
        pct_departure=705.5,
        z_score=5.2,
    )
    assert item.feature == "rainfall"
    assert item.contribution_pct == 55.4
    assert item.direction == "HIGH"


def test_prompt_3_4_prediction_response_schema():
    """Prompt 3.4: Verify PredictionResponse schema."""
    resp = PredictionResponse(
        location="Bengaluru",
        timestamp="2026-09-10T12:00:00",
        is_anomaly=True,
        anomaly_score=0.94,
        severity="CRITICAL",
        anomaly_type="Extreme Rainfall",
        contributors=[
            ContributorItem(
                feature="rainfall",
                contribution_pct=60.0,
                observed=150.0,
                expected=15.0,
                unit="mm",
                direction="HIGH",
            )
        ],
        explanation="Severe rainfall detected above seasonal baseline.",
    )
    assert resp.is_anomaly is True
    assert resp.severity == "CRITICAL"
    assert len(resp.contributors) == 1


def test_prompt_3_5_location_and_historical_schemas():
    """Prompt 3.5: Verify LocationInfo and HistoricalDataPoint schemas."""
    loc = LocationInfo(
        city="Bengaluru",
        lat=12.9716,
        lon=77.5946,
        state="Karnataka",
        elevation=920.0,
        current_severity="NORMAL",
        current_score=0.15,
    )
    assert loc.city == "Bengaluru"
    assert loc.elevation == 920.0

    point = HistoricalDataPoint(
        timestamp="2026-09-01",
        observed=27.2,
        expected_normal=27.0,
        upper_bound=31.0,
        lower_bound=23.0,
        is_anomaly=False,
    )
    assert point.observed == 27.2
    assert point.is_anomaly is False


def test_prompt_3_6_root_welcome_endpoint():
    """Prompt 3.6: Verify root welcome endpoint."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["platform"] == "AeroSense-AI Weather Anomaly Platform"
    assert data["docs_url"] == "/docs"


# ==============================================================================
# Phase 2 Tests: Database Layer (Prompts 3.7 - 3.10)
# ==============================================================================

def test_prompt_3_7_to_3_10_database_initialization_and_models():
    """Prompts 3.7 to 3.10: Verify database connection, init_db, and model CRUD."""
    init_db()
    with SessionLocal() as db:
        # Test WeatherObservationModel (Prompt 3.8)
        obs = WeatherObservationModel(
            location="Bengaluru",
            temperature=28.0,
            relative_humidity=70.0,
            pressure=1009.0,
            wind_speed=3.5,
            rainfall=5.0,
        )
        db.add(obs)
        db.commit()
        db.refresh(obs)
        assert obs.id is not None
        assert obs.location == "Bengaluru"

        # Test AnomalyEventModel (Prompt 3.9)
        ev = AnomalyEventModel(
            location="Bengaluru",
            anomaly_score=0.92,
            severity="CRITICAL",
            anomaly_type="Extreme Rainfall",
            contributors_json='[{"feature": "rainfall", "contribution_pct": 80.0, "observed": 120.0, "expected": 15.0, "unit": "mm", "direction": "HIGH"}]',
            explanation="Severe rainfall cloudburst detected.",
        )
        db.add(ev)
        db.commit()
        db.refresh(ev)
        assert ev.id is not None
        assert ev.severity == "CRITICAL"
        ev_dict = ev.to_dict()
        assert len(ev_dict["contributors"]) == 1


# ==============================================================================
# Phase 3 Tests: Services & Fallback Resilience (Prompts 3.11 - 3.13)
# ==============================================================================

def test_prompt_3_11_model_loader_singleton():
    """Prompt 3.11: Verify model loader singleton and baselines availability."""
    assert model_loader is not None
    assert model_loader.stat_engine is not None
    locs = model_loader.get_available_locations()
    assert "Bengaluru" in locs
    assert "Delhi" in locs
    assert "Mumbai" in locs

    baseline_bengaluru = model_loader.get_baseline("Bengaluru", 9)
    assert "temperature" in baseline_bengaluru
    assert "rainfall" in baseline_bengaluru


def test_prompt_3_12_and_3_13_prediction_and_explanation_services():
    """Prompts 3.12 & 3.13: Verify prediction_service and explanation_service."""
    # Test Normal Scenario in Bengaluru (September)
    normal_req = PredictionRequest(
        location="Bengaluru",
        month=9,
        temperature=25.0,
        relative_humidity=78.0,
        pressure=1008.0,
        wind_speed=3.5,
        rainfall=6.0,
    )
    with SessionLocal() as db:
        resp_normal = prediction_service.predict_weather_anomaly(normal_req, db=db)
    assert resp_normal.location == "Bengaluru"
    assert resp_normal.anomaly_score < 0.40
    assert resp_normal.severity == "NORMAL"
    assert resp_normal.is_anomaly is False

    # Test Critical Cloudburst Scenario in Bengaluru (September)
    cloudburst_req = PredictionRequest(
        location="Bengaluru",
        month=9,
        temperature=37.0,
        relative_humidity=96.0,
        pressure=992.0,
        wind_speed=16.5,
        rainfall=165.0,
    )
    with SessionLocal() as db:
        resp_cloudburst = prediction_service.predict_weather_anomaly(cloudburst_req, db=db)
    assert resp_cloudburst.anomaly_score > 0.90
    assert resp_cloudburst.severity == "CRITICAL"
    assert resp_cloudburst.is_anomaly is True
    assert len(resp_cloudburst.contributors) > 0
    assert "Rainfall" in resp_cloudburst.explanation or "CRITICAL" in resp_cloudburst.explanation


# ==============================================================================
# Phase 4 Tests: REST API Endpoints & Error Handling (Prompts 3.14 - 3.20)
# ==============================================================================

def test_prompt_3_14_health_endpoint():
    """Prompt 3.14: GET /api/v1/health and GET /health."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    assert data["database_connectivity"] is True
    assert data["version"] == settings.VERSION

    # Also test root alias /health
    res_root = client.get("/health")
    assert res_root.status_code == 200


def test_prompt_3_15_locations_endpoint():
    """Prompt 3.15: GET /api/v1/locations returns all 10 monitored Indian cities."""
    res = client.get("/api/v1/locations")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 10

    city_names = [c["city"] for c in data]
    expected_cities = [
        "Bengaluru", "Mumbai", "Delhi", "Chennai", "Kolkata",
        "Hyderabad", "Ahmedabad", "Jaipur", "Shimla", "Bhubaneswar"
    ]
    for exp_city in expected_cities:
        assert exp_city in city_names, f"Expected city {exp_city} missing from /locations response"

    # Verify fields in location objects
    first = data[0]
    assert "lat" in first
    assert "lon" in first
    assert "elevation" in first
    assert "current_severity" in first
    assert "current_score" in first


def test_prompt_3_16_weather_endpoint():
    """Prompt 3.16: GET /api/v1/weather/{location}."""
    res = client.get("/api/v1/weather/Bengaluru")
    assert res.status_code == 200
    data = res.json()
    assert data["location"] == "Bengaluru"
    assert "observed" in data
    assert "expected_normals" in data
    assert "departures" in data
    assert "current_anomaly_score" in data

    # Test unknown location returns 404
    res_404 = client.get("/api/v1/weather/AtlantisCity")
    assert res_404.status_code == 404
    assert res_404.json()["status"] == "error"


def test_prompt_3_17_anomalies_endpoints():
    """Prompt 3.17: GET /api/v1/anomalies and GET /api/v1/anomalies/{location}."""
    res_national = client.get("/api/v1/anomalies?limit=20")
    assert res_national.status_code == 200
    national_data = res_national.json()
    assert isinstance(national_data, list)
    assert len(national_data) > 0

    res_city = client.get("/api/v1/anomalies/Bengaluru")
    assert res_city.status_code == 200
    city_data = res_city.json()
    assert isinstance(city_data, list)


def test_prompt_3_18_history_endpoint():
    """Prompt 3.18: GET /api/v1/history/{location}."""
    res = client.get("/api/v1/history/Bengaluru?variable=temperature&days=30")
    assert res.status_code == 200
    data = res.json()
    assert data["location"] == "Bengaluru"
    assert data["variable"] == "temperature"
    assert data["unit"] == "°C"
    assert len(data["data"]) == 30

    first_point = data["data"][0]
    assert "observed" in first_point
    assert "expected_normal" in first_point
    assert "upper_bound" in first_point
    assert "lower_bound" in first_point

    # Test invalid variable returns 400
    res_bad_var = client.get("/api/v1/history/Bengaluru?variable=cosmic_radiation")
    assert res_bad_var.status_code == 400


def test_prompt_3_19_predict_endpoint_and_latency():
    """Prompt 3.19: POST /api/v1/predict with latency benchmark <15ms."""
    payload = {
        "location": "Bengaluru",
        "month": 9,
        "temperature": 37.0,
        "relative_humidity": 96.0,
        "pressure": 992.0,
        "wind_speed": 16.5,
        "rainfall": 165.0,
    }

    t0 = time.perf_counter()
    res = client.post("/api/v1/predict", json=payload)
    latency_ms = (time.perf_counter() - t0) * 1000.0

    assert res.status_code == 200
    data = res.json()
    assert data["location"] == "Bengaluru"
    assert data["is_anomaly"] is True
    assert data["severity"] == "CRITICAL"
    assert data["anomaly_score"] > 0.90
    assert len(data["contributors"]) > 0

    # Benchmark average latency across 30 live endpoint requests
    latencies = []
    for _ in range(30):
        t_start = time.perf_counter()
        r = client.post("/api/v1/predict", json=payload)
        latencies.append((time.perf_counter() - t_start) * 1000.0)
        assert r.status_code == 200

    avg_lat = sum(latencies) / len(latencies)
    print(f"\n[POST /api/v1/predict Live Latency] Average: {avg_lat:.2f}ms (Threshold: <15ms)")
    assert avg_lat < 15.0, f"Endpoint latency {avg_lat:.2f}ms exceeded 15ms target."


def test_prompt_3_20_exception_handlers_and_swagger():
    """Prompt 3.20: Verify 400, 404, 422 exception handlers and Swagger docs."""
    # 422 Validation Error on invalid temperature
    res_422 = client.post(
        "/api/v1/predict",
        json={
            "location": "Bengaluru",
            "temperature": 150.0,  # Invalid
            "relative_humidity": 50.0,
            "pressure": 1010.0,
            "wind_speed": 5.0,
            "rainfall": 0.0,
        },
    )
    assert res_422.status_code == 422
    assert res_422.json()["status"] == "validation_error"

    # 404 Not Found
    res_404 = client.get("/api/v1/weather/NonExistentCity123")
    assert res_404.status_code == 404
    assert res_404.json()["status"] == "error"

    # Swagger / OpenAPI documentation availability
    res_docs = client.get("/docs")
    assert res_docs.status_code == 200

    res_openapi = client.get("/openapi.json")
    assert res_openapi.status_code == 200
    openapi_data = res_openapi.json()
    assert "paths" in openapi_data
    assert f"{settings.API_V1_STR}/predict" in openapi_data["paths"]
    assert f"{settings.API_V1_STR}/locations" in openapi_data["paths"]
    assert f"{settings.API_V1_STR}/health" in openapi_data["paths"]

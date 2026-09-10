"""
Weather Observation & Historical Normals Endpoint.

Returns the latest weather observation for a given Indian city alongside
precomputed seasonal expected normals and metric departures.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import WeatherObservationModel
from backend.schemas.weather import WeatherSummaryResponse
from backend.services.explanation_service import explanation_service
from backend.services.model_loader import INDIAN_CITIES_METADATA, model_loader

router = APIRouter(tags=["Weather"])


@router.get(
    "/weather/{location}",
    response_model=WeatherSummaryResponse,
    summary="Get Latest Weather Observation & Expected Monthly Normals",
)
def get_weather_for_location(
    location: str = Path(..., description="City or station name (e.g. 'Bengaluru', 'Delhi')"),
    db: Session = Depends(get_db),
) -> WeatherSummaryResponse:
    """Returns latest weather observation for given city alongside expected monthly normals."""
    # Normalize city name
    matched_city = None
    for city in model_loader.get_available_locations():
        if city.lower() == location.strip().lower():
            matched_city = city
            break

    if not matched_city:
        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' is not monitored. Available locations: {model_loader.get_available_locations()}",
        )

    now = datetime.now(timezone.utc)
    current_month = now.month
    baseline = model_loader.get_baseline(matched_city, current_month)

    # Check for latest recorded observation in database
    latest_obs = (
        db.query(WeatherObservationModel)
        .filter(WeatherObservationModel.location == matched_city)
        .order_by(WeatherObservationModel.timestamp.desc())
        .first()
    )

    if latest_obs:
        obs_dict: Dict[str, float] = {
            "temperature": round(float(latest_obs.temperature), 2),
            "relative_humidity": round(float(latest_obs.relative_humidity), 2),
            "pressure": round(float(latest_obs.pressure), 2),
            "wind_speed": round(float(latest_obs.wind_speed), 2),
            "rainfall": round(float(latest_obs.rainfall), 2),
        }
        obs_timestamp = latest_obs.timestamp.isoformat()
    else:
        # Generate default current normal reading from baseline
        obs_dict = {
            "temperature": round(float(baseline.get("temperature", {}).get("mean", 27.0)), 2),
            "relative_humidity": round(float(baseline.get("relative_humidity", {}).get("mean", 65.0)), 2),
            "pressure": round(float(baseline.get("pressure", {}).get("mean", 1010.0)), 2),
            "wind_speed": round(float(baseline.get("wind_speed", {}).get("mean", 3.5)), 2),
            "rainfall": round(float(baseline.get("rainfall", {}).get("mean", 10.0)), 2),
        }
        obs_timestamp = now.isoformat()

    expected_normals: Dict[str, float] = {}
    departures: Dict[str, float] = {}
    pct_departures: Dict[str, float] = {}
    z_scores: Dict[str, float] = {}

    for feat in ["temperature", "relative_humidity", "pressure", "wind_speed", "rainfall"]:
        obs_val = obs_dict[feat]
        mu = float(baseline.get(feat, {}).get("mean", obs_val))
        sigma = float(max(baseline.get(feat, {}).get("std", 1.0), 0.1))

        expected_normals[feat] = round(mu, 2)
        dep = round(obs_val - mu, 2)
        departures[feat] = dep
        pct_dep = round((dep / abs(mu) * 100.0) if mu != 0.0 else 0.0, 1)
        pct_departures[feat] = pct_dep
        z_scores[feat] = round(dep / sigma, 2)

    # Evaluate severity
    if model_loader.dual_engine is not None:
        pred = model_loader.dual_engine.predict(obs_dict, matched_city, current_month)
        current_score = float(pred["final_score"])
        current_sev = str(pred["severity"])
        anomaly_type = str(pred["anomaly_type"])
    else:
        current_score = 0.20
        current_sev = "NORMAL"
        anomaly_type = "Normal Seasonal Variation"

    contributors = explanation_service.compute_contributors(
        z_scores=z_scores,
        observation=obs_dict,
        baseline=baseline,
    )
    explanation = explanation_service.generate_explanation(
        severity=current_sev,
        anomaly_type=anomaly_type,
        contributors=contributors,
        location=matched_city,
        month=current_month,
    )

    return WeatherSummaryResponse(
        location=matched_city,
        timestamp=obs_timestamp,
        month=current_month,
        observed=obs_dict,
        expected_normals=expected_normals,
        departures=departures,
        percentage_departures=pct_departures,
        current_anomaly_score=current_score,
        current_severity=current_sev,
        anomaly_type=anomaly_type,
        explanation=explanation,
    )

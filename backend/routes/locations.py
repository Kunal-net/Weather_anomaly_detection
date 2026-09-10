"""
Monitored Locations & National Anomaly Map Endpoints.

Returns all 10 monitored Indian stations with geographic coordinates, elevation,
active anomaly scores, and severity classifications.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import AnomalyEventModel
from backend.schemas.weather import LocationInfo
from backend.services.model_loader import INDIAN_CITIES_METADATA, model_loader

router = APIRouter(tags=["Locations"])


@router.get(
    "/locations",
    response_model=List[LocationInfo],
    summary="Get All 10 Monitored Indian Cities & Current Anomaly Status",
)
def get_locations(db: Session = Depends(get_db)) -> List[LocationInfo]:
    """Returns all 10 monitored Indian cities with lat, lon, elevation, current anomaly score,

    and active severity level.
    """
    results: List[LocationInfo] = []
    current_month = datetime.now(timezone.utc).month

    # Retrieve most recent anomaly events per city from DB if available
    recent_events_query = (
        db.query(AnomalyEventModel)
        .order_by(AnomalyEventModel.timestamp.desc())
        .limit(50)
        .all()
    )
    latest_event_by_city = {}
    for ev in recent_events_query:
        if ev.location not in latest_event_by_city:
            latest_event_by_city[ev.location] = ev

    for city, meta in INDIAN_CITIES_METADATA.items():
        baseline = model_loader.get_baseline(city, current_month)

        # Baseline expected values for current month
        temp_mean = float(baseline.get("temperature", {}).get("mean", 27.0))
        rh_mean = float(baseline.get("relative_humidity", {}).get("mean", 65.0))
        press_mean = float(baseline.get("pressure", {}).get("mean", 1010.0))
        wind_mean = float(baseline.get("wind_speed", {}).get("mean", 3.5))
        rain_mean = float(baseline.get("rainfall", {}).get("mean", 10.0))

        # Check if there is an active logged anomaly event
        if city in latest_event_by_city:
            ev = latest_event_by_city[city]
            current_score = round(float(ev.anomaly_score), 4)
            current_sev = str(ev.severity)
        else:
            # Evaluate baseline condition
            current_score = 0.18
            current_sev = "NORMAL"

        loc_info = LocationInfo(
            city=city,
            lat=float(meta["lat"]),
            lon=float(meta["lon"]),
            state=str(meta["state"]),
            elevation=float(meta["elevation"]),
            current_severity=current_sev,
            current_score=current_score,
            current_anomaly_score=current_score,
            active_severity_level=current_sev,
            temperature=round(temp_mean, 1),
            relative_humidity=round(rh_mean, 1),
            pressure=round(press_mean, 1),
            wind_speed=round(wind_mean, 1),
            rainfall=round(rain_mean, 1),
        )
        results.append(loc_info)

    return results

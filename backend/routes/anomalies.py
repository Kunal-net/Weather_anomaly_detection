"""
Anomaly Event History & National Incident Logs Endpoints (Prompt 3.17).

Provides national and station-specific historical anomaly event streams with
diagnostic explanations and contributor breakdowns.
"""

from __future__ import annotations

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import AnomalyEventModel
from backend.schemas.weather import AnomalyEventResponse, ContributorItem
from backend.services.model_loader import model_loader

router = APIRouter(tags=["Anomalies"])


def _model_to_response(event: AnomalyEventModel) -> AnomalyEventResponse:
    """Converts AnomalyEventModel to Pydantic AnomalyEventResponse."""
    contributors: List[ContributorItem] = []
    if event.contributors_json:
        try:
            raw_list = json.loads(event.contributors_json)
            for item in raw_list:
                contributors.append(ContributorItem(**item))
        except Exception:
            contributors = []

    return AnomalyEventResponse(
        id=event.id,
        location=event.location,
        timestamp=event.timestamp.isoformat() if event.timestamp else "",
        anomaly_score=round(float(event.anomaly_score), 4),
        severity=event.severity,
        anomaly_type=event.anomaly_type,
        contributors=contributors,
        explanation=event.explanation,
        created_at=event.created_at.isoformat() if event.created_at else "",
    )


@router.get(
    "/anomalies",
    response_model=List[AnomalyEventResponse],
    summary="Get 20 Most Recent National Weather Anomalies",
)
def get_recent_anomalies(
    limit: int = Query(default=20, ge=1, le=100, description="Number of events to retrieve"),
    db: Session = Depends(get_db),
) -> List[AnomalyEventResponse]:
    """Returns 20 most recent national anomalies across all monitored stations (Prompt 3.17)."""
    events = (
        db.query(AnomalyEventModel)
        .order_by(AnomalyEventModel.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [_model_to_response(ev) for ev in events]


@router.get(
    "/anomalies/{location}",
    response_model=List[AnomalyEventResponse],
    summary="Get Historical Anomalies for a Specific City",
)
def get_anomalies_for_location(
    location: str = Path(..., description="City or station name (e.g. 'Bengaluru', 'Delhi')"),
    limit: int = Query(default=50, ge=1, le=200, description="Max history events to retrieve"),
    db: Session = Depends(get_db),
) -> List[AnomalyEventResponse]:
    """Returns historical anomalies for a specific city (Prompt 3.17)."""
    matched_city = None
    for city in model_loader.get_available_locations():
        if city.lower() == location.strip().lower():
            matched_city = city
            break

    if not matched_city:
        matched_city = location.strip()

    events = (
        db.query(AnomalyEventModel)
        .filter(AnomalyEventModel.location.ilike(matched_city))
        .order_by(AnomalyEventModel.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [_model_to_response(ev) for ev in events]

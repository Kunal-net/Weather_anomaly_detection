"""
Prediction & Live Inference REST Endpoint (Prompt 3.19).

Processes real-time weather observations, validates physical bounds, executes
dual-engine anomaly detection, logs anomaly events to the database, and returns
an actionable diagnostic payload in <15ms.
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.schemas.weather import PredictionRequest, PredictionResponse
from backend.services.prediction_service import prediction_service

logger = logging.getLogger("backend.routes.predictions")

router = APIRouter(tags=["Predictions"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Weather Anomaly with Explainability",
    description=(
        "Evaluates a single weather observation against location- and season-specific "
        "historical baselines using Dual-Engine (Statistical Z-scores + Isolation Forest). "
        "Automatically logs anomalous events to the database and returns in <15ms."
    ),
)
def predict_anomaly(
    request: PredictionRequest,
    db: Session = Depends(get_db),
) -> PredictionResponse:
    """Validates payload, invokes prediction_service, logs if anomalous, and returns PredictionResponse (Prompt 3.19)."""
    response = prediction_service.predict_weather_anomaly(
        request=request,
        db=db,
        save_observation=True,
    )
    return response

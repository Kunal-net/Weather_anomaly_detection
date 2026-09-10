"""
Health Check & System Status Endpoint.

Returns operational readiness, ML model loading status, database connectivity,
and application version.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database.connection import get_db
from backend.schemas.weather import HealthResponse
from backend.services.model_loader import model_loader

logger = logging.getLogger("backend.routes.health")

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="System Health & Diagnostic Status")
def get_health(db: Session = Depends(get_db)) -> HealthResponse:
    """Returns system status 'ok', ML model loaded status, DB connectivity, and version."""
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception as exc:
        logger.warning(f"Database health check probe failed: {exc}")
        db_connected = False

    engine_name = "DualAnomalyEngine (IsolationForest + Z-Score)"
    if model_loader.is_mock_fallback:
        engine_name = "RuleBasedMockStatisticalEngine (Fallback Mode)"

    return HealthResponse(
        status="ok" if db_connected else "degraded",
        model_loaded=model_loader.is_model_loaded or model_loader.stat_engine is not None,
        database_connectivity=db_connected,
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        active_engine=engine_name,
    )

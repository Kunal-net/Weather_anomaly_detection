"""Routes package for AeroSense-AI Weather Anomaly Platform."""

from backend.routes.anomalies import router as anomalies_router
from backend.routes.health import router as health_router
from backend.routes.history import router as history_router
from backend.routes.locations import router as locations_router
from backend.routes.predictions import router as predictions_router
from backend.routes.weather import router as weather_router

__all__ = [
    "health_router",
    "locations_router",
    "weather_router",
    "anomalies_router",
    "history_router",
    "predictions_router",
]

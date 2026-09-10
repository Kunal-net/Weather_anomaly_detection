"""Pydantic v2 schemas package for AeroSense-AI."""

from backend.schemas.weather import (
    AnomalyEventResponse,
    ContributorItem,
    HealthResponse,
    HistoricalDataPoint,
    HistoricalSeriesResponse,
    LocationInfo,
    PredictionRequest,
    PredictionResponse,
    WeatherSummaryResponse,
)

__all__ = [
    "PredictionRequest",
    "ContributorItem",
    "PredictionResponse",
    "LocationInfo",
    "HistoricalDataPoint",
    "HistoricalSeriesResponse",
    "WeatherSummaryResponse",
    "AnomalyEventResponse",
    "HealthResponse",
]

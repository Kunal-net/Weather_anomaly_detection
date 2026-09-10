"""
SQLAlchemy Database Models for AeroSense-AI Weather Platform.

Defines tables for WeatherObservationModel (Prompt 3.8) and AnomalyEventModel (Prompt 3.9).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
import json

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def utc_now():
    return datetime.now(timezone.utc)


class WeatherObservationModel(Base):
    """Stores incoming or historical weather observations (Prompt 3.8)."""

    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    location = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=utc_now, index=True)
    temperature = Column(Float, nullable=False)
    relative_humidity = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    rainfall = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes model instance to dictionary."""
        return {
            "id": self.id,
            "location": self.location,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "temperature": self.temperature,
            "relative_humidity": self.relative_humidity,
            "pressure": self.pressure,
            "wind_speed": self.wind_speed,
            "rainfall": self.rainfall,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AnomalyEventModel(Base):
    """Stores detected anomalies with scores and explainability diagnostic logs (Prompt 3.9)."""

    __tablename__ = "anomaly_events"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    location = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=utc_now, index=True)
    anomaly_score = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    anomaly_type = Column(String(100), nullable=False)
    contributors_json = Column(Text, nullable=True)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes model instance to dictionary."""
        contributors: List[Dict[str, Any]] = []
        if self.contributors_json:
            try:
                contributors = json.loads(self.contributors_json)
            except Exception:
                contributors = []

        return {
            "id": self.id,
            "location": self.location,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "anomaly_score": self.anomaly_score,
            "severity": self.severity,
            "anomaly_type": self.anomaly_type,
            "contributors": contributors,
            "explanation": self.explanation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

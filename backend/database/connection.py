"""
SQLAlchemy Database Connection & Session Management.

Provides database engine, scoped sessions, Base metadata, get_db generator,
and init_db table initialization on application startup (Prompts 3.7 & 3.10).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config import settings
from backend.database.models import AnomalyEventModel, Base, WeatherObservationModel

logger = logging.getLogger("backend.database")

# Database engine configuration with SQLite zero-setup defaults
database_url = settings.DATABASE_URL
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database session with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_initial_demo_data(db: Session) -> None:
    """Seeds realistic demonstration data across Indian stations if database is empty."""
    # Seed sample anomaly events if none exist
    anomaly_count = db.query(AnomalyEventModel).count()
    if anomaly_count == 0:
        logger.info("🌱 Seeding initial demonstration anomaly events...")
        now = datetime.now(timezone.utc)
        sample_events = [
            {
                "location": "Bengaluru",
                "timestamp": now - timedelta(hours=2),
                "anomaly_score": 0.94,
                "severity": "CRITICAL",
                "anomaly_type": "Extreme Rainfall",
                "contributors_json": json.dumps([
                    {
                        "feature": "rainfall",
                        "contribution_pct": 52.4,
                        "observed": 145.0,
                        "expected": 18.2,
                        "unit": "mm",
                        "direction": "HIGH",
                        "departure": 126.8,
                        "pct_departure": 696.7,
                        "z_score": 5.4,
                    },
                    {
                        "feature": "pressure",
                        "contribution_pct": 28.1,
                        "observed": 994.0,
                        "expected": 1008.0,
                        "unit": "hPa",
                        "direction": "LOW",
                        "departure": -14.0,
                        "pct_departure": -1.4,
                        "z_score": -3.8,
                    },
                    {
                        "feature": "wind_speed",
                        "contribution_pct": 19.5,
                        "observed": 15.2,
                        "expected": 3.8,
                        "unit": "m/s",
                        "direction": "HIGH",
                        "departure": 11.4,
                        "pct_departure": 300.0,
                        "z_score": 3.2,
                    },
                ]),
                "explanation": (
                    "CRITICAL ALERT in Bengaluru: Severe Extreme Rainfall detected relative to September baseline. "
                    "Primary drivers: Rainfall is +697% above normal (145.0mm vs 18.2mm normal, Z=+5.4); "
                    "Atmospheric Pressure departure of -14.0hPa (994.0 vs 1008.0 normal, Z=-3.8)."
                ),
            },
            {
                "location": "Delhi",
                "timestamp": now - timedelta(hours=6),
                "anomaly_score": 0.88,
                "severity": "HIGH",
                "anomaly_type": "Heat Wave",
                "contributors_json": json.dumps([
                    {
                        "feature": "temperature",
                        "contribution_pct": 65.0,
                        "observed": 43.5,
                        "expected": 34.0,
                        "unit": "°C",
                        "direction": "HIGH",
                        "departure": 9.5,
                        "pct_departure": 27.9,
                        "z_score": 4.1,
                    },
                    {
                        "feature": "relative_humidity",
                        "contribution_pct": 25.0,
                        "observed": 18.0,
                        "expected": 35.0,
                        "unit": "%",
                        "direction": "LOW",
                        "departure": -17.0,
                        "pct_departure": -48.6,
                        "z_score": -2.6,
                    },
                ]),
                "explanation": (
                    "HIGH ADVISORY in Delhi: Significant Heat Wave departing from seasonal baseline. "
                    "Primary drivers: Temperature departure of +9.5°C (43.5°C observed vs 34.0°C normal, Z=+4.1)."
                ),
            },
            {
                "location": "Mumbai",
                "timestamp": now - timedelta(hours=12),
                "anomaly_score": 0.78,
                "severity": "HIGH",
                "anomaly_type": "Deep Depression",
                "contributors_json": json.dumps([
                    {
                        "feature": "pressure",
                        "contribution_pct": 48.0,
                        "observed": 995.0,
                        "expected": 1005.0,
                        "unit": "hPa",
                        "direction": "LOW",
                        "departure": -10.0,
                        "pct_departure": -1.0,
                        "z_score": -3.5,
                    },
                    {
                        "feature": "wind_speed",
                        "contribution_pct": 32.0,
                        "observed": 14.5,
                        "expected": 5.0,
                        "unit": "m/s",
                        "direction": "HIGH",
                        "departure": 9.5,
                        "pct_departure": 190.0,
                        "z_score": 2.8,
                    },
                ]),
                "explanation": (
                    "HIGH ADVISORY in Mumbai: Significant Deep Depression departing from seasonal baseline. "
                    "Primary drivers: Pressure drop of -10.0hPa (995.0 vs 1005.0 normal, Z=-3.5)."
                ),
            },
            {
                "location": "Shimla",
                "timestamp": now - timedelta(days=1),
                "anomaly_score": 0.62,
                "severity": "WATCH",
                "anomaly_type": "Cold Wave",
                "contributors_json": json.dumps([
                    {
                        "feature": "temperature",
                        "contribution_pct": 70.0,
                        "observed": -2.0,
                        "expected": 5.5,
                        "unit": "°C",
                        "direction": "LOW",
                        "departure": -7.5,
                        "pct_departure": -136.4,
                        "z_score": -2.8,
                    }
                ]),
                "explanation": (
                    "WATCH MONITORING in Shimla: Noticeable Cold Wave observed relative to seasonal baseline. "
                    "Primary drivers: Temperature departure of -7.5°C (-2.0°C vs 5.5°C normal, Z=-2.8)."
                ),
            },
            {
                "location": "Chennai",
                "timestamp": now - timedelta(days=2),
                "anomaly_score": 0.45,
                "severity": "WATCH",
                "anomaly_type": "Compound Weather Anomaly",
                "contributors_json": json.dumps([
                    {
                        "feature": "relative_humidity",
                        "contribution_pct": 55.0,
                        "observed": 92.0,
                        "expected": 73.0,
                        "unit": "%",
                        "direction": "HIGH",
                        "departure": 19.0,
                        "pct_departure": 26.0,
                        "z_score": 2.1,
                    }
                ]),
                "explanation": (
                    "WATCH MONITORING in Chennai: Noticeable Compound Weather Anomaly observed relative to baseline."
                ),
            },
        ]

        for item in sample_events:
            event = AnomalyEventModel(**item)
            db.add(event)
        db.commit()


def init_db() -> None:
    """Creates all database tables on application startup and seeds initial records (Prompt 3.10)."""
    try:
        logger.info("Initializing database schema...")
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            seed_initial_demo_data(db)
        logger.info("Database schema initialized successfully.")
    except Exception as exc:
        logger.error(f"Error during database initialization: {exc}", exc_info=True)
        raise

"""
Prediction Service for Weather Anomaly Inference & Database Logging.

Provides end-to-end orchestration for evaluating weather observations against historical
baselines, invoking dual-engine inference, calculating explainability contributors,
and persisting anomaly events to the database.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from backend.database.models import AnomalyEventModel, WeatherObservationModel
from backend.schemas.weather import PredictionRequest, PredictionResponse
from backend.services.explanation_service import explanation_service
from backend.services.model_loader import model_loader

logger = logging.getLogger("backend.services.prediction_service")


class PredictionService:
    """Orchestrates weather anomaly evaluation, explainability, and database logging."""

    def predict_weather_anomaly(
        self,
        request: PredictionRequest,
        db: Optional[Session] = None,
        save_observation: bool = True,
    ) -> PredictionResponse:
        """Evaluates a weather observation against historical baselines.

        Args:
            request (PredictionRequest): Validated observation payload.
            db (Optional[Session], optional): SQLAlchemy database session for logging.
            save_observation (bool, optional): If True, stores observation record in DB.

        Returns:
            PredictionResponse: Complete prediction result with severity and contributors.
        """
        t0 = time.perf_counter()
        now = datetime.now(timezone.utc)
        timestamp_str = now.isoformat()

        # Determine effective month (from request or current system date)
        month = request.month if request.month is not None else now.month
        location = request.location.strip()

        obs_dict: Dict[str, float] = {
            "temperature": request.temperature,
            "relative_humidity": request.relative_humidity,
            "pressure": request.pressure,
            "wind_speed": request.wind_speed,
            "rainfall": request.rainfall,
        }

        # 1. Fetch Location-Month Baselines
        baseline = model_loader.get_baseline(location, month)

        # 2. Invoke Dual Anomaly Engine
        dual_engine = model_loader.dual_engine
        if dual_engine is not None:
            pred_result = dual_engine.predict(
                observation=obs_dict,
                location=location,
                month=month,
            )
            final_score = float(pred_result["final_score"])
            severity = str(pred_result["severity"])
            is_anomaly = bool(pred_result["is_anomaly"])
            anomaly_type = str(pred_result["anomaly_type"])
            z_scores = pred_result["z_scores"]
            stat_score = float(pred_result["statistical_score"])
            ml_score = float(pred_result["ml_score"])
        else:
            # Fallback if engine unavailable
            final_score = 0.25
            severity = "NORMAL"
            is_anomaly = False
            anomaly_type = "Normal Seasonal Variation"
            z_scores = {k: 0.0 for k in obs_dict.keys()}
            stat_score = 0.25
            ml_score = 0.25

        # 3. Compute Explainability & Diagnostic Narrative
        contributors = explanation_service.compute_contributors(
            z_scores=z_scores,
            observation=obs_dict,
            baseline=baseline,
        )

        explanation = explanation_service.generate_explanation(
            severity=severity,
            anomaly_type=anomaly_type,
            contributors=contributors,
            location=location,
            month=month,
        )

        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 3)

        # 4. Optional Database Logging
        if db is not None:
            try:
                if save_observation:
                    obs_record = WeatherObservationModel(
                        location=location,
                        timestamp=now,
                        temperature=request.temperature,
                        relative_humidity=request.relative_humidity,
                        pressure=request.pressure,
                        wind_speed=request.wind_speed,
                        rainfall=request.rainfall,
                    )
                    db.add(obs_record)

                if is_anomaly:
                    event_record = AnomalyEventModel(
                        location=location,
                        timestamp=now,
                        anomaly_score=final_score,
                        severity=severity,
                        anomaly_type=anomaly_type,
                        contributors_json=json.dumps([c.model_dump() for c in contributors]),
                        explanation=explanation,
                    )
                    db.add(event_record)

                db.commit()
            except Exception as db_err:
                logger.warning(f"Database logging failed: {db_err}. Rolling back transaction.")
                db.rollback()

        return PredictionResponse(
            location=location,
            timestamp=timestamp_str,
            is_anomaly=is_anomaly,
            anomaly_score=final_score,
            severity=severity,
            anomaly_type=anomaly_type,
            contributors=contributors,
            explanation=explanation,
            statistical_score=stat_score,
            ml_score=ml_score,
            processing_time_ms=elapsed_ms,
        )


# Global service instance
prediction_service = PredictionService()

"""
Singleton Model & Baseline Loader with Graceful Mock Fallbacks.

Loads Isolation Forest, StandardScaler, and historical baseline statistics
from disk. If artifacts are missing, gracefully initializes rule-based mock
engines so the API works immediately without breaking (Prompt 3.11).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from backend.config import settings
from ml.anomaly_engine import DualAnomalyEngine, MLAnomalyEngine, StatisticalEngine
from ml.baseline import BaselineCalculator

logger = logging.getLogger("backend.services.model_loader")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Canonical dictionary of 10 monitored Indian cities and geographical metadata
INDIAN_CITIES_METADATA: Dict[str, Dict[str, Any]] = {
    "Bengaluru": {
        "state": "Karnataka",
        "lat": 12.9716,
        "lon": 77.5946,
        "elevation": 920.0,
        "climate_zone": "Deccan Plateau",
    },
    "Mumbai": {
        "state": "Maharashtra",
        "lat": 19.0760,
        "lon": 72.8777,
        "elevation": 14.0,
        "climate_zone": "Coastal Tropical",
    },
    "Delhi": {
        "state": "Delhi NCR",
        "lat": 28.6139,
        "lon": 77.2090,
        "elevation": 216.0,
        "climate_zone": "Northern Subtropical",
    },
    "Chennai": {
        "state": "Tamil Nadu",
        "lat": 13.0827,
        "lon": 80.2707,
        "elevation": 6.0,
        "climate_zone": "Coromandel Coast",
    },
    "Kolkata": {
        "state": "West Bengal",
        "lat": 22.5726,
        "lon": 88.3639,
        "elevation": 9.0,
        "climate_zone": "Gangetic Delta",
    },
    "Hyderabad": {
        "state": "Telangana",
        "lat": 17.3850,
        "lon": 78.4867,
        "elevation": 542.0,
        "climate_zone": "Semiarid Deccan",
    },
    "Ahmedabad": {
        "state": "Gujarat",
        "lat": 23.0225,
        "lon": 72.5714,
        "elevation": 53.0,
        "climate_zone": "Hot Semiarid",
    },
    "Jaipur": {
        "state": "Rajasthan",
        "lat": 26.9124,
        "lon": 75.7873,
        "elevation": 431.0,
        "climate_zone": "Arid Desert Border",
    },
    "Shimla": {
        "state": "Himachal Pradesh",
        "lat": 31.1048,
        "lon": 77.1734,
        "elevation": 2276.0,
        "climate_zone": "Himalayan Alpine",
    },
    "Bhubaneswar": {
        "state": "Odisha",
        "lat": 20.2961,
        "lon": 85.8245,
        "elevation": 45.0,
        "climate_zone": "Eastern Coastal",
    },
}

# Rule-based fallback baseline statistics if baseline_statistics.json is missing
DEFAULT_MOCK_BASELINES: Dict[str, Dict[str, float]] = {
    "temperature": {"mean": 26.5, "std": 3.2, "median": 26.0, "q25": 24.0, "q75": 29.0, "iqr": 5.0, "min": 15.0, "max": 42.0},
    "relative_humidity": {"mean": 65.0, "std": 12.0, "median": 65.0, "q25": 55.0, "q75": 75.0, "iqr": 20.0, "min": 20.0, "max": 98.0},
    "pressure": {"mean": 1010.0, "std": 4.0, "median": 1010.0, "q25": 1007.0, "q75": 1013.0, "iqr": 6.0, "min": 980.0, "max": 1025.0},
    "wind_speed": {"mean": 3.5, "std": 1.5, "median": 3.2, "q25": 2.2, "q75": 4.5, "iqr": 2.3, "min": 0.0, "max": 25.0},
    "rainfall": {"mean": 15.0, "std": 25.0, "median": 0.0, "q25": 0.0, "q75": 18.0, "iqr": 18.0, "min": 0.0, "max": 250.0},
}


class ModelLoader:
    """Singleton loader for ML models, scalers, and historical baseline statistics."""

    _instance: Optional[ModelLoader] = None

    def __new__(cls) -> ModelLoader:
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self.model_path = _PROJECT_ROOT / settings.MODEL_PATH
        self.scaler_path = _PROJECT_ROOT / settings.SCALER_PATH
        self.baseline_path = _PROJECT_ROOT / settings.BASELINE_STATS_PATH

        self.baseline_calculator: Optional[BaselineCalculator] = None
        self.ml_engine: Optional[MLAnomalyEngine] = None
        self.stat_engine: Optional[StatisticalEngine] = None
        self.dual_engine: Optional[DualAnomalyEngine] = None

        self.is_model_loaded: bool = False
        self.is_mock_fallback: bool = False

        self._load_all_artifacts()
        self._initialized = True

    def _load_all_artifacts(self) -> None:
        """Attempts to load real model & baselines; falls back gracefully if absent."""
        try:
            # 1. Load Baseline Calculator
            target_baseline = self.baseline_path
            if not target_baseline.exists():
                alt_path = _PROJECT_ROOT / "data/processed/baseline_stats.json"
                if alt_path.exists():
                    target_baseline = alt_path

            if target_baseline.exists():
                logger.info(f"Loading baseline statistics from {target_baseline}...")
                self.baseline_calculator = BaselineCalculator.load_from_json(target_baseline)
            else:
                logger.warning("Baseline statistics JSON not found on disk. Initializing mock baseline fallback.")
                self._create_mock_baseline_calculator()

            # 2. Initialize Statistical Engine
            self.stat_engine = StatisticalEngine(
                baseline_calculator=self.baseline_calculator,
                sigma_min=0.1,
            )

            # 3. Load ML Engine (Isolation Forest + Scaler)
            if self.model_path.exists() and self.scaler_path.exists():
                logger.info(f"Loading ML models from {self.model_path} and {self.scaler_path}...")
                self.ml_engine = MLAnomalyEngine.load(
                    model_path=self.model_path,
                    scaler_path=self.scaler_path,
                    baseline_calculator=self.baseline_calculator,
                )
                self.is_model_loaded = True
            else:
                logger.warning(
                    f"ML model artifacts ({self.model_path}, {self.scaler_path}) not found. "
                    "Operating with Statistical engine and fallback."
                )
                self.is_mock_fallback = True

            # 4. Initialize Dual Anomaly Engine
            self.dual_engine = DualAnomalyEngine(
                stat_engine=self.stat_engine,
                ml_engine=self.ml_engine,
                stat_weight=0.4,
                ml_weight=0.6,
            )
            logger.info("AeroSense-AI Anomaly Engines initialized successfully.")

        except Exception as exc:
            logger.error(f"Error loading model artifacts: {exc}. Initializing fallback engines.", exc_info=True)
            self._create_mock_baseline_calculator()
            self.stat_engine = StatisticalEngine(baseline_calculator=self.baseline_calculator)
            self.dual_engine = DualAnomalyEngine(stat_engine=self.stat_engine, ml_engine=None)
            self.is_mock_fallback = True
            self.is_model_loaded = False

    def _create_mock_baseline_calculator(self) -> None:
        """Constructs an in-memory BaselineCalculator containing calibrated Indian city normals."""
        rng = np.random.RandomState(42)
        rows = []
        for city in INDIAN_CITIES_METADATA.keys():
            for m in range(1, 13):
                t_base = 27.0 if city != "Shimla" else 15.0
                rh_base = 65.0
                p_base = 1010.0
                w_base = 3.5
                r_base = 10.0
                for _ in range(30):
                    rows.append({
                        "location": city,
                        "month": m,
                        "temperature": float(rng.normal(t_base, 2.5)),
                        "relative_humidity": float(np.clip(rng.normal(rh_base, 8.0), 10, 100)),
                        "pressure": float(rng.normal(p_base, 3.0)),
                        "wind_speed": float(np.clip(rng.normal(w_base, 1.2), 0.1, 30)),
                        "rainfall": float(np.clip(rng.exponential(r_base), 0, 300)),
                    })
        mock_df = pd.DataFrame(rows)
        self.baseline_calculator = BaselineCalculator(mock_df, sigma_min=0.1, auto_compute=True)
        self.is_mock_fallback = True

    def get_baseline(self, location: str, month: int) -> Dict[str, Dict[str, float]]:
        """Safely fetches location-month baseline dictionary, with fallback if unknown."""
        if self.baseline_calculator is not None:
            try:
                return self.baseline_calculator.get_baseline(location, month)
            except Exception:
                # Try case-insensitive lookup
                for loc in self.baseline_calculator.get_available_locations():
                    if loc.lower() == location.lower():
                        try:
                            return self.baseline_calculator.get_baseline(loc, month)
                        except Exception:
                            pass
        return DEFAULT_MOCK_BASELINES

    def get_available_locations(self) -> List[str]:
        """Returns list of monitored Indian cities."""
        if self.baseline_calculator is not None:
            locs = self.baseline_calculator.get_available_locations()
            if locs:
                all_locs = list(dict.fromkeys(list(INDIAN_CITIES_METADATA.keys()) + locs))
                return all_locs
        return list(INDIAN_CITIES_METADATA.keys())

    def get_city_metadata(self, city: str) -> Dict[str, Any]:
        """Returns geo coordinates, state, and elevation for a city."""
        for name, meta in INDIAN_CITIES_METADATA.items():
            if name.lower() == city.lower():
                return {
                    "city": name,
                    "state": meta["state"],
                    "lat": meta["lat"],
                    "lon": meta["lon"],
                    "elevation": meta["elevation"],
                }
        return {
            "city": city,
            "state": "India",
            "lat": 20.5937,
            "lon": 78.9629,
            "elevation": 100.0,
        }


# Global singleton instance
model_loader = ModelLoader()

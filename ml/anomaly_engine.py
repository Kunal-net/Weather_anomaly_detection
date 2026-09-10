"""
Weather Anomaly Detection Engine.

This module provides the core anomaly detection engines for the weather platform:
1. `StatisticalEngine`: Classical standardized Z-score deviations from historical baselines.
2. `MLAnomalyEngine`: Scikit-learn Isolation Forest on multi-variable feature vectors.
3. `DualAnomalyEngine`: Hybrid engine fusing Statistical and ML engines (Final = 0.4*Stat + 0.6*ML)
   with severity mapping and anomaly type classification.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from ml.baseline import BaselineCalculator, get_baseline


class StatisticalEngine:
    r"""Statistical Anomaly Detection Engine based on standardized Z-score deviations.

    The StatisticalEngine computes standardized departures ($Z = \frac{X - \mu}{\sigma}$)
    from historical baseline distributions for individual weather metrics. It maps
    multivariate Z-scores into a calibrated composite anomaly score in $[0.00, 1.00]$
    and classifies severity into four tiers: NORMAL, WATCH, HIGH, CRITICAL.

    Attributes:
        baseline_calculator (Optional[BaselineCalculator]): Baseline calculator
            instance providing location-monthly distributions.
        sigma_min (float): Floor on standard deviation to prevent division by zero.
        weights (Dict[str, float]): Feature importance weights for composite score.
        PHYSICAL_BOUNDS (Dict[str, Tuple[float, float]]): Valid physical domain ranges
            for sensor sanity checks.
    """

    WEATHER_FEATURES: List[str] = [
        "temperature",
        "relative_humidity",
        "pressure",
        "wind_speed",
        "rainfall",
    ]

    # Physical domain bounds for meteorological sanity validation
    PHYSICAL_BOUNDS: Dict[str, Tuple[float, float]] = {
        "temperature": (-50.0, 65.0),
        "relative_humidity": (0.0, 100.0),
        "pressure": (870.0, 1085.0),
        "wind_speed": (0.0, 120.0),
        "rainfall": (0.0, 1500.0),
    }

    # Default weights for composite multi-feature score calculation
    DEFAULT_WEIGHTS: Dict[str, float] = {
        "rainfall": 0.30,
        "temperature": 0.25,
        "pressure": 0.20,
        "wind_speed": 0.15,
        "relative_humidity": 0.10,
    }

    # Severity score thresholds
    SEVERITY_THRESHOLDS = {
        "NORMAL": (0.00, 0.39),
        "WATCH": (0.40, 0.69),
        "HIGH": (0.70, 0.89),
        "CRITICAL": (0.90, 1.00),
    }

    PRIMARY_DEPARTURE_THRESHOLD_Z: float = 2.5  # |Z| >= 2.5 corresponds to p < 0.01 significance

    def __init__(
        self,
        baseline_calculator: Optional[BaselineCalculator] = None,
        sigma_min: float = 0.1,
        weights: Optional[Dict[str, float]] = None,
    ) -> None:
        """Initializes the StatisticalEngine.

        Args:
            baseline_calculator (Optional[BaselineCalculator], optional): Calculator
                instance for baseline lookups.
            sigma_min (float, optional): Minimum standard deviation floor
                (sigma_min = 0.1). Defaults to 0.1.
            weights (Optional[Dict[str, float]], optional): Feature weighting dictionary.
        """
        self.baseline_calculator: Optional[BaselineCalculator] = baseline_calculator
        self.sigma_min: float = max(float(sigma_min), 1e-6)
        self.weights: Dict[str, float] = weights or dict(self.DEFAULT_WEIGHTS)

    def validate_physical_bounds(
        self, obs: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Validates that observation values fall within physically possible bounds.

        Args:
            obs (Dict[str, Any]): Dictionary of weather observations.

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message).
        """
        for feature, (min_val, max_val) in self.PHYSICAL_BOUNDS.items():
            if feature in obs and obs[feature] is not None:
                try:
                    val = float(obs[feature])
                except (ValueError, TypeError):
                    return False, f"Feature '{feature}' value '{obs[feature]}' is not numeric."

                if val < min_val or val > max_val:
                    return (
                        False,
                        f"Sensor error: '{feature}' value {val} is outside physical bounds [{min_val}, {max_val}].",
                    )
        return True, None

    def calculate_z_scores(
        self,
        obs: Dict[str, Any],
        base: Dict[str, Dict[str, float]],
    ) -> Dict[str, float]:
        """Computes standardized Z-scores: Z = (X - mu) / sigma for each feature.

        Args:
            obs (Dict[str, Any]): Observed weather readings.
            base (Dict[str, Dict[str, float]]): Historical baseline statistics.

        Returns:
            Dict[str, float]: Standardized Z-scores per feature.
        """
        if not isinstance(obs, dict):
            raise TypeError(f"Expected obs to be a dict, got {type(obs).__name__}.")
        if not isinstance(base, dict):
            raise TypeError(f"Expected base to be a dict, got {type(base).__name__}.")

        z_scores: Dict[str, float] = {}

        for feature in self.WEATHER_FEATURES:
            if feature in obs and obs[feature] is not None:
                if feature not in base:
                    continue

                feat_base = base[feature]
                if not isinstance(feat_base, dict):
                    continue

                mu = feat_base.get("mean", feat_base.get("mu", 0.0))
                sigma = feat_base.get("std", feat_base.get("sigma", self.sigma_min))

                try:
                    x = float(obs[feature])
                    mu_val = float(mu)
                    sigma_val = max(float(sigma), self.sigma_min)
                except (ValueError, TypeError) as exc:
                    raise ValueError(
                        f"Failed to convert metric for '{feature}' to float: {exc}"
                    ) from exc

                z = (x - mu_val) / sigma_val
                z_scores[feature] = float(z)

        return z_scores

    def compute_statistical_anomaly_score(
        self,
        z_scores: Dict[str, float],
    ) -> float:
        """Computes a calibrated statistical anomaly score in [0.00, 1.00].

        Uses a normalized weighted Euclidean / Mahalanobis-style norm of Z-scores
        combined with the peak absolute Z-score, mapped monotonically onto [0.00, 1.00]
        using a smooth hyperbolic tangent (tanh) activation function:

            D = sqrt( sum(w_i * Z_i^2) / sum(w_i) )
            Z_composite = alpha * D + (1 - alpha) * max(|Z_i|)
            Anomaly Score = tanh( Z_composite / 3.0 )

        Args:
            z_scores (Dict[str, float]): Standardized Z-scores per weather feature.

        Returns:
            float: Calibrated anomaly score in [0.00, 1.00], rounded to 4 decimals.
        """
        if not z_scores:
            return 0.0

        weighted_sq_sum = 0.0
        total_weight = 0.0
        max_abs_z = 0.0

        for feat, z in z_scores.items():
            abs_z = abs(float(z))
            w = self.weights.get(feat, 0.20)
            weighted_sq_sum += w * (abs_z**2)
            total_weight += w
            if abs_z > max_abs_z:
                max_abs_z = abs_z

        norm_z = math.sqrt(weighted_sq_sum / total_weight) if total_weight > 0 else 0.0
        combined_z = 0.65 * norm_z + 0.35 * max_abs_z
        score = math.tanh(combined_z / 3.0)

        return round(float(min(max(score, 0.0), 1.0)), 4)

    def calculate_composite_score(
        self,
        z_scores: Dict[str, float],
    ) -> float:
        """Alias for compute_statistical_anomaly_score."""
        return self.compute_statistical_anomaly_score(z_scores)

    def get_severity(self, anomaly_score: float) -> str:
        """Classifies calibrated anomaly score into a 4-tier severity label."""
        if anomaly_score >= 0.90:
            return "CRITICAL"
        if anomaly_score >= 0.70:
            return "HIGH"
        if anomaly_score >= 0.40:
            return "WATCH"
        return "NORMAL"

    def get_departure_flags(
        self,
        z_scores: Dict[str, float],
        threshold: float = 2.5,
    ) -> Dict[str, Dict[str, Any]]:
        """Flags each weather variable as a primary departure if |Z| >= threshold."""
        flags: Dict[str, Dict[str, Any]] = {}

        for feature, z in z_scores.items():
            z_val = float(z)
            abs_z = abs(z_val)
            is_primary = abs_z >= threshold

            if abs_z >= 2.576:
                significance = "p < 0.01"
            elif abs_z >= 1.96:
                significance = "p < 0.05"
            else:
                significance = "normal"

            flags[feature] = {
                "z_score": round(z_val, 4),
                "abs_z": round(abs_z, 4),
                "is_primary_departure": is_primary,
                "direction": "HIGH" if z_val >= 0.0 else "LOW",
                "significance": significance,
            }

        return flags

    def get_primary_departures(
        self,
        z_scores: Dict[str, float],
        threshold: float = 2.5,
    ) -> List[Dict[str, Any]]:
        """Returns ranked list of features with significant primary departures (|Z| >= threshold)."""
        flags = self.get_departure_flags(z_scores, threshold=threshold)
        primary = [
            {"feature": feat, **data}
            for feat, data in flags.items()
            if data["is_primary_departure"]
        ]
        primary.sort(key=lambda item: item["abs_z"], reverse=True)
        return primary

    def evaluate(
        self,
        observation: Dict[str, Any],
        location: str,
        month: int,
    ) -> Dict[str, Any]:
        """Evaluates a weather observation against baseline for location and month."""
        is_valid, err_msg = self.validate_physical_bounds(observation)
        if not is_valid:
            raise ValueError(err_msg)

        if self.baseline_calculator is not None:
            baseline = self.baseline_calculator.get_baseline(location, month)
        else:
            baseline = get_baseline(location, month)

        z_scores = self.calculate_z_scores(observation, baseline)
        anomaly_score = self.compute_statistical_anomaly_score(z_scores)
        severity = self.get_severity(anomaly_score)
        is_anomaly = anomaly_score >= 0.40

        departure_flags = self.get_departure_flags(
            z_scores, threshold=self.PRIMARY_DEPARTURE_THRESHOLD_Z
        )
        primary_departures = self.get_primary_departures(
            z_scores, threshold=self.PRIMARY_DEPARTURE_THRESHOLD_Z
        )

        return {
            "location": location,
            "month": month,
            "is_anomaly": is_anomaly,
            "anomaly_score": anomaly_score,
            "severity": severity,
            "z_scores": z_scores,
            "departure_flags": departure_flags,
            "primary_departures": primary_departures,
            "has_primary_departure": len(primary_departures) > 0,
            "baseline": baseline,
        }


class MLAnomalyEngine:
    """Machine Learning Anomaly Detection Engine using Scikit-learn's Isolation Forest.

    Trains and predicts multi-dimensional weather anomalies on scaled feature vectors
    combining raw metrics, seasonal Z-score deviations, cyclical temporal encodings,
    and rolling meteorological indicators.

    Attributes:
        model (IsolationForest): Scikit-learn Isolation Forest model.
        scaler (StandardScaler): Feature standardizer.
        is_fitted (bool): Whether the model and scaler have been fitted.
        baseline_calculator (Optional[BaselineCalculator]): Baseline provider.
    """

    FEATURE_NAMES: List[str] = [
        "temperature",
        "relative_humidity",
        "pressure",
        "wind_speed",
        "rainfall",
        "z_temperature",
        "z_relative_humidity",
        "z_pressure",
        "z_wind_speed",
        "z_rainfall",
        "sin_month",
        "cos_month",
        "temp_humidity_index",
    ]

    def __init__(
        self,
        n_estimators: int = 150,
        contamination: float = 0.03,
        random_state: int = 42,
        n_jobs: int = -1,
        baseline_calculator: Optional[BaselineCalculator] = None,
    ) -> None:
        """Initializes MLAnomalyEngine with IsolationForest parameters.

        Args:
            n_estimators (int, optional): Number of base estimators. Defaults to 150.
            contamination (float, optional): Proportion of expected outliers. Defaults to 0.03.
            random_state (int, optional): Fixed random seed for reproducibility. Defaults to 42.
            n_jobs (int, optional): Parallel processing cores (-1 for all). Defaults to -1.
            baseline_calculator (Optional[BaselineCalculator], optional): Baseline calculator.
        """
        self.n_estimators: int = n_estimators
        self.contamination: float = contamination
        self.random_state: int = random_state
        self.n_jobs: int = n_jobs
        self.baseline_calculator: Optional[BaselineCalculator] = baseline_calculator

        self.model: IsolationForest = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=self.n_jobs,
        )
        self.scaler: StandardScaler = StandardScaler()
        self.is_fitted: bool = False

    def _get_baseline_for(
        self, location: str, month: int
    ) -> Dict[str, Dict[str, float]]:
        """Internal helper to retrieve baseline statistics for a location/month."""
        if self.baseline_calculator is not None:
            return self.baseline_calculator.get_baseline(location, month)
        return get_baseline(location, month)

    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Constructs standardized feature vectors for training or batch inference.

        Combines:
        1. Raw weather metrics (5 features)
        2. Seasonal baseline Z-deviations (5 features)
        3. Cyclical temporal sin/cos encodings of month (2 features)
        4. Meteorological interaction index (e.g. Temperature-Humidity heat proxy) (1 feature)

        Args:
            df (pd.DataFrame): Input DataFrame containing observations.

        Returns:
            np.ndarray: 2D feature matrix X of shape (n_samples, 13).
        """
        rows: List[List[float]] = []

        for _, row in df.iterrows():
            loc = str(row.get("location", "Bengaluru"))
            month = int(row.get("month", 1))

            temp = float(row.get("temperature", 25.0))
            rh = float(row.get("relative_humidity", 60.0))
            press = float(row.get("pressure", 1010.0))
            wind = float(row.get("wind_speed", 3.0))
            rain = float(row.get("rainfall", 0.0))

            try:
                base = self._get_baseline_for(loc, month)
            except Exception:
                # Default baseline fallback if location/month missing
                base = {
                    "temperature": {"mean": 25.0, "std": 2.0},
                    "relative_humidity": {"mean": 65.0, "std": 8.0},
                    "pressure": {"mean": 1010.0, "std": 2.5},
                    "wind_speed": {"mean": 3.0, "std": 1.0},
                    "rainfall": {"mean": 10.0, "std": 10.0},
                }

            # Baseline Z-deviations
            z_temp = (temp - base["temperature"]["mean"]) / max(base["temperature"]["std"], 0.1)
            z_rh = (rh - base["relative_humidity"]["mean"]) / max(base["relative_humidity"]["std"], 0.1)
            z_press = (press - base["pressure"]["mean"]) / max(base["pressure"]["std"], 0.1)
            z_wind = (wind - base["wind_speed"]["mean"]) / max(base["wind_speed"]["std"], 0.1)
            z_rain = (rain - base["rainfall"]["mean"]) / max(base["rainfall"]["std"], 0.1)

            # Cyclical month features
            month_angle = 2.0 * math.pi * (month / 12.0)
            sin_month = math.sin(month_angle)
            cos_month = math.cos(month_angle)

            # Temperature-humidity interaction index (simplified discomfort / heat index proxy)
            thi = temp - ((0.55 - 0.0055 * rh) * (temp - 14.5))

            feature_vec = [
                temp,
                rh,
                press,
                wind,
                rain,
                z_temp,
                z_rh,
                z_press,
                z_wind,
                z_rain,
                sin_month,
                cos_month,
                thi,
            ]
            rows.append(feature_vec)

        return np.array(rows, dtype=np.float64)

    def prepare_single_observation(
        self,
        observation: Dict[str, Any],
        location: str,
        month: int,
        base: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> np.ndarray:
        """Constructs a 1x13 feature vector for single live observation scoring."""
        temp = float(observation.get("temperature", 25.0))
        rh = float(observation.get("relative_humidity", 60.0))
        press = float(observation.get("pressure", 1010.0))
        wind = float(observation.get("wind_speed", 3.0))
        rain = float(observation.get("rainfall", 0.0))

        if base is None:
            try:
                base = self._get_baseline_for(location, month)
            except Exception:
                base = {
                    "temperature": {"mean": 25.0, "std": 2.0},
                    "relative_humidity": {"mean": 65.0, "std": 8.0},
                    "pressure": {"mean": 1010.0, "std": 2.5},
                    "wind_speed": {"mean": 3.0, "std": 1.0},
                    "rainfall": {"mean": 10.0, "std": 10.0},
                }

        z_temp = (temp - base["temperature"]["mean"]) / max(base["temperature"]["std"], 0.1)
        z_rh = (rh - base["relative_humidity"]["mean"]) / max(base["relative_humidity"]["std"], 0.1)
        z_press = (press - base["pressure"]["mean"]) / max(base["pressure"]["std"], 0.1)
        z_wind = (wind - base["wind_speed"]["mean"]) / max(base["wind_speed"]["std"], 0.1)
        z_rain = (rain - base["rainfall"]["mean"]) / max(base["rainfall"]["std"], 0.1)

        month_angle = 2.0 * math.pi * (month / 12.0)
        sin_month = math.sin(month_angle)
        cos_month = math.cos(month_angle)
        thi = temp - ((0.55 - 0.0055 * rh) * (temp - 14.5))

        vec = np.array(
            [[
                temp,
                rh,
                press,
                wind,
                rain,
                z_temp,
                z_rh,
                z_press,
                z_wind,
                z_rain,
                sin_month,
                cos_month,
                thi,
            ]],
            dtype=np.float64,
        )
        return vec

    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> MLAnomalyEngine:
        """Fits StandardScaler and IsolationForest with fixed random seed.

        Args:
            X (Union[np.ndarray, pd.DataFrame]): Training feature array or DataFrame.

        Returns:
            MLAnomalyEngine: Fitted instance.
        """
        if isinstance(X, pd.DataFrame):
            X_mat = self.prepare_features(X)
        else:
            X_mat = np.asarray(X, dtype=np.float64)

        if X_mat.ndim == 1:
            X_mat = X_mat.reshape(1, -1)

        # 100% reproducible fitting
        np.random.seed(self.random_state)
        X_scaled = self.scaler.fit_transform(X_mat)
        self.model.fit(X_scaled)
        self.is_fitted = True
        return self

    def predict_raw_score(self, X: np.ndarray) -> Union[float, np.ndarray]:
        """Predicts calibrated anomaly score [0.00, 1.00] from decision_function.

        In Scikit-learn Isolation Forest:
        - decision_function(X) returns > 0 for typical inliers (~ +0.15 to +0.25).
        - decision_function(X) returns < 0 for outliers / anomalies (~ -0.15 to -0.35).

        We map negative decision values into a continuous calibrated score [0.00, 1.00]
        where higher values indicate stronger anomalies using smooth logistic sigmoid:
            score = 1.0 / (1.0 + exp( k * (decision - offset) ))

        Args:
            X (np.ndarray): 1D or 2D feature vector(s).

        Returns:
            Union[float, np.ndarray]: Calibrated anomaly score(s) in [0.00, 1.00].
        """
        if not self.is_fitted:
            raise RuntimeError(
                "MLAnomalyEngine model has not been fitted or loaded. Call fit() or load() first."
            )

        X_arr = np.asarray(X, dtype=np.float64)
        is_single = False
        if X_arr.ndim == 1:
            X_arr = X_arr.reshape(1, -1)
            is_single = True
        elif X_arr.shape[0] == 1:
            is_single = True

        X_scaled = self.scaler.transform(X_arr)
        decision = self.model.decision_function(X_scaled)

        # Calibration: map decision function (~ +0.15 normal -> ~0.15-0.25, ~0.00 boundary -> ~0.55, ~ -0.18 extreme -> ~0.95+)
        # score = 1 / (1 + exp(15.0 * (decision - 0.02)))
        scores = 1.0 / (1.0 + np.exp(15.0 * (decision - 0.02)))
        scores = np.clip(scores, 0.0, 1.0)

        if is_single:
            return round(float(scores[0]), 4)
        return np.round(scores, 4)

    def save(
        self,
        model_path: Union[str, Path] = "ml/models/isolation_forest.joblib",
        scaler_path: Union[str, Path] = "ml/models/scaler.joblib",
    ) -> None:
        """Saves fitted Isolation Forest and StandardScaler to disk."""
        m_path = Path(model_path)
        s_path = Path(scaler_path)
        m_path.parent.mkdir(parents=True, exist_ok=True)
        s_path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.model, m_path)
        joblib.dump(self.scaler, s_path)

    @classmethod
    def load(
        cls,
        model_path: Union[str, Path] = "ml/models/isolation_forest.joblib",
        scaler_path: Union[str, Path] = "ml/models/scaler.joblib",
        baseline_calculator: Optional[BaselineCalculator] = None,
    ) -> MLAnomalyEngine:
        """Loads fitted Isolation Forest and StandardScaler from disk."""
        m_path = Path(model_path)
        s_path = Path(scaler_path)

        if not m_path.exists():
            raise FileNotFoundError(f"Isolation Forest model file not found at: {m_path}")
        if not s_path.exists():
            raise FileNotFoundError(f"Scaler file not found at: {s_path}")

        instance = cls(baseline_calculator=baseline_calculator)
        instance.model = joblib.load(m_path)
        instance.scaler = joblib.load(s_path)
        instance.is_fitted = True
        return instance


class DualAnomalyEngine:
    """Dual-Engine Weather Anomaly Detector fusing Statistical and ML layers.

    Fuses:
        FinalScore = 0.4 * StatScore + 0.6 * MLScore
    Strictly bounded in [0.00, 1.00] with 4 severity levels and anomaly type classification.
    """

    def __init__(
        self,
        stat_engine: Optional[StatisticalEngine] = None,
        ml_engine: Optional[MLAnomalyEngine] = None,
        stat_weight: float = 0.4,
        ml_weight: float = 0.6,
    ) -> None:
        """Initializes DualAnomalyEngine.

        Args:
            stat_engine (Optional[StatisticalEngine], optional): Statistical engine.
            ml_engine (Optional[MLAnomalyEngine], optional): ML anomaly engine.
            stat_weight (float, optional): Weight for statistical score. Defaults to 0.4.
            ml_weight (float, optional): Weight for ML score. Defaults to 0.6.
        """
        self.stat_engine: StatisticalEngine = stat_engine or StatisticalEngine()
        self.ml_engine: Optional[MLAnomalyEngine] = ml_engine
        self.stat_weight: float = stat_weight
        self.ml_weight: float = ml_weight

    def classify_severity(self, score: float) -> str:
        """Maps anomaly score to standardized 4-tier severity levels.

        - 0.00 - 0.39: NORMAL (Emerald Green)
        - 0.40 - 0.69: WATCH (Amber Yellow)
        - 0.70 - 0.89: HIGH (Orange)
        - 0.90 - 1.00: CRITICAL (Crimson Red)

        Args:
            score (float): Anomaly score in [0.00, 1.00].

        Returns:
            str: One of 'NORMAL', 'WATCH', 'HIGH', 'CRITICAL'.
        """
        clamped = min(max(float(score), 0.0), 1.0)
        if clamped >= 0.90:
            return "CRITICAL"
        if clamped >= 0.70:
            return "HIGH"
        if clamped >= 0.40:
            return "WATCH"
        return "NORMAL"

    def classify_anomaly_type(
        self,
        obs: Dict[str, Any],
        base: Dict[str, Dict[str, float]],
        z_scores: Dict[str, float],
    ) -> str:
        """Classifies weather anomaly into specific meteorological event types.

        Identifies:
        - Extreme Rainfall
        - Heat Wave
        - Cold Wave
        - Deep Depression
        - Severe Drought
        - Compound Weather Anomaly
        - Normal Seasonal Variation

        Args:
            obs (Dict[str, Any]): Observed weather readings.
            base (Dict[str, Dict[str, float]]): Baseline stats.
            z_scores (Dict[str, float]): Computed Z-scores per feature.

        Returns:
            str: Descriptive anomaly type name.
        """
        z_temp = z_scores.get("temperature", 0.0)
        z_rain = z_scores.get("rainfall", 0.0)
        z_press = z_scores.get("pressure", 0.0)
        z_wind = z_scores.get("wind_speed", 0.0)
        z_rh = z_scores.get("relative_humidity", 0.0)

        obs_temp = float(obs.get("temperature", 25.0))
        obs_rain = float(obs.get("rainfall", 0.0))

        # 1. Extreme Rainfall
        if z_rain >= 2.5 or obs_rain >= 100.0:
            return "Extreme Rainfall"

        # 2. Heat Wave
        if z_temp >= 2.5 or (z_temp >= 1.8 and obs_temp >= 38.0):
            return "Heat Wave"

        # 3. Cold Wave
        if z_temp <= -2.5 or (z_temp <= -1.8 and obs_temp <= 10.0):
            return "Cold Wave"

        # 4. Deep Depression (Steep pressure drop + high wind or rain)
        if z_press <= -2.2 and (z_wind >= 1.5 or z_rain >= 1.5 or z_press <= -3.0):
            return "Deep Depression"

        # 5. Severe Drought
        if z_rain <= -1.5 and z_temp >= 1.5 and z_rh <= -1.5:
            return "Severe Drought"

        # 6. Compound Weather Anomaly (Multiple simultaneous moderate deviations)
        high_dev_count = sum(1 for z in z_scores.values() if abs(z) >= 1.8)
        if high_dev_count >= 2:
            return "Compound Weather Anomaly"

        # Single moderate deviation check
        if any(abs(z) >= 1.8 for z in z_scores.values()):
            return "Compound Weather Anomaly"

        return "Normal Seasonal Variation"

    def predict(
        self,
        observation: Dict[str, Any],
        location: str,
        month: int,
    ) -> Dict[str, Any]:
        """Evaluates observation using dual-engine fusion.

        Formula:
            FinalScore = 0.4 * StatScore + 0.6 * MLScore
        Strictly bounded in [0.00, 1.00].

        Args:
            observation (Dict[str, Any]): Weather observation readings.
            location (str): Location name.
            month (int): Month of year (1-12).

        Returns:
            Dict[str, Any]: Full prediction result payload.
        """
        # Statistical Layer
        stat_result = self.stat_engine.evaluate(observation, location, month)
        stat_score = stat_result["anomaly_score"]
        z_scores = stat_result["z_scores"]
        baseline = stat_result["baseline"]

        # ML Layer (Isolation Forest)
        if self.ml_engine is not None and self.ml_engine.is_fitted:
            feat_vec = self.ml_engine.prepare_single_observation(
                observation, location, month, base=baseline
            )
            ml_score = float(self.ml_engine.predict_raw_score(feat_vec))
            # Dual engine weighted blend
            final_score = self.stat_weight * stat_score + self.ml_weight * ml_score
        else:
            ml_score = stat_score
            final_score = stat_score

        # Bound strictly in [0.00, 1.00]
        final_score = round(float(min(max(final_score, 0.0), 1.0)), 4)
        ml_score = round(float(min(max(ml_score, 0.0), 1.0)), 4)

        severity = self.classify_severity(final_score)
        is_anomaly = final_score >= 0.40
        anomaly_type = self.classify_anomaly_type(observation, baseline, z_scores)

        return {
            "location": location,
            "month": month,
            "is_anomaly": is_anomaly,
            "final_score": final_score,
            "statistical_score": stat_score,
            "ml_score": ml_score,
            "severity": severity,
            "anomaly_type": anomaly_type,
            "z_scores": z_scores,
            "departure_flags": stat_result["departure_flags"],
            "primary_departures": stat_result["primary_departures"],
            "has_primary_departure": stat_result["has_primary_departure"],
            "baseline": baseline,
        }

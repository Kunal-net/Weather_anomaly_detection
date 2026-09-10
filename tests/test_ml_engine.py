"""Unit tests for MLAnomalyEngine and DualAnomalyEngine in ml/anomaly_engine.py."""

import numpy as np
import pandas as pd
import pytest

from ml.anomaly_engine import DualAnomalyEngine, MLAnomalyEngine, StatisticalEngine
from ml.baseline import BaselineCalculator


@pytest.fixture
def clean_sample_df() -> pd.DataFrame:
    """Fixture with multi-sample observations."""
    np.random.seed(42)
    rows = []
    for m in range(1, 13):
        for _ in range(30):
            rows.append({
                "location": "Bengaluru",
                "month": m,
                "temperature": float(np.random.normal(25.0, 2.0)),
                "relative_humidity": float(np.random.normal(70.0, 5.0)),
                "pressure": float(np.random.normal(1010.0, 2.0)),
                "wind_speed": float(np.random.normal(3.5, 1.0)),
                "rainfall": float(np.random.exponential(5.0)),
            })
    return pd.DataFrame(rows)


def test_ml_anomaly_engine_init_and_features(clean_sample_df: pd.DataFrame) -> None:
    """Test MLAnomalyEngine initialization and prepare_features (Prompts 1.9, 1.10)."""
    calc = BaselineCalculator(clean_sample_df)
    ml_engine = MLAnomalyEngine(
        n_estimators=150,
        contamination=0.03,
        random_state=42,
        n_jobs=-1,
        baseline_calculator=calc,
    )

    X = ml_engine.prepare_features(clean_sample_df)
    assert isinstance(X, np.ndarray)
    assert X.shape[0] == len(clean_sample_df)
    assert X.shape[1] == 13  # 5 raw + 5 z + 2 cyclical + 1 interaction


def test_ml_anomaly_engine_fit_and_predict(clean_sample_df: pd.DataFrame) -> None:
    """Test MLAnomalyEngine fit and predict_raw_score (Prompts 1.11, 1.12)."""
    calc = BaselineCalculator(clean_sample_df)
    ml_engine = MLAnomalyEngine(baseline_calculator=calc)

    assert not ml_engine.is_fitted
    ml_engine.fit(clean_sample_df)
    assert ml_engine.is_fitted

    # Test normal sample prediction
    normal_obs = {
        "temperature": 25.0,
        "relative_humidity": 70.0,
        "pressure": 1010.0,
        "wind_speed": 3.5,
        "rainfall": 5.0,
    }
    vec_normal = ml_engine.prepare_single_observation(normal_obs, "Bengaluru", 9)
    score_normal = ml_engine.predict_raw_score(vec_normal)
    assert isinstance(score_normal, float)
    assert 0.0 <= score_normal < 0.40

    # Test extreme anomaly prediction
    extreme_obs = {
        "temperature": 45.0,
        "relative_humidity": 95.0,
        "pressure": 970.0,
        "wind_speed": 35.0,
        "rainfall": 300.0,
    }
    vec_extreme = ml_engine.prepare_single_observation(extreme_obs, "Bengaluru", 9)
    score_extreme = ml_engine.predict_raw_score(vec_extreme)
    assert 0.85 <= score_extreme <= 1.00


def test_dual_anomaly_engine_fusion(clean_sample_df: pd.DataFrame) -> None:
    """Test DualAnomalyEngine fusion: FinalScore = 0.4 * Stat + 0.6 * ML (Prompt 1.13)."""
    calc = BaselineCalculator(clean_sample_df)
    stat_engine = StatisticalEngine(baseline_calculator=calc)
    ml_engine = MLAnomalyEngine(baseline_calculator=calc).fit(clean_sample_df)

    dual = DualAnomalyEngine(stat_engine=stat_engine, ml_engine=ml_engine, stat_weight=0.4, ml_weight=0.6)

    obs = {
        "temperature": 25.0,
        "relative_humidity": 70.0,
        "pressure": 1010.0,
        "wind_speed": 3.5,
        "rainfall": 5.0,
    }
    pred = dual.predict(obs, "Bengaluru", 9)

    expected_final = round(0.4 * pred["statistical_score"] + 0.6 * pred["ml_score"], 4)
    assert pred["final_score"] == pytest.approx(expected_final, abs=1e-3)
    assert 0.0 <= pred["final_score"] <= 1.0


def test_dual_anomaly_engine_severity_mapping() -> None:
    """Test DualAnomalyEngine severity mapping (Prompt 1.14)."""
    dual = DualAnomalyEngine()

    assert dual.classify_severity(0.15) == "NORMAL"
    assert dual.classify_severity(0.39) == "NORMAL"
    assert dual.classify_severity(0.40) == "WATCH"
    assert dual.classify_severity(0.69) == "WATCH"
    assert dual.classify_severity(0.70) == "HIGH"
    assert dual.classify_severity(0.89) == "HIGH"
    assert dual.classify_severity(0.90) == "CRITICAL"
    assert dual.classify_severity(1.00) == "CRITICAL"


def test_dual_anomaly_engine_anomaly_type_classification() -> None:
    """Test DualAnomalyEngine anomaly type classification (Prompt 1.15)."""
    dual = DualAnomalyEngine()
    base = {"temperature": {"mean": 25.0, "std": 2.0}}

    # Extreme rainfall
    type_rain = dual.classify_anomaly_type(
        {"rainfall": 150.0}, base, {"rainfall": 8.0, "temperature": 0.5}
    )
    assert type_rain == "Extreme Rainfall"

    # Heat wave
    type_heat = dual.classify_anomaly_type(
        {"temperature": 42.0}, base, {"temperature": 3.5, "rainfall": 0.0}
    )
    assert type_heat == "Heat Wave"

    # Cold wave
    type_cold = dual.classify_anomaly_type(
        {"temperature": 5.0}, base, {"temperature": -3.5, "rainfall": 0.0}
    )
    assert type_cold == "Cold Wave"

    # Deep depression
    type_dep = dual.classify_anomaly_type(
        {"pressure": 980.0, "wind_speed": 20.0}, base, {"pressure": -3.5, "wind_speed": 2.5}
    )
    assert type_dep == "Deep Depression"

    # Compound anomaly
    type_compound = dual.classify_anomaly_type(
        {"temperature": 30.0, "pressure": 1000.0}, base, {"temperature": 2.0, "pressure": -2.1}
    )
    assert type_compound == "Compound Weather Anomaly"

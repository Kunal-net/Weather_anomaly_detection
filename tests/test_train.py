"""Unit tests for ml/train.py training pipeline and self-validation."""

from pathlib import Path

import pytest

from ml.anomaly_engine import DualAnomalyEngine, MLAnomalyEngine, StatisticalEngine
from ml.baseline import BaselineCalculator
from ml.train import run_self_validation


def test_train_self_validation_suite() -> None:
    """Test train pipeline self-validation with saved models (Prompt 1.20)."""
    model_path = Path("ml/models/isolation_forest.joblib")
    scaler_path = Path("ml/models/scaler.joblib")
    baseline_path = Path("data/processed/baseline_statistics.json")

    assert model_path.exists(), "Model file should exist after training"
    assert scaler_path.exists(), "Scaler file should exist after training"
    assert baseline_path.exists(), "Baseline file should exist after training"

    calc = BaselineCalculator.load_from_json(baseline_path)
    ml_engine = MLAnomalyEngine.load(model_path, scaler_path, baseline_calculator=calc)
    stat_engine = StatisticalEngine(baseline_calculator=calc)
    dual_engine = DualAnomalyEngine(stat_engine=stat_engine, ml_engine=ml_engine)

    report = run_self_validation(dual_engine)

    assert report["validation_passed"] is True
    assert report["normal_score"] < 0.40
    assert report["normal_severity"] == "NORMAL"
    assert report["cloudburst_score"] > 0.90
    assert report["cloudburst_severity"] == "CRITICAL"
    assert report["avg_latency_ms"] < 15.0

"""Unit tests for ml/anomaly_engine.py."""

import pytest

from ml.anomaly_engine import StatisticalEngine
from ml.baseline import BaselineCalculator


@pytest.fixture
def sample_baseline_dict() -> dict:
    """Sample baseline parameters fixture."""
    return {
        "temperature": {"mean": 27.1, "std": 1.8},
        "rainfall": {"mean": 18.2, "std": 14.5},
        "pressure": {"mean": 1008.0, "std": 2.1},
        "wind_speed": {"mean": 3.5, "std": 1.2},
        "relative_humidity": {"mean": 74.0, "std": 8.2},
    }


def test_calculate_z_scores_basic(sample_baseline_dict: dict) -> None:
    """Test basic Z-score calculation: Z = (X - mu) / sigma."""
    engine = StatisticalEngine()
    obs = {
        "temperature": 37.0,  # (37.0 - 27.1) / 1.8 = 5.5
        "rainfall": 145.0,    # (145.0 - 18.2) / 14.5 = 8.7448
        "pressure": 994.0,    # (994.0 - 1008.0) / 2.1 = -6.6667
    }
    z_scores = engine.calculate_z_scores(obs, sample_baseline_dict)

    assert z_scores["temperature"] == pytest.approx(5.5, rel=1e-3)
    assert z_scores["rainfall"] == pytest.approx(8.7448, rel=1e-3)
    assert z_scores["pressure"] == pytest.approx(-6.6667, rel=1e-3)


def test_calculate_z_scores_zero_variance() -> None:
    """Test Z-score calculation when baseline standard deviation is zero or floored."""
    engine = StatisticalEngine(sigma_min=0.1)
    base = {
        "temperature": {"mean": 25.0, "std": 0.0},
    }
    obs = {"temperature": 27.0}
    z_scores = engine.calculate_z_scores(obs, base)

    # (27.0 - 25.0) / 0.1 = 20.0
    assert z_scores["temperature"] == pytest.approx(20.0)


def test_calculate_z_scores_type_error() -> None:
    """Test TypeError on non-dict inputs."""
    engine = StatisticalEngine()
    with pytest.raises(TypeError, match="Expected obs to be a dict"):
        engine.calculate_z_scores([1, 2, 3], {})  # type: ignore

    with pytest.raises(TypeError, match="Expected base to be a dict"):
        engine.calculate_z_scores({}, [1, 2, 3])  # type: ignore


def test_physical_bounds_validation() -> None:
    """Test sensor sanity checks for out-of-bounds readings."""
    engine = StatisticalEngine()

    # Valid observation
    valid, msg = engine.validate_physical_bounds({"temperature": 30.0, "relative_humidity": 80.0})
    assert valid is True
    assert msg is None

    # Invalid temperature
    valid, msg = engine.validate_physical_bounds({"temperature": 150.0})
    assert valid is False
    assert "outside physical bounds" in str(msg)

    # Invalid humidity
    valid, msg = engine.validate_physical_bounds({"relative_humidity": 120.0})
    assert valid is False
    assert "relative_humidity" in str(msg)


def test_compute_statistical_anomaly_score() -> None:
    """Test normalized Euclidean norm and tanh mapping to [0.00, 1.00]."""
    engine = StatisticalEngine()

    # Empty Z-scores
    assert engine.compute_statistical_anomaly_score({}) == 0.0

    # Zero deviations -> 0.0 (NORMAL)
    zero_z = {"temperature": 0.0, "rainfall": 0.0, "pressure": 0.0}
    assert engine.compute_statistical_anomaly_score(zero_z) == 0.0

    # Mild single variable deviation -> NORMAL (< 0.40)
    mild_z = {"temperature": 1.0, "relative_humidity": 0.5}
    score_mild = engine.compute_statistical_anomaly_score(mild_z)
    assert 0.0 < score_mild < 0.40
    assert engine.get_severity(score_mild) == "NORMAL"

    # Moderate compound deviation -> WATCH (0.40 - 0.69)
    mod_z = {"temperature": 2.0, "rainfall": 2.0, "pressure": -1.8}
    score_mod = engine.compute_statistical_anomaly_score(mod_z)
    assert 0.40 <= score_mod < 0.70
    assert engine.get_severity(score_mod) == "WATCH"

    # High compound deviation -> HIGH (0.70 - 0.89)
    high_z = {"temperature": 3.2, "rainfall": 3.5, "pressure": -2.8}
    score_high = engine.compute_statistical_anomaly_score(high_z)
    assert 0.70 <= score_high < 0.90
    assert engine.get_severity(score_high) == "HIGH"

    # Extreme shock / cloudburst -> CRITICAL (>= 0.90)
    crit_z = {"rainfall": 8.74, "temperature": 5.5, "pressure": -6.67}
    score_crit = engine.compute_statistical_anomaly_score(crit_z)
    assert score_crit >= 0.90
    assert engine.get_severity(score_crit) == "CRITICAL"


def test_severity_classification() -> None:
    """Test mapping score to 4 severity tiers."""
    engine = StatisticalEngine()

    assert engine.get_severity(0.20) == "NORMAL"
    assert engine.get_severity(0.45) == "WATCH"
    assert engine.get_severity(0.75) == "HIGH"
    assert engine.get_severity(0.95) == "CRITICAL"


def test_departure_flags_significance() -> None:
    """Test individual variable departure flags for |Z| >= 2.5 (p < 0.01)."""
    engine = StatisticalEngine()
    z_scores = {
        "rainfall": 8.74,     # |Z| >= 2.5 -> Primary departure (HIGH)
        "pressure": -3.20,    # |Z| >= 2.5 -> Primary departure (LOW)
        "temperature": 1.20,  # |Z| < 2.5  -> Not a primary departure
        "wind_speed": -0.50,  # |Z| < 2.5  -> Not a primary departure
    }

    flags = engine.get_departure_flags(z_scores, threshold=2.5)

    assert flags["rainfall"]["is_primary_departure"] is True
    assert flags["rainfall"]["direction"] == "HIGH"
    assert flags["rainfall"]["significance"] == "p < 0.01"

    assert flags["pressure"]["is_primary_departure"] is True
    assert flags["pressure"]["direction"] == "LOW"
    assert flags["pressure"]["significance"] == "p < 0.01"

    assert flags["temperature"]["is_primary_departure"] is False
    assert flags["wind_speed"]["is_primary_departure"] is False

    primary = engine.get_primary_departures(z_scores, threshold=2.5)
    assert len(primary) == 2
    # Should be ranked by absolute Z descending: rainfall (8.74) then pressure (3.20)
    assert primary[0]["feature"] == "rainfall"
    assert primary[1]["feature"] == "pressure"


def test_evaluate_observation(sample_baseline_dict: dict) -> None:
    """Test full observation evaluation."""
    engine = StatisticalEngine()
    obs = {
        "temperature": 37.0,
        "rainfall": 145.0,
        "pressure": 994.0,
        "wind_speed": 14.5,
        "relative_humidity": 92.0,
    }
    result = engine.evaluate(obs, "Bengaluru", 9)

    assert result["location"] == "Bengaluru"
    assert result["month"] == 9
    assert result["is_anomaly"] is True
    assert result["anomaly_score"] >= 0.90
    assert result["severity"] == "CRITICAL"
    assert "temperature" in result["z_scores"]
    assert "rainfall" in result["z_scores"]
    assert result["has_primary_departure"] is True
    assert len(result["primary_departures"]) > 0
    assert result["departure_flags"]["rainfall"]["is_primary_departure"] is True


"""Unit tests for ml/explainability.py."""

import pytest

from ml.explainability import ExplainabilityEngine


def test_compute_feature_contributions_ranking() -> None:
    """Test feature contribution percentages and descending ranking (Prompt 1.16)."""
    engine = ExplainabilityEngine()
    z_scores = {
        "rainfall": 8.0,
        "temperature": 2.0,
        "pressure": -4.0,
        "wind_speed": 1.0,
        "relative_humidity": 1.0,
    }
    # Total |Z| = 8 + 2 + 4 + 1 + 1 = 16.0
    # rainfall: (8 / 16) * 100 = 50.0%
    # pressure: (4 / 16) * 100 = 25.0%
    # temperature: (2 / 16) * 100 = 12.5%
    # wind_speed: (1 / 16) * 100 = 6.25% (6.2% or 6.3%)
    # relative_humidity: (1 / 16) * 100 = 6.25%
    contributors = engine.compute_feature_contributions(z_scores)

    assert len(contributors) == 5
    assert contributors[0]["feature"] == "rainfall"
    assert contributors[0]["contribution_pct"] == pytest.approx(50.0, rel=1e-2)

    assert contributors[1]["feature"] == "pressure"
    assert contributors[1]["contribution_pct"] == pytest.approx(25.0, rel=1e-2)

    assert contributors[2]["feature"] == "temperature"
    assert contributors[2]["contribution_pct"] == pytest.approx(12.5, rel=1e-2)

    # Check strictly ranked in descending order
    for i in range(len(contributors) - 1):
        assert contributors[i]["contribution_pct"] >= contributors[i + 1]["contribution_pct"]


def test_contributor_formatting_fields() -> None:
    """Test contributor fields: feature, contribution_pct, observed, expected, unit, direction (Prompt 1.17)."""
    engine = ExplainabilityEngine()
    obs = {"temperature": 37.0, "rainfall": 145.0, "pressure": 994.0}
    base = {
        "temperature": {"mean": 27.1, "std": 1.8},
        "rainfall": {"mean": 18.2, "std": 14.5},
        "pressure": {"mean": 1008.0, "std": 2.1},
    }
    z_scores = {
        "rainfall": 8.74,
        "temperature": 5.50,
        "pressure": -6.67,
    }
    contributors = engine.compute_feature_contributions(z_scores, obs=obs, base=base)

    rain_c = next(c for c in contributors if c["feature"] == "rainfall")
    assert rain_c["feature"] == "rainfall"
    assert rain_c["observed"] == 145.0
    assert rain_c["expected"] == 18.2
    assert rain_c["unit"] == "mm"
    assert rain_c["direction"] == "HIGH"
    assert rain_c["departure"] == pytest.approx(126.8, rel=1e-2)

    press_c = next(c for c in contributors if c["feature"] == "pressure")
    assert press_c["feature"] == "pressure"
    assert press_c["observed"] == 994.0
    assert press_c["expected"] == 1008.0
    assert press_c["unit"] == "hPa"
    assert press_c["direction"] == "LOW"
    assert press_c["departure"] == pytest.approx(-14.0, rel=1e-2)


def test_natural_language_summary_generation() -> None:
    """Test natural language summary generator for disaster managers (Prompt 1.18)."""
    engine = ExplainabilityEngine()
    contributors = [
        {
            "feature": "rainfall",
            "contribution_pct": 52.4,
            "observed": 145.0,
            "expected": 18.2,
            "unit": "mm",
            "direction": "HIGH",
            "departure": 126.8,
            "pct_departure": 696.7,
            "z_score": 8.74,
        },
        {
            "feature": "temperature",
            "contribution_pct": 28.1,
            "observed": 37.0,
            "expected": 27.1,
            "unit": "°C",
            "direction": "HIGH",
            "departure": 9.9,
            "pct_departure": 36.5,
            "z_score": 5.50,
        },
    ]

    summary = engine.generate_natural_language_summary(
        severity="CRITICAL",
        anomaly_type="Extreme Rainfall",
        contributors=contributors,
        location="Bengaluru",
        month_name="September",
    )

    assert "CRITICAL ALERT in Bengaluru" in summary
    assert "Extreme Rainfall" in summary
    assert "Rainfall is +697%" in summary or "Rainfall is +696%" in summary
    assert "Temperature departure of +9.9°C" in summary

"""Unit tests for ml/baseline.py."""

import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ml.baseline import BaselineCalculator, compute_baseline_table


@pytest.fixture
def sample_weather_df() -> pd.DataFrame:
    """Provides a sample DataFrame with clean weather observations."""
    return pd.DataFrame(
        {
            "location": ["Bengaluru", "Bengaluru", "Bengaluru", "Delhi", "Delhi"],
            "month": [9, 9, 9, 5, 5],
            "temperature": [26.0, 27.0, 28.0, 40.0, 42.0],
            "relative_humidity": [70.0, 75.0, 80.0, 30.0, 35.0],
            "pressure": [1008.0, 1009.0, 1010.0, 998.0, 1000.0],
            "wind_speed": [3.0, 3.5, 4.0, 5.0, 6.0],
            "rainfall": [10.0, 20.0, 30.0, 0.0, 2.0],
        }
    )


def test_init_valid_dataframe(sample_weather_df: pd.DataFrame) -> None:
    """Test successful initialization with valid observations."""
    calc = BaselineCalculator(sample_weather_df)
    assert calc is not None
    assert calc.df is not None
    assert len(calc.df) == 5
    assert calc.get_available_locations() == ["Bengaluru", "Delhi"]


def test_init_missing_columns_raises_error() -> None:
    """Test that missing required columns raise a ValueError."""
    df_missing = pd.DataFrame(
        {
            "location": ["Bengaluru"],
            "month": [9],
            "temperature": [25.0],
            # missing humidity, pressure, wind_speed, rainfall
        }
    )
    with pytest.raises(ValueError, match="missing required columns"):
        BaselineCalculator(df_missing)


def test_init_empty_dataframe_raises_error() -> None:
    """Test that an empty DataFrame raises a ValueError."""
    empty_df = pd.DataFrame(columns=BaselineCalculator.REQUIRED_COLUMNS)
    with pytest.raises(ValueError, match="Input DataFrame is empty"):
        BaselineCalculator(empty_df)


def test_init_invalid_type_raises_error() -> None:
    """Test that non-DataFrame input raises a TypeError."""
    with pytest.raises(TypeError, match="Expected df to be a pandas DataFrame"):
        BaselineCalculator([{"location": "Bengaluru"}])  # type: ignore


def test_init_invalid_month_raises_error() -> None:
    """Test that month outside 1-12 raises a ValueError."""
    invalid_df = pd.DataFrame(
        {
            "location": ["Bengaluru"],
            "month": [13],  # invalid month
            "temperature": [25.0],
            "relative_humidity": [60.0],
            "pressure": [1010.0],
            "wind_speed": [5.0],
            "rainfall": [0.0],
        }
    )
    with pytest.raises(ValueError, match="invalid month values"):
        BaselineCalculator(invalid_df)


def test_compute_baselines_statistics(sample_weather_df: pd.DataFrame) -> None:
    """Test statistical calculations: mean (mu), std (sigma), median, q25, q75, IQR, p05, p95, min, max, count."""
    calc = BaselineCalculator(sample_weather_df)
    bengaluru_sep = calc.get_baseline("Bengaluru", 9)

    temp_stats = bengaluru_sep["temperature"]
    assert temp_stats["mean"] == pytest.approx(27.0)
    assert temp_stats["mu"] == pytest.approx(27.0)
    assert temp_stats["std"] == pytest.approx(1.0)
    assert temp_stats["sigma"] == pytest.approx(1.0)
    assert temp_stats["median"] == pytest.approx(27.0)
    assert temp_stats["q25"] == pytest.approx(26.5)
    assert temp_stats["q75"] == pytest.approx(27.5)
    assert temp_stats["iqr"] == pytest.approx(1.0)
    assert temp_stats["p05"] == pytest.approx(26.1)
    assert temp_stats["p95"] == pytest.approx(27.9)
    assert temp_stats["min"] == pytest.approx(26.0)
    assert temp_stats["max"] == pytest.approx(28.0)
    assert temp_stats["count"] == 3

    rain_stats = bengaluru_sep["rainfall"]
    assert rain_stats["mean"] == pytest.approx(20.0)
    assert rain_stats["mu"] == pytest.approx(20.0)
    assert rain_stats["std"] == pytest.approx(10.0)
    assert rain_stats["sigma"] == pytest.approx(10.0)
    assert rain_stats["median"] == pytest.approx(20.0)
    assert rain_stats["q25"] == pytest.approx(15.0)
    assert rain_stats["q75"] == pytest.approx(25.0)
    assert rain_stats["iqr"] == pytest.approx(10.0)
    assert rain_stats["p05"] == pytest.approx(11.0)
    assert rain_stats["p95"] == pytest.approx(29.0)
    assert rain_stats["min"] == pytest.approx(10.0)
    assert rain_stats["max"] == pytest.approx(30.0)


def test_get_baseline_validation_errors(sample_weather_df: pd.DataFrame) -> None:
    """Test that querying nonexistent location or month raises clean ValueError."""
    calc = BaselineCalculator(sample_weather_df)

    with pytest.raises(ValueError, match="Unknown location 'Mumbai'"):
        calc.get_baseline("Mumbai", 9)

    with pytest.raises(ValueError, match="Month 12 not found for location 'Bengaluru'"):
        calc.get_baseline("Bengaluru", 12)


def test_module_get_baseline_helper() -> None:
    """Test top-level get_baseline helper function."""
    from ml.baseline import get_baseline as helper_get_baseline

    # Should succeed for precomputed location
    delhi_may = helper_get_baseline("Delhi", 5)
    assert isinstance(delhi_may, dict)
    assert "temperature" in delhi_may
    assert "mean" in delhi_may["temperature"]

    # Should raise clean ValueError for unknown location
    with pytest.raises(ValueError, match="Unknown location 'NonExistentCity'"):
        helper_get_baseline("NonExistentCity", 5)


def test_calculate_z_scores(sample_weather_df: pd.DataFrame) -> None:
    """Test standardized Z-score computation: Z = (X - mu) / sigma."""
    calc = BaselineCalculator(sample_weather_df)
    observation = {
        "temperature": 29.0,  # mu = 27.0, sigma = 1.0 => Z = +2.0
        "rainfall": 50.0,     # mu = 20.0, sigma = 10.0 => Z = +3.0
        "relative_humidity": 75.0,  # mu = 75.0, sigma = 5.0 => Z = 0.0
    }
    z_scores = calc.calculate_z_scores(observation, "Bengaluru", 9)

    assert z_scores["temperature"] == pytest.approx(2.0)
    assert z_scores["rainfall"] == pytest.approx(3.0)
    assert z_scores["relative_humidity"] == pytest.approx(0.0)


def test_calculate_deviations(sample_weather_df: pd.DataFrame) -> None:
    """Test detailed deviation calculation."""
    calc = BaselineCalculator(sample_weather_df)
    obs = {"temperature": 30.0}
    devs = calc.calculate_deviations(obs, "Bengaluru", 9)

    temp_dev = devs["temperature"]
    assert temp_dev["observed"] == 30.0
    assert temp_dev["expected"] == pytest.approx(27.0)
    assert temp_dev["departure"] == pytest.approx(3.0)
    assert temp_dev["pct_departure"] == pytest.approx(3.0 / 27.0 * 100.0)
    assert temp_dev["z_score"] == pytest.approx(3.0)


def test_zero_variance_min_std_flooring() -> None:
    """Test that zero-variance metrics are floored by sigma_min = 0.1 to prevent division by zero."""
    df_constant = pd.DataFrame(
        {
            "location": ["TestCity", "TestCity"],
            "month": [1, 1],
            "temperature": [20.0, 20.0],  # std = 0
            "relative_humidity": [50.0, 50.0],
            "pressure": [1013.0, 1013.0],
            "wind_speed": [2.0, 2.0],
            "rainfall": [0.0, 0.0],
        }
    )
    # Default sigma_min should be 0.1
    calc_default = BaselineCalculator(df_constant)
    baseline_default = calc_default.get_baseline("TestCity", 1)
    assert baseline_default["temperature"]["std"] == pytest.approx(0.1)
    assert baseline_default["temperature"]["sigma"] == pytest.approx(0.1)

    # Z-score computation: (25.0 - 20.0) / 0.1 = 50.0
    z_scores = calc_default.calculate_z_scores({"temperature": 25.0}, "TestCity", 1)
    assert z_scores["temperature"] == pytest.approx(5.0 / 0.1)

    # Custom sigma_min
    calc_custom = BaselineCalculator(df_constant, sigma_min=0.05)
    baseline_custom = calc_custom.get_baseline("TestCity", 1)
    assert baseline_custom["temperature"]["std"] == pytest.approx(0.05)
    z_custom = calc_custom.calculate_z_scores({"temperature": 25.0}, "TestCity", 1)
    assert z_custom["temperature"] == pytest.approx(5.0 / 0.05)


def test_json_export_and_import(sample_weather_df: pd.DataFrame) -> None:
    """Test exporting baselines to JSON and loading them back."""
    calc = BaselineCalculator(sample_weather_df)

    with tempfile.TemporaryDirectory() as tmp_dir:
        json_path = Path(tmp_dir) / "baseline_stats.json"
        calc.save_to_json(json_path)

        assert json_path.exists()
        loaded_calc = BaselineCalculator.load_from_json(json_path)

        bengaluru_original = calc.get_baseline("Bengaluru", 9)
        bengaluru_loaded = loaded_calc.get_baseline("Bengaluru", 9)

        assert bengaluru_loaded["temperature"]["mean"] == bengaluru_original["temperature"]["mean"]
        assert bengaluru_loaded["temperature"]["std"] == bengaluru_original["temperature"]["std"]
def test_precomputed_baseline_statistics_json() -> None:
    """Test loading precomputed baselines from data/processed/baseline_statistics.json."""
    json_path = Path("data/processed/baseline_statistics.json")
    if json_path.exists():
        calc = BaselineCalculator.load_from_json(json_path)
        assert "Bengaluru" in calc.get_available_locations()
        assert "Delhi" in calc.get_available_locations()
        bengaluru_sep = calc.get_baseline("Bengaluru", 9)
        assert "temperature" in bengaluru_sep
        assert bengaluru_sep["temperature"]["mean"] > 0.0

        # Verify O(1) in-memory lookup
        z_scores = calc.calculate_z_scores({"temperature": 35.0, "rainfall": 100.0}, "Bengaluru", 9)
        assert "temperature" in z_scores
        assert "rainfall" in z_scores


def test_convenience_function(sample_weather_df: pd.DataFrame) -> None:
    """Test compute_baseline_table convenience helper function."""
    calc = compute_baseline_table(sample_weather_df)
    assert isinstance(calc, BaselineCalculator)
    assert calc.get_available_locations() == ["Bengaluru", "Delhi"]

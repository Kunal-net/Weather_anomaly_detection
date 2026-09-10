"""
Data Engineering Pipeline Tests (Member 2 Deliverables).

Validates:
- Raw METAR loading & parsing (ml/preprocessing.py)
- Pressure priority fallbacks (altimeter -> sea_level -> station_level)
- Precipitation continuous derivation from codes and accumulations
- Physical domain bounds validation & gap imputation (zero NaNs)
- Cyclical temporal & diurnal encodings (sin/cos bounds [-1, 1])
- 7-day and 30-day rolling statistics
- 10-city climatology & diurnal realism (ml/data_generator.py)
- Historical extreme benchmark injection & ground-truth anomaly tagging
- Integration with BaselineCalculator and ML training pipeline
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np
import pandas as pd
import pytest

from ml.baseline import BaselineCalculator
from ml.data_generator import (
    INDIAN_CITIES_METADATA,
    build_and_save_full_dataset,
    generate_city_observations,
    inject_historical_extreme_events,
)
from ml.preprocessing import (
    PHYSICAL_BOUNDS,
    add_cyclical_features,
    add_rolling_statistics,
    extract_and_clean_core_columns,
    extract_atmospheric_pressure,
    extract_precipitation,
    impute_missing_values,
    load_raw_metar,
    preprocess_bangalore_metar,
    validate_physical_bounds,
)


def test_load_raw_metar():
    """Requirement 1: Test loading raw METAR CSV."""
    df = load_raw_metar("data/raw/bangalore_2024_metar.csv")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) > 10000
    assert "DATE" in df.columns


def test_pressure_fallbacks():
    """Requirement 3: Test pressure fallback hierarchy."""
    sample_df = pd.DataFrame({
        "altimeter": [1015.0, np.nan, np.nan],
        "sea_level_pressure": [1014.0, 1012.0, np.nan],
        "station_level_pressure": [910.0, 911.0, 908.0],
    })
    pressure = extract_atmospheric_pressure(sample_df)
    assert pressure.iloc[0] == 1015.0  # From altimeter
    assert pressure.iloc[1] == 1012.0  # Fallback to sea_level_pressure
    assert pressure.iloc[2] == 908.0   # Fallback to station_level_pressure


def test_precipitation_extraction():
    """Requirement 4: Test continuous precipitation derivation."""
    sample_df = pd.DataFrame({
        "precipitation_3_hour": [6.0, np.nan, 0.0],
        "precipitation_24_hour": [np.nan, 48.0, 0.0],
        "pres_wx_MW1": [np.nan, "RA:63", "TS:95"],
        "REM": ["METAR VOBG", "METAR VOBG -RA", "METAR VOBG +RA TSRA"],
    })
    rainfall = extract_precipitation(sample_df)
    assert len(rainfall) == 3
    assert (rainfall >= 0.0).all()
    # Thunderstorm/heavy rain in row 2 should result in high rainfall
    assert rainfall.iloc[2] >= 15.0


def test_physical_bounds_validation():
    """Requirement 6: Test rejection of sensor glitches and out-of-bounds values."""
    sample_df = pd.DataFrame({
        "temperature": [-60.0, 25.0, 75.0],       # -60 and 75 violate [-50, 60]
        "relative_humidity": [-5.0, 60.0, 120.0],  # -5 and 120 violate [0, 100]
        "pressure": [800.0, 1010.0, 1200.0],      # 800 and 1200 violate [870, 1085]
        "wind_speed": [-10.0, 5.0, 150.0],        # -10 and 150 violate [0, 120]
        "rainfall": [-5.0, 10.0, 2000.0],
    })
    validated = validate_physical_bounds(sample_df)

    assert pd.isna(validated["temperature"].iloc[0])
    assert validated["temperature"].iloc[1] == 25.0
    assert pd.isna(validated["temperature"].iloc[2])

    assert pd.isna(validated["relative_humidity"].iloc[0])
    assert validated["relative_humidity"].iloc[1] == 60.0
    assert pd.isna(validated["relative_humidity"].iloc[2])

    assert pd.isna(validated["pressure"].iloc[0])
    assert pd.isna(validated["wind_speed"].iloc[0])
    assert validated["rainfall"].iloc[0] == 0.0
    assert validated["rainfall"].iloc[2] <= PHYSICAL_BOUNDS["rainfall"][1]


def test_missing_value_imputation():
    """Requirement 7: Test short-gap forward-fill and monthly-hourly median imputation."""
    dates = pd.date_range("2024-01-01", periods=10, freq="1h")
    sample_df = pd.DataFrame({
        "timestamp": dates,
        "location": "Bengaluru",
        "month": dates.month,
        "hour": dates.hour,
        "temperature": [20.0, np.nan, np.nan, 23.0, np.nan, np.nan, np.nan, np.nan, 25.0, 26.0],
        "dew_point_temperature": [15.0] * 10,
        "relative_humidity": [60.0, np.nan, 62.0, 65.0, np.nan, 70.0, 72.0, 75.0, np.nan, 80.0],
        "pressure": [1012.0] * 10,
        "wind_speed": [3.0] * 10,
        "wind_direction": [180.0] * 10,
        "rainfall": [0.0] * 10,
    })
    imputed = impute_missing_values(sample_df)
    assert imputed.isna().sum().sum() == 0
    assert (imputed["temperature"] > 0).all()


def test_cyclical_features():
    """Requirements 9 & 10: Test cyclical temporal and diurnal encodings."""
    sample_df = pd.DataFrame({
        "day_of_year": np.array([1, 91, 182, 273, 365]),
        "hour": np.array([0, 6, 12, 18, 23]),
    })
    encoded = add_cyclical_features(sample_df)

    assert "sin_day" in encoded.columns
    assert "cos_day" in encoded.columns
    assert "sin_hour" in encoded.columns
    assert "cos_hour" in encoded.columns

    # Verify sine/cosine unit circle range [-1, 1]
    assert (encoded["sin_day"] >= -1.0).all() and (encoded["sin_day"] <= 1.0).all()
    assert (encoded["cos_day"] >= -1.0).all() and (encoded["cos_day"] <= 1.0).all()
    assert (encoded["sin_hour"] >= -1.0).all() and (encoded["sin_hour"] <= 1.0).all()
    assert (encoded["cos_hour"] >= -1.0).all() and (encoded["cos_hour"] <= 1.0).all()


def test_rolling_statistics():
    """Requirements 11 & 12: Test 7-day and 30-day rolling corridors."""
    dates = pd.date_range("2024-01-01", periods=100, freq="1h")
    sample_df = pd.DataFrame({
        "timestamp": dates,
        "temperature": np.random.normal(25.0, 2.0, 100),
        "pressure": np.random.normal(1010.0, 3.0, 100),
        "relative_humidity": np.random.normal(65.0, 5.0, 100),
        "rainfall": np.random.exponential(2.0, 100),
    })
    rolling_df = add_rolling_statistics(sample_df)

    assert "temp_rolling_7d" in rolling_df.columns
    assert "press_rolling_7d" in rolling_df.columns
    assert "rh_rolling_7d" in rolling_df.columns
    assert "rain_rolling_7d_sum" in rolling_df.columns
    assert "temp_rolling_30d" in rolling_df.columns
    assert rolling_df["temp_rolling_7d"].notna().all()


def test_multi_city_definitions_and_diurnal_curve():
    """Requirements 14, 15, 16: Test 10 cities and diurnal temperature swing."""
    assert len(INDIAN_CITIES_METADATA) == 10
    expected_cities = [
        "Bengaluru", "Mumbai", "Delhi", "Chennai", "Kolkata",
        "Hyderabad", "Ahmedabad", "Jaipur", "Shimla", "Bhubaneswar"
    ]
    for city in expected_cities:
        assert city in INDIAN_CITIES_METADATA

    blr_meta = INDIAN_CITIES_METADATA["Bengaluru"]
    df_blr = generate_city_observations("Bengaluru", blr_meta, start_year=2024, end_year=2024, freq_hours=1)

    # In diurnal cycle, afternoon (14:00) should on average be warmer than dawn (05:00)
    t_14 = df_blr[df_blr["hour"] == 14]["temperature"].mean()
    t_05 = df_blr[df_blr["hour"] == 5]["temperature"].mean()
    assert t_14 > t_05 + 3.0, f"Expected afternoon temp ({t_14:.1f}) > dawn temp ({t_05:.1f})"


def test_historical_extreme_event_injection():
    """Requirements 17 & 18: Test extreme benchmark injection and ground-truth tagging."""
    df_chennai = generate_city_observations(
        "Chennai", INDIAN_CITIES_METADATA["Chennai"], start_year=2015, end_year=2015, freq_hours=6
    )
    df_kolkata = generate_city_observations(
        "Kolkata", INDIAN_CITIES_METADATA["Kolkata"], start_year=2020, end_year=2020, freq_hours=6
    )
    combined = pd.concat([df_chennai, df_kolkata], ignore_index=True)

    tagged = inject_historical_extreme_events(combined)
    assert "is_ground_truth_anomaly" in tagged.columns
    assert tagged["is_ground_truth_anomaly"].sum() > 0

    # Verify Chennai 2015 cloudburst is tagged
    chennai_event = tagged[(tagged["location"] == "Chennai") & (tagged["month"] == 12) & (tagged["day"] == 1)]
    assert (chennai_event["is_ground_truth_anomaly"] == True).all()
    assert (chennai_event["rainfall"] >= 300.0).all()


def test_processed_dataset_integrity():
    """Requirement 19: Test processed datasets on disk."""
    bangalore_path = Path("data/processed/bangalore_cleaned.csv")
    weather_path = Path("data/processed/weather_cleaned.csv")

    assert bangalore_path.exists()
    assert weather_path.exists()

    df_blr = pd.read_csv(bangalore_path)
    df_all = pd.read_csv(weather_path)

    assert not df_blr.empty
    assert not df_all.empty

    # Check zero NaNs
    assert df_blr.isna().sum().sum() == 0
    assert df_all.isna().sum().sum() == 0

    # Check 10 cities present in weather_cleaned.csv
    assert df_all["location"].nunique() == 10

    # Check ground truth anomaly column
    assert "is_ground_truth_anomaly" in df_all.columns
    assert df_all["is_ground_truth_anomaly"].dtype == bool or df_all["is_ground_truth_anomaly"].isin([True, False, 1, 0]).all()


def test_baseline_calculator_compatibility():
    """Verifies that weather_cleaned.csv works seamlessly with BaselineCalculator."""
    df_all = pd.read_csv("data/processed/weather_cleaned.csv")
    calc = BaselineCalculator(df_all, sigma_min=0.1, auto_compute=True)
    assert len(calc.get_available_locations()) == 10

    bengaluru_sep = calc.get_baseline("Bengaluru", 9)
    assert "temperature" in bengaluru_sep
    assert "rainfall" in bengaluru_sep
    assert bengaluru_sep["temperature"]["mean"] > 0

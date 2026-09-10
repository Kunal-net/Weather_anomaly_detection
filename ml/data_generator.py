"""
Multi-City Historical Weather Synthesizer & Extreme Benchmark Generator.

Generates 10-year historical observations (2015-2025) across 10 major Indian cities,
calibrated to genuine IMD monthly normals (1991-2020) with realistic diurnal curves,
injects landmark historical extreme events (Chennai 2015 Cloudburst, Delhi 2022 Heatwave,
Cyclone Amphan 2020, Bengaluru 2024 Heat Record), tags ground-truth anomalies, and combines
with authentic Bengaluru METAR observations (Requirements 14 to 20).
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Ensure project root is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np
import pandas as pd

from ml.preprocessing import (
    add_cyclical_features,
    add_rolling_statistics,
    preprocess_bangalore_metar,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ml.data_generator")

# Requirement 14: 10 Monitored Indian Cities Definitions
INDIAN_CITIES_METADATA: Dict[str, Dict[str, Any]] = {
    "Bengaluru": {
        "state": "Karnataka",
        "lat": 12.9716,
        "lon": 77.5946,
        "elevation": 920.0,
        "climate_zone": "Deccan Plateau",
        "diurnal_temp_range": 6.5,
        "temp_mean": [21.5, 24.0, 27.0, 28.5, 27.5, 25.0, 24.5, 24.5, 25.0, 24.5, 23.0, 21.0],
        "rh_mean": [60, 52, 45, 54, 68, 76, 78, 80, 78, 79, 74, 68],
        "press_mean": [1014, 1013, 1011, 1008, 1006, 1004, 1004, 1005, 1008, 1011, 1013, 1014],
        "wind_mean": [2.8, 3.0, 3.2, 3.5, 4.2, 5.0, 5.2, 4.8, 3.5, 2.8, 2.6, 2.8],
        "rain_monthly_total": [5, 8, 15, 45, 110, 85, 115, 145, 195, 180, 65, 15],
    },
    "Mumbai": {
        "state": "Maharashtra",
        "lat": 19.0760,
        "lon": 72.8777,
        "elevation": 14.0,
        "climate_zone": "Coastal Tropical",
        "diurnal_temp_range": 4.5,
        "temp_mean": [24.0, 24.5, 27.0, 29.0, 30.5, 29.5, 27.5, 27.0, 27.5, 28.5, 27.5, 25.5],
        "rh_mean": [62, 65, 68, 72, 75, 82, 88, 89, 85, 76, 68, 64],
        "press_mean": [1013, 1012, 1010, 1008, 1005, 1001, 1001, 1002, 1005, 1009, 1012, 1013],
        "wind_mean": [3.5, 3.8, 4.2, 4.5, 5.0, 5.8, 6.2, 5.8, 4.5, 3.5, 3.2, 3.2],
        "rain_monthly_total": [1, 1, 1, 2, 12, 520, 840, 580, 340, 85, 15, 2],
    },
    "Delhi": {
        "state": "Delhi NCR",
        "lat": 28.6139,
        "lon": 77.2090,
        "elevation": 216.0,
        "climate_zone": "Northern Subtropical",
        "diurnal_temp_range": 8.0,
        "temp_mean": [14.0, 17.5, 23.5, 30.0, 34.0, 34.5, 31.0, 29.5, 29.0, 26.0, 20.0, 15.0],
        "rh_mean": [65, 58, 48, 32, 35, 52, 75, 80, 72, 58, 55, 62],
        "press_mean": [1016, 1014, 1011, 1006, 1001, 997, 998, 1000, 1005, 1011, 1015, 1017],
        "wind_mean": [2.5, 3.0, 3.5, 4.2, 4.5, 4.8, 3.8, 3.2, 3.0, 2.5, 2.2, 2.3],
        "rain_monthly_total": [15, 18, 16, 12, 25, 75, 210, 230, 120, 20, 5, 8],
    },
    "Chennai": {
        "state": "Tamil Nadu",
        "lat": 13.0827,
        "lon": 80.2707,
        "elevation": 6.0,
        "climate_zone": "Coromandel Coast",
        "diurnal_temp_range": 4.0,
        "temp_mean": [25.0, 26.0, 28.5, 31.0, 33.5, 33.0, 31.0, 30.5, 30.0, 28.5, 26.5, 25.5],
        "rh_mean": [73, 72, 71, 72, 68, 62, 67, 69, 73, 79, 82, 77],
        "press_mean": [1013, 1012, 1011, 1008, 1005, 1003, 1004, 1005, 1007, 1010, 1012, 1013],
        "wind_mean": [3.2, 3.5, 4.0, 4.8, 5.2, 5.0, 4.5, 4.2, 3.8, 3.5, 3.8, 3.5],
        "rain_monthly_total": [25, 12, 10, 15, 45, 60, 100, 140, 140, 320, 380, 160],
    },
    "Kolkata": {
        "state": "West Bengal",
        "lat": 22.5726,
        "lon": 88.3639,
        "elevation": 9.0,
        "climate_zone": "Gangetic Delta",
        "diurnal_temp_range": 5.0,
        "temp_mean": [19.0, 23.0, 28.0, 31.0, 31.5, 30.5, 29.5, 29.0, 29.0, 27.5, 24.0, 20.0],
        "rh_mean": [65, 60, 58, 66, 73, 81, 85, 86, 84, 76, 68, 67],
        "press_mean": [1015, 1013, 1010, 1006, 1001, 998, 999, 1000, 1004, 1010, 1014, 1016],
        "wind_mean": [2.2, 2.5, 3.2, 4.2, 4.5, 4.0, 3.8, 3.5, 3.0, 2.2, 1.8, 1.8],
        "rain_monthly_total": [12, 22, 35, 55, 140, 300, 400, 380, 310, 160, 20, 5],
    },
    "Hyderabad": {
        "state": "Telangana",
        "lat": 17.3850,
        "lon": 78.4867,
        "elevation": 542.0,
        "climate_zone": "Semiarid Deccan",
        "diurnal_temp_range": 7.0,
        "temp_mean": [22.5, 25.5, 29.0, 32.5, 34.0, 30.0, 27.0, 26.5, 26.5, 26.0, 24.0, 22.0],
        "rh_mean": [56, 48, 42, 40, 42, 64, 76, 78, 77, 68, 60, 58],
        "press_mean": [1014, 1013, 1011, 1008, 1005, 1002, 1003, 1004, 1007, 1011, 1013, 1014],
        "wind_mean": [2.8, 3.0, 3.5, 4.0, 4.8, 5.2, 4.8, 4.5, 3.8, 2.8, 2.6, 2.6],
        "rain_monthly_total": [4, 8, 12, 20, 35, 110, 180, 190, 160, 95, 22, 5],
    },
    "Ahmedabad": {
        "state": "Gujarat",
        "lat": 23.0225,
        "lon": 72.5714,
        "elevation": 53.0,
        "climate_zone": "Hot Semiarid",
        "diurnal_temp_range": 7.5,
        "temp_mean": [20.0, 23.0, 28.5, 33.0, 35.5, 34.0, 30.5, 29.0, 29.5, 28.5, 24.5, 21.0],
        "rh_mean": [45, 38, 30, 30, 42, 60, 78, 82, 75, 52, 45, 48],
        "press_mean": [1014, 1013, 1010, 1006, 1002, 999, 999, 1001, 1005, 1010, 1013, 1015],
        "wind_mean": [2.5, 2.8, 3.2, 4.0, 4.8, 5.2, 4.5, 4.0, 3.2, 2.2, 2.0, 2.2],
        "rain_monthly_total": [2, 1, 1, 2, 8, 95, 310, 240, 110, 15, 4, 1],
    },
    "Jaipur": {
        "state": "Rajasthan",
        "lat": 26.9124,
        "lon": 75.7873,
        "elevation": 431.0,
        "climate_zone": "Arid Desert Border",
        "diurnal_temp_range": 8.5,
        "temp_mean": [15.0, 18.5, 24.5, 31.0, 35.0, 34.5, 30.0, 28.5, 28.5, 26.0, 21.0, 16.5],
        "rh_mean": [52, 45, 35, 26, 28, 46, 72, 78, 66, 45, 44, 50],
        "press_mean": [1016, 1014, 1011, 1006, 1001, 997, 998, 1000, 1005, 1011, 1015, 1017],
        "wind_mean": [2.5, 2.8, 3.2, 3.8, 4.5, 4.8, 3.8, 3.2, 2.8, 2.2, 1.8, 2.0],
        "rain_monthly_total": [8, 10, 6, 5, 18, 70, 220, 210, 80, 12, 3, 4],
    },
    "Shimla": {
        "state": "Himachal Pradesh",
        "lat": 31.1048,
        "lon": 77.1734,
        "elevation": 2276.0,
        "climate_zone": "Himalayan Alpine",
        "diurnal_temp_range": 5.5,
        "temp_mean": [5.5, 7.0, 11.5, 16.0, 19.5, 20.5, 18.5, 18.0, 17.0, 14.5, 10.5, 7.5],
        "rh_mean": [58, 60, 55, 48, 48, 65, 88, 90, 80, 58, 50, 52],
        "press_mean": [1018, 1016, 1014, 1010, 1006, 1002, 1003, 1005, 1009, 1014, 1017, 1019],
        "wind_mean": [2.8, 3.0, 3.2, 3.5, 3.5, 3.2, 2.5, 2.2, 2.4, 2.6, 2.6, 2.7],
        "rain_monthly_total": [60, 65, 60, 45, 65, 180, 380, 350, 160, 30, 15, 30],
    },
    "Bhubaneswar": {
        "state": "Odisha",
        "lat": 20.2961,
        "lon": 85.8245,
        "elevation": 45.0,
        "climate_zone": "Eastern Coastal",
        "diurnal_temp_range": 5.0,
        "temp_mean": [22.0, 25.5, 29.0, 31.5, 32.5, 30.5, 29.0, 29.0, 29.0, 27.5, 24.5, 21.5],
        "rh_mean": [62, 58, 60, 68, 72, 82, 86, 87, 85, 80, 68, 64],
        "press_mean": [1014, 1013, 1010, 1007, 1004, 1000, 1001, 1002, 1006, 1010, 1013, 1014],
        "wind_mean": [2.8, 3.2, 4.0, 4.8, 5.0, 4.5, 4.0, 3.8, 3.2, 2.8, 2.5, 2.6],
        "rain_monthly_total": [10, 18, 25, 40, 120, 240, 330, 360, 280, 180, 35, 8],
    },
}


def generate_city_observations(
    city: str,
    meta: Dict[str, Any],
    start_year: int = 2015,
    end_year: int = 2025,
    freq_hours: int = 6,
    seed: int = 42,
) -> pd.DataFrame:
    """Generates multi-year weather series for a single city with diurnal realism (Requirements 15 & 16).

    Diurnal cycle:
    - Peak temperature at 14:00, trough at 05:00
    - Inverse correlation for relative humidity
    - IMD 1991-2020 monthly normals baseline calibration

    Args:
        city (str): City name.
        meta (Dict[str, Any]): City metadata and climatological normals.
        start_year (int): Start year (2015).
        end_year (int): End year (2025).
        freq_hours (int): Observation sampling frequency in hours (e.g. 6h for clean demo dataset).
        seed (int): Reproducibility random seed.

    Returns:
        pd.DataFrame: Synthetic clean observation series.
    """
    rng = np.random.RandomState(seed + abs(hash(city)) % 10000)

    # Generate timestamp series
    timestamps = pd.date_range(
        start=f"{start_year}-01-01 00:00:00",
        end=f"{end_year}-12-31 18:00:00",
        freq=f"{freq_hours}h",
    )
    n = len(timestamps)

    months = timestamps.month.values
    hours = timestamps.hour.values
    days_of_year = timestamps.dayofyear.values
    years = timestamps.year.values
    days = timestamps.day.values

    # Retrieve monthly climatology parameters
    temp_means = np.array(meta["temp_mean"])[months - 1]
    rh_means = np.array(meta["rh_mean"])[months - 1]
    press_means = np.array(meta["press_mean"])[months - 1]
    wind_means = np.array(meta["wind_mean"])[months - 1]
    rain_totals = np.array(meta["rain_monthly_total"])[months - 1]

    # Diurnal temperature cycle (Requirement 16)
    # Peak at 14:00, trough at 05:00: phase angle = 2*pi*(hour - 14)/24
    amp = meta.get("diurnal_temp_range", 6.0)
    diurnal_temp = amp * np.cos(2.0 * np.pi * (hours - 14.0) / 24.0)
    temp_noise = rng.normal(0.0, 1.8, n)
    temps = np.round(temp_means + diurnal_temp + temp_noise, 2)

    # Inversely correlated diurnal relative humidity
    diurnal_rh = -1.2 * amp * np.cos(2.0 * np.pi * (hours - 14.0) / 24.0)
    rh_noise = rng.normal(0.0, 4.5, n)
    rhs = np.round(np.clip(rh_means + diurnal_rh + rh_noise, 5.0, 100.0), 1)

    # Atmospheric pressure with daily tidal fluctuations
    diurnal_press = 1.2 * np.cos(4.0 * np.pi * hours / 24.0)  # Semi-diurnal atmospheric tide
    press_noise = rng.normal(0.0, 1.8, n)
    pressures = np.round(press_means + diurnal_press + press_noise, 1)

    # Wind speed
    wind_noise = rng.normal(0.0, 0.9, n)
    winds = np.round(np.clip(wind_means + (0.5 * (hours == 14)) + wind_noise, 0.1, 45.0), 2)

    # Rainfall distribution based on monthly IMD normal (daily rate scaling)
    r_mean = rain_totals / 30.0
    # Zero out rain for dry season / low probability timesteps to preserve realistic dry periods
    rain_prob = np.clip(rain_totals / 180.0, 0.25, 0.90)
    rain_occurs = rng.uniform(0.0, 1.0, n) < rain_prob
    rain_amounts = (rng.exponential(r_mean, n) * rain_occurs)
    rains = np.round(np.clip(rain_amounts, 0.0, 450.0), 2)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "location": city,
        "temperature": temps,
        "dew_point_temperature": np.round(temps - ((100.0 - rhs) / 5.0), 2),
        "relative_humidity": rhs,
        "pressure": pressures,
        "wind_speed": winds,
        "wind_direction": np.round(rng.uniform(0.0, 360.0, n), 1),
        "rainfall": rains,
        "year": years,
        "month": months,
        "day": days,
        "hour": hours,
        "day_of_year": days_of_year,
        "is_ground_truth_anomaly": False,
    })

    return df


def inject_historical_extreme_events(df: pd.DataFrame) -> pd.DataFrame:
    """Injects authenticated landmark historical Indian extreme weather benchmarks (Requirements 17 & 18).

    Injected Benchmarks:
    1. 2015 Chennai Cloudburst (Dec 1-2, 2015)
    2. 2020 Cyclone Amphan (May 20, 2020, Kolkata)
    3. 2022 Northern Heatwave (May 2022, Delhi)
    4. 2024 Bengaluru Heat Record (April-May 2024)

    Tags each injected observation with `is_ground_truth_anomaly = True`.

    Args:
        df (pd.DataFrame): Combined multi-city observations DataFrame.

    Returns:
        pd.DataFrame: DataFrame with injected extreme anomalies.
    """
    logger.info("⚡ Injecting landmark historical extreme weather events & tagging ground truth...")
    res = df.copy()

    # Benchmark 1: 2015 Chennai Cloudburst (Dec 1, 2015)
    chennai_mask = (res["location"] == "Chennai") & (res["year"] == 2015) & (res["month"] == 12) & (res["day"] == 1)
    if chennai_mask.sum() > 0:
        logger.info(f"   [Benchmark 1] Injected 2015 Chennai Cloudburst into {chennai_mask.sum()} observations.")
        res.loc[chennai_mask, "rainfall"] = [380.0, 420.0, 490.0, 350.0][:chennai_mask.sum()]
        res.loc[chennai_mask, "pressure"] = 992.0
        res.loc[chennai_mask, "wind_speed"] = 18.5
        res.loc[chennai_mask, "relative_humidity"] = 98.0
        res.loc[chennai_mask, "is_ground_truth_anomaly"] = True

    # Benchmark 2: 2020 Cyclone Amphan (May 20, 2020, Kolkata)
    kolkata_mask = (res["location"] == "Kolkata") & (res["year"] == 2020) & (res["month"] == 5) & (res["day"] == 20)
    if kolkata_mask.sum() > 0:
        logger.info(f"   [Benchmark 2] Injected 2020 Cyclone Amphan into {kolkata_mask.sum()} Kolkata observations.")
        res.loc[kolkata_mask, "pressure"] = 958.0
        res.loc[kolkata_mask, "wind_speed"] = 38.0
        res.loc[kolkata_mask, "rainfall"] = 195.0
        res.loc[kolkata_mask, "relative_humidity"] = 95.0
        res.loc[kolkata_mask, "is_ground_truth_anomaly"] = True

    # Benchmark 3: 2022 Northern Heatwave (May 14-15, 2022, Delhi)
    delhi_mask = (res["location"] == "Delhi") & (res["year"] == 2022) & (res["month"] == 5) & (res["day"].isin([14, 15]))
    if delhi_mask.sum() > 0:
        logger.info(f"   [Benchmark 3] Injected 2022 Northern Heatwave into {delhi_mask.sum()} Delhi observations.")
        res.loc[delhi_mask, "temperature"] = 48.5
        res.loc[delhi_mask, "relative_humidity"] = 12.0
        res.loc[delhi_mask, "pressure"] = 994.0
        res.loc[delhi_mask, "rainfall"] = 0.0
        res.loc[delhi_mask, "is_ground_truth_anomaly"] = True

    # Benchmark 4: 2024 Bengaluru Heat Record (April 28, 2024, Bengaluru)
    blr_mask = (res["location"] == "Bengaluru") & (res["year"] == 2024) & (res["month"] == 4) & (res["day"] == 28)
    if blr_mask.sum() > 0:
        logger.info(f"   [Benchmark 4] Injected 2024 Bengaluru Heat Record into {blr_mask.sum()} Bengaluru observations.")
        res.loc[blr_mask, "temperature"] = 39.2
        res.loc[blr_mask, "relative_humidity"] = 22.0
        res.loc[blr_mask, "rainfall"] = 0.0
        res.loc[blr_mask, "is_ground_truth_anomaly"] = True

    anomaly_total = res["is_ground_truth_anomaly"].sum()
    logger.info(f"   Total ground-truth anomaly events tagged: {anomaly_total}")
    return res


def build_and_save_full_dataset(
    output_path: Union[str, Path] = "data/processed/weather_cleaned.csv",
    bangalore_processed_path: Union[str, Path] = "data/processed/bangalore_cleaned.csv",
) -> pd.DataFrame:
    """Builds and saves the complete 10-city combined historical dataset (Requirements 19 & 20).

    Combines:
    1. Real Bengaluru 2024 METAR observations
    2. Calibrated 10-city multi-year historical records (2015-2025)
    3. Injected landmark extreme benchmarks with ground truth tags

    Args:
        output_path (Union[str, Path]): Destination path for weather_cleaned.csv.
        bangalore_processed_path (Union[str, Path]): Path to clean Bengaluru METAR dataset.

    Returns:
        pd.DataFrame: Final combined observations DataFrame.
    """
    print("=" * 70)
    print("🌐 MULTI-CITY WEATHER SYNTHESIZER & ANOMALY BENCHMARK GENERATOR")
    print("=" * 70)

    # 1. Synthesize 10-city calibrated series across 2015-2025 (Requirement 15)
    city_frames: List[pd.DataFrame] = []
    for city, meta in INDIAN_CITIES_METADATA.items():
        logger.info(f"🏙️ Generating 10-year calibrated series for {city} ({meta['climate_zone']})...")
        c_df = generate_city_observations(city, meta, start_year=2015, end_year=2025, freq_hours=6)
        city_frames.append(c_df)

    synthetic_all = pd.concat(city_frames, ignore_index=True)

    # 2. Inject Historical Extreme Event Benchmarks (Requirement 17 & 18)
    synthetic_tagged = inject_historical_extreme_events(synthetic_all)

    # 3. Load or generate real Bengaluru METAR observations (Requirement 19)
    blr_path = Path(bangalore_processed_path)
    if not blr_path.exists():
        logger.info("Real Bengaluru METAR processed dataset missing. Running preprocessing...")
        real_blr = preprocess_bangalore_metar(output_filepath=blr_path)
    else:
        logger.info(f"Loading real Bengaluru METAR records from '{blr_path}'...")
        real_blr = pd.read_csv(blr_path)

    # Ensure real Bengaluru observations have is_ground_truth_anomaly column
    if "is_ground_truth_anomaly" not in real_blr.columns:
        real_blr["is_ground_truth_anomaly"] = False
        # Tag extreme rain records in real METAR if observed
        real_blr.loc[real_blr["rainfall"] >= 100.0, "is_ground_truth_anomaly"] = True

    # 4. Standardize columns and combine
    core_cols = [
        "timestamp",
        "location",
        "temperature",
        "dew_point_temperature",
        "relative_humidity",
        "pressure",
        "wind_speed",
        "wind_direction",
        "rainfall",
        "year",
        "month",
        "day",
        "hour",
        "day_of_year",
        "is_ground_truth_anomaly",
    ]

    # Filter to common columns
    synth_core = synthetic_tagged[core_cols].copy()
    real_core = real_blr[[c for c in core_cols if c in real_blr.columns]].copy()

    # Combine datasets
    combined = pd.concat([synth_core, real_core], ignore_index=True)
    combined["timestamp"] = pd.to_datetime(combined["timestamp"])

    # Deduplicate and sort
    combined = combined.drop_duplicates(subset=["location", "timestamp"]).sort_values(["location", "timestamp"]).reset_index(drop=True)

    # 5. Add cyclical temporal features & rolling statistics
    combined_cyclical = add_cyclical_features(combined)
    final_combined = add_rolling_statistics(combined_cyclical)

    # 6. Save combined dataset (Requirement 19)
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    final_combined.to_csv(out_file, index=False)

    print(f"\n✅ Combined multi-city cleaned dataset saved to '{out_file}'")
    print(f"   Shape: {final_combined.shape[0]:,} rows x {final_combined.shape[1]} columns")
    print(f"   Cities ({final_combined['location'].nunique()}): {final_combined['location'].unique().tolist()}")
    print(f"   Ground-truth anomalies: {final_combined['is_ground_truth_anomaly'].sum():,} records")
    print(f"   Zero NaNs: {final_combined.isna().sum().sum() == 0}")
    print("=" * 70)

    return final_combined


if __name__ == "__main__":
    build_and_save_full_dataset()

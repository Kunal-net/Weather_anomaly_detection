"""
Data Preprocessing & Cleaning Pipeline for Real METAR Weather Observations.

Processes authentic NOAA ISD / ICAO METAR station reports for Bengaluru (VOBG),
handling pressure fallbacks, continuous precipitation derivation, physical bounds
validation, gap imputation, cyclical temporal encodings, and rolling statistics.
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path
from typing import Optional, Union

# Ensure project root is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ml.preprocessing")

# Default physical domain bounds for meteorological sanity checks
PHYSICAL_BOUNDS = {
    "temperature": (-50.0, 60.0),
    "relative_humidity": (0.0, 100.0),
    "pressure": (870.0, 1085.0),
    "wind_speed": (0.0, 120.0),
    "rainfall": (0.0, 1500.0),
}


def load_raw_metar(
    filepath: Union[str, Path] = "data/raw/bangalore_2024_metar.csv",
) -> pd.DataFrame:
    """Ingests raw METAR CSV efficiently handling mixed types (Requirement 1).

    Args:
        filepath (Union[str, Path]): Path to raw METAR CSV file.

    Returns:
        pd.DataFrame: Loaded raw DataFrame.
    """
    path = Path(filepath)
    if not path.exists():
        # Fall back to root output.csv if relative path differs
        alt_path = Path("output.csv")
        if alt_path.exists():
            path = alt_path
        else:
            raise FileNotFoundError(f"Raw METAR file not found at: {filepath}")

    logger.info(f"📥 Loading raw METAR dataset from '{path}' (low_memory=False)...")
    df = pd.read_csv(path, low_memory=False)
    logger.info(f"   Loaded {len(df):,} raw records with {len(df.columns)} columns.")
    return df


def extract_atmospheric_pressure(df: pd.DataFrame) -> pd.Series:
    """Extracts atmospheric pressure with prioritized fallbacks (Requirement 3).

    Priority:
    1. altimeter (QNH station pressure in hPa)
    2. sea_level_pressure
    3. station_level_pressure

    Args:
        df (pd.DataFrame): Raw observations DataFrame.

    Returns:
        pd.Series: Cleaned continuous atmospheric pressure in hPa.
    """
    pressure = pd.Series(np.nan, index=df.index, dtype=float)

    if "altimeter" in df.columns:
        alt = pd.to_numeric(df["altimeter"], errors="coerce")
        pressure = pressure.fillna(alt)

    if "sea_level_pressure" in df.columns:
        slp = pd.to_numeric(df["sea_level_pressure"], errors="coerce")
        pressure = pressure.fillna(slp)

    if "station_level_pressure" in df.columns:
        stp = pd.to_numeric(df["station_level_pressure"], errors="coerce")
        pressure = pressure.fillna(stp)

    return pressure


def extract_precipitation(df: pd.DataFrame) -> pd.Series:
    """Derives continuous rainfall in mm from accumulation columns & METAR phenomena (Requirement 4).

    Parses precipitation_24_hour, precipitation_3_hour, pres_wx_MW1, and REM remarks.

    Args:
        df (pd.DataFrame): Raw observations DataFrame.

    Returns:
        pd.Series: Continuous precipitation in mm.
    """
    rainfall = pd.Series(0.0, index=df.index, dtype=float)

    # 1. Numerical precipitation columns if available
    if "precipitation_3_hour" in df.columns:
        p3 = pd.to_numeric(df["precipitation_3_hour"], errors="coerce").fillna(0.0)
        # Convert 3-hour accumulation to estimated 30-min increment
        rainfall = np.maximum(rainfall, p3 / 6.0)

    if "precipitation_24_hour" in df.columns:
        p24 = pd.to_numeric(df["precipitation_24_hour"], errors="coerce").fillna(0.0)
        rainfall = np.maximum(rainfall, p24 / 48.0)

    # 2. Weather phenomena codes (pres_wx_MW1)
    if "pres_wx_MW1" in df.columns:
        mw1 = df["pres_wx_MW1"].astype(str).str.upper()
        # Heavy rain / thunderstorm rain
        heavy_mask = mw1.str.contains(r"RA:65|TS:95|TS:97|\+RA", regex=True)
        # Moderate rain
        mod_mask = mw1.str.contains(r"RA:63|RA:62|TS:17|TS", regex=True) & ~heavy_mask
        # Light rain
        light_mask = mw1.str.contains(r"RA:61|RA:60|RA", regex=True) & ~heavy_mask & ~mod_mask
        # Drizzle
        dz_mask = mw1.str.contains(r"DZ", regex=True)

        rainfall = np.where(heavy_mask, np.maximum(rainfall, 18.0), rainfall)
        rainfall = np.where(mod_mask, np.maximum(rainfall, 7.5), rainfall)
        rainfall = np.where(light_mask, np.maximum(rainfall, 2.5), rainfall)
        rainfall = np.where(dz_mask, np.maximum(rainfall, 0.8), rainfall)

    # 3. Text remarks (REM)
    if "REM" in df.columns:
        rem = df["REM"].astype(str).str.upper()
        rem_heavy = rem.str.contains(r"\+RA|TSRA|\+TSRA", regex=True)
        rem_mod = rem.str.contains(r"(?<!-)RA|VCTS", regex=True) & ~rem_heavy
        rem_light = rem.str.contains(r"-RA|-DZ|DZ", regex=True) & ~rem_heavy & ~rem_mod

        rainfall = np.where(rem_heavy, np.maximum(rainfall, 15.0), rainfall)
        rainfall = np.where(rem_mod, np.maximum(rainfall, 6.0), rainfall)
        rainfall = np.where(rem_light, np.maximum(rainfall, 1.8), rainfall)

    return pd.Series(rainfall, index=df.index, dtype=float).clip(lower=0.0)


def extract_and_clean_core_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts core meteorological fields and parses datatypes (Requirement 2 & 5).

    Args:
        df (pd.DataFrame): Raw observations DataFrame.

    Returns:
        pd.DataFrame: Cleaned intermediate DataFrame.
    """
    logger.info("🧹 Extracting and cleaning core meteorological columns...")

    # Timestamp extraction
    if "DATE" in df.columns:
        timestamps = pd.to_datetime(df["DATE"], errors="coerce")
    elif "timestamp" in df.columns:
        timestamps = pd.to_datetime(df["timestamp"], errors="coerce")
    else:
        raise ValueError("Missing 'DATE' or 'timestamp' column in raw dataset.")

    # Core weather variables
    temp = pd.to_numeric(df.get("temperature", np.nan), errors="coerce")
    dew_point = pd.to_numeric(df.get("dew_point_temperature", np.nan), errors="coerce")
    rh = pd.to_numeric(df.get("relative_humidity", np.nan), errors="coerce")
    wind_speed = pd.to_numeric(df.get("wind_speed", np.nan), errors="coerce")
    wind_dir = pd.to_numeric(df.get("wind_direction", np.nan), errors="coerce")

    # If relative humidity is missing, estimate from temperature and dew point
    if rh.isna().sum() > 0 and temp.notna().sum() > 0 and dew_point.notna().sum() > 0:
        # Magnus-Tetens approximation for relative humidity
        rh_approx = 100.0 * (
            np.exp((17.625 * dew_point) / (243.04 + dew_point))
            / np.exp((17.625 * temp) / (243.04 + temp))
        )
        rh = rh.fillna(rh_approx).clip(0.0, 100.0)

    # Pressure & Precipitation extraction
    pressure = extract_atmospheric_pressure(df)
    rainfall = extract_precipitation(df)

    clean_df = pd.DataFrame({
        "timestamp": timestamps,
        "location": "Bengaluru",
        "temperature": temp,
        "dew_point_temperature": dew_point,
        "relative_humidity": rh,
        "pressure": pressure,
        "wind_speed": wind_speed,
        "wind_direction": wind_dir,
        "rainfall": rainfall,
    })

    # Calendar and time components (Requirement 5)
    clean_df["year"] = clean_df["timestamp"].dt.year
    clean_df["month"] = clean_df["timestamp"].dt.month
    clean_df["day"] = clean_df["timestamp"].dt.day
    clean_df["hour"] = clean_df["timestamp"].dt.hour
    clean_df["day_of_year"] = clean_df["timestamp"].dt.dayofyear

    return clean_df


def validate_physical_bounds(df: pd.DataFrame) -> pd.DataFrame:
    """Filters out unphysical sensor values and spikes (Requirement 6).

    Bounds:
    - Temperature: [-50, 60] °C
    - Humidity: [0, 100] %
    - Pressure: [870, 1085] hPa
    - Wind Speed: [0, 120] m/s
    - Rainfall: >= 0 mm

    Args:
        df (pd.DataFrame): Intermediate DataFrame.

    Returns:
        pd.DataFrame: Bounds-validated DataFrame.
    """
    logger.info("🔬 Validating physical domain bounds...")
    validated = df.copy()

    # Temperature bounds
    t_min, t_max = PHYSICAL_BOUNDS["temperature"]
    validated.loc[(validated["temperature"] < t_min) | (validated["temperature"] > t_max), "temperature"] = np.nan

    # Humidity bounds
    rh_min, rh_max = PHYSICAL_BOUNDS["relative_humidity"]
    validated.loc[(validated["relative_humidity"] < rh_min) | (validated["relative_humidity"] > rh_max), "relative_humidity"] = np.nan

    # Pressure bounds
    p_min, p_max = PHYSICAL_BOUNDS["pressure"]
    validated.loc[(validated["pressure"] < p_min) | (validated["pressure"] > p_max), "pressure"] = np.nan

    # Wind speed bounds
    w_min, w_max = PHYSICAL_BOUNDS["wind_speed"]
    validated.loc[(validated["wind_speed"] < w_min) | (validated["wind_speed"] > w_max), "wind_speed"] = np.nan

    # Rainfall bounds
    validated["rainfall"] = validated["rainfall"].clip(lower=0.0, upper=PHYSICAL_BOUNDS["rainfall"][1])

    return validated


def impute_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Imputes missing data using forward-fill for short gaps and monthly-hourly median for larger gaps (Requirement 7).

    Guarantees zero NaN values remain in the final dataset.

    Args:
        df (pd.DataFrame): Validated DataFrame.

    Returns:
        pd.DataFrame: Fully imputed DataFrame with zero NaNs.
    """
    logger.info("🩹 Imputing missing values (gaps <= 3h: ffill; gaps > 3h: monthly-hourly median)...")
    imputed = df.copy()

    # Sort chronologically before forward-filling
    imputed = imputed.sort_values("timestamp").reset_index(drop=True)

    weather_cols = [
        "temperature",
        "dew_point_temperature",
        "relative_humidity",
        "pressure",
        "wind_speed",
        "wind_direction",
        "rainfall",
    ]

    # Step 1: Forward fill short gaps (limit=6 for 30-min data = 3 hours)
    for col in weather_cols:
        if col in imputed.columns:
            imputed[col] = imputed[col].ffill(limit=6).bfill(limit=6)

    # Step 2: Monthly-hourly median imputation for remaining gaps
    for col in weather_cols:
        if col in imputed.columns and imputed[col].isna().sum() > 0:
            medians = imputed.groupby(["month", "hour"])[col].transform("median")
            imputed[col] = imputed[col].fillna(medians)

            # Step 3: Location monthly fallback if any edge NaNs remain
            monthly_medians = imputed.groupby("month")[col].transform("median")
            imputed[col] = imputed[col].fillna(monthly_medians)

            # Step 4: Global median final safety net
            imputed[col] = imputed[col].fillna(imputed[col].median() if not np.isnan(imputed[col].median()) else 0.0)

    # Validate zero remaining NaNs
    nan_count = imputed[weather_cols].isna().sum().sum()
    logger.info(f"   Imputation complete. Total remaining NaNs across weather columns: {nan_count}")
    return imputed


def deduplicate_and_sort(df: pd.DataFrame) -> pd.DataFrame:
    """Deduplicates records on (location, timestamp) and sorts chronologically (Requirement 8).

    Args:
        df (pd.DataFrame): Imputed DataFrame.

    Returns:
        pd.DataFrame: Deduplicated and sorted DataFrame.
    """
    logger.info("🗂️ Deduplicating and sorting records chronologically...")
    clean = df.drop_duplicates(subset=["location", "timestamp"]).sort_values("timestamp").reset_index(drop=True)
    logger.info(f"   Remaining unique records: {len(clean):,}")
    return clean


def add_cyclical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes cyclical seasonal and diurnal sine/cosine encodings (Requirements 9 & 10).

    Seasonal:
        sin_day = sin(2*pi*day_of_year / 365.25)
        cos_day = cos(2*pi*day_of_year / 365.25)

    Diurnal:
        sin_hour = sin(2*pi*hour / 24.0)
        cos_hour = cos(2*pi*hour / 24.0)

    Args:
        df (pd.DataFrame): Deduplicated DataFrame.

    Returns:
        pd.DataFrame: DataFrame with cyclical features.
    """
    logger.info("🔄 Engineering cyclical temporal and diurnal features...")
    res = df.copy()

    day_of_year = res["day_of_year"].values
    hour = res["hour"].values

    # Cyclical seasonal encoding (Requirement 9)
    res["sin_day"] = np.round(np.sin(2.0 * np.pi * day_of_year / 365.25), 6)
    res["cos_day"] = np.round(np.cos(2.0 * np.pi * day_of_year / 365.25), 6)

    # Cyclical diurnal encoding (Requirement 10)
    res["sin_hour"] = np.round(np.sin(2.0 * np.pi * hour / 24.0), 6)
    res["cos_hour"] = np.round(np.cos(2.0 * np.pi * hour / 24.0), 6)

    return res


def add_rolling_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Computes 7-day and 30-day rolling statistics (Requirements 11 & 12).

    - 7-day rolling mean: temperature, pressure, relative_humidity
    - 7-day cumulative sum: rainfall
    - 30-day seasonal moving averages: temperature, pressure, relative_humidity, rainfall

    Args:
        df (pd.DataFrame): Feature-encoded DataFrame.

    Returns:
        pd.DataFrame: DataFrame with rolling statistical corridors.
    """
    logger.info("📈 Computing 7-day and 30-day rolling statistics & seasonal moving averages...")
    res = df.copy()

    # Determine typical samples per day (e.g. 48 for 30-min data, 24 for hourly)
    time_diffs = res["timestamp"].diff().dt.total_seconds().dropna()
    median_interval = time_diffs.median() if not time_diffs.empty else 1800.0
    samples_per_day = max(int(round(86400.0 / median_interval)), 1)

    window_7d = samples_per_day * 7
    window_30d = samples_per_day * 30

    # 7-day rolling statistics (Requirement 11)
    res["temp_rolling_7d"] = np.round(
        res["temperature"].rolling(window=window_7d, min_periods=1).mean(), 2
    )
    res["press_rolling_7d"] = np.round(
        res["pressure"].rolling(window=window_7d, min_periods=1).mean(), 2
    )
    res["rh_rolling_7d"] = np.round(
        res["relative_humidity"].rolling(window=window_7d, min_periods=1).mean(), 2
    )
    res["rain_rolling_7d_sum"] = np.round(
        res["rainfall"].rolling(window=window_7d, min_periods=1).sum(), 2
    )

    # 30-day seasonal moving averages (Requirement 12)
    res["temp_rolling_30d"] = np.round(
        res["temperature"].rolling(window=window_30d, min_periods=1).mean(), 2
    )
    res["press_rolling_30d"] = np.round(
        res["pressure"].rolling(window=window_30d, min_periods=1).mean(), 2
    )
    res["rh_rolling_30d"] = np.round(
        res["relative_humidity"].rolling(window=window_30d, min_periods=1).mean(), 2
    )
    res["rain_rolling_30d_sum"] = np.round(
        res["rainfall"].rolling(window=window_30d, min_periods=1).sum(), 2
    )

    return res


def preprocess_bangalore_metar(
    raw_filepath: Union[str, Path] = "data/raw/bangalore_2024_metar.csv",
    output_filepath: Union[str, Path] = "data/processed/bangalore_cleaned.csv",
) -> pd.DataFrame:
    """Executes the full Bengaluru METAR data cleaning and feature engineering pipeline (Requirement 13).

    Args:
        raw_filepath (Union[str, Path]): Path to raw input METAR CSV.
        output_filepath (Union[str, Path]): Path to save processed CSV.

    Returns:
        pd.DataFrame: Processed clean Bengaluru observations.
    """
    print("=" * 70)
    print("🚀 BENGALURU METAR PREPROCESSING PIPELINE (Member 2: Data Engineer)")
    print("=" * 70)

    # 1. Ingestion
    raw_df = load_raw_metar(raw_filepath)

    # 2. Extraction & Cleaning
    extracted_df = extract_and_clean_core_columns(raw_df)

    # 3. Physical Bounds Validation
    validated_df = validate_physical_bounds(extracted_df)

    # 4. Imputation
    imputed_df = impute_missing_values(validated_df)

    # 5. Deduplication & Sorting
    deduped_df = deduplicate_and_sort(imputed_df)

    # 6. Cyclical Temporal Encodings
    cyclical_df = add_cyclical_features(deduped_df)

    # 7. Rolling Statistics
    final_df = add_rolling_statistics(cyclical_df)

    # 8. Save Output (Requirement 13)
    out_path = Path(output_filepath)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(out_path, index=False)

    print(f"\n✅ Cleaned Bengaluru METAR observations saved to '{out_path}'")
    print(f"   Shape: {final_df.shape[0]:,} rows x {final_df.shape[1]} columns")
    print(f"   Time span: {final_df['timestamp'].min()} to {final_df['timestamp'].max()}")
    print(f"   Zero NaNs verified: {final_df.isna().sum().sum() == 0}")
    print("=" * 70)

    return final_df


def build_and_save_cleaned_dataset(
    output_path: Union[str, Path] = "data/processed/weather_cleaned.csv",
) -> pd.DataFrame:
    """Backward-compatible wrapper building the combined multi-city dataset."""
    from ml.data_generator import build_and_save_full_dataset
    return build_and_save_full_dataset(output_path=output_path)


if __name__ == "__main__":
    preprocess_bangalore_metar()

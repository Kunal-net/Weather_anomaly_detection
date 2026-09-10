"""
Historical Weather Baseline Calculator.

This module provides the `BaselineCalculator` class to compute, store, export,
and query location- and month-specific statistical baselines (mean, standard
deviation, median, IQR, percentiles, min, max) for weather observations.
These baselines serve as the historical foundation for deviation-based weather
anomaly detection.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union, cast

import numpy as np
import pandas as pd


class BaselineCalculator:
    """Calculates and manages historical weather baselines by location and month.

    The BaselineCalculator processes historical weather observations to compute
    statistical reference baselines (mean, standard deviation, median, 25th/75th
    percentiles, IQR, min, max) grouped by location and month of year. These
    baselines allow the anomaly detection engine to evaluate incoming weather
    readings against location-specific seasonal normals rather than static
    thresholds.

    Attributes:
        REQUIRED_COLUMNS (List[str]): List of column names required in the input
            DataFrame: 'location', 'month', 'temperature', 'relative_humidity',
            'pressure', 'wind_speed', 'rainfall'.
        WEATHER_FEATURES (List[str]): List of numerical weather metric columns
            used for baseline calculation.
        df (pd.DataFrame): Validated clean historical observations DataFrame.
        min_std (float): Minimum standard deviation floor to prevent division
            by zero during Z-score computations.
        baselines_df (Optional[pd.DataFrame]): Multi-indexed or flattened
            DataFrame containing calculated baseline metrics.
        baselines_dict (Dict[str, Dict[int, Dict[str, Dict[str, float]]]]):
            Nested dictionary structured as
            `{location: {month: {feature: {stat_name: value}}}}` for fast O(1)
            lookups during live inference.

    Example:
        >>> import pandas as pd
        >>> data = {
        ...     "location": ["Bengaluru", "Bengaluru"],
        ...     "month": [9, 9],
        ...     "temperature": [27.0, 28.0],
        ...     "relative_humidity": [75.0, 80.0],
        ...     "pressure": [1008.0, 1010.0],
        ...     "wind_speed": [3.5, 4.0],
        ...     "rainfall": [15.0, 20.0],
        ... }
        >>> df = pd.DataFrame(data)
        >>> calc = BaselineCalculator(df)
        >>> baseline = calc.get_baseline("Bengaluru", 9)
        >>> print(baseline["temperature"]["mean"])
        27.5
    """

    REQUIRED_COLUMNS: List[str] = [
        "location",
        "month",
        "temperature",
        "relative_humidity",
        "pressure",
        "wind_speed",
        "rainfall",
    ]

    WEATHER_FEATURES: List[str] = [
        "temperature",
        "relative_humidity",
        "pressure",
        "wind_speed",
        "rainfall",
    ]

    SIGMA_MIN: float = 0.1

    def __init__(
        self,
        df: pd.DataFrame,
        sigma_min: float = 0.1,
        min_std: Optional[float] = None,
        auto_compute: bool = True,
    ) -> None:
        """Initializes the BaselineCalculator with cleaned weather observations.

        Args:
            df (pd.DataFrame): Pandas DataFrame containing clean observations.
                Must include the columns: 'location', 'month', 'temperature',
                'relative_humidity', 'pressure', 'wind_speed', 'rainfall'.
            sigma_min (float, optional): Minimum standard deviation / variance
                threshold (sigma_min = 0.1) applied to prevent division by zero
                during Z-score calculations. Defaults to 0.1.
            min_std (Optional[float], optional): Backward-compatible alias for
                `sigma_min`. If specified, overrides `sigma_min`.
            auto_compute (bool, optional): If True, automatically computes baseline
                statistics upon initialization. Defaults to True.

        Raises:
            TypeError: If `df` is not a pandas DataFrame.
            ValueError: If `df` is empty, missing required columns, or contains
                invalid values (e.g. months outside 1-12).
        """
        self._validate_input_dataframe(df)

        self.df: pd.DataFrame = df[self.REQUIRED_COLUMNS].copy()
        effective_sigma_min = float(min_std if min_std is not None else sigma_min)
        self.sigma_min: float = max(effective_sigma_min, 1e-6)
        self.min_std: float = self.sigma_min
        self.baselines_df: Optional[pd.DataFrame] = None
        self.baselines_dict: Dict[str, Dict[int, Dict[str, Dict[str, float]]]] = {}

        if auto_compute:
            self.compute_baselines()

    def _validate_input_dataframe(self, df: Any) -> None:
        """Validates schema, nullity, and value ranges for input DataFrame.

        Args:
            df (Any): The DataFrame to validate.

        Raises:
            TypeError: If input is not a pandas DataFrame.
            ValueError: If required columns are missing, DataFrame is empty, or
                month values are out of bounds (1-12).
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                f"Expected df to be a pandas DataFrame, got {type(df).__name__} instead."
            )

        if df.empty:
            raise ValueError("Input DataFrame is empty. Cannot compute baselines.")

        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(
                f"Input DataFrame is missing required columns: {missing_cols}. "
                f"Required schema: {self.REQUIRED_COLUMNS}"
            )

        # Validate month range (1 to 12)
        invalid_months = df[~df["month"].isin(range(1, 13))]["month"].unique()
        if len(invalid_months) > 0:
            raise ValueError(
                f"Found invalid month values: {invalid_months.tolist()}. "
                f"Months must be integers between 1 and 12."
            )

        # Verify numerical features can be converted to float
        for feature in self.WEATHER_FEATURES:
            if not pd.api.types.is_numeric_dtype(df[feature]):
                try:
                    pd.to_numeric(df[feature], errors="raise")
                except Exception as exc:
                    raise ValueError(
                        f"Column '{feature}' must contain numeric data. Error: {exc}"
                    ) from exc

    def compute_baselines(self) -> pd.DataFrame:
        """Computes statistical baseline metrics grouped by [location, month].

        For each of the 5 weather variables (temperature, relative_humidity,
        pressure, wind_speed, rainfall), calculates:
        - Mean (mu)
        - Standard Deviation (sigma, floored at self.min_std)
        - Median
        - 25th percentile (q25 / p25)
        - 75th percentile (q75 / p75)
        - Interquartile Range (IQR = q75 - q25)
        - 5th percentile (p05)
        - 95th percentile (p95)
        - Min, Max, and Count

        Returns:
            pd.DataFrame: Summary DataFrame with all computed baseline records.
        """
        records: List[Dict[str, Any]] = []
        nested_dict: Dict[str, Dict[int, Dict[str, Dict[str, float]]]] = {}

        grouped = self.df.groupby(["location", "month"], observed=True)

        for (loc, month), group in grouped:
            loc_str = str(loc)
            month_int = int(month)

            if loc_str not in nested_dict:
                nested_dict[loc_str] = {}
            if month_int not in nested_dict[loc_str]:
                nested_dict[loc_str][month_int] = {}

            for feature in self.WEATHER_FEATURES:
                series = group[feature].dropna()

                if series.empty:
                    mean_val = 0.0
                    std_val = self.min_std
                    median_val = 0.0
                    q25_val = 0.0
                    q75_val = 0.0
                    iqr_val = 0.0
                    p05_val = 0.0
                    p95_val = 0.0
                    min_val = 0.0
                    max_val = 0.0
                    count_val = 0
                else:
                    mean_val = float(series.mean())
                    std_calc = float(series.std(ddof=1)) if len(series) > 1 else 0.0
                    std_val = float(max(std_calc, self.min_std)) if not np.isnan(std_calc) else self.min_std
                    median_val = float(series.median())
                    q25_val = float(series.quantile(0.25))
                    q75_val = float(series.quantile(0.75))
                    iqr_val = float(max(q75_val - q25_val, 0.0))
                    p05_val = float(series.quantile(0.05))
                    p95_val = float(series.quantile(0.95))
                    min_val = float(series.min())
                    max_val = float(series.max())
                    count_val = int(len(series))

                stat_dict: Dict[str, float] = {
                    "mean": mean_val,
                    "mu": mean_val,
                    "std": std_val,
                    "sigma": std_val,
                    "median": median_val,
                    "q25": q25_val,
                    "p25": q25_val,
                    "q75": q75_val,
                    "p75": q75_val,
                    "iqr": iqr_val,
                    "p05": p05_val,
                    "p95": p95_val,
                    "min": min_val,
                    "max": max_val,
                    "count": float(count_val),
                }

                nested_dict[loc_str][month_int][feature] = stat_dict

                record: Dict[str, Any] = {
                    "location": loc_str,
                    "month": month_int,
                    "feature": feature,
                    **stat_dict,
                }
                records.append(record)

        self.baselines_dict = nested_dict
        self.baselines_df = pd.DataFrame(records)
        return self.baselines_df

    def get_baseline(
        self, location: str, month: int
    ) -> Dict[str, Dict[str, float]]:
        """Retrieves precomputed baseline statistics for a location and month.

        Args:
            location (str): Location identifier (e.g. 'Bengaluru', 'Delhi').
            month (int): Month of the year (1 to 12).

        Returns:
            Dict[str, Dict[str, float]]: Mapping of weather features to their
                statistical baselines (mean, std, median, q25, q75, iqr, min, max, count).

        Raises:
            ValueError: If the location is unknown, month is not found, or
                baselines have not been computed yet.
        """
        if not self.baselines_dict:
            raise ValueError(
                "Baselines have not been computed. Call compute_baselines() first."
            )

        loc_str = str(location)
        if loc_str not in self.baselines_dict:
            available_locs = list(self.baselines_dict.keys())
            raise ValueError(
                f"Unknown location '{loc_str}'. Available locations: {available_locs}"
            )

        month_int = int(month)
        if month_int not in self.baselines_dict[loc_str]:
            available_months = sorted(self.baselines_dict[loc_str].keys())
            raise ValueError(
                f"Month {month_int} not found for location '{loc_str}'. "
                f"Available months: {available_months}"
            )

        return self.baselines_dict[loc_str][month_int]

    def calculate_z_scores(
        self,
        observation: Dict[str, float],
        location: str,
        month: int,
    ) -> Dict[str, float]:
        """Calculates standardized Z-scores for an observation against baseline.

        For each weather feature:
            Z = (observed_value - expected_mean) / expected_std

        Args:
            observation (Dict[str, float]): Dictionary mapping weather feature
                names to numeric observed values.
            location (str): Observation location.
            month (int): Observation month (1 to 12).

        Returns:
            Dict[str, float]: Dictionary of feature names mapped to their Z-scores.
        """
        baseline = self.get_baseline(location, month)
        z_scores: Dict[str, float] = {}

        for feature in self.WEATHER_FEATURES:
            if feature in observation and observation[feature] is not None:
                val = float(observation[feature])
                mean = baseline[feature]["mean"]
                std = max(baseline[feature]["std"], self.min_std)
                z_scores[feature] = float((val - mean) / std)

        return z_scores

    def calculate_deviations(
        self,
        observation: Dict[str, float],
        location: str,
        month: int,
    ) -> Dict[str, Dict[str, float]]:
        """Calculates comprehensive deviation metrics for an observation.

        Computes observed value, baseline expected mean, absolute departure,
        percentage departure, and standardized Z-score for each feature.

        Args:
            observation (Dict[str, float]): Dictionary of observed weather values.
            location (str): Observation location.
            month (int): Observation month (1 to 12).

        Returns:
            Dict[str, Dict[str, float]]: Mapping of each feature to a detailed
                deviation dictionary containing:
                - 'observed': Observed value
                - 'expected': Historical mean
                - 'std': Historical standard deviation
                - 'departure': Observed - Expected
                - 'pct_departure': Percentage change relative to mean (if mean != 0)
                - 'z_score': Standardized Z-score
        """
        baseline = self.get_baseline(location, month)
        deviations: Dict[str, Dict[str, float]] = {}

        for feature in self.WEATHER_FEATURES:
            if feature in observation and observation[feature] is not None:
                observed_val = float(observation[feature])
                mean_val = baseline[feature]["mean"]
                std_val = max(baseline[feature]["std"], self.min_std)
                departure = observed_val - mean_val
                pct_dep = (departure / abs(mean_val) * 100.0) if mean_val != 0.0 else 0.0
                z_val = departure / std_val

                deviations[feature] = {
                    "observed": observed_val,
                    "expected": mean_val,
                    "std": std_val,
                    "departure": departure,
                    "pct_departure": pct_dep,
                    "z_score": z_val,
                }

        return deviations

    def get_available_locations(self) -> List[str]:
        """Returns a sorted list of all locations present in baselines.

        Returns:
            List[str]: Sorted list of location names.
        """
        return sorted(self.baselines_dict.keys())

    def get_available_months(self, location: Optional[str] = None) -> List[int]:
        """Returns available months, optionally filtered for a specific location.

        Args:
            location (Optional[str], optional): Specific location name.
                If None, returns all months available across all locations.

        Returns:
            List[int]: Sorted list of month integers (1 to 12).
        """
        if location is not None:
            loc_str = str(location)
            if loc_str in self.baselines_dict:
                return sorted(self.baselines_dict[loc_str].keys())
            return []

        all_months: set[int] = set()
        for loc_data in self.baselines_dict.values():
            all_months.update(loc_data.keys())
        return sorted(all_months)

    def to_dict(self) -> Dict[str, Any]:
        """Exports baseline statistics as a JSON-serializable dictionary.

        Returns:
            Dict[str, Any]: Nested dictionary formatted as
                `{location: {month_str: {feature: {stat: value}}}}`.
        """
        # Convert month integer keys to strings for clean JSON serialization
        serialized: Dict[str, Any] = {}
        for loc, months_dict in self.baselines_dict.items():
            serialized[loc] = {}
            for month, features_dict in months_dict.items():
                serialized[loc][str(month)] = features_dict
        return serialized

    def to_dataframe(self) -> pd.DataFrame:
        """Returns baseline statistics as a flattened DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing all computed baseline records.
        """
        if self.baselines_df is None:
            self.compute_baselines()
        return cast(pd.DataFrame, self.baselines_df).copy()

    DEFAULT_BASELINE_PATH: Path = Path("data/processed/baseline_statistics.json")

    def save_to_json(
        self, filepath: Union[str, Path] = DEFAULT_BASELINE_PATH
    ) -> None:
        """Saves precomputed baseline statistics to a JSON file.

        Args:
            filepath (Union[str, Path], optional): Destination file path.
                Defaults to 'data/processed/baseline_statistics.json'.
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_dict(
        cls,
        baselines_dict: Dict[str, Any],
        sigma_min: float = 0.1,
    ) -> BaselineCalculator:
        """Creates a BaselineCalculator instance from precomputed dictionary.

        Args:
            baselines_dict (Dict[str, Any]): Dictionary of baseline statistics.
            sigma_min (float, optional): Epsilon / minimum variance floor for
                standard deviation (sigma_min = 0.1). Defaults to 0.1.

        Returns:
            BaselineCalculator: Instantiated calculator with loaded baselines.
        """
        # Create minimal placeholder dataframe to satisfy init validation
        dummy_df = pd.DataFrame(
            {
                "location": ["dummy"],
                "month": [1],
                "temperature": [0.0],
                "relative_humidity": [0.0],
                "pressure": [1000.0],
                "wind_speed": [0.0],
                "rainfall": [0.0],
            }
        )
        instance = cls(dummy_df, sigma_min=sigma_min, auto_compute=False)

        parsed_dict: Dict[str, Dict[int, Dict[str, Dict[str, float]]]] = {}
        records: List[Dict[str, Any]] = []

        for loc, months_data in baselines_dict.items():
            parsed_dict[str(loc)] = {}
            for month_key, features_data in months_data.items():
                month_int = int(month_key)
                parsed_dict[str(loc)][month_int] = {}
                for feature, stats in features_data.items():
                    parsed_dict[str(loc)][month_int][feature] = dict(stats)
                    records.append(
                        {
                            "location": str(loc),
                            "month": month_int,
                            "feature": feature,
                            **stats,
                        }
                    )

        instance.baselines_dict = parsed_dict
        instance.baselines_df = pd.DataFrame(records)
        return instance

    @classmethod
    def load_from_json(
        cls,
        filepath: Union[str, Path] = DEFAULT_BASELINE_PATH,
        sigma_min: float = 0.1,
    ) -> BaselineCalculator:
        """Loads precomputed baselines from a JSON file for O(1) in-memory lookup.

        Args:
            filepath (Union[str, Path], optional): Path to JSON file containing
                precomputed baselines. Defaults to 'data/processed/baseline_statistics.json'.
            sigma_min (float, optional): Minimum standard deviation floor
                (sigma_min = 0.1). Defaults to 0.1.

        Returns:
            BaselineCalculator: Calculator initialized with the saved baselines.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Baseline JSON file not found at: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data, sigma_min=sigma_min)

    from_json = load_from_json


def compute_baseline_table(
    df: pd.DataFrame, sigma_min: float = 0.1
) -> BaselineCalculator:
    """Convenience factory function to compute and return a BaselineCalculator.

    Args:
        df (pd.DataFrame): Clean weather observations DataFrame.
        sigma_min (float, optional): Minimum standard deviation / variance
            threshold (sigma_min = 0.1). Defaults to 0.1.

    Returns:
        BaselineCalculator: Initialized and computed BaselineCalculator.
    """
    return BaselineCalculator(df, sigma_min=sigma_min, auto_compute=True)


_CACHED_BASELINE_CALCULATOR: Optional[BaselineCalculator] = None


def get_baseline(
    location: str,
    month: int,
    filepath: Union[str, Path] = BaselineCalculator.DEFAULT_BASELINE_PATH,
    sigma_min: float = 0.1,
) -> Dict[str, Dict[str, float]]:
    """Helper function that returns baseline stats for a given location and month.

    Queries precomputed baselines stored in JSON for sub-millisecond lookup,
    raising a clean ValueError if the location or month is unknown.

    Args:
        location (str): Name of location (e.g. 'Bengaluru', 'Delhi').
        month (int): Month integer (1-12).
        filepath (Union[str, Path], optional): Path to baseline JSON file.
            Defaults to 'data/processed/baseline_statistics.json'.
        sigma_min (float, optional): Minimum standard deviation floor. Defaults to 0.1.

    Returns:
        Dict[str, Dict[str, float]]: Mapping of weather features to statistical
            baseline parameters (mean, std, median, q25, q75, iqr, p05, p95, min, max, count).

    Raises:
        ValueError: If the location is unknown, month is not found, or month is invalid.
        FileNotFoundError: If the baseline JSON file does not exist.
    """
    global _CACHED_BASELINE_CALCULATOR
    if _CACHED_BASELINE_CALCULATOR is None:
        _CACHED_BASELINE_CALCULATOR = BaselineCalculator.load_from_json(
            filepath=filepath, sigma_min=sigma_min
        )

    return _CACHED_BASELINE_CALCULATOR.get_baseline(location, month)


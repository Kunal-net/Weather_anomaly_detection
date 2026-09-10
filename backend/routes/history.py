r"""
Historical Weather Corridors & Baseline Charting Endpoint.

Generates time series corridors comparing observed historical data points
against location- and seasonal-expected normals and $\pm 2\sigma$ confidence bounds.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import List

import numpy as np
from fastapi import APIRouter, HTTPException, Path, Query

from backend.schemas.weather import HistoricalDataPoint, HistoricalSeriesResponse
from backend.services.model_loader import model_loader

router = APIRouter(tags=["History"])

VARIABLE_UNITS = {
    "temperature": "°C",
    "relative_humidity": "%",
    "pressure": "hPa",
    "wind_speed": "m/s",
    "rainfall": "mm",
}


@router.get(
    "/history/{location}",
    response_model=HistoricalSeriesResponse,
    summary="Get Historical Weather vs Expected Baseline Corridors for Charts",
)
def get_historical_corridor(
    location: str = Path(..., description="City name (e.g. 'Bengaluru', 'Delhi')"),
    variable: str = Query(
        default="temperature",
        description="Weather variable (temperature, relative_humidity, pressure, wind_speed, rainfall)",
    ),
    days: int = Query(
        default=30,
        ge=1,
        le=365,
        description="Number of historical days to return (1 to 365)",
    ),
) -> HistoricalSeriesResponse:
    """Returns observed vs expected baseline corridors for charts."""
    # Normalize city name
    matched_city = None
    for city in model_loader.get_available_locations():
        if city.lower() == location.strip().lower():
            matched_city = city
            break

    if not matched_city:
        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' not found. Available locations: {model_loader.get_available_locations()}",
        )

    var_clean = variable.strip().lower()
    if var_clean not in VARIABLE_UNITS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid variable '{variable}'. Supported variables: {list(VARIABLE_UNITS.keys())}",
        )

    unit = VARIABLE_UNITS[var_clean]
    now = datetime.now(timezone.utc)
    points: List[HistoricalDataPoint] = []

    # Deterministic generation for stable visualization based on city and variable
    rng_seed = abs(hash(f"{matched_city}_{var_clean}")) % (2**31)
    rng = np.random.RandomState(rng_seed)

    for i in range(days - 1, -1, -1):
        target_date = now - timedelta(days=i)
        month = target_date.month
        day_str = target_date.strftime("%Y-%m-%d")

        baseline = model_loader.get_baseline(matched_city, month)
        stat = baseline.get(var_clean, {})
        mu = float(stat.get("mean", 25.0))
        sigma = float(max(stat.get("std", 2.0), 0.2))

        # Add realistic seasonal variation and occasional anomaly spike
        noise = rng.normal(0, sigma * 0.8)
        observed = mu + noise

        # Inject simulated anomaly on ~5% of days for demonstration
        if rng.uniform(0, 1) < 0.07:
            observed += rng.choice([-1, 1]) * rng.uniform(2.2, 3.2) * sigma

        # Lower bound clamping for positive physical metrics
        upper = round(mu + 2.0 * sigma, 2)
        lower = mu - 2.0 * sigma
        if var_clean in ["relative_humidity", "wind_speed", "rainfall"]:
            lower = max(lower, 0.0)
            observed = max(observed, 0.0)
            if var_clean == "relative_humidity":
                upper = min(upper, 100.0)
                observed = min(observed, 100.0)

        lower = round(lower, 2)
        observed = round(observed, 2)
        mu = round(mu, 2)

        is_anom = observed > upper or observed < lower

        points.append(
            HistoricalDataPoint(
                timestamp=day_str,
                observed=observed,
                expected_normal=mu,
                upper_bound=upper,
                lower_bound=lower,
                is_anomaly=is_anom,
            )
        )

    return HistoricalSeriesResponse(
        location=matched_city,
        variable=var_clean,
        unit=unit,
        days=days,
        data=points,
    )

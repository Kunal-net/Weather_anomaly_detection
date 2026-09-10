"""
Pydantic v2 Schemas for Weather Anomaly Detection & Monitoring Platform.

Implements typed, validated request and response schemas for prediction,
explainability contributors, historical corridors, location summaries, and health checks.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class PredictionRequest(BaseModel):
    """Weather observation payload for anomaly evaluation with physical bounds validation (Prompt 3.2)."""

    location: str = Field(
        ...,
        description="Monitored station or city name (e.g. 'Bengaluru', 'Delhi')",
        examples=["Bengaluru"],
    )
    month: Optional[int] = Field(
        default=None,
        description="Month of the observation (1 to 12). If omitted, inferred from current date.",
        examples=[9],
    )
    temperature: float = Field(
        ...,
        description="Air temperature in degrees Celsius (°C). Valid range: -50.0 to 65.0",
        examples=[27.5],
    )
    relative_humidity: float = Field(
        ...,
        description="Relative humidity percentage (%). Valid range: 0.0 to 100.0",
        examples=[75.0],
    )
    pressure: float = Field(
        ...,
        description="Atmospheric sea-level or station pressure in hPa. Valid range: 870.0 to 1085.0",
        examples=[1008.5],
    )
    wind_speed: float = Field(
        ...,
        description="Sustained wind speed in m/s. Valid range: 0.0 to 120.0",
        examples=[4.2],
    )
    rainfall: float = Field(
        ...,
        description="Precipitation accumulation in mm. Valid range: 0.0 to 1500.0",
        examples=[12.0],
    )

    # Physical domain bounds validators
    @field_validator("location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        loc = v.strip()
        if not loc:
            raise ValueError("Location name cannot be empty.")
        return loc

    @field_validator("month")
    @classmethod
    def validate_month(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (1 <= v <= 12):
            raise ValueError(f"Month must be an integer between 1 and 12, got {v}")
        return v

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not (-50.0 <= v <= 65.0):
            raise ValueError(
                f"Temperature {v}°C violates physical domain bounds [-50.0, 65.0]°C."
            )
        return round(float(v), 2)

    @field_validator("relative_humidity")
    @classmethod
    def validate_humidity(cls, v: float) -> float:
        if not (0.0 <= v <= 100.0):
            raise ValueError(
                f"Relative humidity {v}% violates physical domain bounds [0.0, 100.0]%."
            )
        return round(float(v), 2)

    @field_validator("pressure")
    @classmethod
    def validate_pressure(cls, v: float) -> float:
        if not (870.0 <= v <= 1085.0):
            raise ValueError(
                f"Atmospheric pressure {v} hPa violates physical domain bounds [870.0, 1085.0] hPa."
            )
        return round(float(v), 2)

    @field_validator("wind_speed")
    @classmethod
    def validate_wind(cls, v: float) -> float:
        if not (0.0 <= v <= 120.0):
            raise ValueError(
                f"Wind speed {v} m/s violates physical domain bounds [0.0, 120.0] m/s."
            )
        return round(float(v), 2)

    @field_validator("rainfall")
    @classmethod
    def validate_rain(cls, v: float) -> float:
        if not (0.0 <= v <= 1500.0):
            raise ValueError(
                f"Rainfall {v} mm violates physical domain bounds [0.0, 1500.0] mm."
            )
        return round(float(v), 2)


class ContributorItem(BaseModel):
    """Ranked meteorological contributor explaining an anomaly (Prompt 3.3)."""

    feature: str = Field(..., description="Weather variable name (e.g. 'rainfall', 'temperature')")
    contribution_pct: float = Field(..., description="Percentage contribution to anomaly score (0-100%)")
    observed: float = Field(..., description="Observed weather value")
    expected: float = Field(..., description="Expected historical baseline normal (mean)")
    unit: str = Field(..., description="Unit of measurement (°C, mm, hPa, m/s, %)")
    direction: str = Field(..., description="Deviation direction: 'HIGH' or 'LOW'")
    departure: Optional[float] = Field(default=None, description="Absolute difference: observed - expected")
    pct_departure: Optional[float] = Field(default=None, description="Percentage departure relative to expected")
    z_score: Optional[float] = Field(default=None, description="Standardized Z-score deviation")


class PredictionResponse(BaseModel):
    """Complete anomaly prediction response with explainability (Prompt 3.4)."""

    location: str = Field(..., description="Location evaluated")
    timestamp: str = Field(..., description="ISO timestamp of observation")
    is_anomaly: bool = Field(..., description="True if anomaly_score >= 0.40")
    anomaly_score: float = Field(..., description="Calibrated anomaly score in [0.00, 1.00]")
    severity: str = Field(..., description="Severity classification: NORMAL, WATCH, HIGH, CRITICAL")
    anomaly_type: str = Field(..., description="Meteorological classification (e.g. 'Extreme Rainfall', 'Heat Wave')")
    contributors: List[ContributorItem] = Field(..., description="Ranked list of top meteorological contributors")
    explanation: str = Field(..., description="Human-readable diagnostic explanation sentence")
    statistical_score: Optional[float] = Field(default=None, description="Layer 1 Statistical Z-Score score")
    ml_score: Optional[float] = Field(default=None, description="Layer 2 Isolation Forest score")
    processing_time_ms: Optional[float] = Field(default=None, description="Inference latency in milliseconds")


class LocationInfo(BaseModel):
    """Monitored station / Indian city metadata and current status (Prompt 3.5 & 3.15)."""

    city: str = Field(..., description="City / Station name")
    lat: float = Field(..., description="Latitude coordinate")
    lon: float = Field(..., description="Longitude coordinate")
    state: str = Field(..., description="Indian State or Union Territory")
    elevation: Optional[float] = Field(default=None, description="Elevation in meters above sea level")
    current_severity: str = Field(..., description="Active severity tier: NORMAL, WATCH, HIGH, CRITICAL")
    current_score: float = Field(..., description="Current anomaly score [0.00, 1.00]")
    current_anomaly_score: Optional[float] = Field(default=None, description="Alias for current_score")
    active_severity_level: Optional[str] = Field(default=None, description="Alias for current_severity")
    temperature: Optional[float] = Field(default=None, description="Latest temperature in °C")
    relative_humidity: Optional[float] = Field(default=None, description="Latest relative humidity in %")
    pressure: Optional[float] = Field(default=None, description="Latest pressure in hPa")
    wind_speed: Optional[float] = Field(default=None, description="Latest wind speed in m/s")
    rainfall: Optional[float] = Field(default=None, description="Latest rainfall in mm")

    # Dual alias compatibility for frontend components
    location: Optional[str] = Field(default=None, description="Alias for city")
    severity: Optional[str] = Field(default=None, description="Alias for current_severity")
    anomaly_score: Optional[float] = Field(default=None, description="Alias for current_score")

    @model_validator(mode="after")
    def populate_aliases(self) -> LocationInfo:
        if self.location is None:
            self.location = self.city
        if self.severity is None:
            self.severity = self.current_severity
        if self.anomaly_score is None:
            self.anomaly_score = self.current_score
        if self.current_anomaly_score is None:
            self.current_anomaly_score = self.current_score
        if self.active_severity_level is None:
            self.active_severity_level = self.current_severity
        return self


class HistoricalDataPoint(BaseModel):
    """Historical time series point with baseline normal and corridor bounds (Prompt 3.5 & 3.18)."""

    timestamp: str = Field(..., description="ISO date or timestamp")
    observed: float = Field(..., description="Observed weather value")
    expected_normal: float = Field(..., description="Expected seasonal baseline mean (mu)")
    upper_bound: float = Field(..., description="Upper baseline corridor bound (mu + 2*sigma)")
    lower_bound: float = Field(..., description="Lower baseline corridor bound (mu - 2*sigma)")
    is_anomaly: Optional[bool] = Field(default=False, description="True if observed falls outside corridor")


class HistoricalSeriesResponse(BaseModel):
    """Historical corridor data series response for charts (Prompt 3.18)."""

    location: str = Field(..., description="City or station name")
    variable: str = Field(..., description="Weather variable (temperature, rainfall, pressure, wind_speed, relative_humidity)")
    unit: str = Field(..., description="Unit of measurement")
    days: int = Field(..., description="Number of historical days")
    data: List[HistoricalDataPoint] = Field(..., description="Time series points")


class WeatherSummaryResponse(BaseModel):
    """Latest city weather observation with seasonal normal comparison (Prompt 3.16)."""

    location: str = Field(..., description="City name")
    city: Optional[str] = Field(default=None, description="Alias for location")
    timestamp: str = Field(..., description="ISO observation timestamp")
    month: int = Field(..., description="Observation month")
    observed: Dict[str, float] = Field(..., description="Latest weather readings")
    expected_normals: Dict[str, float] = Field(..., description="Historical seasonal normals (means)")
    departures: Dict[str, float] = Field(..., description="Absolute departures (observed - expected)")
    percentage_departures: Dict[str, float] = Field(..., description="Percentage departures relative to normal")
    current_anomaly_score: float = Field(..., description="Current anomaly score")
    anomaly_score: Optional[float] = Field(default=None, description="Alias for current_anomaly_score")
    current_severity: str = Field(..., description="Current severity level")
    severity: Optional[str] = Field(default=None, description="Alias for current_severity")
    anomaly_type: str = Field(..., description="Current anomaly type")
    explanation: str = Field(..., description="Diagnostic summary")

    @model_validator(mode="after")
    def populate_aliases(self) -> WeatherSummaryResponse:
        if self.city is None:
            self.city = self.location
        if self.severity is None:
            self.severity = self.current_severity
        if self.anomaly_score is None:
            self.anomaly_score = self.current_anomaly_score
        return self


class AnomalyEventResponse(BaseModel):
    """Historical anomaly log entry (Prompt 3.9 & 3.17)."""

    id: int = Field(..., description="Unique event identifier")
    location: str = Field(..., description="City name")
    city: Optional[str] = Field(default=None, description="Alias for location")
    timestamp: str = Field(..., description="Timestamp of event occurrence")
    anomaly_score: float = Field(..., description="Anomaly score [0.00, 1.00]")
    current_score: Optional[float] = Field(default=None, description="Alias for anomaly_score")
    severity: str = Field(..., description="Severity tier")
    current_severity: Optional[str] = Field(default=None, description="Alias for severity")
    anomaly_type: str = Field(..., description="Anomaly classification")
    contributors: List[ContributorItem] = Field(default_factory=list, description="Top contributors")
    explanation: str = Field(..., description="Natural language diagnostic explanation")
    created_at: str = Field(..., description="Database record creation timestamp")

    @model_validator(mode="after")
    def populate_aliases(self) -> AnomalyEventResponse:
        if self.city is None:
            self.city = self.location
        if self.current_severity is None:
            self.current_severity = self.severity
        if self.current_score is None:
            self.current_score = self.anomaly_score
        return self


class HealthResponse(BaseModel):
    """System health and operational readiness status (Prompt 3.14)."""

    status: str = Field(..., description="Operational status ('ok' or 'degraded')")
    model_loaded: bool = Field(..., description="True if ML model and baseline statistics are loaded")
    database_connectivity: bool = Field(..., description="True if database connection is functional")
    version: str = Field(..., description="Backend API version")
    timestamp: str = Field(..., description="Current server ISO timestamp")
    active_engine: Optional[str] = Field(default=None, description="Anomaly engine type")

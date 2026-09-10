"""
Explainability Engine for Weather Anomaly Detection.

This module provides transparent, human-understandable diagnostic reasoning
for weather anomalies, quantifying individual variable contributions, absolute
and percentage departures, and natural language executive summaries for disaster managers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union


class ExplainabilityEngine:
    """Computes transparent feature contributions and natural language summaries.

    Attributes:
        UNITS (Dict[str, str]): Measurement units for each weather feature.
        FRIENDLY_NAMES (Dict[str, str]): Human-readable feature names.
    """

    UNITS: Dict[str, str] = {
        "temperature": "°C",
        "relative_humidity": "%",
        "pressure": "hPa",
        "wind_speed": "m/s",
        "rainfall": "mm",
    }

    FRIENDLY_NAMES: Dict[str, str] = {
        "temperature": "Temperature",
        "relative_humidity": "Relative Humidity",
        "pressure": "Atmospheric Pressure",
        "wind_speed": "Wind Speed",
        "rainfall": "Rainfall",
    }

    def __init__(self) -> None:
        """Initializes the ExplainabilityEngine."""
        pass

    def compute_feature_contributions(
        self,
        z_scores: Dict[str, float],
        obs: Optional[Dict[str, Any]] = None,
        base: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> List[Dict[str, Any]]:
        """Calculates relative feature contributions and formats contributor objects (Prompts 1.16, 1.17).

        Formula:
            Contrib_i = (|Z_i| / sum(|Z_j|)) * 100

        Ranked in descending order of contribution percentage.

        Formatted fields per contributor (Prompt 1.17):
            - feature (str): Feature name (e.g. 'rainfall')
            - contribution_pct (float): Relative percentage contribution
            - observed (float): Observed weather value
            - expected (float): Expected historical baseline normal (mean)
            - unit (str): Measurement unit ('°C', 'mm', 'hPa', etc.)
            - direction (str): 'HIGH' or 'LOW'
            - departure (float): Observed - Expected
            - pct_departure (float): Percentage change relative to normal
            - z_score (float): Standardized Z-score

        Args:
            z_scores (Dict[str, float]): Dictionary of Z-scores per feature.
            obs (Optional[Dict[str, Any]], optional): Observed weather readings.
            base (Optional[Dict[str, Dict[str, float]]], optional): Baseline statistics.

        Returns:
            List[Dict[str, Any]]: Ranked list of contributor dictionaries.
        """
        if not z_scores:
            return []

        # Sum of absolute Z-scores
        total_abs_z = sum(abs(float(z)) for z in z_scores.values())
        contributors: List[Dict[str, Any]] = []

        for feature, z in z_scores.items():
            z_val = float(z)
            abs_z = abs(z_val)

            # Contrib_i = (|Z_i| / sum(|Z_j|)) * 100
            if total_abs_z > 0.0:
                contrib_pct = (abs_z / total_abs_z) * 100.0
            else:
                contrib_pct = 100.0 / max(len(z_scores), 1)

            unit = self.UNITS.get(feature, "")
            direction = "HIGH" if z_val >= 0.0 else "LOW"

            # Retrieve observed and expected if provided
            observed_val = float(obs.get(feature, 0.0)) if obs and feature in obs and obs[feature] is not None else 0.0
            expected_val = 0.0
            if base and feature in base and isinstance(base[feature], dict):
                expected_val = float(base[feature].get("mean", base[feature].get("mu", 0.0)))

            departure = observed_val - expected_val
            pct_departure = (departure / abs(expected_val) * 100.0) if expected_val != 0.0 else 0.0

            contributor = {
                "feature": feature,
                "contribution_pct": round(contrib_pct, 1),
                "observed": round(observed_val, 2),
                "expected": round(expected_val, 2),
                "unit": unit,
                "direction": direction,
                "departure": round(departure, 2),
                "pct_departure": round(pct_departure, 1),
                "z_score": round(z_val, 2),
            }
            contributors.append(contributor)

        # Rank in descending order of contribution percentage (Prompt 1.16)
        contributors.sort(key=lambda item: item["contribution_pct"], reverse=True)
        return contributors

    def generate_natural_language_summary(
        self,
        severity: str,
        anomaly_type: str,
        contributors: List[Dict[str, Any]],
        location: Optional[str] = None,
        month_name: Optional[str] = None,
    ) -> str:
        """Generates natural language diagnostic summary for disaster managers (Prompt 1.18).

        Produces clear, actionable explanations detailing top meteorological drivers,
        departures from seasonal baseline, and potential hazard implications.

        Args:
            severity (str): Severity classification ('NORMAL', 'WATCH', 'HIGH', 'CRITICAL').
            anomaly_type (str): Specific anomaly type (e.g. 'Extreme Rainfall', 'Heat Wave').
            contributors (List[Dict[str, Any]]): Ranked list of contributor objects.
            location (Optional[str], optional): City or station name.
            month_name (Optional[str], optional): Month name string.

        Returns:
            str: Diagnostic explanation sentence.
        """
        loc_str = f" in {location}" if location else ""
        month_str = f" ({month_name} baseline)" if month_name else " seasonal baseline"

        if severity == "NORMAL" or not contributors or (len(contributors) > 0 and abs(contributors[0]["z_score"]) < 1.5):
            return f"Weather conditions{loc_str} are behaving within normal seasonal variation ({severity}) with no significant meteorological departures."

        top_drivers: List[str] = []
        for c in contributors[:3]:
            # Only mention drivers with noticeable departure
            if abs(c["z_score"]) < 1.0 and len(top_drivers) > 0:
                continue

            feat_name = self.FRIENDLY_NAMES.get(c["feature"], c["feature"])
            unit = c["unit"]
            obs = c["observed"]
            exp = c["expected"]
            pct = c["pct_departure"]
            z = c["z_score"]

            if c["feature"] == "rainfall":
                if pct > 0:
                    top_drivers.append(
                        f"Rainfall is {pct:+.0f}% above normal ({obs:.1f}{unit} observed vs {exp:.1f}{unit} normal, Z={z:+.1f})"
                    )
                else:
                    top_drivers.append(
                        f"Rainfall deficit of {abs(pct):.0f}% ({obs:.1f}{unit} observed vs {exp:.1f}{unit} normal)"
                    )
            elif c["feature"] == "temperature":
                top_drivers.append(
                    f"{feat_name} departure of {c['departure']:+.1f}{unit} ({obs:.1f}{unit} observed vs {exp:.1f}{unit} normal, Z={z:+.1f})"
                )
            elif c["feature"] == "pressure":
                top_drivers.append(
                    f"Atmospheric Pressure departure of {c['departure']:+.1f}{unit} ({obs:.1f}{unit} vs {exp:.1f}{unit} normal, Z={z:+.1f})"
                )
            else:
                top_drivers.append(
                    f"{feat_name} of {obs:.1f}{unit} ({pct:+.0f}% departure vs normal, Z={z:+.1f})"
                )

        drivers_text = "; ".join(top_drivers)

        if severity == "CRITICAL":
            return (
                f"CRITICAL ALERT{loc_str}: Severe {anomaly_type} detected relative to{month_str}. "
                f"Primary drivers: {drivers_text}."
            )
        elif severity == "HIGH":
            return (
                f"HIGH ADVISORY{loc_str}: Significant {anomaly_type} departing from{month_str}. "
                f"Primary drivers: {drivers_text}."
            )
        elif severity == "WATCH":
            return (
                f"WATCH MONITORING{loc_str}: Noticeable {anomaly_type} observed relative to{month_str}. "
                f"Primary drivers: {drivers_text}."
            )
        else:
            return (
                f"NORMAL{loc_str}: Weather readings are within expected limits. "
                f"Minor variations: {drivers_text}."
            )

    def explain(
        self,
        z_scores: Dict[str, float],
        severity: str,
        anomaly_type: str,
        obs: Optional[Dict[str, Any]] = None,
        base: Optional[Dict[str, Dict[str, float]]] = None,
        location: Optional[str] = None,
        month: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Comprehensive explainability payload generator.

        Returns:
            Dict[str, Any]: Dictionary containing 'contributors' and 'explanation'.
        """
        month_names = [
            "", "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        m_name = month_names[month] if month and 1 <= month <= 12 else None

        contributors = self.compute_feature_contributions(z_scores, obs=obs, base=base)
        summary = self.generate_natural_language_summary(
            severity=severity,
            anomaly_type=anomaly_type,
            contributors=contributors,
            location=location,
            month_name=m_name,
        )

        return {
            "contributors": contributors,
            "explanation": summary,
        }

"""
Explanation Service for Weather Anomaly Diagnostic Reasoning.

Calculates individual feature percentage contributions, percentage and absolute departures,
and generates natural language diagnostic rationale for disaster management operators.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from backend.schemas.weather import ContributorItem
from ml.explainability import ExplainabilityEngine


class ExplanationService:
    """Service layer for computing anomaly explainability and diagnostic narratives."""

    def __init__(self) -> None:
        self.engine = ExplainabilityEngine()

    def compute_contributors(
        self,
        z_scores: Dict[str, float],
        observation: Dict[str, Any],
        baseline: Dict[str, Dict[str, float]],
    ) -> List[ContributorItem]:
        """Calculates relative feature percentage contributions and formats ContributorItem schemas.

        Formula:
            Contribution_i = (|Z_i| / sum(|Z_j|)) * 100
        """
        raw_contributors = self.engine.compute_feature_contributions(
            z_scores=z_scores,
            obs=observation,
            base=baseline,
        )

        items: List[ContributorItem] = []
        for item in raw_contributors:
            items.append(
                ContributorItem(
                    feature=item["feature"],
                    contribution_pct=float(item["contribution_pct"]),
                    observed=float(item["observed"]),
                    expected=float(item["expected"]),
                    unit=str(item["unit"]),
                    direction=str(item["direction"]),
                    departure=float(item.get("departure", 0.0)),
                    pct_departure=float(item.get("pct_departure", 0.0)),
                    z_score=float(item.get("z_score", 0.0)),
                )
            )
        return items

    def generate_explanation(
        self,
        severity: str,
        anomaly_type: str,
        contributors: List[ContributorItem],
        location: Optional[str] = None,
        month: Optional[int] = None,
    ) -> str:
        """Constructs a natural language diagnostic sentence."""
        month_names = [
            "", "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        m_name = month_names[month] if month and 1 <= month <= 12 else None
        
        contrib_dicts = [c.model_dump() for c in contributors]
        return self.engine.generate_natural_language_summary(
            severity=severity,
            anomaly_type=anomaly_type,
            contributors=contrib_dicts,
            location=location,
            month_name=m_name,
        )


# Global service instance
explanation_service = ExplanationService()

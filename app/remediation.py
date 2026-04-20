"""
Remediation Priority Scoring -- ranks remediation actions by combining
control risk score with control severity to produce a prioritized action plan.

Priority = risk_score * severity_weight
  - critical = 4
  - high = 3
  - medium = 2
  - low = 1
"""

from typing import Any

SEVERITY_WEIGHT = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


def compute_priority_score(risk_score: float, severity: str) -> float:
    """Compute a priority score for a single control result."""
    weight = SEVERITY_WEIGHT.get(severity.lower(), 2)
    return round(risk_score * weight, 2)


def generate_remediation_plan(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Generate a prioritized remediation plan from compliance results.
    Returns a sorted list of actions, highest priority first.
    Only includes controls that are not fully compliant.
    """
    plan: list[dict[str, Any]] = []

    for r in results:
        if r.get("status") == "Yes":
            continue

        severity = r.get("severity", "medium")
        risk = r.get("risk_score", 0.5)
        priority = compute_priority_score(risk, severity)

        plan.append({
            "control_id": r.get("control_id", ""),
            "control_title": r.get("control_title", ""),
            "status": r.get("status", ""),
            "severity": severity,
            "risk_score": risk,
            "priority_score": priority,
            "recommendation": r.get("recommendation", ""),
            "gaps": r.get("gaps", []),
        })

    plan.sort(key=lambda x: x["priority_score"], reverse=True)
    return plan

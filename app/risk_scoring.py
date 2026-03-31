"""
Risk Scoring — computes aggregate risk metrics from compliance evaluation results.
"""

from typing import Any


def compute_risk_score(results: list[dict[str, Any]]) -> float:
    """Compute average risk score across all controls. Yes=0, Partial=0.5, No=1."""
    score_map = {"Yes": 0.0, "Partial": 0.5, "No": 1.0}
    if not results:
        return 0.0
    total = sum(score_map.get(r.get("status", "No"), 1.0) for r in results)
    return round(total / len(results), 2)


def get_high_risk_controls(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return controls with status 'No' or 'Partial', sorted by severity."""
    high_risk = [r for r in results if r.get("status") in ("No", "Partial")]
    high_risk.sort(key=lambda r: (0 if r["status"] == "No" else 1))
    return high_risk


def generate_risk_summary(results: list[dict[str, Any]], risk_score: float) -> dict[str, Any]:
    """
    Generate a structured risk summary including score interpretation,
    high-risk controls, and top recommendations.
    """
    high_risk = get_high_risk_controls(results)
    total = len(results)
    compliant = sum(1 for r in results if r.get("status") == "Yes")
    partial = sum(1 for r in results if r.get("status") == "Partial")
    non_compliant = sum(1 for r in results if r.get("status") == "No")

    if risk_score <= 0.3:
        interpretation = "Low risk — strong compliance posture with minor gaps."
    elif risk_score <= 0.6:
        interpretation = "Medium risk — partial compliance detected, several controls need attention."
    else:
        interpretation = "High risk — significant compliance gaps, immediate remediation recommended."

    return {
        "risk_score": risk_score,
        "interpretation": interpretation,
        "total_controls": total,
        "compliant": compliant,
        "partial": partial,
        "non_compliant": non_compliant,
        "high_risk_controls": [
            {"control_id": r["control_id"], "title": r["control_title"], "status": r["status"]}
            for r in high_risk[:5]
        ],
        "top_recommendations": [r["recommendation"] for r in high_risk[:5]],
    }

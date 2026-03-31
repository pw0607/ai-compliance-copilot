"""Tests for app.risk_scoring module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.risk_scoring import compute_risk_score, get_high_risk_controls, generate_risk_summary


def _make_result(control_id: str, status: str) -> dict:
    return {
        "control_id": control_id,
        "control_title": f"Control {control_id}",
        "status": status,
        "risk_score": {"Yes": 0, "Partial": 0.5, "No": 1}[status],
        "explanation": "test",
        "evidence_found": [],
        "gaps": [],
        "recommendation": "test",
    }


def test_compute_risk_score_all_yes():
    results = [_make_result("C1", "Yes"), _make_result("C2", "Yes")]
    assert compute_risk_score(results) == 0.0


def test_compute_risk_score_all_no():
    results = [_make_result("C1", "No"), _make_result("C2", "No")]
    assert compute_risk_score(results) == 1.0


def test_compute_risk_score_mixed():
    results = [_make_result("C1", "Yes"), _make_result("C2", "No")]
    assert compute_risk_score(results) == 0.5


def test_compute_risk_score_empty():
    assert compute_risk_score([]) == 0.0


def test_get_high_risk_controls():
    results = [
        _make_result("C1", "Yes"),
        _make_result("C2", "Partial"),
        _make_result("C3", "No"),
    ]
    high_risk = get_high_risk_controls(results)
    assert len(high_risk) == 2
    assert high_risk[0]["status"] == "No"
    assert high_risk[1]["status"] == "Partial"


def test_generate_risk_summary_low():
    results = [_make_result("C1", "Yes"), _make_result("C2", "Yes")]
    summary = generate_risk_summary(results, 0.0)
    assert summary["compliant"] == 2
    assert summary["non_compliant"] == 0
    assert "Low risk" in summary["interpretation"]


def test_generate_risk_summary_high():
    results = [_make_result("C1", "No"), _make_result("C2", "No")]
    summary = generate_risk_summary(results, 1.0)
    assert summary["non_compliant"] == 2
    assert "High risk" in summary["interpretation"]

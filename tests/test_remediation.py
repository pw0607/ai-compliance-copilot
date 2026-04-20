"""Tests for app.remediation module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.remediation import compute_priority_score, generate_remediation_plan


def test_priority_score_critical():
    assert compute_priority_score(1.0, "critical") == 4.0


def test_priority_score_low():
    assert compute_priority_score(0.5, "low") == 0.5


def test_priority_score_partial_high():
    assert compute_priority_score(0.5, "high") == 1.5


def test_remediation_plan_excludes_compliant():
    results = [
        {"control_id": "C1", "control_title": "T1", "status": "Yes", "risk_score": 0,
         "severity": "critical", "recommendation": "None", "gaps": []},
        {"control_id": "C2", "control_title": "T2", "status": "No", "risk_score": 1,
         "severity": "critical", "recommendation": "Fix it", "gaps": ["missing"]},
    ]
    plan = generate_remediation_plan(results)
    assert len(plan) == 1
    assert plan[0]["control_id"] == "C2"


def test_remediation_plan_sorted_by_priority():
    results = [
        {"control_id": "C1", "control_title": "T1", "status": "No", "risk_score": 1,
         "severity": "low", "recommendation": "R1", "gaps": []},
        {"control_id": "C2", "control_title": "T2", "status": "No", "risk_score": 1,
         "severity": "critical", "recommendation": "R2", "gaps": []},
        {"control_id": "C3", "control_title": "T3", "status": "Partial", "risk_score": 0.5,
         "severity": "high", "recommendation": "R3", "gaps": []},
    ]
    plan = generate_remediation_plan(results)
    assert plan[0]["control_id"] == "C2"
    assert plan[0]["priority_score"] == 4.0

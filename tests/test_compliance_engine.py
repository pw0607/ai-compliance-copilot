"""Tests for app.compliance_engine module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.compliance_engine import load_controls, evaluate_control, analyze


def test_load_controls_nist():
    controls = load_controls("nist")
    assert len(controls) == 10
    assert all("id" in c and "title" in c and "description" in c for c in controls)


def test_load_controls_all_frameworks():
    """Every registered framework should load without error."""
    from app.utils import FRAMEWORK_FILES
    for fw in FRAMEWORK_FILES:
        controls = load_controls(fw)
        assert len(controls) >= 10, f"{fw} has fewer than 10 controls"


def test_load_controls_invalid():
    try:
        load_controls("nonexistent")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_evaluate_control_returns_required_fields():
    control = {"id": "HIPAA-01", "title": "Access Controls", "description": "Test"}
    result = evaluate_control("A system with role-based access control and authentication", "hipaa", control)
    required_fields = ["control_id", "control_title", "status", "risk_score", "explanation", "evidence_found", "gaps", "recommendation"]
    for field in required_fields:
        assert field in result, f"Missing field: {field}"
    assert result["status"] in ("Yes", "Partial", "No")


def test_analyze_hipaa():
    result = analyze(
        "A healthcare AI with encryption at rest using AES-256 and TLS in transit. "
        "Role-based access controls with audit logging. Business associate agreement in place.",
        "hipaa",
    )
    assert result["framework"] == "hipaa"
    assert 0 <= result["risk_score"] <= 1
    assert len(result["compliance_results"]) == 10
    assert "risk_summary" in result

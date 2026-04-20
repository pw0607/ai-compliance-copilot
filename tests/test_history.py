"""Tests for app.history module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.history import save_analysis, load_history, clear_history


def test_save_and_load():
    clear_history()
    analysis = {
        "framework": "nist",
        "framework_name": "NIST AI RMF",
        "risk_score": 0.5,
        "summary": "Test",
        "risk_summary": {"total_controls": 10, "compliant": 5, "partial": 3, "non_compliant": 2},
        "prompt_injection_detected": False,
    }
    aid = save_analysis(analysis)
    assert len(aid) == 8

    history = load_history()
    assert len(history) >= 1
    assert history[-1]["framework"] == "nist"


def test_clear_history():
    save_analysis({"framework": "test", "risk_score": 0, "risk_summary": {}})
    count = clear_history()
    assert count >= 1
    assert len(load_history()) == 0

"""
Compliance Engine — orchestrates per-control evaluation using the prompt builder,
LLM client, and risk scoring modules.
"""

import json
import logging
from pathlib import Path
from typing import Any

from app.llm_client import call_llm
from app.prompts.prompt_builder import build_prompt
from app.risk_scoring import compute_risk_score, generate_risk_summary
from app.utils import (
    FRAMEWORK_FILES,
    detect_prompt_injection,
    get_framework_display_name,
    validate_framework,
)

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_controls(framework: str) -> list[dict[str, str]]:
    """Load compliance controls from the JSON file for the given framework."""
    filename = FRAMEWORK_FILES.get(framework)
    if not filename:
        raise ValueError(f"Unsupported framework: {framework}")
    filepath = DATA_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Controls file not found: {filepath}")
    with open(filepath, "r") as f:
        controls = json.load(f)
    logger.info("Loaded %d controls for framework '%s'", len(controls), framework)
    return controls


def evaluate_control(system_description: str, framework: str, control: dict[str, str]) -> dict[str, Any]:
    """
    Evaluate a single control by building a prompt and calling the LLM client.
    """
    control_id = control["id"]
    control_title = control["title"]
    control_description = control["description"]

    prompt = build_prompt(
        system_description=system_description,
        framework=framework,
        control_id=control_id,
        control_title=control_title,
        control_description=control_description,
    )

    result = call_llm(
        prompt=prompt,
        control_id=control_id,
        control_title=control_title,
        system_description=system_description,
    )

    return result


def analyze(system_description: str, framework: str) -> dict[str, Any]:
    """
    Run a full compliance analysis: load controls, evaluate each one,
    compute risk score, and return structured results.
    """
    if not validate_framework(framework):
        raise ValueError(f"Unsupported framework: {framework}. Supported: {list(FRAMEWORK_FILES.keys())}")

    injection_flag = detect_prompt_injection(system_description)
    controls = load_controls(framework)

    # Evaluate each control individually
    results: list[dict[str, Any]] = []
    for control in controls:
        result = evaluate_control(system_description, framework, control)
        results.append(result)

    # Compute risk metrics
    risk_score = compute_risk_score(results)
    risk_summary = generate_risk_summary(results, risk_score)

    return {
        "framework": framework,
        "framework_name": get_framework_display_name(framework),
        "risk_score": risk_score,
        "summary": risk_summary["interpretation"],
        "compliance_results": results,
        "risk_summary": risk_summary,
        "recommendations": risk_summary["top_recommendations"],
        "prompt_injection_detected": injection_flag,
        "human_review_recommended": injection_flag or risk_score > 0.7,
    }

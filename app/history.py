"""
Compliance History -- persists analysis results to JSON for tracking over time.

Stores each analysis run with a timestamp and unique ID so organizations
can demonstrate compliance posture changes across audits.
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

HISTORY_DIR = Path(__file__).resolve().parent.parent / "history"
HISTORY_FILE = HISTORY_DIR / "analysis_history.json"


def _ensure_history_file() -> None:
    """Create the history directory and file if they don't exist."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]")


def save_analysis(analysis: dict[str, Any]) -> str:
    """
    Save an analysis result to the history file.
    Returns the unique analysis ID.
    """
    _ensure_history_file()
    analysis_id = str(uuid.uuid4())[:8]

    record = {
        "id": analysis_id,
        "timestamp": datetime.now().isoformat(),
        "framework": analysis.get("framework", ""),
        "framework_name": analysis.get("framework_name", ""),
        "risk_score": analysis.get("risk_score", 0),
        "summary": analysis.get("summary", ""),
        "total_controls": analysis.get("risk_summary", {}).get("total_controls", 0),
        "compliant": analysis.get("risk_summary", {}).get("compliant", 0),
        "partial": analysis.get("risk_summary", {}).get("partial", 0),
        "non_compliant": analysis.get("risk_summary", {}).get("non_compliant", 0),
        "prompt_injection_detected": analysis.get("prompt_injection_detected", False),
    }

    try:
        history = json.loads(HISTORY_FILE.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        history = []

    history.append(record)
    HISTORY_FILE.write_text(json.dumps(history, indent=2))
    logger.info("Saved analysis %s to history", analysis_id)
    return analysis_id


def load_history() -> list[dict[str, Any]]:
    """Load all historical analysis records."""
    _ensure_history_file()
    try:
        history = json.loads(HISTORY_FILE.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        history = []
    return history


def get_analysis_by_id(analysis_id: str) -> Optional[dict[str, Any]]:
    """Retrieve a specific analysis record by ID."""
    history = load_history()
    for record in history:
        if record.get("id") == analysis_id:
            return record
    return None


def clear_history() -> int:
    """Clear all history records. Returns the number of records deleted."""
    _ensure_history_file()
    try:
        history = json.loads(HISTORY_FILE.read_text())
        count = len(history)
    except (json.JSONDecodeError, FileNotFoundError):
        count = 0
    HISTORY_FILE.write_text("[]")
    logger.info("Cleared %d history records", count)
    return count

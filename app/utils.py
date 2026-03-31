"""
Utility functions for AI Compliance Copilot.
"""

import logging
import re

logger = logging.getLogger(__name__)

# Patterns that indicate potential prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+instructions",
    r"you\s+are\s+now",
    r"system\s*:\s*",
    r"<\s*script",
    r"forget\s+(everything|all|your)",
    r"new\s+instructions?\s*:",
    r"override\s+(previous|system)",
    r"disregard\s+(previous|above|all)",
]

# Supported frameworks and their display names
FRAMEWORK_REGISTRY: dict[str, str] = {
    "nist": "NIST AI RMF",
    "hipaa": "HIPAA",
    "nist_csf": "NIST CSF",
    "fedramp": "FedRAMP",
    "iso": "ISO 27001",
    "owasp": "OWASP LLM Top 10",
    "gdpr": "GDPR",
}

# Maps framework keys to their JSON data filenames
FRAMEWORK_FILES: dict[str, str] = {
    "nist": "nist_controls.json",
    "hipaa": "hipaa_controls.json",
    "nist_csf": "nist_csf.json",
    "fedramp": "fedramp_controls.json",
    "iso": "iso_controls.json",
    "owasp": "owasp_controls.json",
    "gdpr": "gdpr_controls.json",
}


def detect_prompt_injection(text: str) -> bool:
    """Return True if the input text contains suspicious prompt-injection patterns."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning("Prompt injection pattern detected in input.")
            return True
    return False


def validate_framework(framework: str) -> bool:
    """Check if the given framework key is supported."""
    return framework in FRAMEWORK_REGISTRY


def get_framework_display_name(framework: str) -> str:
    """Return the human-readable name for a framework key."""
    return FRAMEWORK_REGISTRY.get(framework, framework.upper())

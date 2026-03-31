"""
LLM Client — handles mock and real LLM integration for compliance evaluation.

Default mode is mock, which uses keyword heuristics to simulate LLM reasoning.
Set USE_REAL_LLM=true and provide OPENAI_API_KEY to use a real LLM.
"""

import json
import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)

USE_REAL_LLM = os.getenv("USE_REAL_LLM", "false").lower() == "true"

# Keyword signals used by the mock evaluator, keyed by control ID.
KEYWORD_MAP: dict[str, list[str]] = {
    # NIST AI RMF
    "NIST-AI-01": ["risk assessment", "risk management", "risk mapping", "risk analysis", "lifecycle"],
    "NIST-AI-02": ["data governance", "data quality", "provenance", "data pipeline", "representative"],
    "NIST-AI-03": ["explainability", "interpretable", "transparency", "explain", "xai", "shap", "lime"],
    "NIST-AI-04": ["bias", "fairness", "demographic", "equity", "disparate impact"],
    "NIST-AI-05": ["human oversight", "human review", "human-in-the-loop", "override", "manual review"],
    "NIST-AI-06": ["adversarial", "security", "resilience", "attack", "robustness", "incident response"],
    "NIST-AI-07": ["privacy", "anonymi", "de-identif", "pii", "differential privacy", "minimiz"],
    "NIST-AI-08": ["validation", "testing", "accuracy", "edge case", "benchmark", "evaluation"],
    "NIST-AI-09": ["accountability", "documentation", "roles", "responsible", "governance"],
    "NIST-AI-10": ["monitoring", "drift", "post-deployment", "continuous", "alerting", "observability"],
    # HIPAA
    "HIPAA-01": ["access control", "rbac", "authentication", "authorization", "role-based", "least privilege"],
    "HIPAA-02": ["audit", "logging", "log", "trail", "record", "examine"],
    "HIPAA-03": ["integrity", "checksum", "hash", "tamper", "alteration"],
    "HIPAA-04": ["encryption in transit", "tls", "ssl", "https", "transmission security", "vpn"],
    "HIPAA-05": ["encryption at rest", "aes", "encrypted storage", "encrypt", "kms"],
    "HIPAA-06": ["minimum necessary", "least privilege", "need-to-know", "data minimization"],
    "HIPAA-07": ["business associate", "baa", "vendor", "third-party", "contract"],
    "HIPAA-08": ["breach notification", "incident report", "breach detect", "notify"],
    "HIPAA-09": ["risk analysis", "risk assessment", "vulnerability", "threat model"],
    "HIPAA-10": ["training", "workforce", "security awareness", "education", "onboarding"],
    # NIST CSF
    "CSF-ID-01": ["asset", "inventory", "data flow", "catalog"],
    "CSF-ID-02": ["risk assessment", "risk analysis", "threat", "vulnerability"],
    "CSF-PR-01": ["access control", "rbac", "authentication", "authorization", "least privilege"],
    "CSF-PR-02": ["encryption", "data security", "integrity", "secure storage", "tls"],
    "CSF-PR-03": ["firewall", "waf", "ids", "ips", "endpoint protection"],
    "CSF-DE-01": ["anomaly", "detection", "alerting", "siem", "monitoring"],
    "CSF-DE-02": ["monitoring", "continuous", "observability", "log analysis"],
    "CSF-RS-01": ["incident response", "playbook", "response plan", "escalation"],
    "CSF-RS-02": ["communication", "stakeholder", "notification", "coordination"],
    "CSF-RC-01": ["recovery", "backup", "disaster recovery", "restoration", "business continuity"],
    # FedRAMP
    "FEDRAMP-AC-01": ["access control policy", "access policy", "authorization policy"],
    "FEDRAMP-AC-02": ["mfa", "multi-factor", "two-factor", "2fa", "totp"],
    "FEDRAMP-AU-01": ["audit log", "audit record", "logging", "event log"],
    "FEDRAMP-AU-02": ["log retention", "audit retention", "log storage", "archive"],
    "FEDRAMP-SC-01": ["boundary", "firewall", "network segment", "dmz", "perimeter"],
    "FEDRAMP-SC-02": ["tls", "ssl", "encryption in transit", "https", "ipsec"],
    "FEDRAMP-CM-01": ["configuration management", "baseline", "hardening", "golden image"],
    "FEDRAMP-RA-01": ["vulnerability scan", "penetration test", "patch management", "remediation"],
    "FEDRAMP-IA-01": ["identity", "authentication", "credential", "sso", "ldap"],
    "FEDRAMP-CA-01": ["continuous monitoring", "ongoing assessment", "security posture"],
    # ISO 27001
    "ISO-A5": ["security policy", "information security policy", "policy document"],
    "ISO-A6": ["security organization", "security roles", "security framework", "ciso"],
    "ISO-A7": ["background check", "security training", "awareness", "onboarding"],
    "ISO-A8": ["asset management", "asset inventory", "classification", "ownership"],
    "ISO-A9": ["access control", "rbac", "least privilege", "authorization"],
    "ISO-A12": ["operations security", "change management", "capacity management", "malware"],
    "ISO-A13": ["network security", "network control", "segmentation", "transfer policy"],
    "ISO-A16": ["incident management", "incident response", "escalation", "forensic"],
    "ISO-A17": ["business continuity", "disaster recovery", "resilience", "backup"],
    "ISO-A18": ["legal compliance", "regulatory", "statutory", "contractual"],
    # OWASP LLM
    "OWASP-LLM-01": ["prompt injection", "input sanitization", "system prompt", "guardrail", "input filter"],
    "OWASP-LLM-02": ["output validation", "output sanitization", "output filter", "xss prevention"],
    "OWASP-LLM-03": ["training data", "data poisoning", "data integrity", "provenance"],
    "OWASP-LLM-04": ["rate limit", "throttling", "input size", "resource limit", "dos protection"],
    "OWASP-LLM-05": ["supply chain", "dependency", "third-party model", "model provenance"],
    "OWASP-LLM-06": ["pii filter", "data leakage", "sensitive data", "output scanning", "redaction"],
    "OWASP-LLM-07": ["plugin security", "tool sandbox", "least privilege", "plugin validation"],
    "OWASP-LLM-08": ["human approval", "human-in-the-loop", "action limit", "agency control"],
    "OWASP-LLM-09": ["confidence score", "verification", "disclaimer", "overreliance warning"],
    "OWASP-LLM-10": ["model protection", "api key", "model access", "weight protection", "endpoint security"],
    # GDPR
    "GDPR-01": ["lawful basis", "consent", "legitimate interest", "legal obligation", "contract"],
    "GDPR-02": ["data minimization", "minimal data", "necessary data", "proportionate"],
    "GDPR-03": ["purpose limitation", "specified purpose", "compatible purpose"],
    "GDPR-04": ["data subject rights", "access request", "erasure", "portability", "rectification"],
    "GDPR-05": ["privacy by design", "privacy by default", "data protection by design"],
    "GDPR-06": ["dpia", "impact assessment", "privacy impact", "risk assessment"],
    "GDPR-07": ["data processing agreement", "dpa", "processor agreement", "sub-processor"],
    "GDPR-08": ["breach notification", "72 hours", "supervisory authority", "data breach"],
    "GDPR-09": ["cross-border", "data transfer", "scc", "adequacy", "standard contractual"],
    "GDPR-10": ["automated decision", "profiling", "human intervention", "right to contest"],
}


def _mock_evaluate(prompt: str, control_id: str, control_title: str, system_description: str) -> dict[str, Any]:
    """
    Mock LLM evaluation using keyword heuristics.
    Simulates structured reasoning by matching keywords against the system description.
    """
    desc_lower = system_description.lower()
    keywords = KEYWORD_MAP.get(control_id, [])

    matched = [kw for kw in keywords if kw in desc_lower]
    match_ratio = len(matched) / max(len(keywords), 1)

    if match_ratio >= 0.5:
        status = "Yes"
        risk_score = 0
        explanation = (
            f"The system description provides sufficient evidence of compliance with "
            f"'{control_title}'. Matched signals: {', '.join(matched)}."
        )
        evidence_found = matched
        gaps = []
        recommendation = "Continue maintaining current practices and ensure formal documentation."
    elif match_ratio > 0:
        status = "Partial"
        risk_score = 0.5
        explanation = (
            f"Some evidence found for '{control_title}' (matched: {', '.join(matched)}), "
            f"but coverage appears incomplete."
        )
        evidence_found = matched
        missing = [kw for kw in keywords if kw not in desc_lower]
        gaps = [f"No evidence of: {kw}" for kw in missing[:3]]
        recommendation = f"Strengthen compliance by addressing all aspects of '{control_title}'."
    else:
        status = "No"
        risk_score = 1
        explanation = f"No evidence found in the system description for '{control_title}'."
        evidence_found = []
        gaps = [f"Missing: {kw}" for kw in keywords[:3]]
        recommendation = f"Implement measures to satisfy '{control_title}'."

    return {
        "control_id": control_id,
        "control_title": control_title,
        "status": status,
        "risk_score": risk_score,
        "explanation": explanation,
        "evidence_found": evidence_found,
        "gaps": gaps,
        "recommendation": recommendation,
    }


def _real_llm_evaluate(prompt: str, control_id: str, control_title: str) -> dict[str, Any]:
    """
    Call a real LLM (OpenAI) for evaluation. Requires OPENAI_API_KEY env var.
    Falls back to mock if the call fails.
    """
    try:
        import openai

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500,
        )
        content = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        content = re.sub(r"^```json\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        result = json.loads(content)
        # Validate required fields
        for field in ["status", "explanation", "recommendation"]:
            if field not in result:
                raise ValueError(f"Missing field: {field}")
        result["control_id"] = control_id
        result["control_title"] = control_title
        return result
    except Exception as exc:
        logger.warning("Real LLM call failed for %s, falling back to mock: %s", control_id, exc)
        return _mock_evaluate(prompt, control_id, control_title, "")


def call_llm(
    prompt: str,
    control_id: str,
    control_title: str,
    system_description: str = "",
) -> dict[str, Any]:
    """
    Evaluate a single control. Routes to real LLM or mock based on configuration.
    """
    if USE_REAL_LLM:
        logger.info("Using real LLM for control %s", control_id)
        return _real_llm_evaluate(prompt, control_id, control_title)
    else:
        logger.info("Using mock evaluator for control %s", control_id)
        return _mock_evaluate(prompt, control_id, control_title, system_description)

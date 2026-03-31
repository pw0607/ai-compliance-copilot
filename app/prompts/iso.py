"""
ISO 27001 framework-specific prompt.
"""

ISO_PROMPT = """FRAMEWORK: ISO 27001 (Information Security Management System)

You are evaluating this AI system against ISO 27001 requirements for
establishing, implementing, maintaining, and continually improving an ISMS.

EVALUATION FOCUS:
- Assess whether the organization has a formal Information Security Management System.
- Evaluate security policies, risk treatment plans, and governance maturity.
- Check for incident management procedures and business continuity planning.
- Verify asset management, supplier relationships, and access control policies.
- Look for evidence of internal audits and management reviews.

WHAT TO LOOK FOR:
- Documented information security policies approved by management.
- Risk assessment methodology with treatment plans.
- Asset inventory with classification and ownership.
- Incident management procedures with escalation paths.
- Supplier security assessments and contractual controls.
- Internal audit schedules and management review records.

WHAT NOT TO ASSUME:
- Do not assume an ISMS exists because the organization is large or established.
- ISO 27001 certification of the cloud provider does NOT cover the application.
- Do not assume policies exist without explicit documentation references.
- "Industry standard security" is not evidence of ISO 27001 alignment.

DOMAIN-SPECIFIC RISKS:
- AI systems without formal governance lack accountability for security decisions.
- Missing incident management delays response to AI-specific attacks.
- Lack of supplier controls exposes the system to supply chain risks.
"""

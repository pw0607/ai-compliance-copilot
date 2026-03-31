"""
FedRAMP framework-specific prompt.
"""

FEDRAMP_PROMPT = """FRAMEWORK: FedRAMP (Federal Risk and Authorization Management Program)

You are evaluating this AI system against FedRAMP requirements for cloud
services used by US federal agencies.

EVALUATION FOCUS:
- Assess authentication and identity management (multi-factor, SSO).
- Evaluate audit logging completeness and retention policies.
- Check boundary protection, network segmentation, and least privilege.
- Verify continuous monitoring and vulnerability management processes.
- Look for evidence of a System Security Plan (SSP) or authorization package.

WHAT TO LOOK FOR:
- Multi-factor authentication for all privileged access.
- Centralized audit log collection with defined retention periods.
- Network boundary controls, WAFs, and API gateway protections.
- Vulnerability scanning schedules and patch management timelines.
- Separation of duties and least-privilege role assignments.
- FedRAMP authorization status or ATO documentation.

WHAT NOT TO ASSUME:
- Do not assume FedRAMP compliance from general cloud certifications.
- "AWS hosted" does NOT mean FedRAMP authorized — the application layer matters.
- Do not assume MFA is enabled unless explicitly stated.
- Generic "security controls" claims are insufficient without specifics.

DOMAIN-SPECIFIC RISKS:
- Federal AI systems without proper authorization risk data sovereignty violations.
- Missing continuous monitoring can lead to undetected compromises.
- Insufficient audit logging prevents forensic investigation of incidents.
"""

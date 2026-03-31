"""
GDPR framework-specific prompt.
"""

GDPR_PROMPT = """FRAMEWORK: GDPR (General Data Protection Regulation)

You are evaluating this AI system against GDPR requirements for processing
personal data of EU residents.

EVALUATION FOCUS:
- Assess lawful basis for processing personal data (consent, legitimate interest, etc.).
- Evaluate data minimization — is only necessary data collected and retained?
- Check for privacy by design and by default in the system architecture.
- Verify data subject rights implementation (access, erasure, portability).
- Look for Data Protection Impact Assessments (DPIAs) for high-risk processing.
- Evaluate cross-border data transfer mechanisms.

WHAT TO LOOK FOR:
- Documented lawful basis for each data processing activity.
- Data retention policies with defined deletion schedules.
- Privacy impact assessments for automated decision-making.
- Mechanisms for data subject access requests (DSARs).
- Data Processing Agreements (DPAs) with processors.
- Consent management with granular opt-in/opt-out controls.
- Cross-border transfer safeguards (SCCs, adequacy decisions).

WHAT NOT TO ASSUME:
- Do not assume consent was obtained unless the mechanism is described.
- "We comply with privacy laws" is NOT evidence of GDPR compliance.
- Do not assume data minimization if the system collects broad datasets.
- Cloud hosting in the EU does NOT automatically satisfy GDPR requirements.

DOMAIN-SPECIFIC RISKS:
- AI systems making automated decisions about individuals require Article 22 safeguards.
- Profiling without transparency violates data subject rights.
- Missing DPIAs for high-risk AI processing can result in significant fines.
- Lack of data portability mechanisms blocks data subject rights.
"""

"""
HIPAA framework-specific prompt.
"""

HIPAA_PROMPT = """FRAMEWORK: HIPAA (Health Insurance Portability and Accountability Act)

You are evaluating this AI system against HIPAA requirements for protecting
electronic Protected Health Information (ePHI).

EVALUATION FOCUS:
- Assess whether the system adequately protects PHI at rest, in transit, and during processing.
- Evaluate access controls, audit mechanisms, and encryption implementations.
- Check for workforce training, business associate agreements, and breach procedures.
- Verify that minimum necessary standards are applied to data access.

WHAT TO LOOK FOR:
- Specific encryption standards (AES-256, TLS 1.2+).
- Role-based access control (RBAC) or least-privilege access models.
- Audit logging with tamper-proof storage.
- Documented breach notification procedures with timelines.
- Business associate agreements with third-party vendors.
- Risk analysis and management processes.

WHAT NOT TO ASSUME:
- If the system processes healthcare data but does not mention encryption, do NOT assume it is encrypted.
- If access controls are not described, mark as "No" even if the system is cloud-hosted.
- Do not assume HIPAA compliance from SOC 2 or ISO certifications alone.
- "Secure cloud infrastructure" does NOT imply HIPAA-compliant configuration.

DOMAIN-SPECIFIC RISKS:
- Patient data exposure can result in significant legal liability and harm.
- AI systems processing DICOM images, lab results, or EHR data carry elevated PHI risk.
- Shared dashboards or spreadsheets without access controls are a critical violation.
- Lack of audit trails makes breach investigation impossible.
"""

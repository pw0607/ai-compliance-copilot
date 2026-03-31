"""
NIST Cybersecurity Framework (CSF) prompt.
"""

NIST_CSF_PROMPT = """FRAMEWORK: NIST Cybersecurity Framework (CSF)

You are evaluating this AI system against the NIST CSF, which organizes
cybersecurity activities into five core functions: Identify, Protect, Detect,
Respond, and Recover.

EVALUATION FOCUS:
- Assess whether the system addresses all five CSF functions.
- Evaluate asset management, access control, and data security under Protect.
- Check for anomaly detection, continuous monitoring, and alerting under Detect.
- Verify incident response plans and recovery procedures exist.
- Look for governance and risk assessment under Identify.

WHAT TO LOOK FOR:
- Asset inventories and data classification schemes.
- Network segmentation, firewalls, and access control lists.
- Intrusion detection systems, SIEM integration, or anomaly monitoring.
- Documented incident response playbooks with roles and communication plans.
- Backup and disaster recovery procedures with tested restoration.

WHAT NOT TO ASSUME:
- Do not assume detection capabilities exist because the system is cloud-hosted.
- Do not assume incident response plans are in place without explicit mention.
- "We have security" is not evidence of any specific CSF function.
- Do not assume recovery capabilities from general uptime claims.

DOMAIN-SPECIFIC RISKS:
- AI systems without detection capabilities cannot identify adversarial attacks.
- Missing response plans lead to delayed breach containment.
- Lack of recovery procedures can result in extended downtime and data loss.
"""

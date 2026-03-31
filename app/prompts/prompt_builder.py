"""
Prompt Builder — assembles the final evaluation prompt from base + framework + control + input.
"""

from app.prompts.base import BASE_PROMPT
from app.prompts.nist import NIST_PROMPT
from app.prompts.hipaa import HIPAA_PROMPT
from app.prompts.nist_csf import NIST_CSF_PROMPT
from app.prompts.fedramp import FEDRAMP_PROMPT
from app.prompts.iso import ISO_PROMPT
from app.prompts.owasp import OWASP_PROMPT
from app.prompts.gdpr import GDPR_PROMPT

FRAMEWORK_PROMPTS: dict[str, str] = {
    "nist": NIST_PROMPT,
    "hipaa": HIPAA_PROMPT,
    "nist_csf": NIST_CSF_PROMPT,
    "fedramp": FEDRAMP_PROMPT,
    "iso": ISO_PROMPT,
    "owasp": OWASP_PROMPT,
    "gdpr": GDPR_PROMPT,
}


def build_prompt(
    system_description: str,
    framework: str,
    control_id: str,
    control_title: str,
    control_description: str,
) -> str:
    """
    Combine base prompt + framework prompt + control details + system description
    into a single evaluation prompt string.
    """
    framework_prompt = FRAMEWORK_PROMPTS.get(framework, "")

    prompt = f"""{BASE_PROMPT.format(control_id=control_id, control_title=control_title)}

{framework_prompt}

CONTROL TO EVALUATE:
- Control ID: {control_id}
- Control Title: {control_title}
- Control Description: {control_description}

AI SYSTEM DESCRIPTION:
---
{system_description}
---

Evaluate this system against the control above. Respond with valid JSON only."""

    return prompt

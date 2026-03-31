# Prompt Design — AI Compliance Copilot

## Overview

The prompt system is modular and layered. Each evaluation prompt is assembled from three components combined by the prompt builder.

## Architecture

```
┌──────────────┐   ┌────────────────────┐   ┌──────────────────┐
│  Base Prompt  │ + │  Framework Prompt   │ + │  Control + Input  │
│  (base.py)    │   │  (nist.py, etc.)    │   │  (dynamic)        │
└──────────────┘   └────────────────────┘   └──────────────────┘
        │                    │                        │
        └────────────────────┼────────────────────────┘
                             ▼
                    ┌─────────────────┐
                    │  prompt_builder  │
                    │  .build_prompt() │
                    └─────────────────┘
                             │
                             ▼
                    Final evaluation prompt
```

## Layer 1: Base Prompt (`base.py`)

Defines the evaluator role, strict rules, and output JSON schema. This is shared across all frameworks and ensures:

- The evaluator does NOT assume missing safeguards
- Output is always valid JSON with a fixed schema
- Scoring rules are consistent (Yes=0, Partial=0.5, No=1)

## Layer 2: Framework Prompts

Each framework file (e.g., `hipaa.py`, `owasp.py`) adds domain-specific instructions:

- What to evaluate (specific focus areas)
- What evidence to look for (concrete signals)
- What NOT to assume (prevents false positives)
- Domain-specific risks (contextual awareness)

### Framework Files

| File         | Framework          | Focus Areas                                      |
|--------------|--------------------|--------------------------------------------------|
| `nist.py`    | NIST AI RMF        | Governance, risk lifecycle, measurement           |
| `hipaa.py`   | HIPAA              | PHI protection, encryption, access controls       |
| `nist_csf.py`| NIST CSF           | Identify, Protect, Detect, Respond, Recover       |
| `fedramp.py` | FedRAMP            | Authentication, audit logs, boundary protection    |
| `iso.py`     | ISO 27001          | ISMS, policies, incident management               |
| `owasp.py`   | OWASP LLM Top 10   | Prompt injection, data leakage, model security     |
| `gdpr.py`    | GDPR               | Data minimization, privacy by design, DPIA         |

## Layer 3: Dynamic Context

The prompt builder injects:
- The specific control being evaluated (ID, title, description)
- The user's AI system description

## Design Principles

1. Strict output format prevents parsing failures
2. "Do NOT assume" rules reduce false positives
3. Framework-specific context improves evaluation accuracy
4. Modular design allows adding new frameworks by creating one file

## Adding a New Framework

1. Create `app/prompts/new_framework.py` with the prompt string
2. Add the control data file to `data/new_framework_controls.json`
3. Register in `app/prompts/prompt_builder.py` and `app/utils.py`

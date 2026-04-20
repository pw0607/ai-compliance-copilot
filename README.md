# 🛡️ AI Compliance Copilot

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-34%20passing-brightgreen.svg)](tests/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](Dockerfile)

A production-quality, multi-framework AI compliance evaluation system. Assess AI systems against 7 regulatory frameworks with severity-weighted remediation plans, multi-framework comparison, compliance history tracking, and structured exports.

---

## Problem Statement

AI adoption is accelerating across healthcare, government, finance, and critical infrastructure -- but compliance evaluation remains manual, slow, and inconsistent.

Organizations deploying AI systems face:

- Dozens of controls across multiple frameworks with no automated way to assess them
- Compliance teams that lack AI-specific expertise to interpret framework requirements
- No way to compare compliance posture across frameworks simultaneously
- No historical tracking to demonstrate compliance improvements over time
- Undetected gaps that expose organizations to regulatory penalties and patient safety risks

---

## Solution

AI Compliance Copilot automates compliance evaluation with structured, LLM-powered reasoning:

1. Describe your AI system in plain text
2. Select one or more of 7 supported frameworks
3. Receive per-control compliance status with evidence, gaps, severity, and remediation steps
4. Get a prioritized remediation plan ranked by risk x severity
5. Compare results across frameworks side by side
6. Track compliance history over time
7. Export as PDF or JSON for audit documentation

---

## Key Features

- **7 compliance frameworks** with 70 controls total, each with severity ratings
- **Multi-framework comparison** -- evaluate against multiple frameworks in one request
- **Prioritized remediation plans** -- actions ranked by risk score x control severity
- **Compliance history** -- track and review past analyses over time
- **Dual export** -- download results as PDF report or structured JSON
- **Prompt injection detection** -- flags suspicious inputs for human review
- **Mock + real LLM** -- works out of the box with mock evaluator, optional OpenAI integration
- **34 automated tests** covering engine, scoring, remediation, history, and API

---

## Supported Frameworks

| Framework           | Focus Areas                                              | Controls | Severities          |
|---------------------|----------------------------------------------------------|----------|---------------------|
| NIST AI RMF         | Governance, risk lifecycle, measurement, accountability   | 10       | 4 critical, 5 high  |
| HIPAA               | PHI protection, encryption, access controls, audit logs   | 10       | 4 critical, 3 high  |
| NIST CSF            | Identify, Protect, Detect, Respond, Recover               | 10       | 4 critical, 4 high  |
| FedRAMP             | Authentication, audit logs, boundary protection            | 10       | 5 critical, 3 high  |
| ISO 27001           | ISMS, policies, incident management, governance maturity   | 10       | 3 critical, 5 high  |
| OWASP LLM Top 10   | Prompt injection, data leakage, insecure output handling   | 10       | 3 critical, 5 high  |
| GDPR                | Data minimization, privacy by design, DPIA, subject rights | 10       | 5 critical, 4 high  |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend (v3)                   │
│   Single Analysis | Multi-Framework Comparison | History      │
│   Remediation Plan | PDF + JSON Export | Severity Badges      │
└──────────────────────────┬───────────────────────────────────┘
                           │ POST /analyze, /analyze/multi
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (v3.0)                     │
│   Request ID tracking | Structured errors | CORS              │
│                                                              │
│  Compliance Engine                                           │
│    ├── Load controls + severity from JSON                    │
│    ├── For each control:                                     │
│    │     ├── Prompt Builder (base + framework + control)      │
│    │     └── LLM Client (mock or OpenAI)                     │
│    ├── Risk Scoring (Yes=0, Partial=0.5, No=1, averaged)     │
│    ├── Remediation Priority (risk x severity weight)          │
│    └── Report Generator (PDF)                                │
│                                                              │
│  History Layer (JSON persistence)                            │
│  Data Layer: 7 JSON control files (70 controls total)        │
└─────────────────────────────────────────────────────────────┘
```

---

## National Impact

- **Healthcare Safety**: Evaluate AI/ML models against HIPAA and NIST before deployment, reducing PHI exposure and patient harm risk.
- **Critical Infrastructure**: FedRAMP and NIST CSF alignment for AI in government and defense.
- **Regulatory Alignment**: Supports Executive Order 14110 on Safe, Secure, and Trustworthy AI.
- **Risk Quantification**: Severity-weighted remediation plans enable leadership to prioritize fixes by impact.
- **International Coverage**: GDPR and ISO 27001 for cross-jurisdictional operations.

---

## Quick Start

### Option 1: Docker

```bash
cp .env.example .env
docker compose up --build
```

Backend: `localhost:8000` | Frontend: `localhost:8501` | API Docs: `localhost:8000/docs`

### Option 2: Local

```bash
python3 -m venv venv && source venv/bin/activate
python3 -m pip install -r requirements.txt

# Terminal 1
python3 -m uvicorn app.main:app --reload --port 8000

# Terminal 2
python3 -m streamlit run frontend/streamlit_app.py
```

### Option 3: Make

```bash
make install
make run-backend   # Terminal 1
make run-frontend  # Terminal 2
```

---

## API Reference

Interactive docs at `localhost:8000/docs` when running.

### `POST /analyze` -- Single framework analysis

```bash
curl -X POST localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"system_description": "A radiology AI with RBAC and TLS.", "framework": "hipaa"}'
```

### `POST /analyze/multi` -- Multi-framework comparison

```bash
curl -X POST localhost:8000/analyze/multi \
  -H "Content-Type: application/json" \
  -d '{"system_description": "A radiology AI with RBAC and TLS.", "frameworks": ["hipaa", "nist", "gdpr"]}'
```

### `GET /history` -- View analysis history

### `DELETE /history` -- Clear analysis history

### `GET /frameworks` -- List supported frameworks

### `GET /health` -- Liveness probe

---

## Configuration

| Variable        | Default       | Description                              |
|-----------------|---------------|------------------------------------------|
| `USE_REAL_LLM`  | `false`       | Set `true` to use OpenAI instead of mock |
| `OPENAI_API_KEY`| --            | Required when `USE_REAL_LLM=true`        |
| `OPENAI_MODEL`  | `gpt-4o-mini` | OpenAI model to use                      |
| `API_URL`       | `localhost:8000` | Backend URL (for frontend)            |
| `LOG_LEVEL`     | `INFO`        | Logging verbosity                        |

---

## Testing

```bash
make test
# or
python3 -m pytest tests/ -v
```

34 tests covering: API endpoints, compliance engine, risk scoring, remediation priority, history, and utilities.

---

## Project Structure

```
ai-compliance-copilot/
├── app/
│   ├── main.py                  # FastAPI backend with multi-framework support
│   ├── compliance_engine.py     # Evaluation orchestrator
│   ├── llm_client.py            # Mock + OpenAI LLM integration
│   ├── risk_scoring.py          # Risk computation and summary
│   ├── remediation.py           # Priority-ranked remediation plans
│   ├── history.py               # JSON-based compliance history
│   ├── report_generator.py      # PDF generation with Unicode sanitization
│   ├── utils.py                 # Shared utilities and registries
│   └── prompts/                 # Modular prompt system (7 frameworks)
├── frontend/
│   └── streamlit_app.py         # Tabbed UI: single, multi, history
├── data/                        # 7 JSON control files with severity levels
├── tests/                       # 34 pytest tests
├── history/                     # Analysis history (JSON persistence)
├── examples/                    # Sample input and output
├── reports/                     # Generated PDF reports
├── docs/                        # Architecture + prompt design docs
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
└── README.md
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md).

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT -- see [LICENSE](LICENSE).

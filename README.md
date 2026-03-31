# 🛡️ AI Compliance Copilot

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](Dockerfile)

A production-quality, multi-framework AI compliance evaluation system. Helps organizations assess AI systems against 7 regulatory frameworks using structured, LLM-powered reasoning with explainable outputs.

---

## Problem Statement

AI adoption is accelerating across healthcare, government, finance, and critical infrastructure — but compliance evaluation remains manual, slow, and inconsistent.

Organizations deploying AI systems face:

- Dozens of controls across multiple frameworks with no automated way to assess them
- Compliance teams that lack AI-specific expertise to interpret framework requirements
- Audit bottlenecks that delay deployments by weeks or months
- Undetected gaps that expose organizations to regulatory penalties and patient safety risks

In healthcare alone, AI systems processing patient data must satisfy HIPAA, and increasingly NIST AI RMF, before deployment. Most teams evaluate these manually — if at all.

---

## Solution

AI Compliance Copilot automates compliance evaluation:

1. Describe your AI system in plain text
2. Select one of 7 supported frameworks
3. Receive per-control compliance status with evidence, gaps, and remediation steps
4. Download a PDF report for audit documentation

Each control is evaluated individually using a modular prompt pipeline: strict base prompt + framework-specific reasoning + control definition + system description.

---

## Supported Frameworks

| Framework           | Focus Areas                                              | Controls |
|---------------------|----------------------------------------------------------|----------|
| NIST AI RMF         | Governance, risk lifecycle, measurement, accountability   | 10       |
| HIPAA               | PHI protection, encryption, access controls, audit logs   | 10       |
| NIST CSF            | Identify, Protect, Detect, Respond, Recover               | 10       |
| FedRAMP             | Authentication, audit logs, boundary protection            | 10       |
| ISO 27001           | ISMS, policies, incident management, governance maturity   | 10       |
| OWASP LLM Top 10   | Prompt injection, data leakage, insecure output handling   | 10       |
| GDPR                | Data minimization, privacy by design, DPIA, subject rights | 10       |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│   Text Input  |  Framework Dropdown (7)  |  Run Analysis     │
│   Metrics Dashboard  |  Results Table  |  PDF Download       │
└──────────────────────────┬───────────────────────────────────┘
                           │ POST /analyze
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (v2.1)                     │
│   Request ID tracking  |  Structured errors  |  CORS         │
│                                                              │
│  Compliance Engine                                           │
│    ├── Load controls from JSON (10 per framework)            │
│    ├── For each control:                                     │
│    │     ├── Prompt Builder (base + framework + control)      │
│    │     └── LLM Client (mock or OpenAI)                     │
│    ├── Risk Scoring (Yes=0, Partial=0.5, No=1, averaged)     │
│    └── Report Generator (PDF)                                │
│                                                              │
│  Data Layer: 7 JSON control files (70 controls total)        │
└─────────────────────────────────────────────────────────────┘
```

For detailed architecture, see [docs/architecture.md](docs/architecture.md).
For prompt design details, see [docs/prompt_design.md](docs/prompt_design.md).

---

## National Impact

- **Healthcare Safety**: Evaluate AI/ML models against HIPAA and NIST before deployment, reducing PHI exposure and patient harm risk.
- **Critical Infrastructure**: FedRAMP and NIST CSF alignment for AI in government and defense.
- **Regulatory Alignment**: Supports Executive Order 14110 on Safe, Secure, and Trustworthy AI.
- **Risk Quantification**: Measurable risk scores and actionable remediation for go/no-go decisions.
- **International Coverage**: GDPR and ISO 27001 for cross-jurisdictional operations.

---

## Quick Start

### Option 1: Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs

### Option 2: Local

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt

# Terminal 1: Backend
python3 -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
python3 -m streamlit run frontend/streamlit_app.py
```

### Option 3: Make

```bash
make install
make run-backend   # Terminal 1
make run-frontend  # Terminal 2
```

---

## Configuration

Copy `.env.example` to `.env` and configure:

| Variable        | Default       | Description                              |
|-----------------|---------------|------------------------------------------|
| `USE_REAL_LLM`  | `false`       | Set `true` to use OpenAI instead of mock |
| `OPENAI_API_KEY`| —             | Required when `USE_REAL_LLM=true`        |
| `OPENAI_MODEL`  | `gpt-4o-mini` | OpenAI model to use                      |
| `API_HOST`      | `0.0.0.0`    | FastAPI bind address                     |
| `API_PORT`      | `8000`        | FastAPI port                             |
| `LOG_LEVEL`     | `INFO`        | Logging verbosity                        |

---

## API Reference

Interactive docs available at http://localhost:8000/docs when the backend is running.

### `POST /analyze`

Evaluate an AI system against a compliance framework.

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "system_description": "A radiology AI that analyzes chest X-rays with role-based access controls and TLS encryption.",
    "framework": "hipaa"
  }'
```

Response includes: `risk_score`, `compliance_results` (per-control with evidence, gaps, recommendations), `risk_summary`, and `recommendations`.

### `GET /frameworks`

List all supported frameworks.

### `GET /health`

Liveness probe. Returns `{"status": "ok", "version": "2.1.0"}`.

---

## Testing

```bash
python3 -m pip install pytest
python3 -m pytest tests/ -v
```

Or with Make:

```bash
make test
```

---

## Project Structure

```
ai-compliance-copilot/
├── app/
│   ├── main.py                  # FastAPI backend with request tracking
│   ├── compliance_engine.py     # Evaluation orchestrator
│   ├── llm_client.py            # Mock + OpenAI LLM integration
│   ├── risk_scoring.py          # Risk computation and summary
│   ├── report_generator.py     # PDF generation with Unicode sanitization
│   ├── utils.py                 # Shared utilities and registries
│   └── prompts/
│       ├── base.py              # Base evaluation prompt (strict rules)
│       ├── nist.py              # NIST AI RMF prompt
│       ├── hipaa.py             # HIPAA prompt
│       ├── nist_csf.py          # NIST CSF prompt
│       ├── fedramp.py           # FedRAMP prompt
│       ├── iso.py               # ISO 27001 prompt
│       ├── owasp.py             # OWASP LLM Top 10 prompt
│       ├── gdpr.py              # GDPR prompt
│       └── prompt_builder.py    # Prompt assembly
├── frontend/
│   └── streamlit_app.py         # Streamlit UI with sidebar + metrics
├── data/                        # 7 JSON control files (70 controls)
├── tests/                       # Pytest test suite
├── examples/                    # Sample input and output
├── reports/                     # Generated PDF reports
├── docs/
│   ├── architecture.md          # System design
│   └── prompt_design.md         # Prompt modularity
├── Dockerfile                   # Container image
├── docker-compose.yml           # Multi-service orchestration
├── Makefile                     # Development commands
├── .env.example                 # Environment template
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
├── test_cases.md               # Sample inputs for testing
└── README.md
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code standards, and how to add new frameworks.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and security considerations.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT — see [LICENSE](LICENSE).

# Architecture — AI Compliance Copilot v2

## Overview

AI Compliance Copilot is a modular, multi-framework compliance evaluation system. It follows a three-tier architecture: Streamlit frontend, FastAPI backend, and a pluggable evaluation pipeline backed by structured prompts and an LLM client.

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  ┌────────────┐  ┌───────────────┐  ┌────────────────────┐  │
│  │ Text Input  │  │  Framework    │  │  Run Analysis      │  │
│  │ (AI System) │  │  Dropdown     │  │  Button            │  │
│  └─────┬───────┘  └──────┬────────┘  └────────┬───────────┘  │
│        └─────────────────┼─────────────────────┘              │
└──────────────────────────┼────────────────────────────────────┘
                           │ POST /analyze
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                            │
│                      app/main.py                             │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  /analyze  →  Validates input → Calls engine          │   │
│  │  /frameworks → Lists supported frameworks             │   │
│  │  /health   →  Health check                            │   │
│  └───────────────────────┬───────────────────────────────┘   │
│                          │                                    │
│  ┌───────────────────────▼───────────────────────────────┐   │
│  │            Compliance Engine                           │   │
│  │         app/compliance_engine.py                       │   │
│  │  - Loads controls from JSON                            │   │
│  │  - Loops through controls one at a time                │   │
│  │  - Builds prompt via prompt_builder                    │   │
│  │  - Calls LLM client for each control                   │   │
│  │  - Aggregates results                                  │   │
│  └──────┬──────────────────┬─────────────────────────────┘   │
│         │                  │                                  │
│  ┌──────▼──────┐   ┌──────▼──────────────────────────────┐   │
│  │ LLM Client  │   │  Prompt Builder                     │   │
│  │ llm_client  │   │  prompts/prompt_builder.py           │   │
│  │ .call_llm() │   │  base.py + framework.py + control    │   │
│  └──────┬──────┘   └────────────────────────────────────┘   │
│         │                                                    │
│  ┌──────▼──────────────────────────────────────────────┐     │
│  │  Risk Scoring (risk_scoring.py)                      │     │
│  │  - Computes average risk score                       │     │
│  │  - Identifies high-risk controls                     │     │
│  │  - Generates risk summary                            │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │  Report Generator (report_generator.py)              │     │
│  │  - PDF with summary, table, recommendations          │     │
│  └─────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

## Components

### 1. FastAPI Backend (`app/main.py`)
- Exposes `/analyze`, `/frameworks`, and `/health` endpoints
- Validates input via Pydantic models
- Routes to the compliance engine

### 2. Compliance Engine (`app/compliance_engine.py`)
- Loads controls from JSON for the selected framework
- Evaluates each control individually (one prompt per control)
- Delegates prompt construction to the prompt builder
- Delegates evaluation to the LLM client
- Computes risk metrics via the risk scoring module

### 3. Prompt Builder (`app/prompts/prompt_builder.py`)
- Assembles: base prompt + framework prompt + control details + system description
- See [docs/prompt_design.md](prompt_design.md) for details

### 4. LLM Client (`app/llm_client.py`)
- Mock mode (default): keyword heuristic evaluation
- Real mode: OpenAI API integration (set `USE_REAL_LLM=true`)
- Falls back to mock if real LLM call fails

### 5. Risk Scoring (`app/risk_scoring.py`)
- Yes=0, Partial=0.5, No=1, averaged across controls
- Identifies high-risk controls and generates summary

### 6. Report Generator (`app/report_generator.py`)
- PDF output with summary, risk breakdown, results table, recommendations

### 7. Streamlit Frontend (`frontend/streamlit_app.py`)
- Framework dropdown with 7 options
- Risk score with color indicator
- Metrics row (total, compliant, partial, non-compliant)
- Interactive results table
- PDF download button

## Data Flow

```
User Input → Streamlit → POST /analyze → FastAPI
  → Compliance Engine
    → Load controls (JSON)
    → For each control:
        → Prompt Builder (base + framework + control + input)
        → LLM Client (mock or real)
        → Structured result
    → Risk Scoring (aggregate)
  → JSON Response → Streamlit renders results
  → Report Generator → PDF
```

## Supported Frameworks

| Key       | Framework           | Controls |
|-----------|---------------------|----------|
| nist      | NIST AI RMF         | 10       |
| hipaa     | HIPAA               | 10       |
| nist_csf  | NIST CSF            | 10       |
| fedramp   | FedRAMP             | 10       |
| iso       | ISO 27001           | 10       |
| owasp     | OWASP LLM Top 10   | 10       |
| gdpr      | GDPR                | 10       |

## Extensibility

- Add a new framework: create prompt file, JSON controls, register in utils and prompt_builder
- Swap to real LLM: set `USE_REAL_LLM=true` and `OPENAI_API_KEY`
- Integrate with CI/CD via the REST API

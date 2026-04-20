"""
FastAPI backend for AI Compliance Copilot.

Production-ready API with request tracking, structured error responses,
multi-framework analysis, compliance history, and JSON export.
"""

import json
import logging
import time
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.compliance_engine import analyze
from app.history import save_analysis, load_history, clear_history
from app.utils import FRAMEWORK_REGISTRY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Compliance Copilot",
    description=(
        "Evaluate AI systems against NIST AI RMF, HIPAA, NIST CSF, FedRAMP, "
        "ISO 27001, OWASP LLM Top 10, and GDPR compliance frameworks."
    ),
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_DESCRIPTION_LENGTH = 10_000


# ---------------------------------------------------------------------------
# Middleware: request ID + timing
# ---------------------------------------------------------------------------

@app.middleware("http")
async def add_request_metadata(request: Request, call_next):
    """Attach a unique request ID and measure response time."""
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 1)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = str(duration_ms)
    logger.info("request_id=%s method=%s path=%s status=%d duration=%sms",
                request_id, request.method, request.url.path, response.status_code, duration_ms)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception("Unhandled error request_id=%s: %s", request_id, exc)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "message": "An unexpected error occurred.", "request_id": request_id},
    )


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

SUPPORTED_KEYS = list(FRAMEWORK_REGISTRY.keys())


class AnalyzeRequest(BaseModel):
    system_description: str = Field(..., min_length=20, max_length=MAX_DESCRIPTION_LENGTH,
                                     description="Plain-text description of the AI system to evaluate.")
    framework: str = Field(..., description=f"Framework key. One of: {', '.join(SUPPORTED_KEYS)}")


class MultiAnalyzeRequest(BaseModel):
    """Evaluate against multiple frameworks in one request."""
    system_description: str = Field(..., min_length=20, max_length=MAX_DESCRIPTION_LENGTH,
                                     description="Plain-text description of the AI system to evaluate.")
    frameworks: list[str] = Field(..., min_length=1, description=f"List of framework keys: {', '.join(SUPPORTED_KEYS)}")


class RemediationItem(BaseModel):
    control_id: str
    control_title: str
    status: str
    severity: str
    risk_score: float
    priority_score: float
    recommendation: str
    gaps: list[str]


class ControlResult(BaseModel):
    control_id: str
    control_title: str
    status: str
    risk_score: float
    explanation: str
    evidence_found: list[str]
    gaps: list[str]
    recommendation: str
    severity: str = "medium"


class RiskSummary(BaseModel):
    risk_score: float
    interpretation: str
    total_controls: int
    compliant: int
    partial: int
    non_compliant: int
    high_risk_controls: list[dict[str, Any]]
    top_recommendations: list[str]


class AnalyzeResponse(BaseModel):
    framework: str
    framework_name: str
    risk_score: float = Field(..., ge=0, le=1)
    summary: str
    compliance_results: list[ControlResult]
    risk_summary: RiskSummary
    recommendations: list[str]
    remediation_plan: list[RemediationItem]
    prompt_injection_detected: bool
    human_review_recommended: bool


class ErrorResponse(BaseModel):
    error: str
    message: str
    request_id: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/analyze", response_model=AnalyzeResponse, summary="Analyze AI system compliance")
async def analyze_system(request: AnalyzeRequest, req: Request):
    """Evaluate an AI system description against a single compliance framework."""
    request_id = getattr(req.state, "request_id", "unknown")
    logger.info("request_id=%s framework=%s desc_length=%d",
                request_id, request.framework, len(request.system_description))
    try:
        result = analyze(request.system_description, request.framework)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Save to history
    save_analysis(result)
    return result


@app.post("/analyze/multi", summary="Multi-framework analysis")
async def analyze_multi(request: MultiAnalyzeRequest, req: Request):
    """Evaluate an AI system against multiple frameworks in one request."""
    request_id = getattr(req.state, "request_id", "unknown")
    logger.info("request_id=%s multi-framework=%s", request_id, request.frameworks)

    results = {}
    for fw in request.frameworks:
        try:
            result = analyze(request.system_description, fw)
            save_analysis(result)
            results[fw] = result
        except (FileNotFoundError, ValueError) as exc:
            results[fw] = {"error": str(exc)}

    # Build comparison summary
    comparison = []
    for fw, res in results.items():
        if "error" not in res:
            comparison.append({
                "framework": fw,
                "framework_name": res.get("framework_name", fw),
                "risk_score": res.get("risk_score", 0),
                "compliant": res.get("risk_summary", {}).get("compliant", 0),
                "partial": res.get("risk_summary", {}).get("partial", 0),
                "non_compliant": res.get("risk_summary", {}).get("non_compliant", 0),
            })

    return {"results": results, "comparison": comparison}


@app.get("/history", summary="Get analysis history")
async def get_history():
    """Return all historical analysis records."""
    return {"history": load_history()}


@app.delete("/history", summary="Clear analysis history")
async def delete_history():
    """Clear all historical analysis records."""
    count = clear_history()
    return {"deleted": count}


@app.get("/frameworks", summary="List supported frameworks")
async def list_frameworks():
    """Return all supported compliance frameworks with their display names."""
    return {"frameworks": FRAMEWORK_REGISTRY}


@app.get("/health", summary="Health check")
async def health():
    """Liveness probe for container orchestration."""
    return {"status": "ok", "version": "3.0.0"}

"""
FastAPI backend for AI Compliance Copilot.

Production-ready API with request tracking, structured error responses,
and comprehensive input validation.
"""

import logging
import time
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.compliance_engine import analyze
from app.utils import FRAMEWORK_REGISTRY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Compliance Copilot",
    description=(
        "Evaluate AI systems against NIST AI RMF, HIPAA, NIST CSF, FedRAMP, "
        "ISO 27001, OWASP LLM Top 10, and GDPR compliance frameworks."
    ),
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
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


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Return a structured error response for unhandled exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception("Unhandled error request_id=%s: %s", request_id, exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Please try again.",
            "request_id": request_id,
        },
    )


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

SUPPORTED_KEYS = list(FRAMEWORK_REGISTRY.keys())


class AnalyzeRequest(BaseModel):
    """Input payload for compliance analysis."""
    system_description: str = Field(
        ...,
        min_length=20,
        max_length=MAX_DESCRIPTION_LENGTH,
        description="Plain-text description of the AI system to evaluate.",
        json_schema_extra={"example": "A radiology AI that analyzes chest X-rays using patient DICOM images."},
    )
    framework: str = Field(
        ...,
        description=f"Compliance framework key. One of: {', '.join(SUPPORTED_KEYS)}",
        json_schema_extra={"example": "hipaa"},
    )


class ControlResult(BaseModel):
    control_id: str
    control_title: str
    status: str
    risk_score: float
    explanation: str
    evidence_found: list[str]
    gaps: list[str]
    recommendation: str


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
    """Structured compliance analysis output."""
    framework: str
    framework_name: str
    risk_score: float = Field(..., ge=0, le=1, description="Aggregate risk score from 0 (low) to 1 (high).")
    summary: str
    compliance_results: list[ControlResult]
    risk_summary: RiskSummary
    recommendations: list[str]
    prompt_injection_detected: bool
    human_review_recommended: bool


class ErrorResponse(BaseModel):
    error: str
    message: str
    request_id: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Analyze AI system compliance",
    description="Evaluate an AI system description against the selected compliance framework.",
)
async def analyze_system(request: AnalyzeRequest, req: Request):
    request_id = getattr(req.state, "request_id", "unknown")
    logger.info("request_id=%s framework=%s desc_length=%d",
                request_id, request.framework, len(request.system_description))

    try:
        result = analyze(request.system_description, request.framework)
    except FileNotFoundError as exc:
        logger.error("request_id=%s controls file missing: %s", request_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except ValueError as exc:
        logger.error("request_id=%s invalid request: %s", request_id, exc)
        raise HTTPException(status_code=400, detail=str(exc))

    if result.get("prompt_injection_detected"):
        logger.warning("request_id=%s prompt injection detected", request_id)

    return result


@app.get("/frameworks", summary="List supported frameworks")
async def list_frameworks():
    """Return all supported compliance frameworks with their display names."""
    return {"frameworks": FRAMEWORK_REGISTRY}


@app.get("/health", summary="Health check")
async def health():
    """Liveness probe for container orchestration."""
    return {"status": "ok", "version": "2.1.0"}

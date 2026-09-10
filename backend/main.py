"""
AeroSense-AI Weather Anomaly Detection & Monitoring Platform.

FastAPI Application Entrypoint (Prompts 3.6 & 3.20).
Initializes database schema, mounts modular routers under /api/v1, configures
CORS middleware, and provides structured custom exception handlers.
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure project root is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.config import settings
from backend.database.connection import init_db
from backend.routes import (
    anomalies_router,
    health_router,
    history_router,
    locations_router,
    predictions_router,
    weather_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("backend.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown hooks."""
    logger.info("⚡ Starting AeroSense-AI Weather Anomaly Platform...")
    try:
        init_db()
        logger.info("✅ Database tables and demo data ready.")
    except Exception as exc:
        logger.error(f"❌ Failed to initialize database on startup: {exc}", exc_info=True)
    yield
    logger.info("🛑 Shutting down AeroSense-AI Platform.")


# FastAPI Application Instance
app = FastAPI(
    title="AeroSense-AI Weather Anomaly Platform",
    description=(
        "AI/ML-Powered Weather Anomaly Detection, Monitoring, and Explainability Platform "
        "for Smart India Hackathon (SIH 2026). Detects compound climate departures relative "
        "to historical location- and season-specific normals."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Middleware (Prompt 3.6)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# Custom Exception Handlers (Prompt 3.20)
# ==============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Custom handler for HTTPExceptions (400, 404, etc.)."""
    logger.warning(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Custom handler for Pydantic v2 input validation errors (422 Unprocessable Entity)."""
    error_details = []
    for err in exc.errors():
        field_path = " -> ".join(str(loc) for loc in err.get("loc", []))
        error_details.append({
            "field": field_path,
            "message": err.get("msg"),
            "type": err.get("type"),
        })

    logger.warning(f"Validation error on {request.url.path}: {error_details}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "validation_error",
            "status_code": 422,
            "message": "Input validation failed. Please review the parameter constraints.",
            "errors": error_details,
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Maps unhandled ValueError exceptions to structured 400 Bad Request."""
    logger.warning(f"Bad Request (ValueError) on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "error",
            "status_code": 400,
            "message": str(exc),
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for uncaught server exceptions (500 Internal Server Error)."""
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "status_code": 500,
            "message": "An internal server error occurred. Please contact the administrator.",
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


# ==============================================================================
# Router Inclusions (Prompt 3.20)
# ==============================================================================

# API v1 Prefixed Routes
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(locations_router, prefix=settings.API_V1_STR)
app.include_router(weather_router, prefix=settings.API_V1_STR)
app.include_router(anomalies_router, prefix=settings.API_V1_STR)
app.include_router(history_router, prefix=settings.API_V1_STR)
app.include_router(predictions_router, prefix=settings.API_V1_STR)

# Direct Root Aliases (for backward compatibility and convenience)
app.include_router(health_router, include_in_schema=False)
app.include_router(locations_router, include_in_schema=False)
app.include_router(weather_router, include_in_schema=False)
app.include_router(anomalies_router, include_in_schema=False)
app.include_router(history_router, include_in_schema=False)
app.include_router(predictions_router, include_in_schema=False)


# Root Welcome Endpoint (Prompt 3.6)
@app.get("/", summary="Root Welcome Endpoint", tags=["Root"])
def root_welcome() -> Dict[str, Any]:
    """Root endpoint welcoming users and directing to interactive API documentation."""
    return {
        "platform": "AeroSense-AI Weather Anomaly Platform",
        "team": "Team ILLUMINATI (SIH 2026 - Problem SIH1642)",
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_v1_prefix": settings.API_V1_STR,
        "endpoints": {
            "health": f"{settings.API_V1_STR}/health",
            "locations": f"{settings.API_V1_STR}/locations",
            "weather": f"{settings.API_V1_STR}/weather/{{location}}",
            "anomalies": f"{settings.API_V1_STR}/anomalies",
            "history": f"{settings.API_V1_STR}/history/{{location}}?variable=temperature&days=30",
            "predict": f"{settings.API_V1_STR}/predict",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

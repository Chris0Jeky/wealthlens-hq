"""WealthLens UK — FastAPI backend.

Serves processed UK wealth inequality datasets as JSON for the Vue 3 frontend.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.error_handlers import register_error_handlers
from app.lifespan import lifespan
from app.logging_config import setup_logging
from app.logging_middleware import RequestLoggingMiddleware
from app.middleware import SecurityHeadersMiddleware
from app.routers import data
from app.timeout_middleware import TimeoutMiddleware

setup_logging(os.environ.get("LOG_LEVEL", "INFO"))

_started_at: float = time.time()


def _get_git_commit() -> str:
    """Return the short git commit hash, or 'dev' if unavailable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "dev"


_git_commit: str = _get_git_commit()

# ---------------------------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------------------------
# Override with the CORS_ORIGINS env var (comma-separated list of allowed
# origins).  Defaults to the local Vite dev server addresses so development
# works out of the box.
# ---------------------------------------------------------------------------
_default_origins = "http://localhost:3000,http://127.0.0.1:3000"
_raw = os.environ.get("CORS_ORIGINS", _default_origins)
cors_origins = [o.strip() for o in _raw.split(",") if o.strip()]
if not cors_origins:
    cors_origins = [o.strip() for o in _default_origins.split(",")]

tags_metadata = [
    {"name": "data", "description": "Dataset access and metadata endpoints"},
    {"name": "health", "description": "Service health and availability checks"},
]

app = FastAPI(
    title="WealthLens UK API",
    version="0.2.0",
    description=(
        "Open API for UK wealth inequality data. "
        "Serves processed datasets from the World Inequality Database, "
        "ONS, and HMRC as paginated JSON."
    ),
    contact={
        "name": "WealthLens UK",
        "url": "https://github.com/Chris0Jeky/wealthlens-hq",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.add_middleware(TimeoutMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
    max_age=3600,
)
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(RequestLoggingMiddleware)

register_error_handlers(app)

app.include_router(data.router, prefix="/api/data", tags=["data"])


@app.get("/api/health/data", tags=["health"], summary="Dataset availability check")
def health_data() -> dict:
    """Check which CSV datasets are present and readable.

    Returns overall status (healthy / degraded / unavailable) plus
    per-dataset availability and file size.
    """
    return data.health_data()


@app.get("/health", tags=["health"], summary="Liveness probe")
def health() -> dict:
    """Enhanced liveness probe with dataset availability info.

    Returns status, dataset count, and ISO timestamp for load balancers
    and uptime monitors.
    """
    return {
        "status": "healthy",
        "datasets_loaded": len(data.DATASETS),
        "timestamp": datetime.now(tz=UTC).isoformat(),
    }


@app.get("/api/version", tags=["health"], summary="API version and runtime info")
def version() -> dict:
    """Return API version, git commit, environment, and runtime details.

    Useful for debugging deployments, monitoring dashboards, and the
    frontend health status widget.
    """
    return {
        "version": app.version,
        "commit": _git_commit,
        "environment": os.environ.get("APP_ENV", "development"),
        "python_version": sys.version,
        "datasets_available": len(data.DATASETS),
        "uptime_seconds": round(time.time() - _started_at, 2),
    }

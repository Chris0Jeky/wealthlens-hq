"""WealthLens UK — FastAPI backend.

Serves processed UK wealth inequality datasets as JSON for the Vue 3 frontend.
"""

from __future__ import annotations

import logging
import os
import platform
import subprocess
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
from app.rate_limit import RateLimitMiddleware
from app.routers import data
from app.timeout_middleware import TimeoutMiddleware

setup_logging(os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger("wealthlens.main")

_started_at: float = time.time()


def _get_git_commit() -> str:
    """Return the short git commit hash, or 'unknown' if unavailable.

    Checks the GIT_COMMIT environment variable first (standard in CI/CD),
    then falls back to subprocess.  Gracefully handles missing git binary,
    missing .git directory, timeouts, and any other subprocess failures so
    CI environments without git still start cleanly.
    """
    env_commit = os.environ.get("GIT_COMMIT")
    if env_commit:
        return env_commit[:7]
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


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

_rate_limit_enabled = os.environ.get("RATE_LIMIT_ENABLED", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

if _rate_limit_enabled:
    _rpm_raw = os.environ.get("RATE_LIMIT_RPM", "60")
    try:
        _rpm = max(int(_rpm_raw), 1)
    except (ValueError, TypeError):
        logger.warning("Invalid RATE_LIMIT_RPM value %r, defaulting to 60", _rpm_raw)
        _rpm = 60

    app.add_middleware(RateLimitMiddleware, requests_per_minute=_rpm)
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
    and uptime monitors.  Preserves backward-compatible ``"status": "ok"``
    while adding new informational fields.
    """
    return {
        "status": "ok",
        "datasets_loaded": len(data.DATASETS),
        "timestamp": datetime.now(tz=UTC).isoformat(),
    }


@app.get("/api/version", tags=["health"], summary="API version info")
def version() -> dict:
    """Return public API version metadata.

    Only exposes fields safe for unauthenticated access and consumed by
    the frontend health status widget: version, dataset count, and status.
    """
    return {
        "version": app.version,
        "datasets_available": len(data.DATASETS),
        "status": "ok",
    }


@app.get("/api/version/debug", tags=["health"], summary="Debug runtime info")
def version_debug() -> dict:
    """Return detailed runtime info for debugging deployments.

    Only available in non-production environments.  Returns 404 when
    APP_ENV is set to 'production'.
    """
    from fastapi import HTTPException

    if os.environ.get("APP_ENV") == "production":
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "version": app.version,
        "commit": _git_commit,
        "environment": os.environ.get("APP_ENV", "development"),
        "python_version": platform.python_version(),
        "datasets_available": len(data.DATASETS),
        "uptime_seconds": round(time.time() - _started_at, 2),
    }

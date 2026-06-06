"""WealthLens UK — FastAPI backend.

Serves processed UK wealth inequality datasets as JSON for the Vue 3 frontend.
"""

from __future__ import annotations

import logging
import os
import platform
import time
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.error_handlers import register_error_handlers
from app.lifespan import lifespan
from app.logging_config import setup_logging
from app.logging_middleware import RequestLoggingMiddleware
from app.middleware import SecurityHeadersMiddleware
from app.rate_limit import RateLimitMiddleware
from app.routers import data, simulator
from app.timeout_middleware import TimeoutMiddleware

setup_logging(os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger("wealthlens.main")

_started_at: float = time.time()


def _get_git_commit() -> str:
    """Return the short git commit hash, or 'unknown' if unavailable.

    Checks the GIT_COMMIT environment variable first (standard in CI/CD),
    then falls back to reading local Git metadata. Gracefully handles
    packaged deployments and CI environments without a .git directory.
    """
    env_commit = os.environ.get("GIT_COMMIT")
    if env_commit:
        return env_commit[:7]

    repo_root = Path(__file__).resolve().parents[4]
    git_dir = _resolve_git_dir(repo_root)
    if git_dir is None:
        return "unknown"

    commit = _read_git_head(git_dir)
    if commit:
        return commit[:7]
    return "unknown"


def _resolve_git_dir(repo_root: Path) -> Path | None:
    """Resolve the Git metadata directory for normal and worktree checkouts."""
    dot_git = repo_root / ".git"
    try:
        if dot_git.is_dir():
            return dot_git
        if dot_git.is_file():
            marker = dot_git.read_text(encoding="utf-8").strip()
            if marker.startswith("gitdir:"):
                git_dir = Path(marker.removeprefix("gitdir:").strip())
                if not git_dir.is_absolute():
                    git_dir = (repo_root / git_dir).resolve()
                return git_dir
    except OSError:
        return None
    return None


def _read_git_head(git_dir: Path) -> str | None:
    """Read the current commit hash directly from Git metadata."""
    try:
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
        if not head:
            return None
        if not head.startswith("ref:"):
            return head

        ref = head.removeprefix("ref:").strip()
        ref_path = git_dir / ref
        if ref_path.is_file():
            return ref_path.read_text(encoding="utf-8").strip()

        packed_refs = git_dir / "packed-refs"
        if packed_refs.is_file():
            for line in packed_refs.read_text(encoding="utf-8").splitlines():
                if line.startswith("#") or line.startswith("^"):
                    continue
                parts = line.split(" ", 1)
                if len(parts) == 2 and parts[1] == ref:
                    return parts[0]
    except OSError:
        return None
    return None


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
    {"name": "simulator", "description": "WealthLens-Sim scenario dashboard results"},
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
app.include_router(simulator.router, prefix="/api/simulator", tags=["simulator"])


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
        # Clamp at 0: an NTP step-back could otherwise report a negative uptime.
        "uptime_seconds": round(max(0.0, time.time() - _started_at), 2),
    }

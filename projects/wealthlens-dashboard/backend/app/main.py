"""WealthLens UK — FastAPI backend.

Serves processed UK wealth inequality datasets as JSON for the Vue 3 frontend.
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.lifespan import lifespan
from app.logging_config import setup_logging
from app.middleware import SecurityHeadersMiddleware
from app.routers import data
from app.timeout_middleware import TimeoutMiddleware

setup_logging(os.environ.get("LOG_LEVEL", "INFO"))

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
    version="0.1.0",
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

app.include_router(data.router, prefix="/api/data", tags=["data"])


@app.get("/api/health/data", tags=["health"], summary="Dataset availability check")
def health_data() -> dict:
    """Check which CSV datasets are present and readable.

    Returns overall status (healthy / degraded / unavailable) plus
    per-dataset availability and file size.
    """
    return data.health_data()


@app.get("/health", tags=["health"], summary="Liveness probe")
def health() -> dict[str, str]:
    """Minimal liveness check for load balancers and uptime monitors.

    Returns ``{"status": "ok"}`` when the process is running.
    """
    return {"status": "ok"}

"""WealthLens UK — FastAPI backend.

Serves processed UK wealth inequality datasets as JSON for the Vue 3 frontend.
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.logging_config import configure_logging
from app.routers import data

# ---------------------------------------------------------------------------
# Logging — structured JSON to stdout for production monitoring
# ---------------------------------------------------------------------------
configure_logging()

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

app = FastAPI(
    title="WealthLens UK API",
    version="0.1.0",
    description="Open API for UK wealth inequality data",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(data.router, prefix="/api/data", tags=["data"])


@app.get("/api/health/data", tags=["health"])
def health_data() -> dict:
    """Dataset availability check — delegates to the data module."""
    return data.health_data()


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}

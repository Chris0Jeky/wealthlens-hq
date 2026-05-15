"""WealthLens UK — FastAPI backend.

Serves processed UK wealth inequality datasets as JSON for the Vue 3 frontend.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import data
from app.routers.data import health_data

app = FastAPI(
    title="WealthLens UK API",
    version="0.1.0",
    description="Open API for UK wealth inequality data",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(data.router, prefix="/api/data", tags=["data"])

# Register the data-health check separately so it lives at /api/health/data
# rather than under the /api/data prefix.
app.get("/api/health/data", tags=["health"])(health_data)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}

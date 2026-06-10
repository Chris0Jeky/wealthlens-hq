"""FastAPI application factory.

Kept tiny on purpose: routes live in routes.py, enforcement in
budget/middleware.py, configuration in config.py. OTel/Langfuse
instrumentation is attached here when H1-28 lands.

Run locally with `make dev` (uvicorn, 127.0.0.1:8100).
"""

from __future__ import annotations

from fastapi import FastAPI

from wealthlens_analyst.api.routes import router


def create_app() -> FastAPI:
    """Build the application instance."""
    app = FastAPI(
        title="WealthLens Analyst",
        description=(
            "Evidence-backed research analyst over official UK wealth "
            "statistics. Citation-first answers with honest abstention."
        ),
        version="0.1.0.dev0",
    )
    app.include_router(router)
    return app

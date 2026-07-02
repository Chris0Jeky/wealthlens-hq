"""FastAPI application factory.

Kept tiny on purpose: routes live in routes.py, enforcement in
budget/middleware.py, configuration in config.py. OTel/Langfuse
instrumentation is attached here when H1-28 lands.

The application owns ONE shared SQLAlchemy engine (created at startup,
disposed at shutdown) so the request path never builds a connection pool
per query — search_fts/search_dense receive it via the get_engine
dependency in routes.py (H1-13).

Run locally with `make dev` (uvicorn, 127.0.0.1:8100).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from wealthlens_analyst.api.routes import router
from wealthlens_analyst.config import load_settings
from wealthlens_analyst.db import engine_from_settings


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create the shared engine at startup; dispose its pool at shutdown.

    engine_from_settings fails loudly when DATABASE_URL is unset, so a
    misconfigured deployment dies at startup instead of 500-ing on the first
    query. Engine creation itself opens no connection (SQLAlchemy pools
    lazily); /healthz is the first thing that actually touches the database.
    """
    engine = engine_from_settings(load_settings())
    app.state.engine = engine
    try:
        yield
    finally:
        engine.dispose()


def create_app() -> FastAPI:
    """Build the application instance."""
    app = FastAPI(
        title="WealthLens Analyst",
        description=(
            "Evidence-backed research analyst over official UK wealth "
            "statistics. Citation-first answers with honest abstention."
        ),
        version="0.1.0.dev0",
        lifespan=_lifespan,
    )
    app.include_router(router)
    return app

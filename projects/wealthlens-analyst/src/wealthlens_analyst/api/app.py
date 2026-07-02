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

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from wealthlens_analyst.api.routes import router
from wealthlens_analyst.config import load_settings
from wealthlens_analyst.db import engine_from_settings
from wealthlens_analyst.llm.client import get_client


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create the shared engine at startup; dispose its pool at shutdown.

    Startup validates the WHOLE configuration the request path needs, so a
    misconfigured deployment dies at startup instead of 500-ing on the first
    query: engine_from_settings fails loudly when DATABASE_URL is unset, and
    get_client() fails loudly when OPENAI_API_KEY / EMBEDDING_MODEL are unset
    (the dense leg would need them on every /ask). Neither opens a connection
    or spends anything — get_client's result is discarded; SQLAlchemy pools
    lazily, so /healthz is the first thing that actually touches the database.
    """
    # Uvicorn configures only its own loggers, so without this the package's
    # INFO logs (notably search_dense's per-request embedding cost — visible
    # cost is a product goal) are silently dropped under `make dev`.
    # basicConfig is a no-op when the deployment already configured the root
    # logger, so this never overrides real logging config.
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    engine = engine_from_settings(load_settings())
    try:
        get_client()  # result discarded — this is the config validation only
        app.state.engine = engine
        yield
    finally:
        # Covers the validation failure too: an engine created and then
        # abandoned on a get_client() raise must still release its pool.
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

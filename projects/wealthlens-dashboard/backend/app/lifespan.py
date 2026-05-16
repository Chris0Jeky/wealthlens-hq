"""FastAPI lifespan context manager for startup and shutdown hooks."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger("wealthlens")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown."""
    logger.info("Starting WealthLens API")
    _warm_metadata_cache()
    yield
    logger.info("Shutting down WealthLens API")


def _warm_metadata_cache() -> None:
    """Pre-populate the metadata cache so the first request is fast."""
    from app.routers.data import DATASETS, _build_metadata

    for name in DATASETS:
        try:
            _build_metadata(name)
            logger.info("Cached metadata for %s", name)
        except Exception:
            logger.warning("Could not cache metadata for %s — CSV may be missing", name, exc_info=True)

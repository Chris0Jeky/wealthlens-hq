"""Cache-Control header utilities for static dataset responses."""

from __future__ import annotations

from starlette.responses import Response


def add_cache_headers(response: Response, *, max_age: int) -> None:
    """Set Cache-Control and Vary headers on a response."""
    response.headers["Cache-Control"] = f"public, max-age={max_age}"
    response.headers["Vary"] = "Accept-Encoding"

"""Standardized error response handlers for the WealthLens API.

Ensures all error responses follow a consistent JSON envelope:
{
    "error": {
        "code": <HTTP status code>,
        "message": <human-readable message>,
        "type": <error classification>
    }
}
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("wealthlens.errors")


def _error_response(status_code: int, message: str, error_type: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": status_code,
                "message": message,
                "type": error_type,
            }
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    error_type = "not_found" if exc.status_code == 404 else "http_error"
    if exc.status_code == 503:
        error_type = "unavailable"
    if exc.status_code >= 500:
        logger.error("HTTP %d on %s: %s", exc.status_code, request.url.path, exc.detail)
        message = "Service temporarily unavailable" if exc.status_code == 503 else "Server error"
    else:
        message = str(exc.detail)
    return _error_response(exc.status_code, message, error_type)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    messages = []
    for err in exc.errors():
        loc_parts = [str(part) for part in err["loc"]]
        if loc_parts and loc_parts[0] in ("body", "query", "path", "header"):
            loc_parts = loc_parts[1:]
        loc = " -> ".join(loc_parts) if loc_parts else "input"
        messages.append(f"{loc}: {err['msg']}")
    return _error_response(422, "; ".join(messages), "validation_error")


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return _error_response(500, "Internal server error", "internal_error")


def register_error_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the app."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)

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

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


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
    return _error_response(exc.status_code, str(exc.detail), error_type)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    messages = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err["loc"])
        messages.append(f"{loc}: {err['msg']}")
    return _error_response(422, "; ".join(messages), "validation_error")


def register_error_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the app."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

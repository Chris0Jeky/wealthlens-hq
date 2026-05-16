"""Tests for standardized error response handlers.

Verifies that:
- HTTPException with 4xx returns the correct error envelope.
- HTTPException with 5xx sanitizes the message (no internal detail leakage).
- Unhandled exceptions return 500 with a generic message.
- Validation errors return 422 with field-level detail.
- The error envelope structure matches {error: {code, message, type}}.
"""

from __future__ import annotations

from app.error_handlers import register_error_handlers
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient


def _make_app() -> FastAPI:
    """Create a minimal FastAPI app with error handlers registered."""
    app = FastAPI()
    register_error_handlers(app)
    return app


# ---------------------------------------------------------------------------
# Tests — 4xx pass-through
# ---------------------------------------------------------------------------


class TestHTTPException4xx:
    """4xx errors should pass through the original detail message."""

    def test_400_returns_error_envelope(self) -> None:
        app = _make_app()

        @app.get("/bad")
        def _bad() -> None:
            raise HTTPException(status_code=400, detail="Missing required field")

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/bad")

        assert resp.status_code == 400
        body = resp.json()
        assert body == {
            "error": {
                "code": 400,
                "message": "Missing required field",
                "type": "http_error",
            }
        }

    def test_404_returns_not_found_type(self) -> None:
        app = _make_app()

        @app.get("/missing")
        def _missing() -> None:
            raise HTTPException(status_code=404, detail="Dataset not found")

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/missing")

        assert resp.status_code == 404
        body = resp.json()
        assert body["error"]["type"] == "not_found"
        assert body["error"]["message"] == "Dataset not found"
        assert body["error"]["code"] == 404

    def test_422_via_http_exception(self) -> None:
        """A manually raised 422 HTTPException uses http_error type."""
        app = _make_app()

        @app.get("/unprocessable")
        def _unprocessable() -> None:
            raise HTTPException(status_code=422, detail="Invalid date range")

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/unprocessable")

        assert resp.status_code == 422
        body = resp.json()
        assert body["error"]["type"] == "http_error"
        assert body["error"]["message"] == "Invalid date range"

    def test_4xx_with_dict_detail(self) -> None:
        """Non-string detail (dict) is stringified in the error message."""
        app = _make_app()

        @app.get("/structured")
        def _structured() -> None:
            raise HTTPException(status_code=400, detail={"fields": ["name"]})

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/structured")

        assert resp.status_code == 400
        body = resp.json()
        assert body["error"]["code"] == 400
        assert isinstance(body["error"]["message"], str)
        assert body["error"]["type"] == "http_error"


# ---------------------------------------------------------------------------
# Tests — 5xx sanitization
# ---------------------------------------------------------------------------


class TestHTTPException5xx:
    """5xx errors should NOT leak internal details to the client."""

    def test_500_sanitizes_message(self) -> None:
        app = _make_app()

        @app.get("/crash")
        def _crash() -> None:
            raise HTTPException(
                status_code=500,
                detail="psycopg2.OperationalError: connection refused",
            )

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/crash")

        assert resp.status_code == 500
        body = resp.json()
        assert body["error"]["message"] == "Server error"
        assert body["error"]["type"] == "http_error"
        assert body["error"]["code"] == 500
        # Internal detail must NOT appear in the response
        assert "psycopg2" not in resp.text

    def test_503_returns_unavailable_type(self) -> None:
        app = _make_app()

        @app.get("/down")
        def _down() -> None:
            raise HTTPException(status_code=503, detail="DB pool exhausted")

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/down")

        assert resp.status_code == 503
        body = resp.json()
        assert body["error"]["type"] == "unavailable"
        assert body["error"]["message"] == "Service temporarily unavailable"
        assert body["error"]["code"] == 503
        # Internal detail must NOT appear in the response
        assert "DB pool" not in resp.text

    def test_502_sanitizes_and_uses_http_error_type(self) -> None:
        app = _make_app()

        @app.get("/gateway")
        def _gateway() -> None:
            raise HTTPException(
                status_code=502, detail="upstream timeout at 10.0.0.5:5432"
            )

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/gateway")

        assert resp.status_code == 502
        body = resp.json()
        assert body["error"]["type"] == "http_error"
        assert body["error"]["message"] == "Server error"
        assert body["error"]["code"] == 502
        assert "upstream" not in resp.text


# ---------------------------------------------------------------------------
# Tests — Unhandled exceptions
# ---------------------------------------------------------------------------


class TestUnhandledException:
    """Unhandled exceptions should return a generic 500 response."""

    def test_unhandled_returns_500_generic(self) -> None:
        app = _make_app()

        @app.get("/explode")
        def _explode() -> None:
            raise RuntimeError("segfault in C extension")

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/explode")

        assert resp.status_code == 500
        body = resp.json()
        assert body == {
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "internal_error",
            }
        }
        # Internal detail must NOT appear in the response
        assert "segfault" not in resp.text

    def test_unhandled_key_error(self) -> None:
        app = _make_app()

        @app.get("/key-err")
        def _key_err() -> dict:
            d: dict[str, str] = {}
            return {"v": d["missing"]}

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/key-err")

        assert resp.status_code == 500
        body = resp.json()
        assert body["error"]["type"] == "internal_error"
        assert body["error"]["message"] == "Internal server error"


# ---------------------------------------------------------------------------
# Tests — Validation errors (RequestValidationError)
# ---------------------------------------------------------------------------


class TestValidationError:
    """FastAPI validation errors should return 422 with field detail."""

    def test_missing_required_query_param(self) -> None:
        app = _make_app()

        @app.get("/items")
        def _items(year: int) -> dict:
            return {"year": year}

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/items")

        assert resp.status_code == 422
        body = resp.json()
        assert body["error"]["code"] == 422
        assert body["error"]["type"] == "validation_error"
        # Message should reference the field name
        assert "year" in body["error"]["message"]

    def test_invalid_type_query_param(self) -> None:
        app = _make_app()

        @app.get("/items")
        def _items(year: int) -> dict:
            return {"year": year}

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/items", params={"year": "not-a-number"})

        assert resp.status_code == 422
        body = resp.json()
        assert body["error"]["code"] == 422
        assert body["error"]["type"] == "validation_error"
        assert "year" in body["error"]["message"]


# ---------------------------------------------------------------------------
# Tests — Envelope structure
# ---------------------------------------------------------------------------


class TestEnvelopeStructure:
    """The error envelope must always have exactly {error: {code, message, type}}."""

    def test_envelope_keys_are_exact(self) -> None:
        app = _make_app()

        @app.get("/err")
        def _err() -> None:
            raise HTTPException(status_code=400, detail="bad")

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/err")
        body = resp.json()

        # Top level has only "error"
        assert set(body.keys()) == {"error"}
        # Inner object has exactly code, message, type
        assert set(body["error"].keys()) == {"code", "message", "type"}

    def test_code_is_integer(self) -> None:
        app = _make_app()

        @app.get("/err")
        def _err() -> None:
            raise HTTPException(status_code=404, detail="gone")

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/err")
        body = resp.json()

        assert isinstance(body["error"]["code"], int)

    def test_message_is_string(self) -> None:
        app = _make_app()

        @app.get("/err")
        def _err() -> None:
            raise HTTPException(status_code=400, detail="oops")

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/err")
        body = resp.json()

        assert isinstance(body["error"]["message"], str)

    def test_type_is_string(self) -> None:
        app = _make_app()

        @app.get("/err")
        def _err() -> None:
            raise HTTPException(status_code=400, detail="oops")

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/err")
        body = resp.json()

        assert isinstance(body["error"]["type"], str)

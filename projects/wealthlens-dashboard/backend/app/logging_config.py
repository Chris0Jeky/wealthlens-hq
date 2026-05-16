"""Structured JSON logging configuration for the WealthLens backend.

Produces one JSON object per log line with fields: timestamp, level, logger,
message.  Exception info includes exc_type, exc_message, and full traceback.

Note: log messages may contain user-supplied data. Operators should configure
log redaction in their aggregator for production deployments.

Usage:
    from app.logging_config import configure_logging
    configure_logging()
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, str] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exc_type"] = record.exc_info[0].__name__
            exc_value = record.exc_info[1]
            log_entry["exc_message"] = str(exc_value) if exc_value else ""
            log_entry["traceback"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def configure_logging(log_level: str | None = None) -> None:
    """Set up structured JSON logging on the root logger.

    Parameters
    ----------
    log_level:
        Logging level name (e.g. "DEBUG", "INFO").  Falls back to the
        ``LOG_LEVEL`` environment variable, then to "INFO".
    """
    level = log_level or os.environ.get("LOG_LEVEL", "INFO")

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(level.upper())
    # Avoid duplicate handlers on repeated calls (e.g. tests).
    root.handlers = [handler]

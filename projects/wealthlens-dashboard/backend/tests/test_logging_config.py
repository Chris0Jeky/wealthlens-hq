"""Tests for structured JSON logging configuration."""

from __future__ import annotations

import json
import logging
import os
from unittest.mock import patch

import pytest

from app.logging_config import JsonFormatter, configure_logging


class TestJsonFormatter:
    """Verify JsonFormatter produces valid, complete JSON log lines."""

    def setup_method(self) -> None:
        self.formatter = JsonFormatter()

    def test_output_is_valid_json(self) -> None:
        record = logging.LogRecord(
            name="test.module",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="hello world",
            args=None,
            exc_info=None,
        )
        output = self.formatter.format(record)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_expected_keys_present(self) -> None:
        record = logging.LogRecord(
            name="test.module",
            level=logging.WARNING,
            pathname="test.py",
            lineno=10,
            msg="something happened",
            args=None,
            exc_info=None,
        )
        parsed = json.loads(self.formatter.format(record))
        assert set(parsed.keys()) == {"timestamp", "level", "logger", "message"}
        assert parsed["level"] == "WARNING"
        assert parsed["logger"] == "test.module"
        assert parsed["message"] == "something happened"

    def test_timestamp_is_iso8601(self) -> None:
        record = logging.LogRecord(
            name="t",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="x",
            args=None,
            exc_info=None,
        )
        parsed = json.loads(self.formatter.format(record))
        # ISO 8601 with timezone offset (e.g. +00:00)
        assert "T" in parsed["timestamp"]
        assert "+" in parsed["timestamp"] or "Z" in parsed["timestamp"]

    def test_exception_info_included(self) -> None:
        try:
            raise ValueError("bad value")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="exc.test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=5,
            msg="failure",
            args=None,
            exc_info=exc_info,
        )
        parsed = json.loads(self.formatter.format(record))
        assert parsed["exc_type"] == "ValueError"
        assert parsed["exc_message"] == "bad value"
        assert "traceback" in parsed
        assert "ValueError: bad value" in parsed["traceback"]


class TestConfigureLogging:
    """Verify configure_logging sets up the root logger correctly."""

    def teardown_method(self) -> None:
        # Reset root logger to avoid test pollution.
        root = logging.getLogger()
        root.handlers = []
        root.setLevel(logging.WARNING)

    def test_installs_json_formatter_handler(self) -> None:
        configure_logging()
        root = logging.getLogger()
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, JsonFormatter)

    def test_default_level_is_info(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            # Ensure LOG_LEVEL is not set
            os.environ.pop("LOG_LEVEL", None)
            configure_logging()
        root = logging.getLogger()
        assert root.level == logging.INFO

    def test_log_level_env_var_respected(self) -> None:
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            configure_logging()
        root = logging.getLogger()
        assert root.level == logging.DEBUG

    def test_explicit_level_parameter_overrides_env(self) -> None:
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            configure_logging(log_level="ERROR")
        root = logging.getLogger()
        assert root.level == logging.ERROR

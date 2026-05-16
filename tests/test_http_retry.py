"""Tests for the HTTP retry utility."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "automation" / "data-pipelines"))

from http_retry import fetch_with_retry


def _mock_response(status_code: int = 200) -> MagicMock:
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    return resp


def test_success_on_first_attempt():
    with patch("http_retry.requests.get", return_value=_mock_response(200)) as mock_get:
        resp = fetch_with_retry("https://example.com", max_retries=3)
    assert resp.status_code == 200
    assert mock_get.call_count == 1


def test_retries_on_500_then_succeeds():
    responses = [_mock_response(500), _mock_response(200)]
    with (
        patch("http_retry.requests.get", side_effect=responses) as mock_get,
        patch("http_retry.time.sleep"),
    ):
        resp = fetch_with_retry("https://example.com", max_retries=3)
    assert resp.status_code == 200
    assert mock_get.call_count == 2


def test_retries_on_connection_error_then_succeeds():
    side_effects = [requests.ConnectionError("fail"), _mock_response(200)]
    with (
        patch("http_retry.requests.get", side_effect=side_effects) as mock_get,
        patch("http_retry.time.sleep"),
    ):
        resp = fetch_with_retry("https://example.com", max_retries=3)
    assert resp.status_code == 200
    assert mock_get.call_count == 2


def test_raises_after_all_retries_exhausted():
    with (
        patch("http_retry.requests.get", side_effect=requests.Timeout("timeout")),
        patch("http_retry.time.sleep"),
        pytest.raises(requests.Timeout),
    ):
        fetch_with_retry("https://example.com", max_retries=2)


def test_does_not_retry_on_4xx():
    with patch("http_retry.requests.get", return_value=_mock_response(404)) as mock_get:
        resp = fetch_with_retry("https://example.com", max_retries=3)
    assert resp.status_code == 404
    assert mock_get.call_count == 1


def test_backoff_sleep_called_with_increasing_delays():
    with (
        patch("http_retry.requests.get", side_effect=requests.Timeout("timeout")),
        patch("http_retry.time.sleep") as mock_sleep,
        pytest.raises(requests.Timeout),
    ):
        fetch_with_retry("https://example.com", max_retries=3, backoff_base=2.0)
    delays = [call.args[0] for call in mock_sleep.call_args_list]
    assert delays == [1.0, 2.0, 4.0]  # 2^0, 2^1, 2^2

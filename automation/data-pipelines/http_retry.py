"""HTTP request helper with exponential backoff retry."""

from __future__ import annotations

import logging
import time

import requests

logger = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE = 2.0
DEFAULT_BACKOFF_MAX = 30.0


def fetch_with_retry(
    url: str,
    *,
    timeout: int = 60,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_base: float = DEFAULT_BACKOFF_BASE,
    backoff_max: float = DEFAULT_BACKOFF_MAX,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
) -> requests.Response:
    """GET a URL with exponential backoff on transient failures.

    Retries on connection errors, timeouts, and 5xx status codes.
    Raises the last exception after all retries are exhausted.
    """
    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(url, timeout=timeout, headers=headers, params=params)
            if resp.status_code < 500:
                return resp
            logger.warning(
                "Attempt %d/%d: %s returned %d",
                attempt + 1, max_retries + 1, url, resp.status_code,
            )
            last_exc = requests.HTTPError(f"Server error {resp.status_code}", response=resp)
        except (requests.ConnectionError, requests.Timeout) as exc:
            logger.warning(
                "Attempt %d/%d: %s failed: %s",
                attempt + 1, max_retries + 1, url, exc,
            )
            last_exc = exc

        if attempt < max_retries:
            delay = min(backoff_base ** attempt, backoff_max)
            logger.info("Retrying in %.1fs...", delay)
            time.sleep(delay)

    raise last_exc  # type: ignore[misc]

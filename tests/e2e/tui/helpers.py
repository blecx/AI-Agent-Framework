"""Deterministic helper utilities for TUI E2E tests."""

from __future__ import annotations

import time

import httpx


def wait_for_http_ok(
    url: str, timeout_seconds: float = 10.0, attempt_timeout: float = 0.5
) -> None:
    """Wait until an HTTP endpoint responds with 200, else raise TimeoutError."""
    start_time = time.monotonic()
    with httpx.Client(timeout=timeout_seconds) as client:
        while True:
            remaining = timeout_seconds - (time.monotonic() - start_time)
            if remaining <= 0:
                break

            timeout = min(attempt_timeout, remaining)
            try:
                response = client.get(url, timeout=timeout)
                if response.status_code == 200:
                    return
            except (httpx.ConnectError, httpx.ReadTimeout):
                pass

    raise TimeoutError(
        f"Endpoint did not become healthy in {timeout_seconds:.1f}s: {url}"
    )

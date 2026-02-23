#!/usr/bin/env python3
"""Unit tests for LLM request throttle and env configuration."""

from agents.llm_client import LLMClientFactory, _LLMRequestThrottle


class _FakeClock:
    def __init__(self):
        self.now_value = 0.0
        self.sleeps: list[float] = []

    def now(self) -> float:
        return self.now_value

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now_value += seconds


def test_rps_settings_use_safe_defaults(monkeypatch):
    monkeypatch.delenv("WORK_ISSUE_MAX_RPS", raising=False)
    monkeypatch.delenv("WORK_ISSUE_RPS_JITTER", raising=False)

    max_rps, jitter_ratio = LLMClientFactory._get_rps_settings()

    assert max_rps == 0.2
    assert jitter_ratio == 0.1


def test_rps_settings_fallback_for_invalid_values(monkeypatch):
    monkeypatch.setenv("WORK_ISSUE_MAX_RPS", "0")
    monkeypatch.setenv("WORK_ISSUE_RPS_JITTER", "not-a-number")

    max_rps, jitter_ratio = LLMClientFactory._get_rps_settings()

    assert max_rps == 0.2
    assert jitter_ratio == 0.1


async def test_throttle_enforces_min_interval_without_jitter():
    fake = _FakeClock()
    throttle = _LLMRequestThrottle(
        max_rps=2.0,
        jitter_ratio=0.0,
        clock=fake.now,
        sleeper=fake.sleep,
        jitter_fn=lambda low, high: 0.0,
    )

    await throttle.acquire()
    await throttle.acquire()
    await throttle.acquire()

    assert fake.sleeps == [0.5, 0.5]


async def test_throttle_adds_positive_jitter_without_breaking_max_rps():
    fake = _FakeClock()
    throttle = _LLMRequestThrottle(
        max_rps=1.0,
        jitter_ratio=0.2,
        clock=fake.now,
        sleeper=fake.sleep,
        jitter_fn=lambda low, high: high,
    )

    await throttle.acquire()
    await throttle.acquire()

    assert len(fake.sleeps) == 1
    assert fake.sleeps[0] == 1.2


def test_shared_throttle_reuses_instance_for_same_settings(monkeypatch):
    monkeypatch.setenv("WORK_ISSUE_MAX_RPS", "0.25")
    monkeypatch.setenv("WORK_ISSUE_RPS_JITTER", "0.2")

    LLMClientFactory._shared_request_throttle = None
    LLMClientFactory._shared_request_throttle_key = None

    first = LLMClientFactory._get_shared_request_throttle()
    second = LLMClientFactory._get_shared_request_throttle()

    assert first is second

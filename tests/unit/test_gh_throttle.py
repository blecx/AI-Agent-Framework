import subprocess

from agents.tooling import gh_throttle


def test_run_gh_throttled_retries_on_rate_limit(monkeypatch):
    monkeypatch.setattr(gh_throttle, "_LAST_GH_CALL_TS", None)
    monkeypatch.setenv("GH_THROTTLE_MAX_ATTEMPTS", "3")
    monkeypatch.setenv("GH_THROTTLE_BACKOFF_SECONDS", "1")

    run_calls = {"count": 0}
    sleep_calls = []

    def _fake_run(command, **kwargs):
        run_calls["count"] += 1
        if run_calls["count"] == 1:
            return subprocess.CompletedProcess(
                command,
                1,
                stdout="",
                stderr="secondary rate limit hit, retry after 1 seconds",
            )
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    def _fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr(subprocess, "run", _fake_run)
    monkeypatch.setattr(gh_throttle.time, "sleep", _fake_sleep)

    result = gh_throttle.run_gh_throttled(["gh", "issue", "list"], text=True)

    assert result.returncode == 0
    assert run_calls["count"] == 2
    assert sleep_calls
    assert sleep_calls[0] >= 1


def test_run_gh_throttled_does_not_retry_on_non_rate_limit(monkeypatch):
    monkeypatch.setattr(gh_throttle, "_LAST_GH_CALL_TS", None)
    monkeypatch.setenv("GH_THROTTLE_MAX_ATTEMPTS", "5")

    run_calls = {"count": 0}

    def _fake_run(command, **kwargs):
        run_calls["count"] += 1
        return subprocess.CompletedProcess(
            command,
            1,
            stdout="",
            stderr="validation failed",
        )

    monkeypatch.setattr(subprocess, "run", _fake_run)

    result = gh_throttle.run_gh_throttled(["gh", "issue", "list"], text=True)

    assert result.returncode == 1
    assert run_calls["count"] == 1


def test_run_gh_throttled_check_true_raises_after_retries(monkeypatch):
    monkeypatch.setattr(gh_throttle, "_LAST_GH_CALL_TS", None)
    monkeypatch.setenv("GH_THROTTLE_MAX_ATTEMPTS", "2")
    monkeypatch.setenv("GH_THROTTLE_BACKOFF_SECONDS", "1")

    run_calls = {"count": 0}

    def _fake_run(command, **kwargs):
        run_calls["count"] += 1
        return subprocess.CompletedProcess(
            command,
            1,
            stdout="",
            stderr="too many requests",
        )

    monkeypatch.setattr(subprocess, "run", _fake_run)
    monkeypatch.setattr(gh_throttle.time, "sleep", lambda _: None)

    try:
        gh_throttle.run_gh_throttled(["gh", "issue", "list"], text=True, check=True)
        assert False, "Expected CalledProcessError"
    except subprocess.CalledProcessError:
        pass

    assert run_calls["count"] == 2

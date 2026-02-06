"""Tests for command_cache module."""

import time
from agents.command_cache import CommandCache


def test_cache_miss():
    """Test cache returns None on miss."""
    cache = CommandCache()
    result = cache.get("npm install", "/path")
    assert result is None


def test_cache_hit():
    """Test cache returns stored result on hit."""
    cache = CommandCache()

    # Store result
    cache.set(
        "npm install",
        "/path",
        stdout="installed",
        stderr="",
        returncode=0,
        execution_time_seconds=3.5,
    )

    # Retrieve result
    result = cache.get("npm install", "/path")
    assert result is not None
    assert result.stdout == "installed"
    assert result.stderr == ""
    assert result.returncode == 0
    assert result.execution_time_seconds == 3.5

    # Check metrics
    assert cache.cache_hits == 1
    assert cache.time_saved_seconds == 3.5


def test_cache_key_uses_cwd():
    """Test cache differentiates by cwd."""
    cache = CommandCache()

    # Store for two different directories
    cache.set("npm install", "/path1", "out1", "", 0, 1.0)
    cache.set("npm install", "/path2", "out2", "", 0, 1.0)

    # Retrieve by cwd
    result1 = cache.get("npm install", "/path1")
    result2 = cache.get("npm install", "/path2")

    assert result1.stdout == "out1"
    assert result2.stdout == "out2"


def test_cache_ttl_expiry():
    """Test cache expires after TTL."""
    cache = CommandCache(ttl_seconds=1)  # 1 second TTL

    # Store result
    cache.set("npm install", "/path", "output", "", 0, 1.0)

    # Should hit immediately
    result = cache.get("npm install", "/path")
    assert result is not None

    # Wait for expiry
    time.sleep(1.1)

    # Should miss after TTL
    result = cache.get("npm install", "/path")
    assert result is None


def test_cache_clear():
    """Test cache.clear() removes all entries."""
    cache = CommandCache()

    # Store multiple entries
    cache.set("cmd1", "/path", "out1", "", 0, 1.0)
    cache.set("cmd2", "/path", "out2", "", 0, 1.0)

    # Hit once to accumulate metrics
    cache.get("cmd1", "/path")
    assert cache.cache_hits == 1

    # Clear cache
    cache.clear()

    # Verify cleared
    assert cache.get("cmd1", "/path") is None
    assert cache.get("cmd2", "/path") is None
    assert cache.cache_hits == 0
    assert cache.time_saved_seconds == 0.0


def test_cache_metrics():
    """Test cache.get_metrics() returns correct data."""
    cache = CommandCache()

    # Store and hit multiple times
    cache.set("cmd", "/path", "out", "", 0, 2.5)
    cache.get("cmd", "/path")
    cache.get("cmd", "/path")
    cache.get("cmd", "/path")

    metrics = cache.get_metrics()
    assert metrics["cache_hits"] == 3
    assert metrics["time_saved_from_cache_seconds"] == 7.5  # 3 hits × 2.5s
    assert metrics["cached_entries"] == 1


def test_cleanup_expired():
    """Test cleanup_expired() removes old entries."""
    cache = CommandCache(ttl_seconds=1)

    # Store entries
    cache.set("cmd1", "/path", "out1", "", 0, 1.0)
    cache.set("cmd2", "/path", "out2", "", 0, 1.0)

    # Wait for expiry
    time.sleep(1.1)

    # Cleanup
    removed = cache.cleanup_expired()
    assert removed == 2
    assert cache.get_metrics()["cached_entries"] == 0


def test_cache_handles_failures():
    """Test cache stores non-zero returncodes."""
    cache = CommandCache()

    # Store failed command
    cache.set(
        "invalid-cmd",
        "/path",
        stdout="",
        stderr="command not found",
        returncode=127,
        execution_time_seconds=0.1,
    )

    # Retrieve
    result = cache.get("invalid-cmd", "/path")
    assert result is not None
    assert result.returncode == 127
    assert "command not found" in result.stderr


def test_multiple_cache_hits_accumulate():
    """Test multiple hits accumulate time_saved."""
    cache = CommandCache()

    cache.set("npm install", "/path", "done", "", 0, 10.0)

    # Hit 5 times
    for _ in range(5):
        result = cache.get("npm install", "/path")
        assert result is not None

    # Should accumulate
    assert cache.cache_hits == 5
    assert cache.time_saved_seconds == 50.0


def test_global_cache_singleton():
    """Test get_cache() returns same instance."""
    from agents.command_cache import get_cache

    cache1 = get_cache()
    cache2 = get_cache()

    assert cache1 is cache2

    # Modifications persist
    cache1.set("test", "/", "output", "", 0, 1.0)
    result = cache2.get("test", "/")
    assert result is not None
    assert result.stdout == "output"

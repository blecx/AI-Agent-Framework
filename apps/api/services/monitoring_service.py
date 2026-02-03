"""
Monitoring service with Prometheus metrics collection.

Provides centralized metrics for:
- API request tracking (duration, count, status)
- LLM service operations (latency, success rate)
- Git operations (duration)
- System resources (active connections, memory)
"""

import time
import psutil
from typing import Optional
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)


# Module-level cache to store metrics instances
_metrics_cache = {}


def _get_or_create_metric(metric_class, name, documentation, labelnames=None, **kwargs):
    """
    Get existing metric or create new one, avoiding duplicate registration.
    
    This function is designed to be idempotent - calling it multiple times
    with the same name will return the same metric instance without errors.
    """
    # Check cache first
    if name in _metrics_cache:
        return _metrics_cache[name]

    # Check if already in registry before attempting creation
    for collector in list(REGISTRY._collector_to_names.keys()):
        if hasattr(collector, "_name") and collector._name == name:
            _metrics_cache[name] = collector
            return collector
    
    # Create new metric and handle any registration conflicts
    try:
        if labelnames:
            metric = metric_class(name, documentation, labelnames, **kwargs)
        else:
            metric = metric_class(name, documentation, **kwargs)
        _metrics_cache[name] = metric
        return metric
    except Exception as e:
        # If creation failed due to duplicate, try to find the existing metric
        error_msg = str(e).lower()
        if any(keyword in error_msg for keyword in ["duplicate", "already", "conflict"]):
            # Search registry again more thoroughly
            for collector in list(REGISTRY._collector_to_names.keys()):
                names = REGISTRY._collector_to_names.get(collector, set())
                if name in names or (hasattr(collector, "_name") and collector._name == name):
                    _metrics_cache[name] = collector
                    return collector
        # If we can't find it or it's a different error, re-raise
        raise


# ============================================================================
# API Request Metrics
# ============================================================================

REQUEST_COUNT = _get_or_create_metric(
    Counter,
    "api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = _get_or_create_metric(
    Histogram,
    "api_request_duration_seconds",
    "API request duration in seconds",
    ["method", "endpoint"],
    buckets=(
        0.005,
        0.01,
        0.025,
        0.05,
        0.075,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
    ),
)

REQUEST_IN_PROGRESS = _get_or_create_metric(
    Gauge,
    "api_requests_in_progress",
    "Number of API requests currently being processed",
)

# ============================================================================
# LLM Service Metrics
# ============================================================================

LLM_CALL_COUNT = _get_or_create_metric(
    Counter,
    "llm_calls_total",
    "Total LLM API calls",
    ["provider", "status"],
)

LLM_CALL_DURATION = _get_or_create_metric(
    Histogram,
    "llm_call_duration_seconds",
    "LLM API call duration in seconds",
    ["provider"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 15.0, 30.0, 60.0),
)

LLM_TOKEN_COUNT = _get_or_create_metric(
    Counter,
    "llm_tokens_total",
    "Total tokens processed by LLM",
    ["provider", "type"],  # type: prompt, completion
)

# ============================================================================
# Git Operations Metrics
# ============================================================================

GIT_OPERATION_COUNT = _get_or_create_metric(
    Counter,
    "git_operations_total",
    "Total Git operations",
    ["operation", "status"],
)

GIT_OPERATION_DURATION = _get_or_create_metric(
    Histogram,
    "git_operation_duration_seconds",
    "Git operation duration in seconds",
    ["operation"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# ============================================================================
# System Resource Metrics
# ============================================================================

ACTIVE_CONNECTIONS = _get_or_create_metric(
    Gauge,
    "active_connections",
    "Number of active connections",
)

MEMORY_USAGE_BYTES = _get_or_create_metric(
    Gauge,
    "memory_usage_bytes",
    "Memory usage in bytes",
)

CPU_USAGE_PERCENT = _get_or_create_metric(
    Gauge,
    "cpu_usage_percent",
    "CPU usage percentage",
)

DISK_USAGE_PERCENT = _get_or_create_metric(
    Gauge,
    "disk_usage_percent",
    "Disk usage percentage",
    ["path"],
)

# ============================================================================
# Error Metrics
# ============================================================================

ERROR_COUNT = _get_or_create_metric(
    Counter,
    "errors_total",
    "Total errors",
    ["type", "endpoint"],
)

# ============================================================================
# Performance Monitoring
# ============================================================================

SLOW_OPERATION_COUNT = _get_or_create_metric(
    Counter,
    "slow_operations_total",
    "Number of operations exceeding threshold",
    ["operation", "threshold"],
)


class MetricsCollector:
    """Helper class for collecting and updating metrics."""

    @staticmethod
    def record_request(method: str, endpoint: str, status_code: int, duration: float):
        """Record API request metrics."""
        REQUEST_COUNT.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

        # Track slow requests (>1s)
        if duration > 1.0:
            SLOW_OPERATION_COUNT.labels(
                operation=f"{method} {endpoint}", threshold="1s"
            ).inc()

    @staticmethod
    def record_llm_call(
        provider: str, duration: float, status: str, tokens: Optional[dict] = None
    ):
        """Record LLM service call metrics."""
        LLM_CALL_COUNT.labels(provider=provider, status=status).inc()
        LLM_CALL_DURATION.labels(provider=provider).observe(duration)

        if tokens:
            if "prompt_tokens" in tokens:
                LLM_TOKEN_COUNT.labels(provider=provider, type="prompt").inc(
                    tokens["prompt_tokens"]
                )
            if "completion_tokens" in tokens:
                LLM_TOKEN_COUNT.labels(provider=provider, type="completion").inc(
                    tokens["completion_tokens"]
                )

        # Track slow LLM calls (>5s)
        if duration > 5.0:
            SLOW_OPERATION_COUNT.labels(
                operation=f"llm_{provider}", threshold="5s"
            ).inc()

    @staticmethod
    def record_git_operation(operation: str, duration: float, status: str):
        """Record Git operation metrics."""
        GIT_OPERATION_COUNT.labels(operation=operation, status=status).inc()
        GIT_OPERATION_DURATION.labels(operation=operation).observe(duration)

        # Track slow Git operations (>1s)
        if duration > 1.0:
            SLOW_OPERATION_COUNT.labels(
                operation=f"git_{operation}", threshold="1s"
            ).inc()

    @staticmethod
    def record_error(error_type: str, endpoint: str):
        """Record error metrics."""
        ERROR_COUNT.labels(type=error_type, endpoint=endpoint).inc()

    @staticmethod
    def update_system_metrics():
        """Update system resource metrics."""
        # Memory usage
        memory = psutil.virtual_memory()
        MEMORY_USAGE_BYTES.set(memory.used)

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        CPU_USAGE_PERCENT.set(cpu_percent)

    @staticmethod
    def update_disk_usage(path: str):
        """Update disk usage for given path."""
        usage = psutil.disk_usage(path)
        DISK_USAGE_PERCENT.labels(path=path).set(usage.percent)

    @staticmethod
    def generate_metrics() -> bytes:
        """Generate Prometheus metrics in text format."""
        return generate_latest()

    @staticmethod
    def get_content_type() -> str:
        """Get Prometheus metrics content type."""
        return CONTENT_TYPE_LATEST


class PerformanceTimer:
    """Context manager for timing operations and recording metrics."""

    def __init__(self, operation: str, metric_recorder=None):
        self.operation = operation
        self.metric_recorder = metric_recorder
        self.start_time = None
        self.duration = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = time.time() - self.start_time

        # Record if metric recorder provided
        if self.metric_recorder:
            self.metric_recorder(self.duration)

        return False  # Don't suppress exceptions

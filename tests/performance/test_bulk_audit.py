"""
Performance benchmarks for bulk audit operations.

Measures execution time and memory usage for:
- Creating 100+ projects with audit events
- Retrieving bulk audit logs
- Filtering/querying audit events

Baseline metrics (on reference hardware):
- 100 audit events creation: ~1-2 seconds
- Bulk query (100 events): ~0.5 seconds
- Memory overhead: <50MB for 100 events
"""

import time
import tracemalloc
import pytest
import tempfile
import shutil
import sys
import os

# Add apps/api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))

from services.audit_service import AuditService
from services.git_manager import GitManager


@pytest.fixture
def benchmark_git_manager():
    """Create a temporary Git manager for benchmarking."""
    tmpdir = tempfile.mkdtemp(prefix="benchmark_audit_")
    git_manager = GitManager(tmpdir)
    git_manager.ensure_repository()
    yield git_manager
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def audit_service():
    """Create audit service instance."""
    return AuditService()


def test_bulk_audit_event_creation_performance(benchmark_git_manager, audit_service):
    """
    Benchmark: Create 100 audit events and measure performance.

    Tests:
    - Event creation throughput
    - Memory usage during bulk operations
    - Git commit overhead at scale

    Expected metrics:
    - Time: <3 seconds for 100 events
    - Memory: <50MB peak allocation
    """
    project_key = "BENCH-AUDIT-001"

    # Initialize project
    benchmark_git_manager.create_project(
        project_key, {"key": project_key, "name": "Benchmark Audit Project"}
    )

    # Start performance measurement
    tracemalloc.start()
    start_time = time.perf_counter()

    # Create 100 audit events
    num_events = 100
    for i in range(num_events):
        audit_service.log_audit_event(
            project_key=project_key,
            event_type="test_event",
            actor=f"user_{i % 10}",
            payload_summary={"iteration": i, "data": f"event_{i}"},
            git_manager=benchmark_git_manager,
        )

    # End measurement
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Calculate metrics
    elapsed_time = end_time - start_time
    peak_memory_mb = peak / (1024 * 1024)

    # Log results
    print("\n=== Bulk Audit Creation Benchmark ===")
    print(f"Events created: {num_events}")
    print(f"Total time: {elapsed_time:.2f}s")
    print(f"Time per event: {elapsed_time / num_events * 1000:.2f}ms")
    print(f"Peak memory: {peak_memory_mb:.2f}MB")
    print(f"Throughput: {num_events / elapsed_time:.1f} events/sec")

    # Performance assertions (generous limits for CI)
    assert elapsed_time < 5.0, f"Too slow: {elapsed_time:.2f}s (expected <5s)"
    assert (
        peak_memory_mb < 100
    ), f"Too much memory: {peak_memory_mb:.2f}MB (expected <100MB)"


def test_bulk_audit_event_retrieval_performance(benchmark_git_manager, audit_service):
    """
    Benchmark: Query 100 audit events and measure retrieval performance.

    Tests:
    - Query execution time
    - Filtering performance
    - Memory usage during retrieval

    Expected metrics:
    - Time: <2 seconds for 100 event retrieval
    - Memory: <30MB for query operations
    """
    project_key = "BENCH-AUDIT-002"

    # Setup: Create project with 100 events
    benchmark_git_manager.create_project(
        project_key, {"key": project_key, "name": "Benchmark Query Project"}
    )

    for i in range(100):
        audit_service.log_audit_event(
            project_key=project_key,
            event_type="query_test" if i % 2 == 0 else "other_event",
            actor=f"user_{i % 5}",
            payload_summary={"index": i},
            git_manager=benchmark_git_manager,
        )

    # Start performance measurement
    tracemalloc.start()
    start_time = time.perf_counter()

    # Query all events
    result = audit_service.get_audit_events(
        project_key=project_key,
        git_manager=benchmark_git_manager,
        limit=100,
    )

    # End measurement
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Calculate metrics
    elapsed_time = end_time - start_time
    peak_memory_mb = peak / (1024 * 1024)
    events_count = len(result.get("events", []))

    # Log results
    print("\n=== Bulk Audit Retrieval Benchmark ===")
    print(f"Events retrieved: {events_count}")
    print(f"Query time: {elapsed_time:.3f}s")
    print(f"Peak memory: {peak_memory_mb:.2f}MB")

    # Performance assertions
    assert elapsed_time < 3.0, f"Query too slow: {elapsed_time:.3f}s (expected <3s)"
    assert (
        peak_memory_mb < 50
    ), f"Too much memory: {peak_memory_mb:.2f}MB (expected <50MB)"
    assert events_count == 100, f"Expected 100 events, got {events_count}"


def test_bulk_audit_event_filtering_performance(benchmark_git_manager, audit_service):
    """
    Benchmark: Filter 100 audit events by type and actor.

    Tests:
    - Filter query performance
    - Selective retrieval overhead

    Expected metrics:
    - Time: <2 seconds for filtered queries
    """
    project_key = "BENCH-AUDIT-003"

    # Setup: Create project with diverse event types
    benchmark_git_manager.create_project(
        project_key, {"key": project_key, "name": "Benchmark Filter Project"}
    )

    for i in range(100):
        audit_service.log_audit_event(
            project_key=project_key,
            event_type=f"type_{i % 5}",
            actor=f"user_{i % 10}",
            payload_summary={"index": i},
            git_manager=benchmark_git_manager,
        )

    # Measure filtered query performance
    start_time = time.perf_counter()

    # Query with event_type filter
    filtered_result = audit_service.get_audit_events(
        project_key=project_key,
        git_manager=benchmark_git_manager,
        event_type="type_0",
        limit=100,
    )

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    filtered_count = len(filtered_result.get("events", []))

    # Log results
    print("\n=== Bulk Audit Filtering Benchmark ===")
    print("Total events: 100")
    print(f"Filtered events: {filtered_count}")
    print(f"Query time: {elapsed_time:.3f}s")

    # Performance assertions
    assert elapsed_time < 3.0, f"Filter too slow: {elapsed_time:.3f}s (expected <3s)"
    assert filtered_count == 20, f"Expected 20 filtered events, got {filtered_count}"

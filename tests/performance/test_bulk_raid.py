"""
Performance benchmarks for bulk RAID operations.

Measures execution time and memory usage for:
- Creating 100+ RAID items
- Retrieving bulk RAID registers
- Updating RAID items at scale

Baseline metrics (on reference hardware):
- 100 RAID items creation: ~2-3 seconds
- Bulk retrieval (100 items): ~0.5 seconds
- Memory overhead: <50MB for 100 items
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

from services.raid_service import RAIDService
from services.git_manager import GitManager


@pytest.fixture
def benchmark_git_manager():
    """Create a temporary Git manager for benchmarking."""
    tmpdir = tempfile.mkdtemp(prefix="benchmark_raid_")
    git_manager = GitManager(tmpdir)
    git_manager.ensure_repository()
    yield git_manager
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def raid_service():
    """Create RAID service instance."""
    return RAIDService()


def test_bulk_raid_item_creation_performance(benchmark_git_manager, raid_service):
    """
    Benchmark: Create 100 RAID items and measure performance.

    Tests:
    - RAID item creation throughput
    - Memory usage during bulk operations
    - Git commit overhead at scale

    Expected metrics:
    - Time: <5 seconds for 100 items
    - Memory: <50MB peak allocation
    """
    project_key = "BENCH-RAID-001"

    # Initialize project
    benchmark_git_manager.create_project(
        project_key, {"key": project_key, "name": "Benchmark RAID Project"}
    )

    # Start performance measurement
    tracemalloc.start()
    start_time = time.perf_counter()

    # Create 100 RAID items
    num_items = 100
    raid_types = ["risk", "assumption", "issue", "dependency"]

    for i in range(num_items):
        item_data = {
            "type": raid_types[i % 4],
            "title": f"Test {raid_types[i % 4].capitalize()} {i}",
            "description": f"Benchmark test item number {i}",
            "owner": f"user_{i % 10}",
            "priority": ["low", "medium", "high"][i % 3],
            "status": "open",
            "created_by": "benchmark",
        }

        raid_service.create_raid_item(
            project_key=project_key,
            item_data=item_data,
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
    print("\n=== Bulk RAID Creation Benchmark ===")
    print(f"Items created: {num_items}")
    print(f"Total time: {elapsed_time:.2f}s")
    print(f"Time per item: {elapsed_time / num_items * 1000:.2f}ms")
    print(f"Peak memory: {peak_memory_mb:.2f}MB")
    print(f"Throughput: {num_items / elapsed_time:.1f} items/sec")

    # Performance assertions (generous limits for CI)
    assert elapsed_time < 10.0, f"Too slow: {elapsed_time:.2f}s (expected <10s)"
    assert (
        peak_memory_mb < 100
    ), f"Too much memory: {peak_memory_mb:.2f}MB (expected <100MB)"

    # Verify all items were created
    items = raid_service.get_raid_items(project_key, benchmark_git_manager)
    assert len(items) == num_items, f"Expected {num_items} items, got {len(items)}"


def test_bulk_raid_item_retrieval_performance(benchmark_git_manager, raid_service):
    """
    Benchmark: Retrieve 100 RAID items and measure performance.

    Tests:
    - Retrieval execution time
    - Memory usage during bulk retrieval
    - JSON parsing overhead

    Expected metrics:
    - Time: <2 seconds for 100 item retrieval
    - Memory: <30MB for retrieval operations
    """
    project_key = "BENCH-RAID-002"

    # Setup: Create project with 100 RAID items
    benchmark_git_manager.create_project(
        project_key, {"key": project_key, "name": "Benchmark Retrieval Project"}
    )

    raid_types = ["risk", "assumption", "issue", "dependency"]
    for i in range(100):
        item_data = {
            "type": raid_types[i % 4],
            "title": f"Retrieval Test {i}",
            "description": f"Test item {i}",
            "owner": f"user_{i % 10}",
            "priority": ["low", "medium", "high"][i % 3],
            "status": "open",
            "created_by": "benchmark",
        }
        raid_service.create_raid_item(
            project_key=project_key,
            item_data=item_data,
            git_manager=benchmark_git_manager,
        )

    # Start performance measurement
    tracemalloc.start()
    start_time = time.perf_counter()

    # Retrieve all RAID items
    items = raid_service.get_raid_items(project_key, benchmark_git_manager)

    # End measurement
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Calculate metrics
    elapsed_time = end_time - start_time
    peak_memory_mb = peak / (1024 * 1024)

    # Log results
    print("\n=== Bulk RAID Retrieval Benchmark ===")
    print(f"Items retrieved: {len(items)}")
    print(f"Retrieval time: {elapsed_time:.3f}s")
    print(f"Peak memory: {peak_memory_mb:.2f}MB")

    # Performance assertions
    assert elapsed_time < 2.0, f"Retrieval too slow: {elapsed_time:.3f}s (expected <2s)"
    assert (
        peak_memory_mb < 50
    ), f"Too much memory: {peak_memory_mb:.2f}MB (expected <50MB)"
    assert len(items) == 100, f"Expected 100 items, got {len(items)}"


def test_bulk_raid_item_update_performance(benchmark_git_manager, raid_service):
    """
    Benchmark: Update 50 RAID items and measure performance.

    Tests:
    - Update operation throughput
    - Memory usage during bulk updates
    - Git commit overhead for updates

    Expected metrics:
    - Time: <5 seconds for 50 updates
    - Memory: <50MB peak allocation
    """
    project_key = "BENCH-RAID-003"

    # Setup: Create project with 50 RAID items
    benchmark_git_manager.create_project(
        project_key, {"key": project_key, "name": "Benchmark Update Project"}
    )

    item_ids = []
    for i in range(50):
        item_data = {
            "type": "risk",
            "title": f"Update Test Risk {i}",
            "description": f"Test risk {i}",
            "owner": "benchmark_user",
            "priority": "medium",
            "status": "open",
            "created_by": "benchmark",
        }
        created_item = raid_service.create_raid_item(
            project_key=project_key,
            item_data=item_data,
            git_manager=benchmark_git_manager,
        )
        item_ids.append(created_item["id"])

    # Start performance measurement
    tracemalloc.start()
    start_time = time.perf_counter()

    # Update all items (change status and priority)
    for i, item_id in enumerate(item_ids):
        updates = {
            "status": "mitigated",
            "priority": "low",
            "mitigation_plan": f"Mitigation for item {i}",
        }
        raid_service.update_raid_item(
            project_key=project_key,
            raid_id=item_id,
            updates=updates,
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
    print("\n=== Bulk RAID Update Benchmark ===")
    print(f"Items updated: {len(item_ids)}")
    print(f"Total time: {elapsed_time:.2f}s")
    print(f"Time per update: {elapsed_time / len(item_ids) * 1000:.2f}ms")
    print(f"Peak memory: {peak_memory_mb:.2f}MB")

    # Performance assertions
    assert elapsed_time < 8.0, f"Updates too slow: {elapsed_time:.2f}s (expected <8s)"
    assert (
        peak_memory_mb < 100
    ), f"Too much memory: {peak_memory_mb:.2f}MB (expected <100MB)"

    # Verify updates were applied
    items = raid_service.get_raid_items(project_key, benchmark_git_manager)
    mitigated_count = sum(1 for item in items if item["status"] == "mitigated")
    assert mitigated_count == 50, f"Expected 50 mitigated items, got {mitigated_count}"

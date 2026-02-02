# Performance Benchmarks

This directory contains performance benchmarks for bulk operations in the AI-Agent-Framework.

## Purpose

Establish baseline metrics and detect performance regressions for:
- **Bulk audit operations**: Creating and querying 100+ audit events
- **Bulk RAID operations**: Creating, retrieving, and updating 100+ RAID items

## Running Benchmarks

```bash
# Run all performance benchmarks
pytest tests/performance/ -v

# Run specific benchmark suite
pytest tests/performance/test_bulk_audit.py -v
pytest tests/performance/test_bulk_raid.py -v

# Run with output capture disabled (see print statements)
pytest tests/performance/ -v -s
```

## Benchmark Coverage

### Audit Benchmarks (`test_bulk_audit.py`)
- `test_bulk_audit_event_creation_performance`: Create 100 audit events
- `test_bulk_audit_event_retrieval_performance`: Query 100 audit events
- `test_bulk_audit_event_filtering_performance`: Filter 100 events by type/actor

### RAID Benchmarks (`test_bulk_raid.py`)
- `test_bulk_raid_item_creation_performance`: Create 100 RAID items
- `test_bulk_raid_item_retrieval_performance`: Retrieve 100 RAID items
- `test_bulk_raid_item_update_performance`: Update 50 RAID items

## Performance Metrics

Each benchmark measures:
- **Execution time**: Total time and per-item throughput
- **Memory usage**: Peak memory allocation (via `tracemalloc`)
- **Throughput**: Operations per second

### Baseline Metrics (Reference Hardware)

**Audit Operations:**
- 100 events creation: ~1-5 seconds (target <5s)
- 100 events retrieval: ~0.5-3 seconds (target <3s)
- Filtered queries: ~0.5-3 seconds (target <3s)
- Memory overhead: <100MB peak

**RAID Operations:**
- 100 items creation: ~2-10 seconds (target <10s)
- 100 items retrieval: ~0.5-2 seconds (target <2s)
- 50 items updates: ~2-8 seconds (target <8s)
- Memory overhead: <100MB peak

## Performance Assertions

Each test includes performance assertions to catch regressions:
- Execution time limits (generous for CI environments)
- Memory usage caps
- Data integrity checks

## CI Integration

These benchmarks run as part of the standard test suite:
```bash
pytest  # Includes performance tests by default
```

To skip performance tests in development:
```bash
pytest -m "not performance"  # (requires pytest marks)
```

## Adding New Benchmarks

When adding new bulk operations:

1. Create test file in `tests/performance/`
2. Use `tracemalloc` for memory profiling
3. Use `time.perf_counter()` for timing
4. Set generous assertion limits for CI
5. Document baseline metrics in docstrings
6. Use temporary directories for isolation

**Example structure:**
```python
def test_bulk_operation_performance(benchmark_git_manager, service):
    \"\"\"
    Benchmark: Description of what's being tested.
    
    Expected metrics:
    - Time: <X seconds for N operations
    - Memory: <Y MB peak allocation
    \"\"\"
    tracemalloc.start()
    start_time = time.perf_counter()
    
    # Perform bulk operations
    # ...
    
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Log results and assert performance
    # ...
```

## Troubleshooting

**Slow benchmarks:**
- Check disk I/O (Git operations write to disk)
- Verify no other processes consuming resources
- Run with `-s` flag to see detailed timing output

**Memory errors:**
- Increase limits if running in constrained environments
- Check for memory leaks if peak usage grows unexpectedly

**Flaky tests:**
- Benchmarks use temporary directories for isolation
- Cleanup is automatic (pytest fixtures)
- Increase time limits if CI is slower than local

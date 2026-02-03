# Production Monitoring & Observability

This document describes the monitoring and observability features available in the ISO 21500 Project Management AI Agent system.

## Overview

The system provides comprehensive monitoring capabilities using:

- **Prometheus metrics** - Time-series metrics for performance tracking
- **Enhanced health checks** - Detailed system health status
- **Performance monitoring** - Automatic detection of slow operations

## Quick Start

### 1. Access Metrics

Metrics are exposed at the `/metrics` endpoint in Prometheus format:

```bash
curl http://localhost:8000/metrics
```

### 2. Check System Health

Detailed health information is available at `/api/v1/health`:

```bash
curl http://localhost:8000/api/v1/health | jq
```

### 3. Configure Prometheus

See [prometheus-config.yml](./prometheus-config.yml) for a complete Prometheus configuration example.

### 4. Visualize with Grafana

See [grafana-dashboard.json](./grafana-dashboard.json) for a ready-to-use dashboard.

## Available Metrics

### API Request Metrics

- **`api_requests_total`** (Counter) - Total API requests by method, endpoint, status code
- **`api_request_duration_seconds`** (Histogram) - Request duration distribution
- **`api_requests_in_progress`** (Gauge) - Current number of active requests

Example queries:
```promql
# Request rate by endpoint
rate(api_requests_total[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))

# Error rate
rate(api_requests_total{status_code=~"5.."}[5m])
```

### LLM Service Metrics

- **`llm_calls_total`** (Counter) - Total LLM API calls by provider and status
- **`llm_call_duration_seconds`** (Histogram) - LLM call duration distribution
- **`llm_tokens_total`** (Counter) - Total tokens processed (prompt/completion)

Example queries:
```promql
# LLM success rate
rate(llm_calls_total{status="success"}[5m]) / rate(llm_calls_total[5m])

# Average LLM latency
rate(llm_call_duration_seconds_sum[5m]) / rate(llm_call_duration_seconds_count[5m])
```

### Git Operations Metrics

- **`git_operations_total`** (Counter) - Total Git operations by operation type and status
- **`git_operation_duration_seconds`** (Histogram) - Git operation duration

Example queries:
```promql
# Git operation rate
rate(git_operations_total[5m])

# Git operation latency
histogram_quantile(0.95, rate(git_operation_duration_seconds_bucket[5m]))
```

### System Resource Metrics

- **`active_connections`** (Gauge) - Number of active connections
- **`memory_usage_bytes`** (Gauge) - Memory usage in bytes
- **`cpu_usage_percent`** (Gauge) - CPU usage percentage
- **`disk_usage_percent`** (Gauge) - Disk usage percentage by path

### Error Metrics

- **`errors_total`** (Counter) - Total errors by type and endpoint

### Performance Metrics

- **`slow_operations_total`** (Counter) - Operations exceeding threshold by operation and threshold

Example queries:
```promql
# Slow requests (>1s)
rate(slow_operations_total{threshold="1s"}[5m])

# Slow LLM calls (>5s)
rate(slow_operations_total{threshold="5s"}[5m])
```

## Health Checks

The `/api/v1/health` endpoint provides detailed health status:

```json
{
  "status": "healthy",  // overall: healthy/degraded/unhealthy
  "timestamp": "2026-02-03T12:00:00Z",
  "api_version": "v1",
  "checks": {
    "git_repository": {
      "healthy": true,
      "docs_path": "/projectDocs",
      "docs_exists": true,
      "is_git_repo": true,
      "writable": true,
      "message": "Git repository is healthy"
    },
    "llm_service": {
      "healthy": true,
      "config_exists": true,
      "endpoint_configured": true,
      "message": "LLM service is reachable"
    },
    "disk_space": {
      "healthy": true,
      "path": "/projectDocs",
      "total_gb": 100.0,
      "used_gb": 45.2,
      "free_gb": 54.8,
      "percent_used": 45.2,
      "message": "54.80GB free"
    },
    "memory": {
      "healthy": true,
      "total_gb": 16.0,
      "used_gb": 8.5,
      "free_gb": 7.5,
      "percent_used": 53.1,
      "message": "46.9% free"
    }
  }
}
```

### Health Status Levels

- **healthy** - All critical checks passing, LLM service available
- **degraded** - All critical checks passing, but LLM service unavailable (system can use templates)
- **unhealthy** - One or more critical checks failing (Git, disk, memory)

## Request Tracing

Every API request receives a unique correlation ID in the `X-Correlation-ID` response header:

```bash
curl -i http://localhost:8000/api/v1/health
# HTTP/1.1 200 OK
# x-correlation-id: 550e8400-e29b-41d4-a716-446655440000
```

Use correlation IDs to trace requests through logs and metrics.

## Performance Monitoring

The system automatically tracks slow operations:

- **API requests > 1 second** - Recorded in `slow_operations_total{operation="METHOD /path", threshold="1s"}`
- **LLM calls > 5 seconds** - Recorded in `slow_operations_total{operation="llm_provider", threshold="5s"}`
- **Git operations > 1 second** - Recorded in `slow_operations_total{operation="git_operation", threshold="1s"}`

## Prometheus Setup

### Docker Compose

Add Prometheus to your `docker-compose.yml`:

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./docs/monitoring/prometheus-config.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

volumes:
  prometheus_data:
```

### Standalone

```bash
# Download Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0.linux-amd64

# Copy config
cp /path/to/docs/monitoring/prometheus-config.yml prometheus.yml

# Start
./prometheus --config.file=prometheus.yml
```

Access Prometheus UI at http://localhost:9090

## Grafana Setup

### Docker Compose

Add Grafana to your `docker-compose.yml`:

```yaml
services:
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

### Configuration

1. Access Grafana at http://localhost:3000 (admin/admin)
2. Add Prometheus data source:
   - Configuration → Data Sources → Add data source
   - Select Prometheus
   - URL: `http://prometheus:9090` (Docker) or `http://localhost:9090` (standalone)
   - Save & Test
3. Import dashboard:
   - Create → Import
   - Upload [grafana-dashboard.json](./grafana-dashboard.json)
   - Select Prometheus data source
   - Import

## Alerting Examples

### Prometheus Alerting Rules

Create `alerts.yml`:

```yaml
groups:
  - name: api_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(api_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      - alert: SlowRequests
        expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow API requests detected"
          description: "95th percentile latency is {{ $value }} seconds"

      - alert: LLMServiceDown
        expr: rate(llm_calls_total{status="success"}[5m]) == 0 and rate(llm_calls_total[5m]) > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "LLM service unavailable"
          description: "No successful LLM calls in the last 5 minutes"

      - alert: LowDiskSpace
        expr: disk_usage_percent > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
          description: "Disk usage is {{ $value }}%"
```

Reference this in `prometheus-config.yml`:

```yaml
rule_files:
  - "alerts.yml"
```

## Best Practices

### Metric Naming

- Use snake_case for metric names
- Include units in metric names (e.g., `_seconds`, `_bytes`)
- Use consistent label names across metrics

### Label Cardinality

Avoid high-cardinality labels (e.g., user IDs, timestamps). Current labels are:

- `method`, `endpoint`, `status_code` (bounded by API routes)
- `provider` (bounded by LLM providers)
- `operation` (bounded by Git operations)
- `type` (bounded by error/operation types)

### Retention

Default Prometheus retention is 15 days. For production:

```bash
./prometheus --storage.tsdb.retention.time=90d
```

### Performance

- Prometheus scrapes metrics every 15 seconds (configurable)
- Each scrape takes ~10-50ms depending on active metrics
- Minimal overhead on API performance (<1ms per request)

## Troubleshooting

### Metrics not appearing

1. Check endpoint is accessible: `curl http://localhost:8000/metrics`
2. Verify Prometheus is scraping: http://localhost:9090/targets
3. Check Prometheus logs for scrape errors

### Health check failing

1. Check detailed status: `curl http://localhost:8000/api/v1/health | jq`
2. Review specific check failures in response
3. Common issues:
   - `git_repository.writable=false` - Permission issues on projectDocs
   - `llm_service.healthy=false` - LLM endpoint unreachable
   - `disk_space.healthy=false` - Disk full
   - `memory.healthy=false` - Memory pressure

### High memory usage

Monitor `memory_usage_bytes` metric and consider:
- Reducing concurrent requests
- Adding memory limits in Docker
- Scaling horizontally

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [OpenMetrics Specification](https://openmetrics.io/)
- [FastAPI Monitoring Guide](https://fastapi.tiangolo.com/advanced/custom-request-and-route/)

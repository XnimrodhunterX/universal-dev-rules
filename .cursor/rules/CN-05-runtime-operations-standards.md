---
description: "Universal runtime operations standards: observability, monitoring, resource management, deployment practices. Kubernetes-compatible with enforcement mechanisms."
globs: ["**/*"]
alwaysApply: true
---

# 🔧 Universal Runtime Operations Standards

## 1. Observability & Monitoring

### Health Endpoints (Kubernetes Specification)
- **MUST** expose `/livez` for liveness probes (process health)
- **MUST** expose `/readyz` for readiness probes (traffic readiness) 
- **MUST** expose `/healthz` for general health checks
- **OPTIONAL:** `/metrics` endpoint in Prometheus format

### Health Endpoint Response Schema
```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.2.3",
  "dependencies": {
    "database": "healthy",
    "redis": "healthy", 
    "external_api": "degraded"
  },
  "checks": [
    {
      "name": "database_connection",
      "status": "healthy",
      "latency_ms": 45
    }
  ]
}
```

### Structured Logging Requirements
- **MUST** emit structured logs in JSON format with contextual information
- **MUST** include correlation/trace IDs in all log entries
- **REQUIRE:** Log level standards (ERROR, WARN, INFO, DEBUG)
- **INCLUDE:** Service name, version, environment, timestamp in all logs

### Log Format Standard
```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "INFO",
  "service": "user-service",
  "version": "1.2.3",
  "environment": "production",
  "trace_id": "abc123def456",
  "message": "User created successfully",
  "user_id": "12345",
  "duration_ms": 234
}
```

### Distributed Tracing
- **MUST** implement distributed tracing (OpenTelemetry, Jaeger, Zipkin)
- **REQUIRE:** Trace context propagation across service boundaries
- **INCLUDE:** Custom spans for business-critical operations
- Log all background task statuses with execution duration

### Metrics & Alerting
- **MUST** export metrics in Prometheus format via `/metrics`
- **REQUIRE:** SLA violation alerting based on performance budgets
- Define alerting runbooks for common failure scenarios
- Monitor resource usage continuously (CPU, memory, disk, network)

## 2. Resource & Deployment Management

### Container Resource Specifications
- **MUST** define resource limits and requests in container specifications
- **REQUIRE:** Memory limits to prevent OOM kills
- **REQUIRE:** CPU limits to ensure fair resource sharing
- **STANDARD:** Non-root container execution (UID > 0)

### Resource Limit Guidelines
```yaml
# Kubernetes example
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"  
    cpu: "500m"
```

### Startup Performance Standards
- **TARGET:** Application boot time < 30 seconds (< 5 seconds preferred)
- **EXCEPTION:** ML/AI workloads may exceed with ADR justification
- **REQUIRE:** Document startup time in performance budget
- **MEASURE:** Track cold start vs warm start metrics

### Deployment Practices  
- **MUST** use Infrastructure as Code (Dockerfile, Helm charts, Terraform)
- **MUST** support zero-downtime deployments with rolling updates
- **REQUIRE:** Blue-green or canary deployment capability for critical services
- **INCLUDE:** Deployment rollback procedures documented

### Container Best Practices
- **MUST** use multi-stage Docker builds to minimize image size
- **TARGET:** Compressed image size < 200MB unless justified
- **REQUIRE:** Container vulnerability scanning (Trivy, Grype) in CI
- **BASE:** Use distroless or minimal base images where possible

## 3. Graceful Operations

### Shutdown Handling
- **MUST** implement graceful shutdown handling for SIGTERM/SIGINT
- **REQUIRE:** Connection draining during shutdown process
- **TIMEOUT:** Complete shutdown within 30 seconds
- **PRESERVE:** In-flight requests completed before termination

### Graceful Shutdown Example
```python
import signal
import sys
import threading

class GracefulKiller:
    kill_now = threading.Event()
    
    def __init__(self):
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        self.kill_now.set()
        
    def shutdown_handler(self):
        # Complete in-flight requests
        # Close database connections
        # Stop background tasks
        sys.exit(0)
```

### Liveness and Readiness Probes
- **Liveness:** Process is running and not deadlocked
- **Readiness:** Service can handle requests (dependencies available)
- **Startup:** Service has completed initialization
- **Configure:** Appropriate timeouts and failure thresholds

### Probe Configuration Examples
```yaml
# Kubernetes probe configuration
livenessProbe:
  httpGet:
    path: /livez
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  
readinessProbe:
  httpGet:
    path: /readyz
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
```

## 4. Configuration Management

### Environment Detection
- **MUST** auto-detect runtime environment via standard environment variables
- **STANDARD:** Use `NODE_ENV`, `ENVIRONMENT`, `DEPLOY_ENV` consistently
- **VALUES:** dev, test, staging, production (no custom names)
- **VALIDATE:** Configuration schema on startup

### Configuration Loading
- **PRIORITY:** Environment variables > config files > defaults
- **REQUIRE:** Configuration validation with meaningful error messages
- **SUPPORT:** Live configuration reloading where feasible (non-breaking changes)
- **ENCRYPT:** Sensitive configuration values using SOPS, SealedSecrets, or Vault

### Configuration Schema Validation
```yaml
# config-schema.yaml example
type: object
required: [database_url, redis_url, log_level]
properties:
  database_url:
    type: string
    format: uri
  log_level:
    type: string
    enum: [DEBUG, INFO, WARN, ERROR]
  max_connections:
    type: integer
    minimum: 1
    maximum: 100
    default: 10
```

---

## 🛠️ Enforcement & Tooling

### Required CI Checks
- [ ] Health endpoint presence and response format validation
- [ ] Container resource limits defined
- [ ] Graceful shutdown implementation verified
- [ ] Configuration schema validation
- [ ] Container security scanning (Trivy/Grype)

### Repository Requirements
- [ ] `/healthz`, `/livez`, `/readyz` endpoints implemented
- [ ] Dockerfile with multi-stage build and resource limits
- [ ] `config-schema.yaml` or equivalent validation
- [ ] Deployment manifests with probe configurations
- [ ] Graceful shutdown handling implemented

### Recommended Tools
- **Observability:** OpenTelemetry, Prometheus, Grafana, Jaeger
- **Container Security:** Trivy, Grype, Dockle
- **Configuration:** JSON Schema, Ajv, Cerberus
- **Health Checking:** Docker HEALTHCHECK, Kubernetes probes

### Monitoring Integration
- Set up dashboards for key metrics (latency, errors, throughput)
- Configure alerting rules based on SLO violations
- Implement log aggregation and searching (ELK, Loki)
- Track deployment success/failure rates

---

*This rule focuses on runtime operational requirements. See also: AR-05-design-architecture-principles.md for design standards and CN-10-governance-principles.md for development governance.* 
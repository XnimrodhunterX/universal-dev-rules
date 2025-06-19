---
description: "Universal design and architecture principles: API-first, distributed systems, async patterns, fault tolerance. Enforceable standards with tooling integration."
globs: ["**/*"]
alwaysApply: true
---

# 🏗️ Universal Design & Architecture Principles

<!-- CURSOR: highlight: api:design -->
<!-- CURSOR: context: microservices, rest-api, distributed-systems -->
<!-- CURSOR: complexity: intermediate -->
<!-- CURSOR: priority: high -->

## 1. API-First Design

### Core Requirements
- **MUST** define APIs via OpenAPI 3.1.0+ before implementation
- **MUST** enforce versioned endpoints (e.g., `/v1/users`, `/v2/orders`)
- **MUST** validate input/output schemas with automated testing
- **MUST** expose unified error schema using RFC 9457 (problem+json format)

### Error Object Schema (RFC 9457)
```json
{
  "type": "https://example.com/errors/invalid-input",
  "title": "Invalid Input Parameters",
  "status": 400,
  "detail": "The 'email' field must be a valid email address",
  "instance": "/users/create",
  "trace_id": "abc123def456"
}
```

### API Contract Enforcement
- Use DTOs to decouple internal models from API contracts
- Follow REST/GraphQL naming conventions consistently
- Include gRPC reflection and protobuf versioning for RPC APIs
- **REQUIRE:** `/docs/openapi.yaml` presence via CI linter

### gRPC Protocol Standards
```protobuf
// users.proto - Versioned gRPC service definition
syntax = "proto3";

package users.v1;

import "google/protobuf/timestamp.proto";
import "google/api/annotations.proto";

service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse) {
    option (google.api.http) = {
      get: "/v1/users/{user_id}"
    };
  }
  
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse) {
    option (google.api.http) = {
      post: "/v1/users"
      body: "*"
    };
  }
}

message User {
  string id = 1;
  string email = 2;
  string name = 3;
  google.protobuf.Timestamp created_at = 4;
}
```

### AsyncAPI Message Contracts
```yaml
# asyncapi.yaml - Event-driven API documentation
asyncapi: 3.0.0
info:
  title: User Events API
  version: 1.0.0
  description: User lifecycle events for microservices integration

channels:
  user/created:
    description: User creation events
    messages:
      UserCreated:
        payload:
          type: object
          properties:
            user_id:
              type: string
              description: Unique user identifier
            email:
              type: string
              format: email
            created_at:
              type: string
              format: date-time
          required: [user_id, email, created_at]

  user/updated:
    description: User profile update events
    messages:
      UserUpdated:
        payload:
          type: object
          properties:
            user_id:
              type: string
            changes:
              type: object
              description: Changed fields
            updated_at:
              type: string
              format: date-time

operations:
  publishUserCreated:
    action: send
    channel:
      $ref: '#/channels/user~1created'
    description: Publish when a new user is created
```

### Tooling Requirements
- **Spectral** or **openapi-cli** for OpenAPI validation
- **Contract testing** against published schemas
- **AsyncAPI** documentation for message-based APIs
- **buf** for protobuf linting and breaking change detection
- **grpc-gateway** for REST-to-gRPC transcoding

## 2. Distributed Systems & Resilience

### CAP Theorem Documentation
- **MUST** explicitly document CAP trade-offs in Architecture Decision Records (ADRs)
- **REQUIRE:** CAP discussion section in `docs/adr/` template
- Define consistency, availability, and partition tolerance choices per service

### Service Independence
- Ensure loose coupling between services with independent failure modes
- Implement bulkhead isolation patterns to prevent cascade failures
- Use correlation IDs across all services and log entries
- Register services with discovery mechanism (DNS, service registry, K8s)

### Sample ADR Template Addition
```markdown
## CAP Theorem Analysis
**Consistency:** [Strong/Eventual] - Justification...
**Availability:** [High/Moderate] - Trade-offs...
**Partition Tolerance:** [Required/Optional] - Network assumptions...
```

## 3. Async/Synchronous Patterns

### Async Pattern Standards
- **MUST** use async patterns for high-latency I/O operations (>100ms)
- **MUST** avoid blocking operations in async execution flows
- **MUST** use message queues for background processing and decoupling
- **REQUIRE:** Clear annotation of async/sync code paths using `async_` prefixes or folder structure

### Annotation Convention
```python
# Python example
async def async_process_payment(payment_data):  # Clear async prefix
    return await external_payment_service.charge(payment_data)

def sync_validate_input(data):  # Clear sync naming
    return schema.validate(data)
```

### Message Contracts
- Use idempotency tokens for write operations
- Implement AsyncAPI specs for message queue contracts
- Define retry and dead letter queue policies

## 4. Fault Tolerance & Error Handling

### Retry Strategies (Consolidated from multiple sections)
- **MUST** implement exponential-backoff retry strategies with jitter
- **MUST** use circuit breakers on all external service calls
- **MUST** define bounded retry attempts (max 3-5 attempts)
- **MUST** ensure only idempotent operations are retried

### Implementation Libraries
- **Polly** (.NET), **Resilience4j** (Java), **Tenacity** (Python)
- Circuit breaker patterns with configurable thresholds
- Timeout standardization per service type

### Error Response Standards
- Fail fast and degrade gracefully under load
- Handle partial failures and prevent cascading failures
- Provide meaningful error messages with actionable guidance
- Include trace IDs in all error responses

## 5. Performance & Scalability Foundation

### SLO Integration Requirements
- **MUST** define SLO targets in ADR with performance budget YAML
- **REQUIRE:** `perf-budget.yaml` in root directory with:
  - Latency targets (P95 < 200ms, P99 < 500ms)
  - Throughput expectations (TPS/RPS)
  - Error rate thresholds (<0.1%)

### Performance Budget Schema
```yaml
# perf-budget.yaml
service_name: "user-service"
version: "1.0"
targets:
  latency:
    p95_ms: 200
    p99_ms: 500
  throughput:
    target_rps: 1000
    burst_rps: 2000
  availability:
    target_percentage: 99.9
  error_rate:
    max_percentage: 0.1
```

### Scalability Patterns
- Design stateless services; externalize session data to Redis/database
- Support horizontal scaling (containers, load balancers)
- Document autoscaling triggers (CPU >70%, latency >300ms, queue depth >100)

---

## 🛠️ Enforcement & Tooling

### Required CI Checks
- [ ] OpenAPI schema validation (`spectral lint docs/openapi.yaml`)
- [ ] Performance budget validation (`perf-budget.yaml` present and valid)
- [ ] ADR presence for distributed system decisions
- [ ] Async/sync pattern annotation compliance

### Repository Requirements
- [ ] `/docs/openapi.yaml` or equivalent API specification
- [ ] `perf-budget.yaml` with documented SLO targets
- [ ] `docs/adr/` folder with CAP theorem analysis for distributed services
- [ ] Service discovery configuration documented

### Recommended Tools
- **API Design:** Swagger Editor, Insomnia, Postman
- **Circuit Breakers:** Polly, Resilience4j, Hystrix
- **Service Discovery:** Consul, etcd, Kubernetes DNS
- **Performance Testing:** k6, Artillery, Locust

---

*This rule focuses on foundational design decisions that affect system architecture. See also: CN-05-runtime-operations-standards.md for operational requirements and CN-10-governance-principles.md for development governance.* 
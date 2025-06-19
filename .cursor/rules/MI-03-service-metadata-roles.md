---
description: "Universal service metadata and roles: RBAC, service accounts, ownership, lifecycle management. Identity and access management standards."
globs: ["**/*"]
alwaysApply: true
---

# 👥 Universal Service Metadata & Roles

## 1. Service Metadata Standards

### Required Metadata Schema
- **MUST** include `metadata.yaml` in repository root following standard schema
- **REQUIRE:** Service name, description, owner, tier, type, and dependencies
- **VALIDATE:** Metadata completeness and format via CI/CD pipeline
- **MAINTAIN:** Metadata freshness with automated validation and updates

### Complete Metadata Template
```yaml
# metadata.yaml - REQUIRED in all service repositories
schema_version: "1.2.0"
last_updated: "2024-01-15T10:30:00Z"

# Basic Service Information
service:
  name: "user-service"                    # REQUIRED: Kebab-case, unique identifier
  display_name: "User Management Service" # REQUIRED: Human-readable name
  description: "Manages user accounts, authentication, and profile data for the platform"
  version: "2.1.3"                      # REQUIRED: Semantic versioning
  type: "API"                           # REQUIRED: API, Worker, CLI, Library, Frontend
  tier: 1                               # REQUIRED: 1 (critical), 2 (important), 3 (nice-to-have)
  
# Ownership and Contact
ownership:
  team: "platform-team"                 # REQUIRED: Team identifier
  email: "platform-team@example.com"    # REQUIRED: Team contact email
  slack_channel: "#platform-team"       # OPTIONAL: Team Slack channel
  oncall_rotation: "platform-oncall"    # OPTIONAL: PagerDuty/oncall rotation
  tech_lead: "tech-lead@example.com"        # OPTIONAL: Technical lead contact
  product_owner: "product-owner@example.com"      # OPTIONAL: Product owner contact

# Service Classification
classification:
  domain: "user-management"             # REQUIRED: Business domain
  subdomain: "authentication"          # OPTIONAL: Business subdomain
  data_classification: "PII"           # REQUIRED: Public, Internal, Confidential, PII
  compliance_requirements: ["SOC2", "GDPR", "HIPAA"] # Compliance frameworks
  business_criticality: "mission-critical" # mission-critical, business-critical, important, low

# Technical Specification
technical:
  language: "typescript"               # REQUIRED: Primary programming language
  framework: "express"                 # REQUIRED: Primary framework/library
  runtime_version: "node:18"           # REQUIRED: Runtime version specification
  build_tool: "npm"                   # REQUIRED: Build tool (npm, gradle, cargo, etc.)
  
  # Resource Requirements
  resources:
    cpu_request: "100m"
    cpu_limit: "500m"
    memory_request: "128Mi"
    memory_limit: "512Mi"
    storage_request: "1Gi"
    
  # Network Configuration  
  networking:
    internal_port: 8080
    health_check_path: "/healthz"
    readiness_check_path: "/readyz"
    metrics_port: 9090
    debug_port: 9229
    
# Dependencies
dependencies:
  services:
    - name: "postgres-primary"
      type: "database"
      critical: true
      version: "14.x"
      purpose: "Primary data storage"
    - name: "redis-cache"
      type: "cache"
      critical: false
      version: "7.x"
      purpose: "Session and data caching"
    - name: "email-service"
      type: "internal_api"
      critical: false
      version: "v1"
      purpose: "Send verification emails"
      
  external_apis:
    - name: "auth0"
      url: "https://example.auth0.com"
      critical: true
      purpose: "Identity provider"
      sla: "99.9%"
    - name: "sendgrid"
      url: "https://api.sendgrid.com"
      critical: false
      purpose: "Email delivery"
      
  infrastructure:
    - name: "kubernetes"
      version: "1.28+"
      critical: true
    - name: "nginx-ingress"
      version: "1.9+"
      critical: true

# API Specification
api:
  type: "REST"                         # REST, GraphQL, gRPC, WebSocket
  version: "v2"                        # API version
  openapi_spec: "docs/openapi.yaml"    # Path to OpenAPI specification
  base_path: "/api/v2"                 # API base path
  authentication: "JWT"               # Authentication method
  rate_limits:
    default: "100/minute"
    authenticated: "1000/minute"
    
# Data and Storage
data:
  stores:
    - name: "user_database"
      type: "postgresql"
      purpose: "User accounts and profiles"
      backup_frequency: "daily"
      retention: "7_years"
    - name: "session_cache"
      type: "redis"
      purpose: "User sessions and temporary data"
      backup_frequency: "none"
      retention: "24_hours"
      
  sensitive_data: ["email", "phone", "address", "payment_info"]
  data_retention_policy: "7_years_after_account_deletion"
  backup_schedule: "0 2 * * *"  # Daily at 2 AM UTC

# Security Configuration
security:
  authentication_required: true
  authorization_model: "RBAC"          # RBAC, ABAC, Custom
  encryption_at_rest: true
  encryption_in_transit: true
  security_contacts: ["security@example.com"]
  vulnerability_disclosure: "security@example.com"
  
  # Security scanning
  sast_enabled: true
  dast_enabled: true
  dependency_scanning: true
  container_scanning: true

# Monitoring and Observability
monitoring:
  health_checks:
    liveness: "/livez"
    readiness: "/readyz"
    startup: "/healthz"
    
  metrics:
    prometheus_endpoint: "/metrics"
    custom_metrics: ["user_registrations_total", "login_attempts_total"]
    
  logging:
    level: "INFO"
    format: "json"
    retention: "30d"
    
  tracing:
    enabled: true
    sample_rate: 0.1
    
  alerting:
    runbook_url: "https://wiki.example.com/runbooks/user-service"
    escalation_policy: "platform-team-oncall"

# Deployment Configuration
deployment:
  environments: ["development", "staging", "production"]
  deployment_strategy: "rolling"       # rolling, blue-green, canary
  rollback_strategy: "automatic"       # automatic, manual
  
  # Environment-specific overrides
  environment_configs:
    production:
      replicas: 3
      resources:
        cpu_limit: "1000m"
        memory_limit: "1Gi"
      monitoring:
        sample_rate: 0.01
        
    staging:
      replicas: 1
      monitoring:
        sample_rate: 0.1
        
# Quality Gates
quality:
  code_coverage_threshold: 80
  performance_budgets:
    p95_latency_ms: 200
    throughput_rps: 500
    error_rate_percent: 0.1
    
  testing:
    unit_tests_required: true
    integration_tests_required: true
    e2e_tests_required: false
    load_tests_required: true

# Documentation
documentation:
  readme: "README.md"
  api_docs: "docs/api.md"
  runbook: "docs/runbook.md"
  architecture_decision_records: "docs/adr/"
  getting_started: "docs/getting-started.md"
  
# Lifecycle Management
lifecycle:
  status: "active"                     # planned, active, deprecated, retired
  created_date: "2023-01-15"
  last_major_update: "2024-01-10"
  deprecation_date: null               # Date when service will be deprecated
  retirement_date: null                # Date when service will be retired
  
  # Change management
  change_approval_required: true       # For production changes
  change_approval_team: "platform-team"
  maintenance_window: "Saturday 02:00-04:00 UTC"

# Cost and Resource Management
cost:
  budget_owner: "platform-team"
  monthly_budget_usd: 500
  cost_center: "engineering-platform"
  resource_tags:
    Environment: "production"
    Team: "platform"
    CostCenter: "engineering-platform"
    Service: "user-service"

# Additional Metadata
additional:
  repository_url: "https://github.com/example-org/user-service"
  ci_cd_pipeline: "https://ci.example.com/user-service"
  deployment_url: "https://deploy.example.com/user-service"
  monitoring_dashboard: "https://grafana.example.com/d/user-service"
  
# Validation Schema Reference
$schema: "https://schemas.example.com/service-metadata/v1.2.0"
```

## 2. RBAC and Service Accounts

### Service Account Requirements
- **CREATE:** Dedicated service account per service with minimal required permissions
- **IMPLEMENT:** Principle of least privilege for all service accounts
- **ROTATE:** Service account credentials regularly (quarterly)
- **AUDIT:** Service account permissions and usage monthly

### Service Account Template
```yaml
# service-account.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: user-service
  namespace: api
  labels:
    app: user-service
    version: v2.1.3
  annotations:
    # AWS IAM Role for Service Accounts (IRSA)
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/user-service-role
    
    # GCP Workload Identity
    iam.gke.io/gcp-service-account: user-service@project.iam.gserviceaccount.com
    
automountServiceAccountToken: true

---
# Role for service-specific permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: user-service
  namespace: api
rules:
  # Secret access (for database credentials, API keys)
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["user-service-secrets", "database-secrets"]
    verbs: ["get", "list"]
    
  # ConfigMap access (for configuration)
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["user-service-config"]
    verbs: ["get", "list", "watch"]
    
  # Pod logs (for debugging)
  - apiGroups: [""]
    resources: ["pods/log"]
    verbs: ["get", "list"]

---
# Bind role to service account
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: user-service
  namespace: api
subjects:
  - kind: ServiceAccount
    name: user-service
    namespace: api
roleRef:
  kind: Role
  name: user-service
  apiGroup: rbac.authorization.k8s.io
```

### RBAC Best Practices
- **SCOPE:** Namespace-level roles for service-specific permissions
- **LIMIT:** Cluster-level roles only for platform services
- **REVIEW:** RBAC permissions quarterly with access reviews
- **DOCUMENT:** Permission justification in role definitions

## 3. Identity and Access Management

### Authentication Standards
- **REQUIRE:** Service-to-service authentication using mutual TLS or service accounts
- **IMPLEMENT:** JWT-based authentication for API endpoints
- **USE:** Identity providers (OAuth2, OIDC) for user authentication
- **ENFORCE:** Multi-factor authentication for administrative access

### Authorization Model
```yaml
# authorization-policy.yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: user-service-authz
  namespace: api
spec:
  selector:
    matchLabels:
      app: user-service
  rules:
    # Allow health checks from ingress
    - from:
        - source:
            principals: ["cluster.local/ns/ingress-nginx/sa/ingress-nginx"]
      to:
        - operation:
            paths: ["/healthz", "/readyz", "/livez"]
            
    # Allow metrics scraping from monitoring
    - from:
        - source:
            principals: ["cluster.local/ns/monitoring/sa/prometheus"]
      to:
        - operation:
            paths: ["/metrics"]
            
    # Allow authenticated API access
    - from:
        - source:
            requestPrincipals: ["https://auth.example.com/*"]
      to:
        - operation:
            paths: ["/api/v2/*"]
      when:
        - key: request.headers[authorization]
          values: ["Bearer *"]
```

### Access Control Lists
- **MAINTAIN:** Service-to-service communication matrix
- **DOCUMENT:** API access patterns and authentication flows
- **IMPLEMENT:** Rate limiting and quota management per service
- **MONITOR:** Authentication failures and access attempts

## 4. Service Discovery and Registration

### Service Registration
- **REGISTER:** Services automatically via Kubernetes service discovery
- **MAINTAIN:** Service catalog with metadata and health status
- **UPDATE:** Service registry on deployment and configuration changes
- **VALIDATE:** Service registration completeness and accuracy

### Service Catalog Template
```yaml
# service-catalog-entry.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: user-service-catalog
  namespace: service-catalog
  labels:
    service-catalog: "true"
    service-name: "user-service"
data:
  metadata.yaml: |
    # Full service metadata from metadata.yaml
  endpoints.yaml: |
    endpoints:
      api:
        url: "https://api.example.com/api/v2"
        internal_url: "http://user-service.api.svc.cluster.local:8080"
        healthcheck: "https://api.example.com/healthz"
      metrics:
        url: "http://user-service.api.svc.cluster.local:9090/metrics"
  dependencies.yaml: |
    # Service dependency graph for impact analysis
```

### Service Mesh Integration
- **CONFIGURE:** Service mesh sidecars for traffic management
- **IMPLEMENT:** Circuit breakers and retry policies
- **MONITOR:** Service-to-service communication patterns
- **SECURE:** mTLS for inter-service communication

## 5. Lifecycle Management

### Service Lifecycle States
- **PLANNED:** Service design and planning phase
- **ACTIVE:** Service deployed and serving traffic
- **DEPRECATED:** Service marked for replacement (SLA maintained)
- **RETIRED:** Service decommissioned and removed

### Lifecycle Automation
```yaml
# lifecycle-webhook.yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionWebhook
metadata:
  name: service-metadata-validator
webhooks:
  - name: metadata.validator.example.com
    clientConfig:
      service:
        name: metadata-validator
        namespace: platform
        path: /validate
    rules:
      - operations: ["CREATE", "UPDATE"]
        apiGroups: ["apps"]
        apiVersions: ["v1"]
        resources: ["deployments"]
    admissionReviewVersions: ["v1"]
    
# Validates:
# - metadata.yaml presence and completeness
# - Service account configuration
# - RBAC permissions
# - Resource limits and requests
# - Security policy compliance
```

### Deprecation and Retirement Process
- **ANNOUNCE:** Service deprecation 6 months in advance
- **MIGRATE:** Provide migration path and timeline
- **MONITOR:** Deprecated service usage and adoption
- **RETIRE:** Remove service after migration completion and notice period

---

## 🛠️ Enforcement & Tooling

### Required CI Checks
- [ ] `metadata.yaml` presence and schema validation
- [ ] Service account and RBAC configuration validation
- [ ] Security policy compliance check
- [ ] Dependency graph validation
- [ ] Service catalog registration

### Repository Requirements
- [ ] `metadata.yaml` with complete service metadata
- [ ] `rbac.yaml` with service account and role definitions
- [ ] Security policies and authorization rules
- [ ] Service documentation and runbooks
- [ ] Dependency declarations and SLA definitions

### Recommended Tools
- **Metadata:** JSON Schema validation, metadata-validator webhook
- **RBAC:** kubectl, rbac-manager, kube-score
- **Service Catalog:** Service catalog API, discovery tools
- **Identity:** Istio, cert-manager, external-secrets

### Metadata Metrics
- **Completeness:** Percentage of services with complete metadata
- **Freshness:** Time since last metadata update
- **Compliance:** RBAC and security policy adherence
- **Dependencies:** Service dependency map accuracy and currency

---

*This rule focuses on service identity, metadata, and lifecycle management. See also: MI-02-service-container-design.md for container standards and AR-06-network-topology-ingress.md for network configuration.* 
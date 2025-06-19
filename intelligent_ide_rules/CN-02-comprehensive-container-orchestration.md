# CN-02: Comprehensive Container Orchestration & Design

## Purpose & Scope

Comprehensive container orchestration covering the complete containerization lifecycle from Docker design through Kubernetes orchestration to service mesh integration. This rule establishes unified standards for container design, resource management, cluster architecture, service mesh implementation, and production-ready container orchestration.

## Core Standards

### 1. Container Design & Build Standards

#### Docker Build Excellence

**Multi-Stage Build Requirements:**
```dockerfile
# multi-stage-template.dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy source and build
COPY . .
RUN npm run build && npm run test

# Production stage - Distroless for security
FROM gcr.io/distroless/nodejs18-debian11 AS production
WORKDIR /app

# Create non-root user (distroless includes nonroot user)
USER nonroot:nonroot

# Copy only production artifacts
COPY --from=builder --chown=nonroot:nonroot /app/dist ./dist
COPY --from=builder --chown=nonroot:nonroot /app/node_modules ./node_modules
COPY --from=builder --chown=nonroot:nonroot /app/package.json ./package.json

# Health check configuration
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["/nodejs/bin/node", "-e", "require('http').get('http://localhost:3000/healthz', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"]

# Expose port
EXPOSE 3000

# Start application
ENTRYPOINT ["/nodejs/bin/node", "dist/index.js"]
```

**Base Image Standards by Language:**
```yaml
# container-base-images.yaml
base_image_standards:
  python:
    development: "python:3.11-slim-bullseye"
    production: "gcr.io/distroless/python3-debian11"
    security_level: "high"
    
  nodejs:
    development: "node:18-alpine"
    production: "gcr.io/distroless/nodejs18-debian11"
    security_level: "high"
    
  golang:
    development: "golang:1.21-alpine"
    production: "gcr.io/distroless/static-debian11"
    security_level: "maximum"
    
  java:
    development: "openjdk:17-jre-slim"
    production: "gcr.io/distroless/java17-debian11"
    security_level: "high"
    
  rust:
    development: "rust:1.70-slim"
    production: "gcr.io/distroless/cc-debian11"
    security_level: "maximum"

image_requirements:
  max_size: "200MB"  # Compressed
  scan_required: true
  vulnerability_threshold: "medium"  # Fail on HIGH/CRITICAL
  base_image_updates: "weekly"
```

#### Container Security Standards

**Security-First Container Design:**
```dockerfile
# security-hardened-container.dockerfile
FROM golang:1.21-alpine AS builder

# Security: Run as non-root during build
RUN adduser -D -s /bin/sh appuser
USER appuser
WORKDIR /home/appuser/app

# Build with security flags
COPY --chown=appuser:appuser . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -a -installsuffix cgo -o app .

# Production: Minimal distroless image
FROM gcr.io/distroless/static-debian11:nonroot

# Copy binary from builder
COPY --from=builder /home/appuser/app/app /app

# Security: Read-only root filesystem
# Security: Drop all capabilities
# Security: Non-root user (nonroot:nonroot)

EXPOSE 8080
ENTRYPOINT ["/app"]
```

**Container Security Checklist:**
```yaml
# container-security-requirements.yaml
security_requirements:
  user_permissions:
    run_as_non_root: true
    user_id_range: "1000-65535"
    read_only_root_filesystem: true
    
  capabilities:
    drop_all: true
    add_only_required: []  # Justify any additions
    
  resource_limits:
    memory_limit_required: true
    cpu_limit_required: true
    pids_limit: 1024
    
  security_scanning:
    base_image_scan: "required"
    dependency_scan: "required"
    secret_detection: "required"
    fail_on_critical: true
    
  runtime_security:
    privileged_containers: "forbidden"
    host_network: "forbidden"
    host_pid: "forbidden"
    host_ipc: "forbidden"
```

### 2. Service Container Classification & Metadata

#### Service Type Framework

**Comprehensive Service Types:**
```yaml
# service-types-framework.yaml
service_types:
  api_service:
    type: "API"
    characteristics:
      - "HTTP/gRPC endpoints"
      - "Stateless design"
      - "Load balancer integration"
      - "Ingress controller support"
    required_probes:
      - "liveness"
      - "readiness"
      - "startup"
    ports:
      http: 8080
      metrics: 9090
      health: 8081
      
  worker_service:
    type: "Worker"
    characteristics:
      - "Background processing"
      - "Queue/event consumption"
      - "No external traffic"
      - "Horizontal pod autoscaling"
    required_probes:
      - "liveness"
    configuration:
      queue_config: "required"
      concurrency_limits: "required"
      
  scheduled_job:
    type: "CronJob"
    characteristics:
      - "Periodic execution"
      - "Finite runtime"
      - "Resource cleanup"
      - "Completion tracking"
    configuration:
      schedule: "required"
      timeout: "required"
      restart_policy: "OnFailure"
      
  cli_tool:
    type: "CLI"
    characteristics:
      - "Command-line interface"
      - "One-time execution"
      - "Exit code semantics"
      - "Portable binary"
    configuration:
      execution_timeout: "required"
      restart_policy: "Never"
```

#### Resource Sizing Standards

**Service Type Resource Allocation:**
```yaml
# resource-allocation-matrix.yaml
resource_standards:
  api_service:
    small:
      requests: { cpu: "100m", memory: "128Mi", ephemeral-storage: "1Gi" }
      limits: { cpu: "500m", memory: "512Mi", ephemeral-storage: "2Gi" }
    medium:
      requests: { cpu: "200m", memory: "256Mi", ephemeral-storage: "2Gi" }
      limits: { cpu: "1000m", memory: "1Gi", ephemeral-storage: "4Gi" }
    large:
      requests: { cpu: "500m", memory: "512Mi", ephemeral-storage: "4Gi" }
      limits: { cpu: "2000m", memory: "2Gi", ephemeral-storage: "8Gi" }
      
  worker_service:
    small:
      requests: { cpu: "50m", memory: "256Mi", ephemeral-storage: "2Gi" }
      limits: { cpu: "1000m", memory: "1Gi", ephemeral-storage: "4Gi" }
    medium:
      requests: { cpu: "200m", memory: "512Mi", ephemeral-storage: "4Gi" }
      limits: { cpu: "2000m", memory: "2Gi", ephemeral-storage: "8Gi" }
    large:
      requests: { cpu: "500m", memory: "1Gi", ephemeral-storage: "8Gi" }
      limits: { cpu: "4000m", memory: "4Gi", ephemeral-storage: "16Gi" }
      
  database:
    small:
      requests: { cpu: "200m", memory: "512Mi", ephemeral-storage: "4Gi" }
      limits: { cpu: "2000m", memory: "2Gi", ephemeral-storage: "8Gi" }
    medium:
      requests: { cpu: "500m", memory: "1Gi", ephemeral-storage: "8Gi" }
      limits: { cpu: "4000m", memory: "4Gi", ephemeral-storage: "16Gi" }
    large:
      requests: { cpu: "1000m", memory: "2Gi", ephemeral-storage: "16Gi" }
      limits: { cpu: "8000m", memory: "8Gi", ephemeral-storage: "32Gi" }

performance_requirements:
  startup_time:
    api_service: "< 30s"
    worker_service: "< 60s"
    database: "< 120s"
    cli_tool: "< 10s"
  health_check_response: "< 3s"
  graceful_shutdown: "< 30s"
```

### 3. Kubernetes Cluster Architecture

#### Production Cluster Standards

**High-Availability Cluster Configuration:**
```yaml
# ha-cluster-architecture.yaml
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
metadata:
  name: production-cluster
spec:
  kubernetesVersion: v1.28.0
  controlPlaneEndpoint: "k8s-api.example.com:6443"
  
  # Control plane HA configuration
  controllerManager:
    extraArgs:
      cluster-signing-cert-file: "/etc/kubernetes/pki/ca.crt"
      cluster-signing-key-file: "/etc/kubernetes/pki/ca.key"
      leader-elect: "true"
      leader-elect-lease-duration: "30s"
      leader-elect-renew-deadline: "20s"
      leader-elect-retry-period: "5s"
      
  scheduler:
    extraArgs:
      leader-elect: "true"
      leader-elect-lease-duration: "30s"
      
  apiServer:
    extraArgs:
      audit-policy-file: "/etc/kubernetes/audit-policy.yaml"
      audit-log-path: "/var/log/kubernetes/audit.log"
      audit-log-maxage: "30"
      audit-log-maxbackup: "10"
      audit-log-maxsize: "100"
      enable-admission-plugins: "NodeRestriction,PodSecurityPolicy,ResourceQuota,NetworkPolicy"
      
  etcd:
    external:
      endpoints:
        - "https://etcd1.example.com:2379"
        - "https://etcd2.example.com:2379"
        - "https://etcd3.example.com:2379"
      caFile: "/etc/kubernetes/pki/etcd/ca.crt"
      certFile: "/etc/kubernetes/pki/etcd/client.crt"
      keyFile: "/etc/kubernetes/pki/etcd/client.key"

  networking:
    podSubnet: "10.244.0.0/16"
    serviceSubnet: "10.96.0.0/12"
    dnsDomain: "cluster.local"
```

**Node Pool Configuration:**
```yaml
# node-pools-configuration.yaml
node_pools:
  system_pool:
    name: "system"
    role: "control-plane-workloads"
    instance_type: "m5.large"
    min_size: 3
    max_size: 5
    disk_size: "100Gi"
    disk_type: "gp3"
    taints:
      - key: "dedicated"
        value: "system"
        effect: "NoSchedule"
    labels:
      node-type: "system"
      workload-class: "system"
      
  general_pool:
    name: "general"
    role: "application-workloads"
    instance_type: "m5.xlarge"
    min_size: 2
    max_size: 20
    disk_size: "200Gi"
    disk_type: "gp3"
    labels:
      node-type: "general"
      workload-class: "general"
      
  compute_pool:
    name: "compute-intensive"
    role: "high-performance-workloads"
    instance_type: "c5.2xlarge"
    min_size: 0
    max_size: 10
    disk_size: "500Gi"
    disk_type: "gp3"
    labels:
      node-type: "compute"
      workload-class: "compute-intensive"
    taints:
      - key: "dedicated"
        value: "compute"
        effect: "NoSchedule"
        
  memory_pool:
    name: "memory-intensive"
    role: "memory-heavy-workloads"
    instance_type: "r5.2xlarge"
    min_size: 0
    max_size: 8
    disk_size: "500Gi"
    disk_type: "gp3"
    labels:
      node-type: "memory"
      workload-class: "memory-intensive"
    taints:
      - key: "dedicated"
        value: "memory"
        effect: "NoSchedule"
```

#### Resource Management & Governance

**Namespace Resource Governance:**
```yaml
# namespace-resource-governance.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    # Compute resources
    requests.cpu: "50"
    requests.memory: "100Gi"
    requests.ephemeral-storage: "500Gi"
    limits.cpu: "100"
    limits.memory: "200Gi"
    limits.ephemeral-storage: "1Ti"
    
    # Storage resources
    requests.storage: "1Ti"
    persistentvolumeclaims: "50"
    
    # Object counts
    pods: "200"
    services: "100"
    secrets: "200"
    configmaps: "100"
    ingresses: "20"
    networkpolicies: "50"
    
---
apiVersion: v1
kind: LimitRange
metadata:
  name: production-limits
  namespace: production
spec:
  limits:
    - type: "Container"
      default:
        cpu: "500m"
        memory: "512Mi"
        ephemeral-storage: "2Gi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
        ephemeral-storage: "1Gi"
      max:
        cpu: "4"
        memory: "8Gi"
        ephemeral-storage: "16Gi"
      min:
        cpu: "10m"
        memory: "32Mi"
        ephemeral-storage: "100Mi"
    - type: "Pod"
      max:
        cpu: "8"
        memory: "16Gi"
        ephemeral-storage: "32Gi"
```

**Priority Class Hierarchy:**
```yaml
# priority-classes.yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: system-cluster-critical
value: 2000000000
globalDefault: false
description: "System cluster critical workloads (kube-system)"

---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: system-node-critical
value: 2000001000
globalDefault: false
description: "System node critical workloads"

---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: business-critical
value: 1000000
globalDefault: false
description: "Business critical applications"

---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 100000
globalDefault: false
description: "High priority applications"

---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: normal
value: 1000
globalDefault: true
description: "Normal priority workloads"

---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: low-priority
value: 100
globalDefault: false
description: "Low priority batch workloads"
```

### 4. Service Mesh Integration

#### Istio Service Mesh Architecture

**Comprehensive Istio Configuration:**
```yaml
# istio-control-plane.yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: production-control-plane
  namespace: istio-system
spec:
  values:
    global:
      meshID: mesh1
      multiCluster:
        clusterName: production-cluster
      network: network1
      
  components:
    pilot:
      k8s:
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        hpaSpec:
          maxReplicas: 5
          minReplicas: 2
          scaleTargetRef:
            apiVersion: apps/v1
            kind: Deployment
            name: istiod
          metrics:
          - type: Resource
            resource:
              name: cpu
              target:
                type: Utilization
                averageUtilization: 80
                
    ingressGateways:
    - name: istio-ingressgateway
      enabled: true
      k8s:
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 2000m
            memory: 1024Mi
        hpaSpec:
          maxReplicas: 10
          minReplicas: 3
        service:
          type: LoadBalancer
          ports:
          - port: 15021
            targetPort: 15021
            name: status-port
          - port: 80
            targetPort: 8080
            name: http2
          - port: 443
            targetPort: 8443
            name: https
            
    egressGateways:
    - name: istio-egressgateway
      enabled: true
      k8s:
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 1000m
            memory: 512Mi
```

**Traffic Management Policies:**
```yaml
# traffic-management.yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: default-circuit-breaker
  namespace: production
spec:
  host: "*.production.svc.cluster.local"
  trafficPolicy:
    circuitBreaker:
      consecutiveGatewayErrors: 5
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 30
    connectionPool:
      tcp:
        maxConnections: 100
        connectTimeout: 30s
        tcpKeepalive:
          time: 7200s
          interval: 75s
      http:
        http1MaxPendingRequests: 100
        http2MaxRequests: 100
        maxRequestsPerConnection: 10
        maxRetries: 3
        consecutiveGatewayErrors: 5
        h2UpgradePolicy: UPGRADE
        
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: default-retry-policy
  namespace: production
spec:
  hosts:
  - "*.production.svc.cluster.local"
  http:
  - fault:
      delay:
        percentage:
          value: 0.1
        fixedDelay: 5s
    retryPolicy:
      attempts: 3
      perTryTimeout: 2s
      retryOn: gateway-error,connect-failure,refused-stream
      retryRemoteLocalities: true
```

### 5. Health Checks & Observability

#### Comprehensive Health Check Framework

**Kubernetes Health Probes:**
```yaml
# health-check-standards.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: example-service
spec:
  template:
    spec:
      containers:
      - name: app
        image: example/service:latest
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 9090
          name: metrics
        - containerPort: 8081
          name: health
          
        # Startup probe - for slow-starting containers
        startupProbe:
          httpGet:
            path: /healthz
            port: health
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 30  # Allow 150s startup time
          
        # Liveness probe - restart container if failing
        livenessProbe:
          httpGet:
            path: /livez
            port: health
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 3
          
        # Readiness probe - remove from service if failing
        readinessProbe:
          httpGet:
            path: /readyz
            port: health
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 3
          
        # Resource limits
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
            ephemeral-storage: 1Gi
          limits:
            cpu: 500m
            memory: 512Mi
            ephemeral-storage: 2Gi
```

**Application Health Check Implementation:**
```typescript
// health-check-service.ts
export class HealthCheckService {
  private dependencies: HealthCheckDependency[] = [];
  
  constructor(dependencies: HealthCheckDependency[]) {
    this.dependencies = dependencies;
  }
  
  async liveness(): Promise<HealthStatus> {
    // Liveness should only check if the application is alive
    // Don't check external dependencies
    return {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      checks: {
        memory: await this.checkMemoryUsage(),
        runtime: await this.checkRuntimeHealth()
      }
    };
  }
  
  async readiness(): Promise<HealthStatus> {
    // Readiness should check if the application can serve traffic
    const results = await Promise.allSettled([
      this.checkDatabase(),
      this.checkCache(),
      this.checkExternalServices()
    ]);
    
    const failed = results.filter(r => r.status === 'rejected');
    
    return {
      status: failed.length === 0 ? 'healthy' : 'unhealthy',
      timestamp: new Date().toISOString(),
      checks: {
        database: results[0].status === 'fulfilled' ? 'healthy' : 'unhealthy',
        cache: results[1].status === 'fulfilled' ? 'healthy' : 'unhealthy',
        external: results[2].status === 'fulfilled' ? 'healthy' : 'unhealthy'
      }
    };
  }
  
  async startup(): Promise<HealthStatus> {
    // Startup should check if the application has completed initialization
    return {
      status: this.isApplicationInitialized() ? 'healthy' : 'unhealthy',
      timestamp: new Date().toISOString(),
      checks: {
        configuration: await this.checkConfiguration(),
        migrations: await this.checkMigrations(),
        dependencies: await this.checkStartupDependencies()
      }
    };
  }
}
```

### 6. Security & Network Policies

#### Pod Security Standards

**Pod Security Policy Implementation:**
```yaml
# pod-security-standards.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
    
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: production
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: production
          
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to: []
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

## Implementation Requirements

### 1. CI/CD Integration

```yaml
# container-cicd-pipeline.yaml
container_pipeline_stages:
  build:
    - "Multi-stage Docker build"
    - "Dependency vulnerability scanning"
    - "Base image security scanning"
    - "Build artifact signing"
    
  test:
    - "Container image testing"
    - "Health check validation"
    - "Resource limit testing"
    - "Security policy validation"
    
  security:
    - "Image vulnerability scanning (Trivy/Grype)"
    - "Secret detection (GitLeaks)"
    - "Policy compliance checking (OPA)"
    - "Runtime security testing"
    
  deployment:
    - "Kubernetes manifest validation"
    - "Resource quota verification"
    - "Network policy validation"
    - "Service mesh configuration"
```

### 2. Monitoring & Observability

```yaml
# container-monitoring-standards.yaml
monitoring_requirements:
  metrics:
    - name: "container_cpu_usage_seconds_total"
      labels: ["namespace", "pod", "container"]
    - name: "container_memory_usage_bytes"
      labels: ["namespace", "pod", "container"]
    - name: "container_network_receive_bytes_total"
      labels: ["namespace", "pod", "interface"]
    - name: "kubernetes_pod_restart_total"
      labels: ["namespace", "pod", "reason"]
      
  logging:
    structured_logging: true
    log_level: "info"
    log_format: "json"
    retention_days: 30
    
  tracing:
    service_mesh_tracing: true
    sampling_rate: 0.1
    trace_retention_days: 7
```

## Quality Standards & Best Practices

### Container Design Checklist
- ✅ Multi-stage Docker builds for size optimization
- ✅ Distroless or minimal base images
- ✅ Non-root user execution
- ✅ Read-only root filesystem where possible
- ✅ Proper health check implementation
- ✅ Resource limits and requests defined
- ✅ Security scanning in CI pipeline
- ✅ Image vulnerability threshold compliance

### Kubernetes Deployment Standards
- ✅ High availability control plane (3+ masters)
- ✅ Node pool separation by workload type
- ✅ Resource quotas and limit ranges
- ✅ Priority classes for workload prioritization
- ✅ Network policies for traffic segmentation
- ✅ Pod security standards enforcement
- ✅ Comprehensive monitoring and alerting

### Service Mesh Requirements
- ✅ Istio service mesh for production workloads
- ✅ Circuit breaker and retry policies
- ✅ Traffic management and load balancing
- ✅ Security policies and mTLS
- ✅ Observability and distributed tracing
- ✅ Gateway configuration for ingress/egress

This comprehensive container orchestration rule consolidates Docker container design principles with Kubernetes orchestration standards into unified guidance for building scalable, secure, and production-ready containerized applications.
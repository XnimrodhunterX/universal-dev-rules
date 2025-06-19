---
description: "Deployment Strategies: Blue-green, canary, rolling deployments, rollback strategies, environment promotion. Production-ready deployment patterns."
globs: ["**/*"]
alwaysApply: true
---

# 🚀 Advanced Deployment Strategies

<!-- CURSOR: highlight: deployment:strategies -->
<!-- CURSOR: context: kubernetes, docker, cicd, production -->
<!-- CURSOR: complexity: advanced -->
<!-- CURSOR: priority: high -->

## 1. Deployment Pattern Standards

### Core Requirements
- **MUST** implement automated deployment strategies with zero-downtime guarantees
- **MUST** support rollback within 5 minutes of deployment failure detection
- **MUST** use progressive delivery patterns for production deployments
- **MUST** maintain environment parity across development, staging, and production

### Deployment Strategy Selection Matrix
```yaml
# deployment-strategy-matrix.yaml
deployment_strategies:
  by_service_type:
    stateless_web_services:
      recommended: "rolling"
      alternatives: ["blue-green", "canary"]
      rollback_time: "< 2 minutes"
    
    stateful_databases:
      recommended: "blue-green"
      alternatives: ["maintenance-window"]
      rollback_time: "< 10 minutes"
    
    critical_apis:
      recommended: "canary"
      alternatives: ["blue-green"]
      rollback_time: "< 1 minute"
    
    background_services:
      recommended: "rolling"
      alternatives: ["recreate"]
      rollback_time: "< 5 minutes"

  by_risk_level:
    low_risk:
      strategies: ["rolling", "recreate"]
      testing_requirements: ["smoke_tests"]
    
    medium_risk:
      strategies: ["blue-green", "rolling"]
      testing_requirements: ["smoke_tests", "integration_tests"]
    
    high_risk:
      strategies: ["canary", "blue-green"]
      testing_requirements: ["smoke_tests", "integration_tests", "load_tests", "chaos_tests"]
```

## 2. Blue-Green Deployment

### Implementation Standards
- **MUST** maintain two identical production environments (blue/green)
- **MUST** implement automated traffic switching with immediate rollback capability
- **MUST** validate green environment before traffic switch
- **MUST** keep blue environment running for rollback during switch window

### Kubernetes Blue-Green Implementation
```yaml
# k8s-blue-green-deployment.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: user-service-rollout
  namespace: production
spec:
  replicas: 10
  strategy:
    blueGreen:
      activeService: user-service-active
      previewService: user-service-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
      prePromotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: user-service-preview
      postPromotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: user-service-active
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: user-service:{{.Values.image.tag}}
        ports:
        - containerPort: 8080
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: user-service-active
  namespace: production
spec:
  selector:
    app: user-service
  ports:
  - port: 80
    targetPort: 8080

---
apiVersion: v1
kind: Service  
metadata:
  name: user-service-preview
  namespace: production
spec:
  selector:
    app: user-service
  ports:
  - port: 80
    targetPort: 8080
```

### Blue-Green Validation Script
```bash
#!/bin/bash
# scripts/blue-green-validation.sh

set -euo pipefail

SERVICE_NAME="${1:-user-service}"
NAMESPACE="${2:-production}"
HEALTH_ENDPOINT="${3:-/health}"
TIMEOUT="${4:-300}"

echo "🔵 Starting Blue-Green deployment validation for ${SERVICE_NAME}"

# Function to check service health
check_service_health() {
    local service_url=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "${service_url}${HEALTH_ENDPOINT}" > /dev/null; then
            echo "✅ Service health check passed"
            return 0
        fi
        
        echo "⏳ Health check attempt ${attempt}/${max_attempts} failed, retrying..."
        sleep 10
        ((attempt++))
    done
    
    echo "❌ Service health check failed after ${max_attempts} attempts"
    return 1
}

# Function to run smoke tests
run_smoke_tests() {
    local service_url=$1
    
    echo "🧪 Running smoke tests against ${service_url}"
    
    # Basic endpoint tests
    curl -f -s "${service_url}/api/v1/status" | jq '.status' | grep -q "healthy"
    curl -f -s "${service_url}/api/v1/version" | jq '.version' | grep -q -E "^[0-9]+\.[0-9]+\.[0-9]+"
    
    # Load test (light)
    echo "📊 Running light load test"
    ab -n 100 -c 10 "${service_url}/api/v1/status" > /dev/null
    
    echo "✅ Smoke tests passed"
}

# Function to validate green environment
validate_green_environment() {
    local green_url="http://${SERVICE_NAME}-preview.${NAMESPACE}.svc.cluster.local"
    
    echo "🟢 Validating green environment: ${green_url}"
    
    # Health checks
    check_service_health "$green_url"
    
    # Smoke tests
    run_smoke_tests "$green_url"
    
    # Database connectivity test
    echo "🗃️ Testing database connectivity"
    curl -f -s "${green_url}/api/v1/health/db" | jq '.database.status' | grep -q "connected"
    
    # Dependency checks
    echo "🔗 Checking external dependencies"
    curl -f -s "${green_url}/api/v1/health/dependencies" | jq '.dependencies[] | select(.status != "healthy")' | wc -l | grep -q "^0$"
    
    echo "✅ Green environment validation complete"
}

# Function to promote to production
promote_to_production() {
    echo "🚀 Promoting green environment to production"
    
    kubectl argo rollouts promote "${SERVICE_NAME}-rollout" -n "$NAMESPACE"
    
    # Wait for promotion to complete
    kubectl argo rollouts status "${SERVICE_NAME}-rollout" -n "$NAMESPACE" --timeout="${TIMEOUT}s"
    
    echo "✅ Promotion complete"
}

# Function to rollback if needed
rollback_deployment() {
    echo "🔄 Rolling back deployment"
    
    kubectl argo rollouts abort "${SERVICE_NAME}-rollout" -n "$NAMESPACE"
    kubectl argo rollouts undo "${SERVICE_NAME}-rollout" -n "$NAMESPACE"
    
    echo "✅ Rollback complete"
}

# Main deployment flow
main() {
    # Validate green environment
    if validate_green_environment; then
        echo "✅ Green environment validation passed"
        
        # Promote to production
        if promote_to_production; then
            echo "🎉 Blue-Green deployment successful"
            exit 0
        else
            echo "❌ Promotion failed, rolling back"
            rollback_deployment
            exit 1
        fi
    else
        echo "❌ Green environment validation failed"
        exit 1
    fi
}

# Trap for cleanup on script exit
trap 'echo "🧹 Cleaning up..."; kubectl delete pod -l app=deployment-validator -n "$NAMESPACE" 2>/dev/null || true' EXIT

main "$@"
```

## 3. Canary Deployment

### Progressive Traffic Shifting
- **MUST** implement gradual traffic shifting (5% → 25% → 50% → 100%)
- **MUST** monitor key metrics during each phase
- **MUST** automatically rollback on metric threshold breaches
- **MUST** require manual approval for final promotion

### Argo Rollouts Canary Configuration
```yaml
# canary-rollout.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: payment-service-canary
  namespace: production
spec:
  replicas: 20
  strategy:
    canary:
      canaryService: payment-service-canary
      stableService: payment-service-stable
      trafficRouting:
        nginx:
          stableIngress: payment-service-ingress
          additionalIngressAnnotations:
            canary-by-header: "x-canary"
      steps:
      - setWeight: 5
      - pause:
          duration: 2m
      - analysis:
          templates:
          - templateName: success-rate
          - templateName: latency
          args:
          - name: service-name
            value: payment-service-canary
      - setWeight: 25
      - pause:
          duration: 5m
      - analysis:
          templates:
          - templateName: success-rate
          - templateName: latency
          - templateName: error-rate
          args:
          - name: service-name
            value: payment-service-canary
      - setWeight: 50
      - pause:
          duration: 10m
      - analysis:
          templates:
          - templateName: success-rate
          - templateName: latency
          - templateName: error-rate
          - templateName: business-metrics
          args:
          - name: service-name
            value: payment-service-canary
      - setWeight: 100
      - pause:
          duration: 2m
  selector:
    matchLabels:
      app: payment-service
  template:
    metadata:
      labels:
        app: payment-service
    spec:
      containers:
      - name: payment-service
        image: payment-service:{{.Values.image.tag}}
        ports:
        - containerPort: 8080
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "info"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Canary Analysis Templates
```yaml
# analysis-templates.yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
  namespace: production
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 30s
    count: 5
    successCondition: result[0] >= 0.95
    failureLimit: 2
    provider:
      prometheus:
        address: http://prometheus.monitoring.svc.cluster.local:9090
        query: |
          sum(rate(http_requests_total{service="{{args.service-name}}", code!~"5.."}[2m])) /
          sum(rate(http_requests_total{service="{{args.service-name}}"}[2m]))

---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: latency
  namespace: production
spec:
  args:
  - name: service-name
  metrics:
  - name: p99-latency
    interval: 30s
    count: 5
    successCondition: result[0] <= 500
    failureLimit: 2
    provider:
      prometheus:
        address: http://prometheus.monitoring.svc.cluster.local:9090
        query: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket{service="{{args.service-name}}"}[2m])) by (le)
          ) * 1000

---
apiVersion: argoproj.io/v1alpha1  
kind: AnalysisTemplate
metadata:
  name: error-rate
  namespace: production
spec:
  args:
  - name: service-name
  metrics:
  - name: error-rate
    interval: 30s
    count: 5
    successCondition: result[0] <= 0.01
    failureLimit: 2
    provider:
      prometheus:
        address: http://prometheus.monitoring.svc.cluster.local:9090
        query: |
          sum(rate(http_requests_total{service="{{args.service-name}}", code=~"5.."}[2m])) /
          sum(rate(http_requests_total{service="{{args.service-name}}"}[2m]))

---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate  
metadata:
  name: business-metrics
  namespace: production
spec:
  args:
  - name: service-name
  metrics:
  - name: transaction-success-rate
    interval: 60s
    count: 3
    successCondition: result[0] >= 0.98
    failureLimit: 1
    provider:
      prometheus:
        address: http://prometheus.monitoring.svc.cluster.local:9090
        query: |
          sum(rate(business_transactions_total{service="{{args.service-name}}", status="success"}[5m])) /
          sum(rate(business_transactions_total{service="{{args.service-name}}"}[5m]))
```

## 4. Rolling Deployment

### Configuration Standards
- **MUST** implement graceful pod termination with proper shutdown hooks
- **MUST** configure readiness and liveness probes for zero-downtime updates
- **MUST** set appropriate resource requests and limits
- **MUST** use pod disruption budgets to ensure availability

### Rolling Deployment Configuration
```yaml
# rolling-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
  namespace: production
  labels:
    app: order-service
    version: v1.2.0
spec:
  replicas: 15
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%        # Max 4 extra pods (15 * 0.25 = 3.75 → 4)
      maxUnavailable: 10%  # Max 2 pods down (15 * 0.10 = 1.5 → 2)
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
        version: v1.2.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      terminationGracePeriodSeconds: 60
      containers:
      - name: order-service
        image: order-service:v1.2.0
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 8081
          name: admin
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "info"
        - name: GRACEFUL_SHUTDOWN_TIMEOUT
          value: "50s"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          successThreshold: 1
          failureThreshold: 3
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 3
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 10"]
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
      volumes:
      - name: config
        configMap:
          name: order-service-config

---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: order-service-pdb
  namespace: production
spec:
  minAvailable: 70%  # Ensure at least 70% of pods remain available
  selector:
    matchLabels:
      app: order-service
```

## 5. Environment Promotion Pipeline

### Promotion Strategy
- **MUST** follow strict environment progression: dev → staging → production
- **MUST** require successful testing at each stage before promotion
- **MUST** implement automated promotion with manual approval gates
- **MUST** maintain environment-specific configurations

### GitOps Environment Promotion
```yaml
# .github/workflows/environment-promotion.yml
name: Environment Promotion Pipeline

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'staging'
        type: choice
        options: ['staging', 'production']
      service:
        description: 'Service name'
        required: true
        type: string

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
      
      - name: Build and push image
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Run security scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ steps.meta.outputs.tags }}
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload security scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

  deploy-staging:
    if: github.ref == 'refs/heads/main'
    needs: build-and-test
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
        with:
          repository: company/k8s-manifests
          token: ${{ secrets.GITOPS_TOKEN }}
          path: manifests
      
      - name: Update staging manifests
        run: |
          cd manifests
          yq eval '.spec.template.spec.containers[0].image = "${{ needs.build-and-test.outputs.image-tag }}"' \
            -i environments/staging/${{ github.event.inputs.service || 'user-service' }}/deployment.yaml
          
          git config user.name "CI pipeline"
          git config user.email "actions@github.com"
          git add .
          git commit -m "Deploy ${{ github.event.inputs.service || 'user-service' }} to staging: ${{ github.sha }}"
          git push
      
      - name: Wait for staging deployment
        run: |
          kubectl wait --for=condition=available deployment/${{ github.event.inputs.service || 'user-service' }} \
            -n staging --timeout=600s

  staging-tests:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run integration tests
        run: |
          npm ci
          npm run test:integration -- --env staging
      
      - name: Run load tests
        run: |
          k6 run --env ENVIRONMENT=staging tests/load/basic-load-test.js
      
      - name: Run security tests
        run: |
          npm run test:security -- --env staging

  promote-to-production:
    needs: [build-and-test, staging-tests]
    runs-on: ubuntu-latest
    environment: production
    if: github.event.inputs.environment == 'production' || (github.ref == 'refs/heads/main' && success())
    steps:
      - uses: actions/checkout@v4
        with:
          repository: company/k8s-manifests
          token: ${{ secrets.GITOPS_TOKEN }}
          path: manifests
      
      - name: Update production manifests
        run: |
          cd manifests
          yq eval '.spec.template.spec.containers[0].image = "${{ needs.build-and-test.outputs.image-tag }}"' \
            -i environments/production/${{ github.event.inputs.service || 'user-service' }}/rollout.yaml
          
          git config user.name "CI pipeline"
          git config user.email "actions@github.com"
          git add .
          git commit -m "Deploy ${{ github.event.inputs.service || 'user-service' }} to production: ${{ github.sha }}"
          git push
      
      - name: Monitor production deployment
        run: |
          kubectl argo rollouts status ${{ github.event.inputs.service || 'user-service' }}-rollout \
            -n production --timeout=1800s
      
      - name: Run production smoke tests
        run: |
          npm run test:smoke -- --env production
      
      - name: Notify deployment success
        uses: 8398a7/action-slack@v3
        with:
          status: success
          text: "🚀 Successfully deployed ${{ github.event.inputs.service || 'user-service' }} to production"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## 6. Rollback Strategies

### Automated Rollback Triggers
- **MUST** implement automatic rollback on health check failures
- **MUST** rollback on breach of error rate thresholds (>1% for 5 minutes)
- **MUST** rollback on latency threshold breaches (P99 >2s for 3 minutes)
- **MUST** provide manual rollback capability within 30 seconds

### Rollback Implementation
```typescript
// src/deployment/rollback-manager.ts
export class RollbackManager {
  private readonly kubernetesClient: KubernetesClient;
  private readonly metricsClient: PrometheusClient;
  private readonly alertManager: AlertManager;

  constructor(
    kubernetesClient: KubernetesClient,
    metricsClient: PrometheusClient,
    alertManager: AlertManager
  ) {
    this.kubernetesClient = kubernetesClient;
    this.metricsClient = metricsClient;
    this.alertManager = alertManager;
  }

  async monitorDeployment(
    serviceName: string,
    namespace: string,
    rollbackThresholds: RollbackThresholds
  ): Promise<DeploymentMonitorResult> {
    const monitoringSession = new DeploymentMonitoringSession(
      serviceName,
      namespace,
      rollbackThresholds
    );

    try {
      // Start monitoring metrics
      await this.startMetricsMonitoring(monitoringSession);
      
      // Monitor deployment progress
      const deploymentResult = await this.monitorDeploymentProgress(monitoringSession);
      
      if (!deploymentResult.success) {
        await this.executeRollback(monitoringSession, deploymentResult.reason);
        return { success: false, rolledBack: true, reason: deploymentResult.reason };
      }

      return { success: true, rolledBack: false };
    } catch (error) {
      await this.executeRollback(monitoringSession, `Monitoring error: ${error.message}`);
      throw error;
    }
  }

  private async startMetricsMonitoring(session: DeploymentMonitoringSession): Promise<void> {
    const metrics = [
      this.monitorErrorRate(session),
      this.monitorLatency(session),
      this.monitorHealthChecks(session),
      this.monitorBusinessMetrics(session)
    ];

    await Promise.all(metrics);
  }

  private async monitorErrorRate(session: DeploymentMonitoringSession): Promise<void> {
    const query = `
      sum(rate(http_requests_total{service="${session.serviceName}", code=~"5.."}[2m])) /
      sum(rate(http_requests_total{service="${session.serviceName}"}[2m]))
    `;

    const errorRateChecker = setInterval(async () => {
      try {
        const errorRate = await this.metricsClient.query(query);
        
        if (errorRate > session.thresholds.maxErrorRate) {
          session.breachCount.errorRate++;
          
          if (session.breachCount.errorRate >= session.thresholds.maxConsecutiveBreaches) {
            await this.triggerRollback(session, `Error rate ${errorRate * 100}% exceeds threshold ${session.thresholds.maxErrorRate * 100}%`);
          }
        } else {
          session.breachCount.errorRate = 0; // Reset on success
        }
      } catch (error) {
        console.error('Error monitoring error rate:', error);
      }
    }, 30000); // Check every 30 seconds

    session.intervals.push(errorRateChecker);
  }

  private async monitorLatency(session: DeploymentMonitoringSession): Promise<void> {
    const query = `
      histogram_quantile(0.99,
        sum(rate(http_request_duration_seconds_bucket{service="${session.serviceName}"}[2m])) by (le)
      ) * 1000
    `;

    const latencyChecker = setInterval(async () => {
      try {
        const p99Latency = await this.metricsClient.query(query);
        
        if (p99Latency > session.thresholds.maxLatencyMs) {
          session.breachCount.latency++;
          
          if (session.breachCount.latency >= session.thresholds.maxConsecutiveBreaches) {
            await this.triggerRollback(session, `P99 latency ${p99Latency}ms exceeds threshold ${session.thresholds.maxLatencyMs}ms`);
          }
        } else {
          session.breachCount.latency = 0;
        }
      } catch (error) {
        console.error('Error monitoring latency:', error);
      }
    }, 30000);

    session.intervals.push(latencyChecker);
  }

  private async monitorHealthChecks(session: DeploymentMonitoringSession): Promise<void> {
    const healthChecker = setInterval(async () => {
      try {
        const pods = await this.kubernetesClient.getPods(session.serviceName, session.namespace);
        const healthyPods = pods.filter(pod => pod.status.phase === 'Running' && 
                                             pod.status.conditions?.every(c => c.status === 'True'));
        
        const healthyPercentage = healthyPods.length / pods.length;
        
        if (healthyPercentage < session.thresholds.minHealthyPods) {
          session.breachCount.health++;
          
          if (session.breachCount.health >= session.thresholds.maxConsecutiveBreaches) {
            await this.triggerRollback(session, `Only ${Math.round(healthyPercentage * 100)}% pods healthy, below threshold ${session.thresholds.minHealthyPods * 100}%`);
          }
        } else {
          session.breachCount.health = 0;
        }
      } catch (error) {
        console.error('Error monitoring health checks:', error);
      }
    }, 15000); // Check every 15 seconds

    session.intervals.push(healthChecker);
  }

  private async executeRollback(
    session: DeploymentMonitoringSession,
    reason: string
  ): Promise<void> {
    console.log(`🔄 Executing rollback for ${session.serviceName}: ${reason}`);
    
    try {
      // Clear monitoring intervals
      session.intervals.forEach(interval => clearInterval(interval));
      
      // Execute rollback based on deployment type
      if (await this.isArgoRollout(session.serviceName, session.namespace)) {
        await this.rollbackArgoRollout(session.serviceName, session.namespace);
      } else {
        await this.rollbackDeployment(session.serviceName, session.namespace);
      }
      
      // Send alerts
      await this.alertManager.sendAlert({
        severity: 'critical',
        title: `Automatic rollback executed: ${session.serviceName}`,
        description: reason,
        service: session.serviceName,
        namespace: session.namespace,
        timestamp: new Date()
      });
      
      console.log(`✅ Rollback completed for ${session.serviceName}`);
    } catch (error) {
      console.error(`❌ Rollback failed for ${session.serviceName}:`, error);
      throw error;
    }
  }

  private async rollbackArgoRollout(serviceName: string, namespace: string): Promise<void> {
    // Abort current rollout
    await this.kubernetesClient.exec('kubectl', [
      'argo', 'rollouts', 'abort', `${serviceName}-rollout`, '-n', namespace
    ]);
    
    // Rollback to previous version
    await this.kubernetesClient.exec('kubectl', [
      'argo', 'rollouts', 'undo', `${serviceName}-rollout`, '-n', namespace
    ]);
    
    // Wait for rollback to complete
    await this.kubernetesClient.exec('kubectl', [
      'argo', 'rollouts', 'status', `${serviceName}-rollout`, '-n', namespace, '--timeout=300s'
    ]);
  }

  private async rollbackDeployment(serviceName: string, namespace: string): Promise<void> {
    // Rollback deployment
    await this.kubernetesClient.exec('kubectl', [
      'rollout', 'undo', 'deployment', serviceName, '-n', namespace
    ]);
    
    // Wait for rollback to complete
    await this.kubernetesClient.exec('kubectl', [
      'rollout', 'status', 'deployment', serviceName, '-n', namespace, '--timeout=300s'
    ]);
  }
}

export interface RollbackThresholds {
  maxErrorRate: number;      // e.g., 0.01 for 1%
  maxLatencyMs: number;      // e.g., 2000 for 2 seconds
  minHealthyPods: number;    // e.g., 0.8 for 80%
  maxConsecutiveBreaches: number; // e.g., 3
}

export interface DeploymentMonitoringSession {
  serviceName: string;
  namespace: string;
  thresholds: RollbackThresholds;
  breachCount: {
    errorRate: number;
    latency: number;
    health: number;
  };
  intervals: NodeJS.Timeout[];
}
```

## 7. Quality Gates & Monitoring

### Deployment Quality Gates
```yaml
# Quality gates for deployment strategies
deployment_quality_gates:
  blue_green_validation:
    description: "Green environment validation success rate"
    metric: "green_environment_validation_success_rate"
    threshold: 100
    blocking: true

  canary_progression:
    description: "Canary deployments completing without rollback"
    metric: "canary_deployment_success_rate"
    threshold: 95
    blocking: false

  rollback_time:
    description: "Time to complete rollback operation"
    metric: "rollback_completion_time_seconds"
    threshold: 300
    blocking: true

  deployment_frequency:
    description: "DORA metric: Deployment frequency"
    metric: "deployments_per_day"
    threshold: 1
    blocking: false

  lead_time:
    description: "DORA metric: Lead time for changes"
    metric: "lead_time_hours"
    threshold: 24
    blocking: false
```

---

## 📋 **Implementation Checklist**

### Blue-Green Deployment
- [ ] Set up identical production environments (blue/green)
- [ ] Implement automated traffic switching
- [ ] Create validation scripts for green environment
- [ ] Configure rollback mechanisms

### Canary Deployment  
- [ ] Configure Argo Rollouts with canary strategy
- [ ] Set up progressive traffic shifting
- [ ] Implement automated analysis and rollback
- [ ] Create monitoring dashboards

### Rolling Deployment
- [ ] Configure pod disruption budgets
- [ ] Implement graceful shutdown handling
- [ ] Set up readiness and liveness probes
- [ ] Configure resource limits and requests

### Environment Promotion
- [ ] Set up GitOps repository structure
- [ ] Implement automated promotion pipeline
- [ ] Configure approval gates for production
- [ ] Set up environment-specific configurations

### Rollback Strategy
- [ ] Implement automated rollback triggers
- [ ] Set up metrics monitoring and alerting
- [ ] Test rollback procedures regularly
- [ ] Document manual rollback processes

---

## 🎯 **Success Metrics**

- **Deployment Success Rate:** 99.5% of deployments complete without issues
- **Rollback Time:** <5 minutes for automatic rollbacks, <2 minutes for manual
- **Zero-Downtime Deployments:** 100% of deployments maintain service availability
- **Mean Time to Recovery:** <10 minutes from failure detection to service restoration
- **Environment Parity:** 100% configuration consistency across environments 
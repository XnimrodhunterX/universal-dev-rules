---
description: "Universal CI/CD pipelines: automated testing, deployment strategies, pipeline security. Comprehensive DevOps automation standards."
globs: ["**/*"]
alwaysApply: true
---

# 🚀 Universal CI/CD Pipelines

## 1. Pipeline Architecture Standards

### CI/CD Requirements
- **AUTOMATE:** Complete build, test, and deployment pipeline
- **IMPLEMENT:** Multi-stage environments with progressive deployment
- **ENFORCE:** Quality gates and security scanning at each stage
- **ENSURE:** Rollback capability and deployment monitoring

### CI pipeline Pipeline Template
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  release:
    types: [published]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
  NODE_VERSION: '18'
  PNPM_VERSION: '8.15.0'

jobs:
  quality-gates:
    name: Quality Gates
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
      should-deploy: ${{ steps.deploy-check.outputs.should-deploy }}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: ${{ env.PNPM_VERSION }}

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Lint check
        run: pnpm lint

      - name: Type check
        run: pnpm type-check

      - name: Security audit
        run: pnpm audit --audit-level moderate

      - name: License check
        run: pnpm license-checker --onlyAllow 'MIT;Apache-2.0;ISC;BSD;BSD-2-Clause;BSD-3-Clause'

      - name: Generate version
        id: version
        run: |
          if [[ "${{ github.event_name }}" == "release" ]]; then
            VERSION=${{ github.event.release.tag_name }}
          else
            VERSION=$(date +%Y%m%d)-$(git rev-parse --short HEAD)
          fi
          echo "version=${VERSION}" >> $GITHUB_OUTPUT

      - name: Check deployment conditions
        id: deploy-check
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]] || [[ "${{ github.event_name }}" == "release" ]]; then
            echo "should-deploy=true" >> $GITHUB_OUTPUT
          else
            echo "should-deploy=false" >> $GITHUB_OUTPUT
          fi

  test-unit:
    name: Unit Tests
    runs-on: ubuntu-latest
    needs: quality-gates
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: ${{ env.PNPM_VERSION }}

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run unit tests
        run: pnpm test:unit --coverage --reporter=ci-pipeline
        env:
          CI: true

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          file: ./coverage/lcov.info
          flags: unit

      - name: Coverage quality gate
        run: |
          COVERAGE=$(node -pe "JSON.parse(require('fs').readFileSync('./coverage/coverage-summary.json')).total.lines.pct")
          if (( $(echo "$COVERAGE < 90" | bc -l) )); then
            echo "Coverage $COVERAGE% is below 90% threshold"
            exit 1
          fi

  test-integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: quality-gates
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: ${{ env.PNPM_VERSION }}

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run database migrations
        run: pnpm db:migrate
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb

      - name: Run integration tests
        run: pnpm test:integration --coverage
        env:
          CI: true
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379

      - name: Upload integration coverage
        uses: codecov/codecov-action@v3
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          file: ./coverage/lcov.info
          flags: integration

  security-scan:
    name: Security Scanning
    runs-on: ubuntu-latest
    needs: quality-gates
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run Snyk security scan
        uses: snyk/actions/node@master
        continue-on-error: true
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=medium

      - name: SAST with CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: javascript

      - name: CodeQL analysis
        uses: github/codeql-action/analyze@v2

      - name: Container security scan
        if: needs.quality-gates.outputs.should-deploy == 'true'
        run: |
          docker build -t temp-image:latest .
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
            -v $PWD:/tmp/trivy aquasec/trivy:latest image \
            --exit-code 1 --severity HIGH,CRITICAL temp-image:latest

  build-and-push:
    name: Build & Push Container
    runs-on: ubuntu-latest
    needs: [quality-gates, test-unit, test-integration, security-scan]
    if: needs.quality-gates.outputs.should-deploy == 'true'
    
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=raw,value=latest,enable={{is_default_branch}}
            type=raw,value=${{ needs.quality-gates.outputs.version }}

      - name: Build and push container image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          build-args: |
            VERSION=${{ needs.quality-gates.outputs.version }}
            BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
            VCS_REF=${{ github.sha }}

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [quality-gates, build-and-push]
    if: needs.quality-gates.outputs.should-deploy == 'true' && github.ref == 'refs/heads/main'
    environment:
      name: staging
      url: https://staging.example.com
    
    steps:
      - name: Checkout deployment configs
        uses: actions/checkout@v4
        with:
          repository: company/deployment-configs
          token: ${{ secrets.DEPLOY_TOKEN }}
          path: deployment-configs

      - name: Setup kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'latest'

      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBE_CONFIG_STAGING }}" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig

      - name: Deploy to staging
        run: |
          export KUBECONFIG=kubeconfig
          envsubst < deployment-configs/staging/deployment.yaml | kubectl apply -f -
          kubectl set image deployment/api api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ needs.quality-gates.outputs.version }}
          kubectl rollout status deployment/api --timeout=300s
        env:
          IMAGE_TAG: ${{ needs.quality-gates.outputs.version }}
          ENVIRONMENT: staging

      - name: Run smoke tests
        run: |
          sleep 30  # Wait for deployment to stabilize
          curl -f https://staging.example.com/health || exit 1
          # Add more smoke tests here

  test-e2e:
    name: E2E Tests (Staging)
    runs-on: ubuntu-latest
    needs: deploy-staging
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: ${{ env.PNPM_VERSION }}

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run E2E tests
        run: pnpm test:e2e
        env:
          BASE_URL: https://staging.example.com
          CI: true

      - name: Upload E2E artifacts
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: e2e-artifacts
          path: |
            test-results/
            screenshots/
            videos/

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [quality-gates, test-e2e]
    if: github.event_name == 'release'
    environment:
      name: production
      url: https://api.example.com
    
    steps:
      - name: Checkout deployment configs
        uses: actions/checkout@v4
        with:
          repository: company/deployment-configs
          token: ${{ secrets.DEPLOY_TOKEN }}
          path: deployment-configs

      - name: Setup kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'latest'

      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBE_CONFIG_PROD }}" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig

      - name: Blue-Green deployment
        run: |
          export KUBECONFIG=kubeconfig
          # Implementation of blue-green deployment strategy
          ./deployment-configs/scripts/blue-green-deploy.sh \
            --image=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ needs.quality-gates.outputs.version }} \
            --environment=production \
            --timeout=600

      - name: Run production smoke tests
        run: |
          sleep 60  # Wait for deployment to stabilize
          curl -f https://api.example.com/health || exit 1
          # Add production-specific validation

      - name: Update monitoring
        run: |
          # Notify monitoring systems of deployment
          curl -X POST "${{ secrets.MONITORING_WEBHOOK }}" \
            -H "Content-Type: application/json" \
            -d '{
              "event": "deployment",
              "service": "${{ github.repository }}",
              "version": "${{ needs.quality-gates.outputs.version }}",
              "environment": "production",
              "timestamp": "'$(date -u +'%Y-%m-%dT%H:%M:%SZ')'"
            }'

  notify:
    name: Notification
    runs-on: ubuntu-latest
    needs: [deploy-production]
    if: always()
    
    steps:
      - name: Notify team
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
          fields: repo,message,commit,author,action,eventName,ref,workflow
```

## 2. Pipeline Security Standards

### Secret Management in Pipelines
```typescript
// scripts/pipeline-security.ts
export class PipelineSecurityManager {
  private secretsValidator: SecretsValidator;
  private signatureValidator: SignatureValidator;

  constructor() {
    this.secretsValidator = new SecretsValidator();
    this.signatureValidator = new SignatureValidator();
  }

  async validateSecrets(): Promise<ValidationResult> {
    const violations: string[] = [];

    // Check for hardcoded secrets
    const secretsInCode = await this.secretsValidator.scanForSecrets('./');
    if (secretsInCode.length > 0) {
      violations.push(`Found ${secretsInCode.length} potential secrets in code`);
    }

    // Validate secret rotation
    const secretsAge = await this.secretsValidator.checkSecretsAge();
    const expiredSecrets = secretsAge.filter(s => s.ageInDays > 90);
    if (expiredSecrets.length > 0) {
      violations.push(`Found ${expiredSecrets.length} secrets older than 90 days`);
    }

    // Check for proper secret scoping
    const improperlyScopedSecrets = await this.secretsValidator.checkSecretScoping();
    if (improperlyScopedSecrets.length > 0) {
      violations.push(`Found ${improperlyScopedSecrets.length} improperly scoped secrets`);
    }

    return {
      passed: violations.length === 0,
      violations,
      recommendations: this.generateSecurityRecommendations(violations)
    };
  }

  async validateSignatures(): Promise<SignatureValidationResult> {
    // Validate commit signatures
    const unsignedCommits = await this.signatureValidator.checkCommitSignatures();
    
    // Validate artifact signatures
    const unsignedArtifacts = await this.signatureValidator.checkArtifactSignatures();

    return {
      commitsValid: unsignedCommits.length === 0,
      artifactsValid: unsignedArtifacts.length === 0,
      unsignedCommits,
      unsignedArtifacts
    };
  }

  private generateSecurityRecommendations(violations: string[]): string[] {
    const recommendations: string[] = [];

    if (violations.some(v => v.includes('secrets in code'))) {
      recommendations.push('Move secrets to environment variables or secret management system');
      recommendations.push('Use secret scanning tools in pre-commit hooks');
    }

    if (violations.some(v => v.includes('older than 90 days'))) {
      recommendations.push('Implement automated secret rotation');
      recommendations.push('Set up alerts for secret expiration');
    }

    return recommendations;
  }
}

// Pipeline configuration validation
export class PipelineConfigValidator {
  async validateConfiguration(configPath: string): Promise<ConfigValidationResult> {
    const config = await this.loadConfig(configPath);
    const violations: string[] = [];

    // Check required stages
    const requiredStages = ['build', 'test', 'security-scan', 'deploy'];
    const missingStages = requiredStages.filter(stage => !config.stages.includes(stage));
    if (missingStages.length > 0) {
      violations.push(`Missing required stages: ${missingStages.join(', ')}`);
    }

    // Check quality gates
    if (!config.qualityGates || config.qualityGates.length === 0) {
      violations.push('No quality gates defined');
    }

    // Check environment promotion
    if (!config.environments || !config.environments.includes('staging')) {
      violations.push('Missing staging environment');
    }

    // Check rollback capability
    if (!config.rollbackEnabled) {
      violations.push('Rollback capability not enabled');
    }

    return {
      valid: violations.length === 0,
      violations,
      config
    };
  }

  private async loadConfig(configPath: string): Promise<PipelineConfig> {
    // Implementation to load and parse pipeline configuration
    return {} as PipelineConfig;
  }
}
```

### Container Security
```dockerfile
# Dockerfile.secure - Security-focused Dockerfile template
# Use specific version tags, not 'latest'
FROM node:18.19.0-alpine3.19 AS base

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json pnpm-lock.yaml ./

# Install dependencies as root, then switch to non-root
RUN npm install -g pnpm@8.15.0 && \
    pnpm install --frozen-lockfile --only=production && \
    pnpm store prune

# Multi-stage build for smaller production image
FROM node:18.19.0-alpine3.19 AS production

# Install security updates
RUN apk update && apk upgrade

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

WORKDIR /app

# Copy only necessary files
COPY --from=base /app/node_modules ./node_modules
COPY --chown=nextjs:nodejs . .

# Build application
RUN npm run build

# Remove development dependencies and build tools
RUN npm prune --production && \
    rm -rf .git .gitignore README.md docs/ tests/ .eslintrc.js

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Add labels for metadata
LABEL maintainer="platform-team@example.com" \
      version="1.0.0" \
      description="Secure Node.js application container"

# Use exec form for better signal handling
CMD ["node", "dist/server.js"]
```

## 3. Deployment Strategies

### Blue-Green Deployment Script
```bash
#!/bin/bash
# scripts/blue-green-deploy.sh

set -euo pipefail

# Configuration
NAMESPACE=${NAMESPACE:-default}
APP_NAME=${APP_NAME:-api}
NEW_IMAGE=${1:?Image required}
HEALTH_CHECK_URL=${HEALTH_CHECK_URL:-http://localhost:3000/health}
TIMEOUT=${TIMEOUT:-300}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Get current active deployment
get_active_color() {
    kubectl get service ${APP_NAME} -o jsonpath='{.spec.selector.version}' 2>/dev/null || echo "blue"
}

# Switch between blue and green
get_inactive_color() {
    local active_color=$1
    if [[ "$active_color" == "blue" ]]; then
        echo "green"
    else
        echo "blue"
    fi
}

# Deploy to inactive environment
deploy_inactive() {
    local inactive_color=$1
    local image=$2
    
    log "Deploying to $inactive_color environment..."
    
    # Update deployment with new image
    kubectl set image deployment/${APP_NAME}-${inactive_color} \
        ${APP_NAME}=${image} \
        --namespace=${NAMESPACE}
    
    # Wait for deployment to be ready
    log "Waiting for deployment to be ready..."
    kubectl rollout status deployment/${APP_NAME}-${inactive_color} \
        --namespace=${NAMESPACE} \
        --timeout=${TIMEOUT}s
}

# Health check
health_check() {
    local color=$1
    local max_attempts=30
    local attempt=1
    
    log "Running health checks for $color environment..."
    
    # Get service endpoint
    local service_ip=$(kubectl get service ${APP_NAME}-${color} \
        -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "localhost")
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "${HEALTH_CHECK_URL}" > /dev/null; then
            log "Health check passed for $color environment"
            return 0
        fi
        
        warn "Health check failed (attempt $attempt/$max_attempts). Retrying in 10s..."
        sleep 10
        ((attempt++))
    done
    
    error "Health check failed after $max_attempts attempts"
}

# Switch traffic
switch_traffic() {
    local new_active_color=$1
    
    log "Switching traffic to $new_active_color environment..."
    
    # Update service selector
    kubectl patch service ${APP_NAME} \
        -p '{"spec":{"selector":{"version":"'${new_active_color}'"}}}' \
        --namespace=${NAMESPACE}
    
    log "Traffic switched to $new_active_color environment"
}

# Rollback function
rollback() {
    local previous_color=$1
    warn "Rolling back to $previous_color environment..."
    switch_traffic $previous_color
}

# Main deployment flow
main() {
    local image=$1
    
    log "Starting blue-green deployment for image: $image"
    
    # Determine current active color
    local active_color=$(get_active_color)
    local inactive_color=$(get_inactive_color $active_color)
    
    log "Current active environment: $active_color"
    log "Deploying to inactive environment: $inactive_color"
    
    # Deploy to inactive environment
    deploy_inactive $inactive_color $image
    
    # Run health checks
    if ! health_check $inactive_color; then
        error "Health checks failed. Deployment aborted."
    fi
    
    # Switch traffic
    switch_traffic $inactive_color
    
    # Final verification
    log "Running final verification..."
    sleep 30  # Allow time for traffic to switch
    
    if ! health_check $inactive_color; then
        error "Final verification failed. Rolling back..."
        rollback $active_color
    fi
    
    log "Blue-green deployment completed successfully!"
    log "New active environment: $inactive_color"
    log "Previous environment ($active_color) is now inactive and can be used for next deployment"
}

# Trap to handle failures
trap 'error "Deployment failed at line $LINENO"' ERR

# Run main function
main "$@"
```

### Canary Deployment Configuration
```yaml
# k8s/canary-deployment.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: api-rollout
  namespace: default
spec:
  replicas: 10
  strategy:
    canary:
      # Traffic routing
      trafficRouting:
        nginx:
          stableIngress: api-stable
          annotationPrefix: nginx.ingress.kubernetes.io
          additionalIngressAnnotations:
            canary-by-header: X-Canary
            canary-by-header-value: "true"
      
      # Canary steps
      steps:
      - setWeight: 10  # 10% traffic to canary
      - pause: {duration: 2m}  # Wait 2 minutes
      - setWeight: 25  # 25% traffic to canary
      - pause: {duration: 5m}  # Wait 5 minutes
      - setWeight: 50  # 50% traffic to canary
      - pause: {duration: 10m} # Wait 10 minutes
      - setWeight: 75  # 75% traffic to canary
      - pause: {duration: 5m}  # Wait 5 minutes
      
      # Analysis and metrics
      analysis:
        templates:
        - templateName: error-rate
        - templateName: response-time
        args:
        - name: service-name
          value: api
      
      # Automatic rollback conditions
      abortConditions:
      - failureLimit: 3
      - errorRate: 0.05  # 5% error rate
      
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: api:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate
spec:
  args:
  - name: service-name
  metrics:
  - name: error-rate
    interval: 1m
    successCondition: result[0] < 0.05  # Less than 5% error rate
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus.monitoring.svc.cluster.local:9090
        query: |
          sum(rate(http_requests_total{service="{{args.service-name}}",status=~"5.."}[5m])) /
          sum(rate(http_requests_total{service="{{args.service-name}}"}[5m]))

---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: response-time
spec:
  args:
  - name: service-name
  metrics:
  - name: response-time-p95
    interval: 1m
    successCondition: result[0] < 0.5  # Less than 500ms
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus.monitoring.svc.cluster.local:9090
        query: |
          histogram_quantile(0.95,
            rate(http_request_duration_seconds_bucket{service="{{args.service-name}}"}[5m])
          )
```

## 4. Pipeline Monitoring & Metrics

### Pipeline Metrics Collection
```typescript
// src/pipeline/metrics-collector.ts
export class PipelineMetricsCollector {
  private metricsClient: MetricsClient;
  
  constructor(metricsClient: MetricsClient) {
    this.metricsClient = metricsClient;
  }

  async recordDeployment(deployment: DeploymentRecord): Promise<void> {
    // Record deployment metrics
    await this.metricsClient.increment('deployments_total', {
      environment: deployment.environment,
      service: deployment.service,
      status: deployment.status
    });

    await this.metricsClient.histogram('deployment_duration_seconds', 
      deployment.duration, {
        environment: deployment.environment,
        service: deployment.service
      });

    // Lead time metrics
    if (deployment.leadTime) {
      await this.metricsClient.histogram('lead_time_seconds',
        deployment.leadTime, {
          service: deployment.service
        });
    }

    // Deployment frequency
    await this.metricsClient.increment('deployment_frequency', {
      service: deployment.service,
      environment: deployment.environment
    });
  }

  async recordPipelineStage(stage: PipelineStage): Promise<void> {
    await this.metricsClient.histogram('pipeline_stage_duration_seconds',
      stage.duration, {
        stage: stage.name,
        status: stage.status,
        service: stage.service
      });

    if (stage.status === 'failed') {
      await this.metricsClient.increment('pipeline_stage_failures_total', {
        stage: stage.name,
        service: stage.service,
        error_type: stage.errorType
      });
    }
  }

  async recordMTTR(incident: IncidentRecord): Promise<void> {
    await this.metricsClient.histogram('mean_time_to_recovery_seconds',
      incident.recoveryTime, {
        service: incident.service,
        severity: incident.severity
      });
  }

  async recordChangeFailureRate(change: ChangeRecord): Promise<void> {
    await this.metricsClient.increment('changes_total', {
      service: change.service,
      type: change.type
    });

    if (change.failed) {
      await this.metricsClient.increment('change_failures_total', {
        service: change.service,
        type: change.type,
        failure_reason: change.failureReason
      });
    }
  }

  async generateDORAMetrics(): Promise<DORAMetrics> {
    // Deployment Frequency
    const deploymentFreq = await this.metricsClient.query(
      'sum(rate(deployments_total{status="success"}[7d])) by (service)'
    );

    // Lead Time for Changes
    const leadTime = await this.metricsClient.query(
      'histogram_quantile(0.5, rate(lead_time_seconds_bucket[30d]))'
    );

    // Mean Time to Recovery
    const mttr = await this.metricsClient.query(
      'histogram_quantile(0.5, rate(mean_time_to_recovery_seconds_bucket[30d]))'
    );

    // Change Failure Rate
    const changeFailureRate = await this.metricsClient.query(
      'sum(rate(change_failures_total[30d])) / sum(rate(changes_total[30d]))'
    );

    return {
      deploymentFrequency: deploymentFreq.value,
      leadTime: leadTime.value,
      meanTimeToRecovery: mttr.value,
      changeFailureRate: changeFailureRate.value,
      timestamp: new Date().toISOString()
    };
  }
}

export interface DeploymentRecord {
  service: string;
  environment: string;
  version: string;
  status: 'success' | 'failed' | 'rollback';
  duration: number;
  leadTime?: number;
  timestamp: Date;
}

export interface PipelineStage {
  name: string;
  service: string;
  status: 'success' | 'failed' | 'skipped';
  duration: number;
  errorType?: string;
  timestamp: Date;
}

export interface DORAMetrics {
  deploymentFrequency: number;
  leadTime: number;
  meanTimeToRecovery: number;
  changeFailureRate: number;
  timestamp: string;
}
```

## 5. Quality Gates & Validation

### Quality Gate Enforcement
```typescript
// src/pipeline/quality-gates.ts
export class QualityGateValidator {
  async validateCodeQuality(project: string): Promise<QualityResult> {
    const results: QualityResult = {
      passed: true,
      violations: [],
      metrics: {}
    };

    // Code coverage
    const coverage = await this.getCoverageMetrics(project);
    results.metrics.coverage = coverage;
    
    if (coverage.overall < 90) {
      results.passed = false;
      results.violations.push(`Code coverage ${coverage.overall}% below 90% threshold`);
    }

    // Code complexity
    const complexity = await this.getComplexityMetrics(project);
    results.metrics.complexity = complexity;
    
    if (complexity.average > 10) {
      results.passed = false;
      results.violations.push(`Average complexity ${complexity.average} above 10 threshold`);
    }

    // Security vulnerabilities
    const security = await this.getSecurityScanResults(project);
    results.metrics.security = security;
    
    if (security.high > 0 || security.critical > 0) {
      results.passed = false;
      results.violations.push(`Found ${security.high + security.critical} high/critical vulnerabilities`);
    }

    // License compliance
    const licenses = await this.getLicenseCompliance(project);
    results.metrics.licenses = licenses;
    
    if (!licenses.compliant) {
      results.passed = false;
      results.violations.push(`License compliance failed: ${licenses.violations.join(', ')}`);
    }

    return results;
  }

  async validatePerformance(environment: string): Promise<PerformanceResult> {
    const results: PerformanceResult = {
      passed: true,
      violations: [],
      metrics: {}
    };

    // Response time check
    const responseTime = await this.measureResponseTime(environment);
    results.metrics.responseTime = responseTime;
    
    if (responseTime.p95 > 500) {
      results.passed = false;
      results.violations.push(`P95 response time ${responseTime.p95}ms above 500ms threshold`);
    }

    // Resource utilization
    const resources = await this.getResourceUtilization(environment);
    results.metrics.resources = resources;
    
    if (resources.cpu > 80 || resources.memory > 80) {
      results.passed = false;
      results.violations.push(`Resource utilization too high: CPU ${resources.cpu}%, Memory ${resources.memory}%`);
    }

    return results;
  }

  private async getCoverageMetrics(project: string): Promise<CoverageMetrics> {
    // Implementation to read coverage reports
    return {
      overall: 92,
      lines: 94,
      branches: 88,
      functions: 96
    };
  }

  private async getComplexityMetrics(project: string): Promise<ComplexityMetrics> {
    // Implementation to analyze code complexity
    return {
      average: 8.5,
      maximum: 15,
      files: 142
    };
  }

  private async getSecurityScanResults(project: string): Promise<SecurityMetrics> {
    // Implementation to read security scan results
    return {
      critical: 0,
      high: 1,
      medium: 3,
      low: 7,
      total: 11
    };
  }
}

export interface QualityResult {
  passed: boolean;
  violations: string[];
  metrics: Record<string, any>;
}

export interface PerformanceResult {
  passed: boolean;
  violations: string[];
  metrics: Record<string, any>;
}
```

## 6. Configuration Templates

### Pipeline Configuration
```yaml
# .pipeline/config.yaml
pipeline:
  name: "Universal CI/CD Pipeline"
  version: "2.0"
  
  # Triggers
  triggers:
    - branches: [main, develop]
      events: [push, pull_request]
    - tags: ["v*"]
      events: [release]
  
  # Environments
  environments:
    development:
      auto_deploy: true
      approval_required: false
      quality_gates:
        - code_quality
        - unit_tests
    
    staging:
      auto_deploy: true
      approval_required: false
      quality_gates:
        - code_quality
        - unit_tests
        - integration_tests
        - security_scan
        - performance_test
      
    production:
      auto_deploy: false
      approval_required: true
      quality_gates:
        - all_staging_gates
        - e2e_tests
        - manual_approval
  
  # Quality Gates
  quality_gates:
    code_quality:
      type: "sonarqube"
      thresholds:
        coverage: 90
        duplicated_lines: 5
        maintainability_rating: "A"
        reliability_rating: "A"
        security_rating: "A"
    
    unit_tests:
      type: "jest"
      thresholds:
        coverage: 90
        success_rate: 100
    
    integration_tests:
      type: "custom"
      thresholds:
        success_rate: 100
    
    security_scan:
      type: "snyk"
      thresholds:
        critical: 0
        high: 0
        medium: 5
    
    performance_test:
      type: "lighthouse"
      thresholds:
        performance: 90
        accessibility: 90
        best_practices: 90
        seo: 90

  # Deployment Strategies
  deployment:
    staging:
      strategy: "rolling"
      replicas: 3
      max_unavailable: 1
      max_surge: 1
    
    production:
      strategy: "blue_green"
      replicas: 10
      health_check_grace_period: 30
      traffic_switch_delay: 60
  
  # Notifications
  notifications:
    slack:
      channels:
        - name: "#deployments"
          events: [deployment_started, deployment_completed, deployment_failed]
        - name: "#alerts"
          events: [quality_gate_failed, security_violation]
    
    email:
      recipients:
        - "platform-team@example.com"
      events: [production_deployment, security_violation]
  
  # Rollback Configuration
  rollback:
    enabled: true
    automatic: true
    conditions:
      - error_rate > 5%
      - response_time_p95 > 1000ms
      - availability < 99%
    max_rollback_time: 300  # 5 minutes
```

---

## 📋 **Implementation Checklist**

### Pipeline Setup
- [ ] Create CI pipeline workflow templates
- [ ] Set up quality gates and validation
- [ ] Configure secret management
- [ ] Implement security scanning

### Deployment Strategies
- [ ] Implement blue-green deployment
- [ ] Set up canary deployment with Argo Rollouts
- [ ] Configure rolling deployment
- [ ] Add rollback mechanisms

### Monitoring & Metrics
- [ ] Set up pipeline metrics collection
- [ ] Implement DORA metrics tracking
- [ ] Configure deployment monitoring
- [ ] Add performance tracking

### Security & Compliance
- [ ] Implement container security scanning
- [ ] Add SAST/DAST security tests
- [ ] Configure compliance checks
- [ ] Set up audit logging

### Environment Management
- [ ] Configure staging environment
- [ ] Set up production environment
- [ ] Implement environment promotion
- [ ] Add environment-specific configurations

---

## 🎯 **Success Metrics**

- **Deployment Frequency:** Multiple deployments per day
- **Lead Time:** Code to production in under 2 hours
- **MTTR:** Mean time to recovery under 30 minutes
- **Change Failure Rate:** Less than 5% of deployments fail
- **Pipeline Success Rate:** 95% of pipeline runs succeed 
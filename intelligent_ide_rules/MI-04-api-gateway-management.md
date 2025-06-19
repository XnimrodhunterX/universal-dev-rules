# Rule 16B: API Gateway Management

## Overview
Centralized API gateway management providing traffic routing, security enforcement, rate limiting, and observability for all service-to-service and client-to-service communications.

## Core Principles

### Gateway Architecture
- Single entry point for all external traffic
- Service discovery and load balancing
- Cross-cutting concerns implementation
- Protocol translation and mediation

### Traffic Management
```yaml
# gateway-config.yaml
gateway:
  routing:
    strategy: "path_based"
    load_balancing: "round_robin"
    health_checks: true
    circuit_breaker: true
  
  security:
    authentication: "oauth2"
    authorization: "rbac"
    rate_limiting: true
    cors_enabled: true
  
  observability:
    logging: "structured"
    metrics: "prometheus"
    tracing: "jaeger"
    alerting: true
```

## Implementation Standards

### 1. Kong API Gateway Configuration

#### Gateway Setup
```yaml
# kong.yaml
_format_version: "3.0"
_transform: true

services:
  - name: user-service
    url: http://user-service:8080
    connect_timeout: 5000
    write_timeout: 5000
    read_timeout: 5000
    retries: 3
    plugins:
      - name: rate-limiting
        config:
          minute: 100
          hour: 1000
          policy: cluster
      - name: oauth2
        config:
          scopes:
            - read
            - write
          mandatory_scope: true
      - name: prometheus
        config:
          per_consumer: true

  - name: order-service
    url: http://order-service:8080
    connect_timeout: 5000
    write_timeout: 5000
    read_timeout: 5000
    plugins:
      - name: rate-limiting
        config:
          minute: 200
          hour: 2000
          policy: cluster
      - name: oauth2
        config:
          scopes:
            - orders:read
            - orders:write
          mandatory_scope: true

routes:
  - name: user-routes
    service: user-service
    paths:
      - /api/v1/users
    methods:
      - GET
      - POST
      - PUT
      - DELETE
    strip_path: false
    preserve_host: true

  - name: order-routes
    service: order-service
    paths:
      - /api/v1/orders
    methods:
      - GET
      - POST
      - PUT
      - DELETE
    plugins:
      - name: request-validator
        config:
          allowed_content_types:
            - application/json
          body_schema: |
            {
              "type": "object",
              "properties": {
                "amount": {"type": "number", "minimum": 0},
                "currency": {"type": "string", "enum": ["USD", "EUR"]}
              },
              "required": ["amount", "currency"]
            }

consumers:
  - username: mobile-app
    custom_id: mobile-app-v1
    oauth2_credentials:
      - name: mobile-app-credentials
        client_id: mobile_app_client_id
        client_secret: mobile_app_client_secret

plugins:
  - name: cors
    config:
      origins:
        - "https://app.example.com"
        - "https://admin.example.com"
      methods:
        - GET
        - POST
        - PUT
        - DELETE
        - OPTIONS
      headers:
        - Accept
        - Accept-Version
        - Content-Length
        - Content-MD5
        - Content-Type
        - Date
        - Authorization
      exposed_headers:
        - X-Auth-Token
      credentials: true
      max_age: 3600

  - name: prometheus
    config:
      per_consumer: true
      status_code_metrics: true
      latency_metrics: true
      bandwidth_metrics: true
```

#### Rate Limiting Implementation
```javascript
// rate-limiting/policies.js
const RateLimitingPolicies = {
  // Tier-based rate limiting
  tiers: {
    free: {
      requests_per_minute: 100,
      requests_per_hour: 1000,
      requests_per_day: 10000,
      burst_capacity: 20
    },
    pro: {
      requests_per_minute: 500,
      requests_per_hour: 10000,
      requests_per_day: 100000,
      burst_capacity: 100
    },
    enterprise: {
      requests_per_minute: 2000,
      requests_per_hour: 50000,
      requests_per_day: 1000000,
      burst_capacity: 500
    }
  },

  // Endpoint-specific limits
  endpoints: {
    "/api/v1/auth/login": {
      requests_per_minute: 5,
      requests_per_hour: 20,
      window_size: "sliding"
    },
    "/api/v1/users": {
      GET: { requests_per_minute: 200 },
      POST: { requests_per_minute: 50 },
      PUT: { requests_per_minute: 100 },
      DELETE: { requests_per_minute: 10 }
    },
    "/api/v1/orders": {
      requests_per_minute: 300,
      priority: "high"
    }
  },

  // Adaptive rate limiting based on system load
  adaptive: {
    enabled: true,
    cpu_threshold: 80,
    memory_threshold: 85,
    reduction_factor: 0.5,
    recovery_time: 300
  }
};

/**
 * Rate limiting middleware for Express.js gateway
 */
class RateLimiter {
  constructor(redis, policies = RateLimitingPolicies) {
    this.redis = redis;
    this.policies = policies;
  }

  /**
   * Apply rate limiting based on user tier and endpoint
   */
  async applyRateLimit(req, res, next) {
    const userTier = req.user?.tier || 'free';
    const endpoint = req.route?.path || req.path;
    const method = req.method;
    const clientIP = req.ip;

    try {
      // Check user tier rate limiting
      const tierAllowed = await this.checkTierRateLimit(req.user?.id, userTier);
      if (!tierAllowed) {
        return res.status(429).json({
          error: 'Rate limit exceeded for your tier',
          upgrade_url: '/pricing'
        });
      }

      // Check endpoint-specific rate limiting
      const endpointAllowed = await this.checkEndpointRateLimit(
        req.user?.id || clientIP, 
        endpoint, 
        method
      );
      if (!endpointAllowed) {
        return res.status(429).json({
          error: 'Endpoint rate limit exceeded',
          retry_after: 60
        });
      }

      // Add rate limit headers
      const remaining = await this.getRemainingRequests(req.user?.id, userTier);
      res.set({
        'X-RateLimit-Limit': this.policies.tiers[userTier].requests_per_minute,
        'X-RateLimit-Remaining': remaining,
        'X-RateLimit-Reset': new Date(Date.now() + 60000).toISOString()
      });

      next();
    } catch (error) {
      console.error('Rate limiting error:', error);
      next(); // Fail open in case of Redis issues
    }
  }

  /**
   * Check user tier rate limiting with sliding window
   */
  async checkTierRateLimit(userId, tier) {
    if (!userId) return true;

    const policy = this.policies.tiers[tier];
    const key = `user_rate_limit:${userId}`;
    
    // Sliding window rate limiting using Redis sorted sets
    const now = Date.now();
    const windowStart = now - (60 * 1000); // 1 minute window

    // Remove old entries
    await this.redis.zremrangebyscore(key, 0, windowStart);
    
    // Count current requests in window
    const current = await this.redis.zcard(key);
    
    if (current >= policy.requests_per_minute) {
      return false;
    }

    // Add current request
    await this.redis.zadd(key, now, `${now}-${Math.random()}`);
    await this.redis.expire(key, 60);
    
    return true;
  }

  /**
   * Get remaining requests for user
   */
  async getRemainingRequests(userId, tier) {
    if (!userId) return 0;

    const policy = this.policies.tiers[tier];
    const key = `user_rate_limit:${userId}`;
    const current = await this.redis.zcard(key);
    
    return Math.max(0, policy.requests_per_minute - current);
  }
}

module.exports = { RateLimitingPolicies, RateLimiter };
```

### 2. Circuit Breaker Implementation

```javascript
// circuit-breaker/implementation.js
const EventEmitter = require('events');

/**
 * Circuit breaker implementation for API Gateway
 */
class CircuitBreaker extends EventEmitter {
  constructor(options = {}) {
    super();
    
    this.failureThreshold = options.failureThreshold || 5;
    this.successThreshold = options.successThreshold || 2;
    this.timeout = options.timeout || 30000; // 30 seconds
    
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.failureCount = 0;
    this.successCount = 0;
    this.nextAttempt = Date.now();
    
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      timeouts: 0,
      circuitOpened: 0
    };
  }

  /**
   * Execute request through circuit breaker
   */
  async execute(request) {
    this.metrics.totalRequests++;

    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttempt) {
        const error = new Error('Circuit breaker is OPEN');
        error.code = 'CIRCUIT_BREAKER_OPEN';
        throw error;
      }
      
      // Try to transition to HALF_OPEN
      this.state = 'HALF_OPEN';
      this.successCount = 0;
      this.emit('halfOpen');
    }

    try {
      const result = await this.executeRequest(request);
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  /**
   * Execute the actual request with timeout
   */
  async executeRequest(request) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.metrics.timeouts++;
        reject(new Error('Request timeout'));
      }, this.timeout);

      request()
        .then(result => {
          clearTimeout(timer);
          resolve(result);
        })
        .catch(error => {
          clearTimeout(timer);
          reject(error);
        });
    });
  }

  /**
   * Handle successful requests
   */
  onSuccess() {
    this.metrics.successfulRequests++;
    this.failureCount = 0;

    if (this.state === 'HALF_OPEN') {
      this.successCount++;
      if (this.successCount >= this.successThreshold) {
        this.state = 'CLOSED';
        this.emit('closed');
      }
    }
  }

  /**
   * Handle failed requests
   */
  onFailure() {
    this.metrics.failedRequests++;
    this.failureCount++;

    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
      this.nextAttempt = Date.now() + this.timeout;
      this.metrics.circuitOpened++;
      this.emit('opened');
    }
  }

  /**
   * Get current circuit breaker status
   */
  getStatus() {
    return {
      state: this.state,
      failureCount: this.failureCount,
      successCount: this.successCount,
      nextAttempt: this.nextAttempt,
      metrics: this.metrics
    };
  }
}
```

### 3. Service Discovery Integration

```javascript
// service-discovery/consul.js
const consul = require('consul')();

/**
 * Service discovery using Consul
 */
class ConsulServiceDiscovery {
  constructor(options = {}) {
    this.consul = consul;
    this.services = new Map();
    this.healthCheckInterval = options.healthCheckInterval || 30000;
    this.loadBalancer = options.loadBalancer || 'round_robin';
    
    this.startHealthChecking();
  }

  /**
   * Register service with Consul
   */
  async registerService(service) {
    const registration = {
      name: service.name,
      id: service.id || `${service.name}-${Date.now()}`,
      address: service.address,
      port: service.port,
      tags: service.tags || [],
      check: {
        http: `http://${service.address}:${service.port}/health`,
        interval: '10s',
        timeout: '5s'
      },
      meta: service.metadata || {}
    };

    try {
      await this.consul.agent.service.register(registration);
      console.log(`Service registered: ${service.name} at ${service.address}:${service.port}`);
    } catch (error) {
      console.error(`Failed to register service ${service.name}:`, error);
      throw error;
    }
  }

  /**
   * Discover healthy instances of a service
   */
  async discoverService(serviceName) {
    try {
      const result = await this.consul.health.service({
        service: serviceName,
        passing: true
      });

      const instances = result.map(entry => ({
        id: entry.Service.ID,
        address: entry.Service.Address,
        port: entry.Service.Port,
        tags: entry.Service.Tags,
        metadata: entry.Service.Meta,
        health: 'passing'
      }));

      this.services.set(serviceName, instances);
      return instances;
    } catch (error) {
      console.error(`Failed to discover service ${serviceName}:`, error);
      return [];
    }
  }

  /**
   * Get next available instance using load balancing
   */
  async getServiceInstance(serviceName) {
    let instances = this.services.get(serviceName);
    
    if (!instances || instances.length === 0) {
      instances = await this.discoverService(serviceName);
    }

    if (instances.length === 0) {
      throw new Error(`No healthy instances found for service: ${serviceName}`);
    }

    return this.roundRobinSelection(serviceName, instances);
  }

  /**
   * Round robin load balancing
   */
  roundRobinSelection(serviceName, instances) {
    if (!this.roundRobinIndex) {
      this.roundRobinIndex = new Map();
    }

    const currentIndex = this.roundRobinIndex.get(serviceName) || 0;
    const instance = instances[currentIndex];
    
    this.roundRobinIndex.set(serviceName, (currentIndex + 1) % instances.length);
    return instance;
  }

  /**
   * Start periodic health checking
   */
  startHealthChecking() {
    setInterval(async () => {
      for (const serviceName of this.services.keys()) {
        await this.discoverService(serviceName);
      }
    }, this.healthCheckInterval);
  }
}

module.exports = { ConsulServiceDiscovery };
```

### 4. Gateway Monitoring

```javascript
// monitoring/prometheus.js
const prometheus = require('prom-client');

/**
 * API Gateway metrics collection
 */
class GatewayMetrics {
  constructor() {
    this.register = new prometheus.Registry();
    prometheus.collectDefaultMetrics({ register: this.register });
    this.initializeMetrics();
  }

  initializeMetrics() {
    // HTTP request duration histogram
    this.httpRequestDuration = new prometheus.Histogram({
      name: 'gateway_http_request_duration_seconds',
      help: 'Duration of HTTP requests in seconds',
      labelNames: ['method', 'route', 'status_code', 'service'],
      buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10]
    });

    // HTTP request counter
    this.httpRequestTotal = new prometheus.Counter({
      name: 'gateway_http_requests_total',
      help: 'Total number of HTTP requests',
      labelNames: ['method', 'route', 'status_code', 'service']
    });

    // Rate limit counter
    this.rateLimitHits = new prometheus.Counter({
      name: 'gateway_rate_limit_hits_total',
      help: 'Total number of rate limit hits',
      labelNames: ['tier', 'endpoint', 'client_ip']
    });

    // Circuit breaker state gauge
    this.circuitBreakerState = new prometheus.Gauge({
      name: 'gateway_circuit_breaker_state',
      help: 'Circuit breaker state (0=closed, 1=open, 2=half-open)',
      labelNames: ['service']
    });

    // Register metrics
    this.register.registerMetric(this.httpRequestDuration);
    this.register.registerMetric(this.httpRequestTotal);
    this.register.registerMetric(this.rateLimitHits);
    this.register.registerMetric(this.circuitBreakerState);
  }

  /**
   * Middleware to collect HTTP metrics
   */
  httpMetricsMiddleware() {
    return (req, res, next) => {
      const startTime = Date.now();

      const originalEnd = res.end;
      res.end = (...args) => {
        const duration = (Date.now() - startTime) / 1000;
        const route = req.route?.path || req.path;
        const serviceName = this.extractServiceName(req.path) || 'unknown';
        
        this.httpRequestDuration
          .labels(req.method, route, res.statusCode, serviceName)
          .observe(duration);
        
        this.httpRequestTotal
          .labels(req.method, route, res.statusCode, serviceName)
          .inc();

        originalEnd.apply(res, args);
      };

      next();
    };
  }

  extractServiceName(path) {
    const pathParts = path.split('/');
    if (pathParts.length >= 4 && pathParts[1] === 'api') {
      return `${pathParts[3]}-service`;
    }
    return null;
  }

  async getMetrics() {
    return this.register.metrics();
  }
}

module.exports = GatewayMetrics;
```

## CI/CD Integration

### Gateway Deployment Pipeline
```yaml
# .github/workflows/gateway-deploy.yml
name: Gateway Deployment

on:
  push:
    paths:
      - 'gateway/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
        working-directory: gateway
      
      - name: Run tests
        run: npm test
        working-directory: gateway
      
      - name: Validate Kong configuration
        run: |
          docker run --rm -v $(pwd)/gateway/kong.yaml:/kong.yaml kong:2.8 kong config -c /kong.yaml validate

  deploy-staging:
    needs: test
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy Kong configuration
        run: |
          kubectl apply -f gateway/k8s/staging/
          kubectl rollout status deployment/kong-gateway -n gateway
      
      - name: Run smoke tests
        run: npm run test:smoke
        working-directory: gateway

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Blue-green deployment
        run: |
          kubectl apply -f gateway/k8s/production/blue/
          kubectl rollout status deployment/kong-gateway-blue -n gateway
          ./scripts/health-check.sh blue
          kubectl patch service kong-gateway -n gateway -p '{"spec":{"selector":{"version":"blue"}}}'
          sleep 30
          kubectl delete -f gateway/k8s/production/green/ || true
```

## Enforcement Mechanisms

### Quality Gates
```yaml
# quality-gates/gateway.yml
gateway_quality_gates:
  performance:
    response_time_p95: "< 100ms"
    response_time_p99: "< 500ms"
    throughput: "> 1000 rps"
    error_rate: "< 0.1%"
  
  security:
    tls_version: ">= 1.2"
    authentication_required: true
    rate_limiting_enabled: true
    cors_configured: true
  
  reliability:
    circuit_breaker_configured: true
    health_checks_enabled: true
    service_discovery_active: true
    load_balancing_configured: true

validation_rules:
  - name: "Kong configuration validation"
    command: "kong config validate"
    fail_on_error: true
  
  - name: "Rate limiting test"
    command: "npm run test:rate-limiting"
    fail_on_error: true
  
  - name: "Circuit breaker test"
    command: "npm run test:circuit-breaker"
    fail_on_error: true
```

## Success Criteria

- ✅ Single entry point for all external API traffic
- ✅ Comprehensive rate limiting with tier-based policies
- ✅ Circuit breaker pattern preventing cascade failures
- ✅ Automatic service discovery and load balancing
- ✅ Real-time monitoring and alerting
- ✅ Zero-downtime deployments with blue-green strategy
- ✅ Sub-100ms gateway latency (P95)
- ✅ 99.99% gateway availability
- ✅ Comprehensive security policy enforcement 
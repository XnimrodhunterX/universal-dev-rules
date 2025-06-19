# Rule 11B: Performance Optimization Standards

<!-- CURSOR: highlight: Performance engineering with comprehensive monitoring, profiling, and optimization strategies -->

## Purpose & Scope

Performance optimization ensures applications meet response time requirements, handle expected load, and provide optimal user experience while maintaining cost efficiency. This rule establishes comprehensive standards for performance engineering, monitoring, profiling, optimization strategies, and performance testing to deliver high-performance systems at scale.

<!-- CURSOR: complexity: Advanced -->

## Core Standards

### Performance Engineering Framework

#### 1. Performance Requirements Definition

**Performance SLA Framework:**
```yaml
# performance-sla.yaml
performance_requirements:
  response_time_targets:
    api_endpoints:
      critical_operations:
        p50: "50ms"
        p95: "200ms"
        p99: "500ms"
        p99.9: "1000ms"
      standard_operations:
        p50: "100ms"
        p95: "400ms"
        p99: "1000ms"
        p99.9: "2000ms"
      batch_operations:
        p50: "5s"
        p95: "15s"
        p99: "30s"
        
    database_queries:
      simple_queries:
        p50: "5ms"
        p95: "20ms"
        p99: "50ms"
      complex_queries:
        p50: "50ms"
        p95: "200ms"
        p99: "500ms"
      analytical_queries:
        p50: "1s"
        p95: "5s"
        p99: "15s"
        
  throughput_targets:
    api_gateway:
      peak_rps: 10000
      sustained_rps: 5000
      burst_capacity: 15000
      
    message_queue:
      messages_per_second: 50000
      batch_size_optimal: 100
      max_batch_size: 1000
      
    database:
      read_qps: 5000
      write_qps: 1000
      connection_pool_size: 100
      
  resource_utilization:
    cpu_utilization:
      target: "70%"
      warning_threshold: "80%"
      critical_threshold: "90%"
      
    memory_utilization:
      target: "75%"
      warning_threshold: "85%"
      critical_threshold: "95%"
      
    network_utilization:
      target: "60%"
      warning_threshold: "75%"
      critical_threshold: "90%"
      
  availability_targets:
    uptime: "99.99%"
    error_rate: "<0.1%"
    timeout_rate: "<0.01%"
```

**Performance Budget Configuration:**
```yaml
# performance-budget.yaml
performance_budgets:
  frontend:
    page_load_time:
      first_contentful_paint: "1.5s"
      largest_contentful_paint: "2.5s"
      first_input_delay: "100ms"
      cumulative_layout_shift: "0.1"
      
    resource_sizes:
      javascript_bundle: "300KB"
      css_bundle: "100KB"
      images_total: "500KB"
      fonts_total: "50KB"
      
    network_requests:
      total_requests: 50
      critical_path_requests: 10
      third_party_requests: 5
      
  backend:
    api_response_time:
      authentication: "100ms"
      data_retrieval: "200ms"
      data_processing: "500ms"
      
    database_performance:
      query_execution_time: "50ms"
      connection_acquisition: "10ms"
      transaction_duration: "100ms"
      
    cache_performance:
      hit_ratio: "95%"
      response_time: "5ms"
      eviction_rate: "<1%"
```

#### 2. Performance Monitoring Infrastructure

**Comprehensive Metrics Collection:**
```yaml
# performance-monitoring.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: performance-monitoring-config
  namespace: monitoring
data:
  prometheus-config: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
      
    rule_files:
      - "performance-rules/*.yml"
      
    scrape_configs:
    # Application performance metrics
    - job_name: 'application-performance'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      metrics_path: '/metrics'
      scrape_interval: 5s
      
    # Database performance metrics
    - job_name: 'database-performance'
      static_configs:
      - targets: ['postgres-exporter:9187']
      scrape_interval: 15s
      
    # Cache performance metrics
    - job_name: 'redis-performance'
      static_configs:
      - targets: ['redis-exporter:9121']
      scrape_interval: 10s
      
    # Infrastructure performance metrics
    - job_name: 'node-performance'
      kubernetes_sd_configs:
      - role: node
      relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
      scrape_interval: 15s
      
  alerting-rules: |
    groups:
    - name: performance-alerts
      rules:
      # Response time alerts
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }}s"
          
      # Throughput alerts
      - alert: LowThroughput
        expr: rate(http_requests_total[5m]) < 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low throughput detected"
          description: "Request rate is {{ $value }} req/s"
          
      # Resource utilization alerts
      - alert: HighCPUUtilization
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High CPU utilization"
          description: "CPU utilization is {{ $value }}%"
          
      # Database performance alerts
      - alert: SlowDatabaseQueries
        expr: pg_stat_activity_max_tx_duration{datname!~"template.*"} > 300
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Slow database queries detected"
          description: "Longest transaction duration is {{ $value }}s"
```

**Application Performance Monitoring (APM):**
```yaml
# apm-configuration.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: apm-server
  namespace: monitoring
spec:
  replicas: 2
  selector:
    matchLabels:
      app: apm-server
  template:
    metadata:
      labels:
        app: apm-server
    spec:
      containers:
      - name: apm-server
        image: docker.elastic.co/apm/apm-server:8.10.0
        ports:
        - containerPort: 8200
        env:
        - name: ELASTICSEARCH_HOSTS
          value: "https://elasticsearch:9200"
        - name: KIBANA_HOST
          value: "https://kibana:5601"
        volumeMounts:
        - name: apm-config
          mountPath: /usr/share/apm-server/apm-server.yml
          subPath: apm-server.yml
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
      volumes:
      - name: apm-config
        configMap:
          name: apm-server-config
          
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: apm-server-config
  namespace: monitoring
data:
  apm-server.yml: |
    apm-server:
      host: "0.0.0.0:8200"
      max_header_size: 1048576
      max_event_size: 307200
      capture_personal_data: false
      
      # Performance sampling
      sampling:
        keep_unsampled: false
        tail_sampling:
          enabled: true
          interval: 1m
          policies:
            - sample_rate: 0.1
              service.name: "user-service"
            - sample_rate: 0.5
              service.name: "auth-service"
            - sample_rate: 1.0
              trace.outcome: "failure"
              
    output.elasticsearch:
      hosts: ["https://elasticsearch:9200"]
      protocol: "https"
      index: "apm-%{[observer.version]}-%{+yyyy.MM.dd}"
      
    setup.template.settings:
      index.number_of_shards: 2
      index.number_of_replicas: 1
      index.mapping.total_fields.limit: 2000
```

### Application Performance Optimization

#### 1. Code-Level Optimizations

**Performance Profiling Integration:**
```go
// performance-profiling.go
package main

import (
    "context"
    "net/http"
    _ "net/http/pprof"
    "runtime"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/metric"
    "go.opentelemetry.io/otel/trace"
)

var (
    // Prometheus metrics
    requestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "http_request_duration_seconds",
            Help: "The latency of HTTP requests.",
            Buckets: prometheus.DefBuckets,
        },
        []string{"method", "endpoint", "status_code"},
    )
    
    requestCount = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "The total number of HTTP requests.",
        },
        []string{"method", "endpoint", "status_code"},
    )
    
    memoryUsage = promauto.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "memory_usage_bytes",
            Help: "Current memory usage in bytes.",
        },
        []string{"type"},
    )
    
    // OpenTelemetry metrics
    meter = otel.Meter("performance-monitoring")
    tracer = otel.Tracer("performance-monitoring")
)

// PerformanceMiddleware provides comprehensive performance monitoring
func PerformanceMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        
        // Start OpenTelemetry span
        ctx, span := tracer.Start(r.Context(), r.URL.Path)
        defer span.End()
        
        // Add request attributes
        span.SetAttributes(
            attribute.String("http.method", r.Method),
            attribute.String("http.url", r.URL.String()),
            attribute.String("user.agent", r.UserAgent()),
        )
        
        // Capture response
        wrapped := &responseWriter{ResponseWriter: w, statusCode: 200}
        
        // Execute request
        next.ServeHTTP(wrapped, r.WithContext(ctx))
        
        // Record metrics
        duration := time.Since(start).Seconds()
        status := http.StatusText(wrapped.statusCode)
        
        requestDuration.WithLabelValues(r.Method, r.URL.Path, status).Observe(duration)
        requestCount.WithLabelValues(r.Method, r.URL.Path, status).Inc()
        
        // Add span attributes
        span.SetAttributes(
            attribute.Int("http.status_code", wrapped.statusCode),
            attribute.Float64("http.duration", duration),
        )
        
        // Record error if applicable
        if wrapped.statusCode >= 400 {
            span.RecordError(fmt.Errorf("HTTP %d", wrapped.statusCode))
        }
    })
}

// Memory monitoring goroutine
func monitorMemoryUsage(ctx context.Context) {
    ticker := time.NewTicker(30 * time.Second)
    defer ticker.Stop()
    
    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            var m runtime.MemStats
            runtime.ReadMemStats(&m)
            
            memoryUsage.WithLabelValues("heap_alloc").Set(float64(m.HeapAlloc))
            memoryUsage.WithLabelValues("heap_sys").Set(float64(m.HeapSys))
            memoryUsage.WithLabelValues("heap_idle").Set(float64(m.HeapIdle))
            memoryUsage.WithLabelValues("heap_inuse").Set(float64(m.HeapInuse))
            memoryUsage.WithLabelValues("stack_inuse").Set(float64(m.StackInuse))
            memoryUsage.WithLabelValues("stack_sys").Set(float64(m.StackSys))
        }
    }
}

type responseWriter struct {
    http.ResponseWriter
    statusCode int
}

func (rw *responseWriter) WriteHeader(code int) {
    rw.statusCode = code
    rw.ResponseWriter.WriteHeader(code)
}
```

**Database Query Optimization:**
```sql
-- database-performance-optimization.sql

-- Index optimization for common query patterns
CREATE INDEX CONCURRENTLY idx_users_email_active 
ON users (email) WHERE active = true;

CREATE INDEX CONCURRENTLY idx_orders_user_created 
ON orders (user_id, created_at) 
INCLUDE (status, total_amount);

CREATE INDEX CONCURRENTLY idx_products_category_price 
ON products (category_id, price) 
WHERE deleted_at IS NULL;

-- Partial indexes for frequently filtered data
CREATE INDEX CONCURRENTLY idx_events_processed 
ON events (created_at) 
WHERE processed = false;

-- Query performance analysis
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 
SELECT u.id, u.email, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id 
WHERE u.active = true 
  AND u.created_at > NOW() - INTERVAL '1 year'
GROUP BY u.id, u.email
ORDER BY order_count DESC
LIMIT 100;

-- Connection pooling configuration
SET max_connections = 200;
SET shared_buffers = '256MB';
SET effective_cache_size = '1GB';
SET maintenance_work_mem = '64MB';
SET checkpoint_completion_target = 0.9;
SET wal_buffers = '16MB';
SET default_statistics_target = 100;
SET random_page_cost = 1.1;
SET effective_io_concurrency = 200;

-- Query timeout and performance settings
SET statement_timeout = '30s';
SET idle_in_transaction_session_timeout = '10min';
SET lock_timeout = '5s';
```

#### 2. Caching Strategies

**Multi-Layer Caching Implementation:**
```yaml
# caching-configuration.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: caching-config
  namespace: production
data:
  redis-config: |
    # Redis performance configuration
    maxmemory 2gb
    maxmemory-policy allkeys-lru
    save 900 1
    save 300 10
    save 60 10000
    
    # Network optimizations
    tcp-keepalive 300
    tcp-backlog 511
    timeout 0
    
    # Performance tuning
    hash-max-ziplist-entries 512
    hash-max-ziplist-value 64
    list-max-ziplist-size -2
    list-compress-depth 0
    set-max-intset-entries 512
    zset-max-ziplist-entries 128
    zset-max-ziplist-value 64
    
  cache-strategy: |
    cache_layers:
      L1_application:
        type: "in_memory"
        size: "128MB"
        ttl: "5m"
        eviction: "lru"
        
      L2_redis:
        type: "redis_cluster"
        size: "2GB"
        ttl: "1h"
        eviction: "allkeys-lru"
        
      L3_cdn:
        type: "cloudflare"
        ttl: "24h"
        compression: "gzip"
        
    cache_patterns:
      user_sessions:
        layer: "L2_redis"
        ttl: "30m"
        key_pattern: "session:{user_id}"
        
      product_catalog:
        layer: "L1_application,L2_redis"
        ttl: "6h"
        key_pattern: "product:{product_id}"
        
      static_content:
        layer: "L3_cdn"
        ttl: "7d"
        compression: true
        
      api_responses:
        layer: "L1_application"
        ttl: "5m"
        key_pattern: "api:{endpoint}:{params_hash}"
```

**Application Cache Implementation:**
```go
// cache-manager.go
package cache

import (
    "context"
    "encoding/json"
    "fmt"
    "time"

    "github.com/go-redis/redis/v8"
    "github.com/patrickmn/go-cache"
)

type CacheManager struct {
    l1Cache    *cache.Cache     // In-memory cache
    l2Cache    *redis.Client    // Redis cache
    l3Cache    CDNClient        // CDN cache
}

func NewCacheManager(redisClient *redis.Client, cdnClient CDNClient) *CacheManager {
    return &CacheManager{
        l1Cache: cache.New(5*time.Minute, 10*time.Minute),
        l2Cache: redisClient,
        l3Cache: cdnClient,
    }
}

// Multi-layer cache get with fallback
func (cm *CacheManager) Get(ctx context.Context, key string, dest interface{}) error {
    // Try L1 cache first
    if data, found := cm.l1Cache.Get(key); found {
        return json.Unmarshal(data.([]byte), dest)
    }
    
    // Try L2 cache
    data, err := cm.l2Cache.Get(ctx, key).Bytes()
    if err == nil {
        // Store in L1 cache for faster access
        cm.l1Cache.Set(key, data, cache.DefaultExpiration)
        return json.Unmarshal(data, dest)
    }
    
    return fmt.Errorf("cache miss for key: %s", key)
}

// Set with write-through to multiple layers
func (cm *CacheManager) Set(ctx context.Context, key string, value interface{}, ttl time.Duration) error {
    data, err := json.Marshal(value)
    if err != nil {
        return err
    }
    
    // Set in L1 cache
    cm.l1Cache.Set(key, data, ttl)
    
    // Set in L2 cache
    err = cm.l2Cache.Set(ctx, key, data, ttl).Err()
    if err != nil {
        return err
    }
    
    return nil
}

// Cache warming for critical data
func (cm *CacheManager) WarmCache(ctx context.Context, keys []string, loader func(string) (interface{}, error)) {
    for _, key := range keys {
        go func(k string) {
            data, err := loader(k)
            if err == nil {
                cm.Set(ctx, k, data, time.Hour)
            }
        }(key)
    }
}

// Performance monitoring
func (cm *CacheManager) GetStats() CacheStats {
    l1Stats := cm.l1Cache.ItemCount()
    
    l2Info := cm.l2Cache.Info(context.Background()).Val()
    
    return CacheStats{
        L1Items: l1Stats,
        L2Info:  l2Info,
    }
}
```

### Infrastructure Performance Optimization

#### 1. Database Performance Tuning

**PostgreSQL Performance Configuration:**
```sql
-- postgresql-performance.conf

# Memory settings
shared_buffers = 256MB                  # 25% of RAM
effective_cache_size = 1GB              # 75% of RAM
work_mem = 8MB                          # Per operation memory
maintenance_work_mem = 128MB            # Maintenance operations

# Checkpoint settings
checkpoint_completion_target = 0.9
checkpoint_timeout = 10min
max_wal_size = 2GB
min_wal_size = 512MB

# Connection settings
max_connections = 200
superuser_reserved_connections = 3

# Query planning
default_statistics_target = 100
constraint_exclusion = partition
cursor_tuple_fraction = 0.1

# Background writer
bgwriter_delay = 200ms
bgwriter_lru_maxpages = 100
bgwriter_lru_multiplier = 2.0

# WAL settings
wal_level = replica
wal_compression = on
wal_buffers = 16MB
archive_mode = on

# Autovacuum tuning
autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 1min
autovacuum_vacuum_threshold = 50
autovacuum_analyze_threshold = 50
autovacuum_vacuum_scale_factor = 0.1
autovacuum_analyze_scale_factor = 0.05

# Performance monitoring
log_min_duration_statement = 1000      # Log slow queries
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
```

**Database Connection Pooling:**
```yaml
# pgbouncer-performance.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pgbouncer-config
  namespace: production
data:
  pgbouncer.ini: |
    [databases]
    production = host=postgres-primary port=5432 dbname=production
    readonly = host=postgres-replica port=5432 dbname=production
    
    [pgbouncer]
    listen_port = 5432
    listen_addr = *
    auth_type = md5
    auth_file = /etc/pgbouncer/userlist.txt
    
    # Pool configuration
    pool_mode = transaction
    max_client_conn = 1000
    default_pool_size = 50
    min_pool_size = 10
    reserve_pool_size = 10
    max_db_connections = 100
    
    # Performance tuning
    server_reset_query = DISCARD ALL
    server_check_query = SELECT 1
    server_check_delay = 30
    
    # Connection limits
    max_user_connections = 100
    server_round_robin = 1
    ignore_startup_parameters = extra_float_digits
    
    # Logging
    log_connections = 1
    log_disconnections = 1
    log_pooler_errors = 1
    stats_period = 60
    
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pgbouncer
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pgbouncer
  template:
    metadata:
      labels:
        app: pgbouncer
    spec:
      containers:
      - name: pgbouncer
        image: pgbouncer/pgbouncer:latest
        ports:
        - containerPort: 5432
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 256Mi
        livenessProbe:
          tcpSocket:
            port: 5432
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          tcpSocket:
            port: 5432
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### 2. Network Performance Optimization

**Network Configuration:**
```yaml
# network-performance.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: network-performance-config
  namespace: kube-system
data:
  network-optimizations: |
    # CNI performance tuning
    cni_configuration:
      calico:
        ip_pool_size: "/26"
        bgp_enabled: true
        route_reflector_cluster_id: "224.0.0.1"
        
      cilium:
        tunnel_mode: "disabled"
        native_routing: true
        auto_direct_node_routes: true
        enable_bandwidth_manager: true
        
    # Load balancer optimization
    load_balancer:
      algorithm: "least_connections"
      health_check_interval: "5s"
      health_check_timeout: "3s"
      connection_draining_timeout: "30s"
      
    # Service mesh performance
    istio_performance:
      proxy_concurrency: 2
      proxy_cpu_limit: "2000m"
      proxy_memory_limit: "1Gi"
      telemetry_v2_enabled: true
      
  tcp-optimizations: |
    # TCP/IP stack tuning
    net.core.rmem_max = 134217728
    net.core.wmem_max = 134217728
    net.core.netdev_max_backlog = 5000
    net.core.somaxconn = 65535
    net.ipv4.tcp_congestion_control = bbr
    net.ipv4.tcp_rmem = 4096 65536 134217728
    net.ipv4.tcp_wmem = 4096 65536 134217728
    net.ipv4.tcp_max_syn_backlog = 8192
    net.ipv4.tcp_slow_start_after_idle = 0
    net.ipv4.tcp_tw_reuse = 1
```

### Performance Testing Framework

#### 1. Load Testing Configuration

**K6 Performance Testing:**
```javascript
// performance-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
export const errorRate = new Rate('errors');
export const responseTime = new Trend('response_time');
export const requestCount = new Counter('request_count');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 200 },   // Ramp up to 200
    { duration: '5m', target: 200 },   // Stay at 200
    { duration: '2m', target: 300 },   // Ramp up to 300
    { duration: '5m', target: 300 },   // Stay at 300
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.1'],
    response_time: ['p(95)<500'],
    errors: ['rate<0.1'],
  },
};

// Test scenarios
export default function() {
  const scenarios = [
    () => testUserAuthentication(),
    () => testProductCatalog(),
    () => testOrderProcessing(),
    () => testUserProfile(),
  ];
  
  // Randomly select scenario
  const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
  scenario();
  
  sleep(1);
}

function testUserAuthentication() {
  const loginData = {
    username: `user${Math.floor(Math.random() * 1000)}`,
    password: 'password123'
  };
  
  const response = http.post('https://api.example.com/auth/login', 
    JSON.stringify(loginData), {
    headers: { 'Content-Type': 'application/json' },
    tags: { scenario: 'authentication' },
  });
  
  const success = check(response, {
    'login successful': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
  requestCount.add(1);
}

function testProductCatalog() {
  const response = http.get('https://api.example.com/products?page=1&limit=20', {
    tags: { scenario: 'product_catalog' },
  });
  
  const success = check(response, {
    'products loaded': (r) => r.status === 200,
    'response time < 100ms': (r) => r.timings.duration < 100,
    'products count > 0': (r) => JSON.parse(r.body).products.length > 0,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
  requestCount.add(1);
}

function testOrderProcessing() {
  const orderData = {
    product_id: Math.floor(Math.random() * 1000),
    quantity: Math.floor(Math.random() * 5) + 1,
    user_id: Math.floor(Math.random() * 10000),
  };
  
  const response = http.post('https://api.example.com/orders', 
    JSON.stringify(orderData), {
    headers: { 'Content-Type': 'application/json' },
    tags: { scenario: 'order_processing' },
  });
  
  const success = check(response, {
    'order created': (r) => r.status === 201,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
  requestCount.add(1);
}

// Performance test execution
export function handleSummary(data) {
  return {
    'performance-report.json': JSON.stringify(data, null, 2),
    'performance-report.html': generateHTMLReport(data),
  };
}

function generateHTMLReport(data) {
  return `
<!DOCTYPE html>
<html>
<head>
    <title>Performance Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { margin: 10px 0; padding: 10px; background: #f5f5f5; }
        .passed { color: green; }
        .failed { color: red; }
    </style>
</head>
<body>
    <h1>Performance Test Report</h1>
    <div class="metric">
        <h3>Response Time (95th percentile)</h3>
        <p class="${data.metrics.http_req_duration.values.p95 < 500 ? 'passed' : 'failed'}">
            ${data.metrics.http_req_duration.values.p95.toFixed(2)}ms
        </p>
    </div>
    <div class="metric">
        <h3>Error Rate</h3>
        <p class="${data.metrics.http_req_failed.values.rate < 0.1 ? 'passed' : 'failed'}">
            ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%
        </p>
    </div>
    <div class="metric">
        <h3>Total Requests</h3>
        <p>${data.metrics.http_reqs.values.count}</p>
    </div>
</body>
</html>`;
}
```

#### 2. Automated Performance Testing Pipeline

**CI/CD Performance Testing Integration:**
```yaml
# performance-testing-pipeline.yaml
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: performance-testing-pipeline
  namespace: ci-cd
spec:
  params:
  - name: application-url
    type: string
    description: "Target application URL for testing"
  - name: test-duration
    type: string
    default: "10m"
    description: "Duration of performance test"
  - name: performance-threshold
    type: string
    default: "500ms"
    description: "Response time threshold"
    
  tasks:
  - name: setup-test-environment
    taskRef:
      name: setup-task
    params:
    - name: url
      value: $(params.application-url)
      
  - name: baseline-performance-test
    taskRef:
      name: k6-test
    runAfter: ["setup-test-environment"]
    params:
    - name: test-script
      value: "baseline-test.js"
    - name: duration
      value: $(params.test-duration)
    - name: vus
      value: "10"
      
  - name: load-performance-test
    taskRef:
      name: k6-test
    runAfter: ["baseline-performance-test"]
    params:
    - name: test-script
      value: "load-test.js"
    - name: duration
      value: $(params.test-duration)
    - name: vus
      value: "100"
      
  - name: stress-performance-test
    taskRef:
      name: k6-test
    runAfter: ["load-performance-test"]
    params:
    - name: test-script
      value: "stress-test.js"
    - name: duration
      value: $(params.test-duration)
    - name: vus
      value: "500"
      
  - name: spike-performance-test
    taskRef:
      name: k6-test
    runAfter: ["stress-performance-test"]
    params:
    - name: test-script
      value: "spike-test.js"
    - name: duration
      value: "5m"
    - name: vus
      value: "1000"
      
  - name: analyze-results
    taskRef:
      name: performance-analysis
    runAfter: ["spike-performance-test"]
    params:
    - name: threshold
      value: $(params.performance-threshold)
      
  - name: generate-report
    taskRef:
      name: report-generator
    runAfter: ["analyze-results"]
    
---
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: k6-test
  namespace: ci-cd
spec:
  params:
  - name: test-script
    type: string
  - name: duration
    type: string
  - name: vus
    type: string
    
  steps:
  - name: run-k6-test
    image: loadimpact/k6:latest
    script: |
      #!/bin/sh
      k6 run \
        --duration $(params.duration) \
        --vus $(params.vus) \
        --out json=results.json \
        --out influxdb=http://influxdb:8086/performance \
        /scripts/$(params.test-script)
        
  - name: upload-results
    image: alpine/curl:latest
    script: |
      #!/bin/sh
      curl -X POST \
        -H "Content-Type: application/json" \
        -d @results.json \
        http://performance-analyzer:8080/api/results
```

### Performance Optimization Automation

#### 1. Auto-Scaling Based on Performance Metrics

**Predictive Auto-Scaling:**
```yaml
# predictive-autoscaling.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: performance-based-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: user-service
  minReplicas: 3
  maxReplicas: 50
  metrics:
  # CPU-based scaling
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
        
  # Memory-based scaling
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
        
  # Custom performance metrics
  - type: Pods
    pods:
      metric:
        name: response_time_95th_percentile
      target:
        type: AverageValue
        averageValue: "200m"  # 200ms
        
  - type: Pods
    pods:
      metric:
        name: error_rate
      target:
        type: AverageValue
        averageValue: "1"     # 1% error rate
        
  # Predictive scaling behavior
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 5
        periodSeconds: 60
      selectPolicy: Max
      
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Min
```

#### 2. Performance-Based Circuit Breakers

**Adaptive Circuit Breaker:**
```go
// adaptive-circuit-breaker.go
package circuitbreaker

import (
    "context"
    "sync"
    "time"
)

type AdaptiveCircuitBreaker struct {
    mutex                sync.RWMutex
    state               State
    failureThreshold    int
    successThreshold    int
    timeout             time.Duration
    lastFailureTime     time.Time
    consecutiveFailures int
    consecutiveSuccesses int
    
    // Performance-based thresholds
    responseTimeThreshold time.Duration
    errorRateThreshold    float64
    
    // Metrics
    totalRequests   int64
    failedRequests  int64
    responseTimes   []time.Duration
}

type State int

const (
    StateClosed State = iota
    StateOpen
    StateHalfOpen
)

func NewAdaptiveCircuitBreaker(config Config) *AdaptiveCircuitBreaker {
    return &AdaptiveCircuitBreaker{
        state:                 StateClosed,
        failureThreshold:      config.FailureThreshold,
        successThreshold:      config.SuccessThreshold,
        timeout:              config.Timeout,
        responseTimeThreshold: config.ResponseTimeThreshold,
        errorRateThreshold:    config.ErrorRateThreshold,
        responseTimes:         make([]time.Duration, 0, 100),
    }
}

func (cb *AdaptiveCircuitBreaker) Execute(ctx context.Context, operation func() error) error {
    state := cb.getState()
    
    if state == StateOpen {
        if time.Since(cb.lastFailureTime) > cb.timeout {
            cb.setState(StateHalfOpen)
        } else {
            return ErrCircuitBreakerOpen
        }
    }
    
    start := time.Now()
    err := operation()
    duration := time.Since(start)
    
    cb.recordMetrics(duration, err == nil)
    
    if err != nil {
        cb.onFailure()
        return err
    }
    
    // Check performance-based conditions
    if duration > cb.responseTimeThreshold {
        cb.onSlowResponse()
        return ErrSlowResponse
    }
    
    cb.onSuccess()
    return nil
}

func (cb *AdaptiveCircuitBreaker) recordMetrics(duration time.Duration, success bool) {
    cb.mutex.Lock()
    defer cb.mutex.Unlock()
    
    cb.totalRequests++
    if !success {
        cb.failedRequests++
    }
    
    // Keep sliding window of response times
    cb.responseTimes = append(cb.responseTimes, duration)
    if len(cb.responseTimes) > 100 {
        cb.responseTimes = cb.responseTimes[1:]
    }
    
    // Check error rate threshold
    errorRate := float64(cb.failedRequests) / float64(cb.totalRequests)
    if errorRate > cb.errorRateThreshold {
        cb.setState(StateOpen)
    }
}

func (cb *AdaptiveCircuitBreaker) getAverageResponseTime() time.Duration {
    if len(cb.responseTimes) == 0 {
        return 0
    }
    
    var total time.Duration
    for _, rt := range cb.responseTimes {
        total += rt
    }
    
    return total / time.Duration(len(cb.responseTimes))
}
```

This rule establishes comprehensive performance optimization standards ensuring applications deliver optimal user experience while maintaining cost efficiency through systematic performance engineering, monitoring, and continuous optimization. 
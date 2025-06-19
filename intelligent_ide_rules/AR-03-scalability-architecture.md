# Rule 11C: Scalability Architecture Standards

<!-- CURSOR: highlight: Scalable system design with horizontal/vertical scaling, microservices patterns, and distributed architecture -->

## Purpose & Scope

Scalability architecture ensures systems can handle increasing load through horizontal and vertical scaling strategies while maintaining performance, reliability, and cost-effectiveness. This rule establishes comprehensive standards for scalable design patterns, distributed system architecture, microservices scaling, and capacity planning to support business growth and varying demand patterns.

<!-- CURSOR: complexity: Advanced -->

## Core Standards

### Scalability Design Principles

#### 1. Scaling Strategy Framework

**Horizontal vs Vertical Scaling Decision Matrix:**
```yaml
# scaling-strategy.yaml
scaling_framework:
  decision_criteria:
    horizontal_scaling:
      indicators:
        - cpu_utilization > 70%
        - memory_utilization > 75%
        - request_queue_length > 100
        - response_time_p95 > 500ms
      advantages:
        - fault_tolerance
        - unlimited_growth_potential
        - cost_effective_at_scale
        - geographic_distribution
      use_cases:
        - stateless_applications
        - web_services
        - api_gateways
        - microservices
        
    vertical_scaling:
      indicators:
        - single_threaded_bottlenecks
        - memory_intensive_operations
        - database_connections_limited
        - legacy_architecture_constraints
      advantages:
        - simpler_implementation
        - no_data_partitioning_complexity
        - lower_network_overhead
        - easier_consistency_management
      use_cases:
        - databases
        - legacy_monoliths
        - compute_intensive_tasks
        - development_environments
        
  scaling_patterns:
    auto_scaling:
      triggers:
        - performance_metrics
        - predictive_analytics
        - scheduled_events
        - business_metrics
      methods:
        - kubernetes_hpa
        - cloud_auto_scaling_groups
        - custom_controllers
        - serverless_functions
        
    manual_scaling:
      scenarios:
        - planned_traffic_spikes
        - maintenance_windows
        - capacity_testing
        - emergency_response
      approval_process:
        - performance_team_review
        - cost_impact_analysis
        - security_assessment
        - change_management_approval
```

**Capacity Planning Model:**
```yaml
# capacity-planning.yaml
capacity_planning:
  baseline_metrics:
    current_capacity:
      cpu_cores: 1000
      memory_gb: 4000
      storage_tb: 100
      network_gbps: 50
      
    utilization_targets:
      cpu: "70%"
      memory: "75%"
      storage: "80%"
      network: "60%"
      
  growth_projections:
    traffic_growth:
      monthly_growth_rate: "15%"
      seasonal_multiplier: "2.5x"
      peak_hour_multiplier: "4x"
      geographic_expansion: "50%"
      
    data_growth:
      transaction_volume: "20%_monthly"
      storage_requirements: "25%_monthly"
      backup_requirements: "30%_monthly"
      
  scaling_thresholds:
    scale_out_triggers:
      cpu_threshold: "80%"
      memory_threshold: "85%"
      response_time_p95: "200ms"
      error_rate: "1%"
      
    scale_in_triggers:
      cpu_threshold: "30%"
      memory_threshold: "40%"
      idle_duration: "15m"
      cost_optimization: "enabled"
      
  resource_allocation:
    compute_tiers:
      t1_basic:
        cpu: "1-2_cores"
        memory: "2-4GB"
        use_case: "development"
        
      t2_standard:
        cpu: "2-4_cores"
        memory: "4-8GB"
        use_case: "production_low_traffic"
        
      t3_performance:
        cpu: "4-8_cores"
        memory: "8-16GB"
        use_case: "production_high_traffic"
        
      t4_optimized:
        cpu: "8-16_cores"
        memory: "16-32GB"
        use_case: "compute_intensive"
```

#### 2. Microservices Scaling Architecture

**Service Decomposition and Scaling Strategy:**
```yaml
# microservices-scaling.yaml
microservices_architecture:
  service_boundaries:
    user_management:
      responsibilities:
        - user_authentication
        - profile_management
        - preferences
      scaling_characteristics:
        read_heavy: true
        write_pattern: "moderate"
        consistency: "eventual"
        scaling_strategy: "horizontal"
        
    order_processing:
      responsibilities:
        - order_creation
        - payment_processing
        - inventory_management
      scaling_characteristics:
        read_heavy: false
        write_pattern: "high"
        consistency: "strong"
        scaling_strategy: "horizontal_with_sharding"
        
    product_catalog:
      responsibilities:
        - product_information
        - search_functionality
        - recommendations
      scaling_characteristics:
        read_heavy: true
        write_pattern: "low"
        consistency: "eventual"
        scaling_strategy: "horizontal_with_caching"
        
    analytics:
      responsibilities:
        - data_aggregation
        - reporting
        - business_intelligence
      scaling_characteristics:
        read_heavy: true
        write_pattern: "batch"
        consistency: "eventual"
        scaling_strategy: "vertical_and_horizontal"
        
  communication_patterns:
    synchronous:
      use_cases:
        - real_time_queries
        - immediate_consistency_required
        - user_facing_operations
      scaling_considerations:
        - circuit_breakers
        - timeout_management
        - retry_policies
        - load_balancing
        
    asynchronous:
      use_cases:
        - background_processing
        - event_driven_workflows
        - batch_operations
      scaling_considerations:
        - message_queue_scaling
        - consumer_group_management
        - dead_letter_queues
        - backpressure_handling
        
  data_management:
    database_per_service:
      pattern: "microservice_owns_data"
      scaling_approach: "independent_scaling"
      consistency_model: "eventual_consistency"
      
    shared_databases:
      pattern: "legacy_integration"
      scaling_approach: "coordinated_scaling"
      consistency_model: "strong_consistency"
      
    event_sourcing:
      pattern: "event_driven_state"
      scaling_approach: "event_store_scaling"
      consistency_model: "eventual_consistency"
```

### Horizontal Scaling Implementation

#### 1. Stateless Application Scaling

**Kubernetes Horizontal Pod Autoscaler (HPA) Configuration:**
```yaml
# horizontal-scaling-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: user-service-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: user-service
  minReplicas: 5
  maxReplicas: 100
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
        averageUtilization: 75
        
  # Custom metrics scaling
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
        
  - type: Pods
    pods:
      metric:
        name: active_connections
      target:
        type: AverageValue
        averageValue: "500"
        
  # External metrics scaling
  - type: External
    external:
      metric:
        name: queue_depth
        selector:
          matchLabels:
            queue: "user-processing"
      target:
        type: AverageValue
        averageValue: "10"
        
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 10
        periodSeconds: 60
      selectPolicy: Max
      
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 25
        periodSeconds: 60
      - type: Pods
        value: 5
        periodSeconds: 60
      selectPolicy: Min

---
# Vertical Pod Autoscaler for right-sizing
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: user-service-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: user-service
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: user-service
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 4
        memory: 8Gi
      controlledResources: ["cpu", "memory"]
      controlledValues: RequestsAndLimits
```

**Load Balancing Strategy:**
```yaml
# load-balancing-strategy.yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service-lb
  namespace: production
  annotations:
    # AWS Load Balancer annotations
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: "tcp"
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
    service.beta.kubernetes.io/aws-load-balancer-connection-draining-enabled: "true"
    service.beta.kubernetes.io/aws-load-balancer-connection-draining-timeout: "60"
    
    # Health check configuration
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-interval: "10"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-timeout: "5"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-healthy-threshold: "2"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-unhealthy-threshold: "2"
    
spec:
  type: LoadBalancer
  sessionAffinity: None  # For stateless applications
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
  selector:
    app: user-service
    
---
# Istio VirtualService for advanced load balancing
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: user-service-vs
  namespace: production
spec:
  hosts:
  - user-service
  http:
  - match:
    - headers:
        priority:
          exact: "high"
    route:
    - destination:
        host: user-service
        subset: performance-tier
      weight: 100
    timeout: 10s
    retries:
      attempts: 3
      perTryTimeout: 3s
      
  - route:
    - destination:
        host: user-service
        subset: standard-tier
      weight: 100
    timeout: 30s
    retries:
      attempts: 2
      perTryTimeout: 10s
      
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: user-service-dr
  namespace: production
spec:
  host: user-service
  trafficPolicy:
    loadBalancer:
      simple: LEAST_CONN
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
        maxRequestsPerConnection: 10
        maxRetries: 3
        consecutiveGatewayErrors: 5
        interval: 30s
        baseEjectionTime: 30s
        maxEjectionPercent: 50
        
  subsets:
  - name: performance-tier
    labels:
      tier: performance
    trafficPolicy:
      connectionPool:
        tcp:
          maxConnections: 200
        http:
          http1MaxPendingRequests: 100
          
  - name: standard-tier
    labels:
      tier: standard
    trafficPolicy:
      connectionPool:
        tcp:
          maxConnections: 50
        http:
          http1MaxPendingRequests: 25
```

#### 2. Database Scaling Strategies

**Database Horizontal Scaling Implementation:**
```yaml
# database-scaling-strategy.yaml
database_scaling:
  read_scaling:
    read_replicas:
      strategy: "automatic"
      min_replicas: 2
      max_replicas: 10
      scaling_metrics:
        - read_query_rate
        - connection_count
        - cpu_utilization
        
    read_routing:
      pattern: "automatic"
      load_balancer: "pgbouncer"
      health_checks: "enabled"
      failover: "automatic"
      
  write_scaling:
    sharding:
      strategy: "horizontal"
      shard_key: "user_id"
      shard_count: 16
      rebalancing: "automatic"
      
    partitioning:
      strategy: "range_based"
      partition_key: "created_at"
      partition_interval: "monthly"
      retention: "24_months"
      
  connection_pooling:
    pgbouncer:
      pool_mode: "transaction"
      max_client_conn: 1000
      default_pool_size: 50
      max_db_connections: 100
      
    application_level:
      initial_size: 10
      max_size: 50
      min_idle: 5
      max_idle: 20
      validation_query: "SELECT 1"
```

**Database Sharding Implementation:**
```yaml
# database-sharding.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: database-sharding-config
  namespace: production
data:
  sharding-strategy: |
    sharding:
      algorithm: "consistent_hashing"
      shard_count: 16
      replication_factor: 3
      
      shard_mapping:
        shard_0:
          primary: "db-shard-0-primary.rds.amazonaws.com"
          replicas:
            - "db-shard-0-replica-1.rds.amazonaws.com"
            - "db-shard-0-replica-2.rds.amazonaws.com"
          key_range: "0x0000-0x0FFF"
          
        shard_1:
          primary: "db-shard-1-primary.rds.amazonaws.com"
          replicas:
            - "db-shard-1-replica-1.rds.amazonaws.com"
            - "db-shard-1-replica-2.rds.amazonaws.com"
          key_range: "0x1000-0x1FFF"
          
      routing_rules:
        user_data:
          shard_key: "user_id"
          hash_function: "md5"
          
        order_data:
          shard_key: "user_id"  # Co-locate with user data
          hash_function: "md5"
          
        analytics_data:
          shard_key: "timestamp"
          partitioning: "time_based"
          
  connection-routing: |
    routing:
      read_operations:
        default_replica_preference: "nearest"
        fallback_to_primary: true
        max_replica_lag: "10s"
        
      write_operations:
        primary_only: true
        consistency: "strong"
        timeout: "30s"
        
      transaction_routing:
        distributed_transactions: "disabled"
        single_shard_optimization: true
        cross_shard_queries: "limited"
```

### Vertical Scaling Implementation

#### 1. Resource Optimization

**Vertical Pod Autoscaler (VPA) Advanced Configuration:**
```yaml
# vertical-scaling-vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: compute-intensive-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: data-processing-service
  updatePolicy:
    updateMode: "Auto"
    minReplicas: 2  # Ensure availability during updates
  resourcePolicy:
    containerPolicies:
    - containerName: data-processor
      minAllowed:
        cpu: 500m
        memory: 1Gi
      maxAllowed:
        cpu: 16
        memory: 64Gi
      controlledResources: ["cpu", "memory"]
      controlledValues: RequestsAndLimits
      
      # Resource scaling policies
      mode: Auto
      scalingPolicy:
        cpu:
          increment: "1"
          decrement: "0.5"
          stabilizationWindowSeconds: 300
        memory:
          increment: "2Gi"
          decrement: "1Gi"
          stabilizationWindowSeconds: 300
          
---
# Custom Resource Scaler for specific workloads
apiVersion: v1
kind: ConfigMap
metadata:
  name: custom-vertical-scaling
  namespace: production
data:
  scaling-rules: |
    services:
      machine-learning-training:
        scaling_triggers:
          - metric: "training_dataset_size"
            threshold: "10GB"
            cpu_multiplier: 2
            memory_multiplier: 4
          - metric: "model_complexity_score"
            threshold: "0.8"
            cpu_multiplier: 1.5
            memory_multiplier: 2
            
      data-analytics:
        scaling_triggers:
          - metric: "query_complexity"
            threshold: "high"
            cpu_multiplier: 3
            memory_multiplier: 2
          - metric: "data_volume_gb"
            threshold: "100"
            cpu_multiplier: 1.5
            memory_multiplier: 3
            
      image-processing:
        scaling_triggers:
          - metric: "image_resolution"
            threshold: "4K"
            cpu_multiplier: 4
            memory_multiplier: 3
          - metric: "batch_size"
            threshold: "100"
            cpu_multiplier: 2
            memory_multiplier: 1.5
```

#### 2. Database Vertical Scaling

**RDS Instance Scaling Automation:**
```hcl
# rds-vertical-scaling.tf
resource "aws_db_instance" "production" {
  identifier = "production-database"
  
  # Scalable instance configuration
  instance_class = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  
  # Performance optimization
  performance_insights_enabled = true
  monitoring_interval = 60
  
  # Backup and maintenance
  backup_retention_period = 30
  backup_window = "03:00-04:00"
  maintenance_window = "sun:04:00-sun:05:00"
  
  # Scaling configuration
  auto_minor_version_upgrade = true
  allow_major_version_upgrade = false
  
  tags = {
    Name = "Production Database"
    AutoScaling = "enabled"
  }
}

# CloudWatch alarms for scaling triggers
resource "aws_cloudwatch_metric_alarm" "database_cpu_high" {
  alarm_name          = "database-cpu-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors RDS CPU utilization"
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.production.id
  }
  
  alarm_actions = [aws_sns_topic.database_scaling.arn]
}

resource "aws_cloudwatch_metric_alarm" "database_connections_high" {
  alarm_name          = "database-connections-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"  # 80% of max connections
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.production.id
  }
  
  alarm_actions = [aws_sns_topic.database_scaling.arn]
}

# Lambda function for automated scaling
resource "aws_lambda_function" "database_scaler" {
  filename         = "database_scaler.zip"
  function_name    = "database-vertical-scaler"
  role            = aws_iam_role.lambda_role.arn
  handler         = "main.handler"
  runtime         = "python3.9"
  timeout         = 300
  
  environment {
    variables = {
      DB_INSTANCE_ID = aws_db_instance.production.id
      SCALING_POLICY = jsonencode({
        cpu_threshold = 80
        memory_threshold = 85
        connection_threshold = 80
        scaling_cooldown = 900  # 15 minutes
        instance_classes = [
          "db.r6g.large",
          "db.r6g.xlarge", 
          "db.r6g.2xlarge",
          "db.r6g.4xlarge",
          "db.r6g.8xlarge"
        ]
      })
    }
  }
}
```

### Distributed System Scaling

#### 1. Message Queue Scaling

**Apache Kafka Scaling Configuration:**
```yaml
# kafka-scaling.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: production-kafka
  namespace: messaging
spec:
  kafka:
    version: 3.5.0
    replicas: 9  # 3 per AZ for fault tolerance
    
    # Resource configuration
    resources:
      requests:
        cpu: 2
        memory: 8Gi
      limits:
        cpu: 4
        memory: 16Gi
        
    # Storage configuration
    storage:
      type: persistent-claim
      size: 1Ti
      class: fast-ssd
      
    # Performance tuning
    config:
      num.network.threads: 8
      num.io.threads: 16
      socket.send.buffer.bytes: 102400
      socket.receive.buffer.bytes: 102400
      socket.request.max.bytes: 104857600
      num.partitions: 100
      default.replication.factor: 3
      min.insync.replicas: 2
      log.retention.hours: 168
      log.segment.bytes: 1073741824
      log.retention.check.interval.ms: 300000
      
    # Auto-scaling configuration
    template:
      pod:
        metadata:
          annotations:
            cluster-autoscaler.kubernetes.io/safe-to-evict: "false"
            
  zookeeper:
    replicas: 3
    resources:
      requests:
        cpu: 500m
        memory: 2Gi
      limits:
        cpu: 1
        memory: 4Gi
    storage:
      type: persistent-claim
      size: 100Gi
      class: fast-ssd
      
  entityOperator:
    topicOperator:
      resources:
        requests:
          cpu: 100m
          memory: 256Mi
        limits:
          cpu: 500m
          memory: 512Mi
    userOperator:
      resources:
        requests:
          cpu: 100m
          memory: 256Mi
        limits:
          cpu: 500m
          memory: 512Mi

---
# Kafka topic auto-scaling
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: user-events
  namespace: messaging
  labels:
    strimzi.io/cluster: production-kafka
spec:
  partitions: 50
  replicas: 3
  config:
    retention.ms: 604800000  # 7 days
    segment.ms: 3600000      # 1 hour
    cleanup.policy: delete
    compression.type: lz4
    min.insync.replicas: 2
    
---
# Kafka Connect scaling
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnect
metadata:
  name: kafka-connect-cluster
  namespace: messaging
spec:
  version: 3.5.0
  replicas: 6
  resources:
    requests:
      cpu: 1
      memory: 2Gi
    limits:
      cpu: 2
      memory: 4Gi
  config:
    group.id: connect-cluster
    offset.storage.topic: connect-cluster-offsets
    config.storage.topic: connect-cluster-configs
    status.storage.topic: connect-cluster-status
    key.converter: org.apache.kafka.connect.json.JsonConverter
    value.converter: org.apache.kafka.connect.json.JsonConverter
    key.converter.schemas.enable: false
    value.converter.schemas.enable: false
```

#### 2. Cache Scaling Strategy

**Redis Cluster Scaling:**
```yaml
# redis-cluster-scaling.yaml
apiVersion: redis.redis.opstreelabs.in/v1beta1
kind: RedisCluster
metadata:
  name: production-redis-cluster
  namespace: caching
spec:
  clusterSize: 6
  
  # Master configuration
  master:
    replicas: 3
    resources:
      requests:
        cpu: 1
        memory: 4Gi
      limits:
        cpu: 2
        memory: 8Gi
    storage:
      volumeClaimTemplate:
        spec:
          storageClassName: fast-ssd
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: 100Gi
              
  # Replica configuration  
  replica:
    replicas: 3
    resources:
      requests:
        cpu: 500m
        memory: 2Gi
      limits:
        cpu: 1
        memory: 4Gi
    storage:
      volumeClaimTemplate:
        spec:
          storageClassName: fast-ssd
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: 100Gi
              
  # Redis configuration
  redisConfig:
    maxmemory: "7gb"
    maxmemory-policy: "allkeys-lru"
    save: "900 1 300 10 60 10000"
    timeout: "300"
    tcp-keepalive: "300"
    
  # Monitoring
  redisExporter:
    enabled: true
    image: "oliver006/redis_exporter:v1.45.0"
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 200m
        memory: 256Mi
        
---
# Redis scaling automation
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-scaling-config
  namespace: caching
data:
  scaling-policy: |
    scaling_triggers:
      memory_utilization:
        threshold: "80%"
        action: "scale_out"
        cooldown: "300s"
        
      cpu_utilization:
        threshold: "70%"
        action: "scale_up"
        cooldown: "300s"
        
      connection_count:
        threshold: "1000"
        action: "scale_out"
        cooldown: "180s"
        
      eviction_rate:
        threshold: "100/min"
        action: "scale_up_memory"
        cooldown: "600s"
        
    scaling_actions:
      scale_out:
        add_replicas: 2
        max_replicas: 12
        
      scale_up:
        memory_increment: "2Gi"
        cpu_increment: "500m"
        max_memory: "16Gi"
        max_cpu: "4"
        
      scale_in:
        remove_replicas: 1
        min_replicas: 3
        grace_period: "300s"
```

### Auto-Scaling Orchestration

#### 1. Predictive Scaling

**Machine Learning-Based Scaling:**
```python
# predictive-scaling.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from datetime import datetime, timedelta
from kubernetes import client, config

class PredictiveScaler:
    def __init__(self, namespace="production"):
        self.namespace = namespace
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        config.load_incluster_config()
        self.k8s_apps_v1 = client.AppsV1Api()
        self.k8s_autoscaling_v2 = client.AutoscalingV2Api()
        
    def collect_metrics(self, hours_back=168):  # 7 days
        """Collect historical metrics for training"""
        metrics_data = []
        
        # Collect from Prometheus
        prometheus_query = f"""
        avg_over_time(
            rate(http_requests_total[5m])
        [{hours_back}h:5m])
        """
        
        # This would integrate with your metrics system
        return self._fetch_prometheus_data(prometheus_query)
    
    def prepare_features(self, metrics_data):
        """Prepare features for ML model"""
        df = pd.DataFrame(metrics_data)
        
        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Rolling averages
        df['requests_1h_avg'] = df['request_rate'].rolling(window=12).mean()
        df['requests_24h_avg'] = df['request_rate'].rolling(window=288).mean()
        df['requests_7d_avg'] = df['request_rate'].rolling(window=2016).mean()
        
        # Lag features
        df['requests_lag_1h'] = df['request_rate'].shift(12)
        df['requests_lag_24h'] = df['request_rate'].shift(288)
        df['requests_lag_7d'] = df['request_rate'].shift(2016)
        
        # Growth rate
        df['growth_rate'] = df['request_rate'].pct_change(periods=12)
        
        return df.dropna()
    
    def train_model(self, historical_data):
        """Train the predictive model"""
        df = self.prepare_features(historical_data)
        
        features = [
            'hour', 'day_of_week', 'month', 'is_weekend',
            'requests_1h_avg', 'requests_24h_avg', 'requests_7d_avg',
            'requests_lag_1h', 'requests_lag_24h', 'requests_lag_7d',
            'growth_rate', 'cpu_utilization', 'memory_utilization'
        ]
        
        X = df[features]
        y = df['required_replicas']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        
        # Save model
        joblib.dump(self.model, 'predictive_scaling_model.pkl')
        joblib.dump(self.scaler, 'feature_scaler.pkl')
        
        logging.info("Model trained and saved successfully")
    
    def predict_scaling_needs(self, service_name, horizon_hours=2):
        """Predict scaling needs for the next few hours"""
        current_metrics = self._get_current_metrics(service_name)
        predictions = []
        
        for hour_offset in range(1, horizon_hours + 1):
            future_time = datetime.now() + timedelta(hours=hour_offset)
            
            # Prepare features for prediction
            features = self._prepare_prediction_features(
                current_metrics, future_time
            )
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Make prediction
            predicted_replicas = self.model.predict(features_scaled)[0]
            
            predictions.append({
                'time': future_time,
                'predicted_replicas': max(1, int(predicted_replicas)),
                'confidence': self._calculate_confidence(features_scaled)
            })
        
        return predictions
    
    def apply_predictive_scaling(self, service_name):
        """Apply predictive scaling to a service"""
        predictions = self.predict_scaling_needs(service_name)
        
        # Get current HPA
        hpa = self.k8s_autoscaling_v2.read_namespaced_horizontal_pod_autoscaler(
            name=f"{service_name}-hpa",
            namespace=self.namespace
        )
        
        # Calculate recommended replicas for next hour
        next_hour_prediction = predictions[0]
        current_replicas = hpa.status.current_replicas or 1
        predicted_replicas = next_hour_prediction['predicted_replicas']
        confidence = next_hour_prediction['confidence']
        
        # Apply scaling with confidence threshold
        if confidence > 0.8 and abs(predicted_replicas - current_replicas) > 2:
            # Update HPA min replicas for preemptive scaling
            hpa.spec.min_replicas = min(
                predicted_replicas,
                hpa.spec.max_replicas
            )
            
            self.k8s_autoscaling_v2.patch_namespaced_horizontal_pod_autoscaler(
                name=f"{service_name}-hpa",
                namespace=self.namespace,
                body=hpa
            )
            
            logging.info(
                f"Predictive scaling applied to {service_name}: "
                f"{current_replicas} -> {predicted_replicas} "
                f"(confidence: {confidence:.2f})"
            )
    
    def _calculate_confidence(self, features):
        """Calculate prediction confidence"""
        # Use ensemble predictions to estimate confidence
        predictions = []
        for estimator in self.model.estimators_:
            pred = estimator.predict(features)[0]
            predictions.append(pred)
        
        std_dev = np.std(predictions)
        mean_pred = np.mean(predictions)
        
        # Confidence based on prediction variance
        confidence = 1 / (1 + std_dev / max(mean_pred, 1))
        return confidence
```

#### 2. Event-Driven Scaling

**Event-Based Auto-Scaling:**
```yaml
# event-driven-scaling.yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: order-processor-scaler
  namespace: production
spec:
  scaleTargetRef:
    name: order-processing-service
    
  minReplicaCount: 2
  maxReplicaCount: 50
  
  # Advanced scaling configuration
  advanced:
    restoreToOriginalReplicaCount: true
    horizontalPodAutoscalerConfig:
      behavior:
        scaleUp:
          stabilizationWindowSeconds: 60
          policies:
          - type: Percent
            value: 100
            periodSeconds: 15
          - type: Pods
            value: 10
            periodSeconds: 60
        scaleDown:
          stabilizationWindowSeconds: 300
          policies:
          - type: Percent
            value: 25
            periodSeconds: 60
          
  triggers:
  # Kafka message queue trigger
  - type: kafka
    metadata:
      bootstrapServers: kafka-cluster:9092
      consumerGroup: order-processors
      topic: order-events
      lagThreshold: "10"
      offsetResetPolicy: latest
      
  # Redis queue trigger  
  - type: redis
    metadata:
      address: redis-cluster:6379
      listName: priority-orders
      listLength: "5"
      
  # CloudWatch metrics trigger
  - type: aws-cloudwatch
    metadata:
      namespace: AWS/ApplicationELB
      metricName: RequestCountPerTarget
      targetValue: "100"
      minMetricValue: "0"
      
  # Custom metrics trigger
  - type: prometheus
    metadata:
      serverAddress: http://prometheus:9090
      metricName: pending_orders_count
      threshold: "20"
      query: sum(pending_orders{service="order-processing"})
      
---
# KEDA TriggerAuthentication for secure access
apiVersion: keda.sh/v1alpha1
kind: TriggerAuthentication
metadata:
  name: kafka-auth
  namespace: production
spec:
  secretTargetRef:
  - parameter: sasl
    name: kafka-secrets
    key: sasl
  - parameter: username
    name: kafka-secrets
    key: username
  - parameter: password
    name: kafka-secrets
    key: password
```

### Monitoring and Observability for Scaling

#### 1. Scaling Metrics Dashboard

**Grafana Dashboard Configuration:**
```json
{
  "dashboard": {
    "title": "Scalability Monitoring Dashboard",
    "panels": [
      {
        "title": "Horizontal Scaling Metrics",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(kube_deployment_status_replicas) by (deployment)",
            "legendFormat": "Current Replicas - {{deployment}}"
          },
          {
            "expr": "sum(kube_deployment_spec_replicas) by (deployment)",
            "legendFormat": "Desired Replicas - {{deployment}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 5},
                {"color": "red", "value": 10}
              ]
            }
          }
        }
      },
      {
        "title": "Scaling Events Timeline",
        "type": "timeseries",
        "targets": [
          {
            "expr": "increase(kube_hpa_status_desired_replicas[5m])",
            "legendFormat": "Scale Up Events"
          },
          {
            "expr": "decrease(kube_hpa_status_desired_replicas[5m])",
            "legendFormat": "Scale Down Events"
          }
        ]
      },
      {
        "title": "Resource Utilization vs Scaling",
        "type": "timeseries",
        "targets": [
          {
            "expr": "avg(rate(container_cpu_usage_seconds_total[5m]) * 100) by (pod)",
            "legendFormat": "CPU Utilization % - {{pod}}"
          },
          {
            "expr": "avg(container_memory_usage_bytes / container_spec_memory_limit_bytes * 100) by (pod)",
            "legendFormat": "Memory Utilization % - {{pod}}"
          }
        ]
      },
      {
        "title": "Scaling Efficiency",
        "type": "gauge",
        "targets": [
          {
            "expr": "(sum(rate(http_requests_total[5m])) / sum(kube_deployment_status_replicas)) * 100",
            "legendFormat": "Requests per Replica"
          }
        ]
      },
      {
        "title": "Cost Impact of Scaling",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(kube_pod_info{node=~\".*\"}) * 0.05",
            "legendFormat": "Estimated Hourly Cost ($)"
          }
        ]
      }
    ]
  }
}
```

#### 2. Scaling Alerts

**Prometheus Alerting Rules:**
```yaml
# scaling-alerts.yaml
groups:
- name: scaling-alerts
  rules:
  # HPA scaling issues
  - alert: HPAScalingThrashing
    expr: changes(kube_hpa_status_desired_replicas[30m]) > 10
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "HPA is scaling too frequently"
      description: "HPA {{ $labels.hpa }} has changed desired replicas {{ $value }} times in 30 minutes"
      
  - alert: HPAMaxReplicasReached
    expr: kube_hpa_status_desired_replicas >= kube_hpa_spec_max_replicas
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "HPA has reached maximum replicas"
      description: "HPA {{ $labels.hpa }} has reached maximum replicas {{ $value }}"
      
  # Resource utilization alerts
  - alert: HighResourceUtilizationWithoutScaling
    expr: |
      (
        avg(rate(container_cpu_usage_seconds_total[5m]) * 100) by (deployment) > 80
        or
        avg(container_memory_usage_bytes / container_spec_memory_limit_bytes * 100) by (deployment) > 85
      )
      and
      changes(kube_deployment_status_replicas[15m]) == 0
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "High resource utilization without scaling"
      description: "Deployment {{ $labels.deployment }} has high resource utilization but hasn't scaled"
      
  # Scaling lag alerts
  - alert: ScalingLag
    expr: |
      (
        kube_hpa_status_desired_replicas - kube_deployment_status_replicas
      ) > 0
      and
      time() - kube_hpa_status_last_scale_time > 300
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Scaling is lagging behind demand"
      description: "Deployment {{ $labels.deployment }} has been waiting to scale for over 5 minutes"
      
  # Cost optimization alerts
  - alert: UnderUtilizedReplicas
    expr: |
      (
        avg(rate(container_cpu_usage_seconds_total[30m]) * 100) by (deployment) < 20
        and
        avg(container_memory_usage_bytes / container_spec_memory_limit_bytes * 100) by (deployment) < 30
      )
      and
      kube_deployment_status_replicas > 3
    for: 30m
    labels:
      severity: info
    annotations:
      summary: "Potential cost optimization opportunity"
      description: "Deployment {{ $labels.deployment }} appears to be over-provisioned"
```

This rule establishes comprehensive scalability architecture standards ensuring systems can grow efficiently while maintaining performance, reliability, and cost-effectiveness through both horizontal and vertical scaling strategies. 
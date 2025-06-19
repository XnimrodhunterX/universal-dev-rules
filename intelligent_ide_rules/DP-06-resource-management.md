# Rule 12A: Resource Management Standards

<!-- CURSOR: highlight: Comprehensive resource allocation, optimization, governance, and cost management across infrastructure -->

## Purpose & Scope

Resource management ensures optimal allocation, utilization, and governance of computational, storage, and network resources across the entire infrastructure stack. This rule establishes comprehensive standards for resource planning, allocation policies, cost optimization, usage monitoring, and governance frameworks to maximize efficiency while controlling costs and ensuring performance requirements are met.

<!-- CURSOR: complexity: Advanced -->

## Core Standards

### Resource Allocation Framework

#### 1. Resource Classification and Tiering

**Resource Tier Classification:**
```yaml
# resource-tiers.yaml
resource_classification:
  compute_tiers:
    tier_1_critical:
      description: "Business-critical production workloads"
      sla_requirements:
        availability: "99.99%"
        response_time: "<100ms"
        recovery_time: "<5min"
      resource_allocation:
        cpu_limit: "unlimited"
        memory_limit: "unlimited"
        storage_iops: "high_performance"
        network_bandwidth: "dedicated"
      cost_priority: "performance_over_cost"
      
    tier_2_production:
      description: "Standard production workloads"
      sla_requirements:
        availability: "99.9%"
        response_time: "<500ms"
        recovery_time: "<15min"
      resource_allocation:
        cpu_limit: "8_cores_max"
        memory_limit: "32GB_max"
        storage_iops: "standard_performance"
        network_bandwidth: "shared"
      cost_priority: "balanced"
      
    tier_3_development:
      description: "Development and testing environments"
      sla_requirements:
        availability: "99%"
        response_time: "<2s"
        recovery_time: "<1h"
      resource_allocation:
        cpu_limit: "4_cores_max"
        memory_limit: "16GB_max"
        storage_iops: "basic_performance"
        network_bandwidth: "best_effort"
      cost_priority: "cost_over_performance"
      
  storage_tiers:
    hot_storage:
      access_pattern: "frequent"
      performance: "high_iops"
      cost_per_gb: "$0.20"
      use_cases: ["active_databases", "application_data"]
      
    warm_storage:
      access_pattern: "infrequent"
      performance: "standard_iops"
      cost_per_gb: "$0.10"
      use_cases: ["backups", "logs", "analytics"]
      
    cold_storage:
      access_pattern: "archival"
      performance: "low_iops"
      cost_per_gb: "$0.02"
      use_cases: ["compliance", "long_term_backup", "audit_logs"]
      
  network_tiers:
    premium:
      bandwidth: "10Gbps+"
      latency: "<1ms"
      redundancy: "multi_path"
      use_cases: ["real_time_trading", "video_streaming"]
      
    standard:
      bandwidth: "1Gbps"
      latency: "<10ms"
      redundancy: "dual_path"
      use_cases: ["web_applications", "apis"]
      
    basic:
      bandwidth: "100Mbps"
      latency: "<50ms"
      redundancy: "single_path"
      use_cases: ["development", "testing", "batch_processing"]
```

**Resource Allocation Policies:**
```yaml
# resource-allocation-policies.yaml
allocation_policies:
  namespace_quotas:
    production:
      requests:
        cpu: "100"
        memory: "500Gi"
        storage: "10Ti"
      limits:
        cpu: "200"
        memory: "1000Gi"
        storage: "20Ti"
      max_pods: 1000
      max_services: 100
      max_persistent_volumes: 200
      
    staging:
      requests:
        cpu: "50"
        memory: "200Gi"
        storage: "2Ti"
      limits:
        cpu: "100"
        memory: "400Gi"
        storage: "4Ti"
      max_pods: 500
      max_services: 50
      max_persistent_volumes: 100
      
    development:
      requests:
        cpu: "20"
        memory: "100Gi"
        storage: "1Ti"
      limits:
        cpu: "40"
        memory: "200Gi"
        storage: "2Ti"
      max_pods: 200
      max_services: 25
      max_persistent_volumes: 50
      
  quality_of_service:
    guaranteed:
      description: "Highest priority, dedicated resources"
      criteria: "requests == limits"
      scheduling_priority: "highest"
      eviction_policy: "never"
      
    burstable:
      description: "Standard priority, shared resources with burst capability"
      criteria: "requests < limits"
      scheduling_priority: "medium"
      eviction_policy: "under_pressure"
      
    best_effort:
      description: "Lowest priority, shared resources only"
      criteria: "no_requests_or_limits"
      scheduling_priority: "lowest"
      eviction_policy: "first"
      
  resource_sharing:
    cpu_sharing:
      overcommit_ratio: "2:1"
      throttling: "enabled"
      burst_capability: "limited"
      
    memory_sharing:
      overcommit_ratio: "1.2:1"
      swap: "disabled"
      oom_killer: "enabled"
      
    storage_sharing:
      thin_provisioning: "enabled"
      deduplication: "enabled"
      compression: "enabled"
```

#### 2. Kubernetes Resource Management

**Comprehensive Resource Quotas:**
```yaml
# kubernetes-resource-quotas.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    # Compute resources
    requests.cpu: "100"
    requests.memory: "500Gi"
    limits.cpu: "200"
    limits.memory: "1000Gi"
    
    # Storage resources
    requests.storage: "10Ti"
    persistentvolumeclaims: "200"
    requests.ephemeral-storage: "100Gi"
    
    # Network resources
    services: "100"
    services.loadbalancers: "10"
    services.nodeports: "20"
    
    # Object counts
    pods: "1000"
    secrets: "200"
    configmaps: "100"
    
    # Custom resources
    count/deployments.apps: "100"
    count/statefulsets.apps: "20"
    count/jobs.batch: "50"
    count/cronjobs.batch: "20"

---
apiVersion: v1
kind: LimitRange
metadata:
  name: production-limits
  namespace: production
spec:
  limits:
  # Container limits
  - type: "Container"
    default:
      cpu: "1"
      memory: "2Gi"
      ephemeral-storage: "10Gi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
      ephemeral-storage: "1Gi"
    max:
      cpu: "8"
      memory: "32Gi"
      ephemeral-storage: "100Gi"
    min:
      cpu: "10m"
      memory: "32Mi"
      ephemeral-storage: "100Mi"
      
  # Pod limits
  - type: "Pod"
    max:
      cpu: "16"
      memory: "64Gi"
      ephemeral-storage: "200Gi"
    min:
      cpu: "50m"
      memory: "64Mi"
      ephemeral-storage: "200Mi"
      
  # Persistent Volume Claim limits
  - type: "PersistentVolumeClaim"
    max:
      storage: "1Ti"
    min:
      storage: "1Gi"

---
# Network policies for resource isolation
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: production-network-isolation
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
    - namespaceSelector:
        matchLabels:
          name: staging
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: production
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS
    - protocol: TCP
      port: 53   # DNS
    - protocol: UDP
      port: 53   # DNS
```

**Priority Classes for Resource Scheduling:**
```yaml
# priority-classes.yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: system-critical
value: 2000000000
globalDefault: false
description: "Critical system components"

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
  name: standard
value: 1000
globalDefault: true
description: "Standard priority applications"

---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: low-priority
value: 100
globalDefault: false
description: "Low priority, can be preempted"

---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: best-effort
value: 10
globalDefault: false
description: "Best effort, first to be evicted"
```

### Cost Management and Optimization

#### 1. Cost Allocation and Tracking

**Resource Cost Tracking Framework:**
```yaml
# cost-tracking-framework.yaml
cost_management:
  cost_allocation_model:
    dimensions:
      - team
      - project
      - environment
      - cost_center
      - business_unit
      
    tagging_strategy:
      mandatory_tags:
        - "team"
        - "project"
        - "environment"
        - "cost_center"
      optional_tags:
        - "owner"
        - "purpose"
        - "temporary"
        - "experiment"
        
    allocation_methods:
      direct_allocation:
        description: "Resources directly attributable to teams/projects"
        examples: ["dedicated_instances", "project_storage", "team_databases"]
        
      proportional_allocation:
        description: "Shared resources allocated based on usage"
        examples: ["shared_clusters", "monitoring_infrastructure", "network_costs"]
        
      fixed_allocation:
        description: "Fixed costs distributed across all teams"
        examples: ["security_tools", "compliance_infrastructure", "base_networking"]
        
  cost_centers:
    engineering:
      budget_monthly: "$50000"
      allocation_percentage: "60%"
      cost_threshold_warning: "80%"
      cost_threshold_critical: "95%"
      
    product:
      budget_monthly: "$20000"
      allocation_percentage: "25%"
      cost_threshold_warning: "85%"
      cost_threshold_critical: "95%"
      
    infrastructure:
      budget_monthly: "$15000"
      allocation_percentage: "15%"
      cost_threshold_warning: "90%"
      cost_threshold_critical: "98%"
      
  cost_optimization_targets:
    compute:
      right_sizing: "15%_savings"
      reserved_instances: "30%_coverage"
      spot_instances: "20%_of_dev_workloads"
      
    storage:
      lifecycle_management: "25%_savings"
      deduplication: "10%_savings"
      compression: "15%_savings"
      
    network:
      traffic_optimization: "20%_reduction"
      cdn_usage: "80%_static_content"
      regional_optimization: "10%_savings"
```

**Cost Monitoring and Alerting:**
```yaml
# cost-monitoring.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cost-monitoring-config
  namespace: monitoring
data:
  cost-alerts.yml: |
    groups:
    - name: cost-management
      rules:
      # Budget alerts
      - alert: BudgetThresholdWarning
        expr: monthly_spend_by_team / monthly_budget_by_team > 0.8
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Team {{ $labels.team }} approaching budget limit"
          description: "Team {{ $labels.team }} has spent {{ $value | humanizePercentage }} of monthly budget"
          
      - alert: BudgetThresholdCritical
        expr: monthly_spend_by_team / monthly_budget_by_team > 0.95
        for: 30m
        labels:
          severity: critical
        annotations:
          summary: "Team {{ $labels.team }} near budget exhaustion"
          description: "Team {{ $labels.team }} has spent {{ $value | humanizePercentage }} of monthly budget"
          
      # Resource waste alerts
      - alert: UnderutilizedResources
        expr: avg_cpu_utilization_by_workload < 0.1 and workload_running_time > 24*3600
        for: 2h
        labels:
          severity: info
        annotations:
          summary: "Underutilized resource detected"
          description: "Workload {{ $labels.workload }} has {{ $value | humanizePercentage }} CPU utilization"
          
      # Cost anomaly detection
      - alert: CostAnomalyDetected
        expr: daily_cost_by_service > (avg_over_time(daily_cost_by_service[7d]) * 1.5)
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Unusual cost increase detected"
          description: "Service {{ $labels.service }} cost increased by {{ $value }}%"
          
  cost-dashboard-config.json: |
    {
      "dashboard": {
        "title": "Cost Management Dashboard",
        "panels": [
          {
            "title": "Monthly Cost Trends",
            "type": "timeseries",
            "targets": [
              {
                "expr": "sum(monthly_cost) by (team)",
                "legendFormat": "{{team}}"
              }
            ]
          },
          {
            "title": "Cost by Resource Type",
            "type": "piechart",
            "targets": [
              {
                "expr": "sum(daily_cost) by (resource_type)",
                "legendFormat": "{{resource_type}}"
              }
            ]
          },
          {
            "title": "Budget Utilization",
            "type": "bargauge",
            "targets": [
              {
                "expr": "sum(monthly_spend) by (team) / sum(monthly_budget) by (team) * 100",
                "legendFormat": "{{team}}"
              }
            ]
          }
        ]
      }
    }
```

#### 2. Automated Cost Optimization

**Resource Right-Sizing Automation:**
```python
# resource-rightsizing.py
import logging
import numpy as np
from kubernetes import client, config
from datetime import datetime, timedelta
import prometheus_api_client

class ResourceRightSizer:
    def __init__(self, prometheus_url, dry_run=True):
        self.prometheus = prometheus_api_client.PrometheusConnect(
            url=prometheus_url
        )
        self.dry_run = dry_run
        config.load_incluster_config()
        self.k8s_apps = client.AppsV1Api()
        
    def analyze_workload_usage(self, namespace, deployment_name, days=7):
        """Analyze resource usage patterns for a workload"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # CPU usage analysis
        cpu_query = f"""
        avg_over_time(
            rate(container_cpu_usage_seconds_total{{
                namespace="{namespace}",
                pod=~"{deployment_name}-.*"
            }}[5m])
        [{days}d:5m])
        """
        
        cpu_data = self.prometheus.custom_query_range(
            query=cpu_query,
            start_time=start_time,
            end_time=end_time,
            step='1h'
        )
        
        # Memory usage analysis
        memory_query = f"""
        avg_over_time(
            container_memory_usage_bytes{{
                namespace="{namespace}",
                pod=~"{deployment_name}-.*"
            }}
        [{days}d:5m])
        """
        
        memory_data = self.prometheus.custom_query_range(
            query=memory_query,
            start_time=start_time,
            end_time=end_time,
            step='1h'
        )
        
        return self._process_usage_data(cpu_data, memory_data)
    
    def _process_usage_data(self, cpu_data, memory_data):
        """Process and analyze usage data"""
        cpu_values = [float(point[1]) for point in cpu_data[0]['values']]
        memory_values = [float(point[1]) for point in memory_data[0]['values']]
        
        analysis = {
            'cpu': {
                'p50': np.percentile(cpu_values, 50),
                'p95': np.percentile(cpu_values, 95),
                'p99': np.percentile(cpu_values, 99),
                'max': np.max(cpu_values),
                'avg': np.mean(cpu_values),
                'std': np.std(cpu_values)
            },
            'memory': {
                'p50': np.percentile(memory_values, 50),
                'p95': np.percentile(memory_values, 95),
                'p99': np.percentile(memory_values, 99),
                'max': np.max(memory_values),
                'avg': np.mean(memory_values),
                'std': np.std(memory_values)
            }
        }
        
        return analysis
    
    def calculate_optimal_resources(self, usage_analysis, safety_margin=1.2):
        """Calculate optimal resource allocation"""
        # Use P95 + safety margin for CPU
        optimal_cpu = usage_analysis['cpu']['p95'] * safety_margin
        
        # Use P99 + safety margin for memory
        optimal_memory = usage_analysis['memory']['p99'] * safety_margin
        
        # Convert to Kubernetes format
        cpu_millicores = int(optimal_cpu * 1000)
        memory_bytes = int(optimal_memory)
        memory_mi = memory_bytes // (1024 * 1024)
        
        return {
            'cpu': f"{cpu_millicores}m",
            'memory': f"{memory_mi}Mi"
        }
    
    def get_current_resources(self, namespace, deployment_name):
        """Get current resource requests and limits"""
        deployment = self.k8s_apps.read_namespaced_deployment(
            name=deployment_name,
            namespace=namespace
        )
        
        container = deployment.spec.template.spec.containers[0]
        resources = container.resources
        
        return {
            'requests': resources.requests or {},
            'limits': resources.limits or {}
        }
    
    def generate_recommendations(self, namespace, deployment_name):
        """Generate right-sizing recommendations"""
        usage_analysis = self.analyze_workload_usage(namespace, deployment_name)
        optimal_resources = self.calculate_optimal_resources(usage_analysis)
        current_resources = self.get_current_resources(namespace, deployment_name)
        
        # Calculate potential savings
        current_cpu = self._parse_cpu(current_resources['requests'].get('cpu', '0'))
        current_memory = self._parse_memory(current_resources['requests'].get('memory', '0'))
        
        optimal_cpu = self._parse_cpu(optimal_resources['cpu'])
        optimal_memory = self._parse_memory(optimal_resources['memory'])
        
        cpu_savings = (current_cpu - optimal_cpu) / current_cpu * 100 if current_cpu > 0 else 0
        memory_savings = (current_memory - optimal_memory) / current_memory * 100 if current_memory > 0 else 0
        
        recommendation = {
            'deployment': deployment_name,
            'namespace': namespace,
            'current_resources': current_resources,
            'recommended_resources': optimal_resources,
            'usage_analysis': usage_analysis,
            'potential_savings': {
                'cpu_percent': cpu_savings,
                'memory_percent': memory_savings
            },
            'confidence': self._calculate_confidence(usage_analysis)
        }
        
        return recommendation
    
    def apply_recommendations(self, recommendations, min_confidence=0.8):
        """Apply right-sizing recommendations"""
        for rec in recommendations:
            if rec['confidence'] < min_confidence:
                logging.info(f"Skipping {rec['deployment']} due to low confidence")
                continue
                
            if self.dry_run:
                logging.info(f"DRY RUN: Would update {rec['deployment']} resources")
                continue
                
            self._update_deployment_resources(
                rec['namespace'],
                rec['deployment'],
                rec['recommended_resources']
            )
    
    def _update_deployment_resources(self, namespace, deployment_name, resources):
        """Update deployment with new resource allocation"""
        deployment = self.k8s_apps.read_namespaced_deployment(
            name=deployment_name,
            namespace=namespace
        )
        
        # Update container resources
        container = deployment.spec.template.spec.containers[0]
        if not container.resources:
            container.resources = client.V1ResourceRequirements()
        
        container.resources.requests = resources
        container.resources.limits = {
            'cpu': str(int(self._parse_cpu(resources['cpu']) * 1.5)) + 'm',
            'memory': str(int(self._parse_memory(resources['memory']) * 1.2 / (1024*1024))) + 'Mi'
        }
        
        # Apply update
        self.k8s_apps.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=deployment
        )
        
        logging.info(f"Updated {deployment_name} with new resource allocation")
    
    def _parse_cpu(self, cpu_str):
        """Parse CPU string to millicores"""
        if cpu_str.endswith('m'):
            return int(cpu_str[:-1])
        else:
            return int(float(cpu_str) * 1000)
    
    def _parse_memory(self, memory_str):
        """Parse memory string to bytes"""
        if memory_str.endswith('Mi'):
            return int(memory_str[:-2]) * 1024 * 1024
        elif memory_str.endswith('Gi'):
            return int(memory_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(memory_str)
    
    def _calculate_confidence(self, usage_analysis):
        """Calculate confidence score for recommendations"""
        cpu_cv = usage_analysis['cpu']['std'] / usage_analysis['cpu']['avg']
        memory_cv = usage_analysis['memory']['std'] / usage_analysis['memory']['avg']
        
        # Higher confidence for more stable workloads
        confidence = 1 / (1 + (cpu_cv + memory_cv) / 2)
        return min(confidence, 1.0)

# Automated right-sizing job
def run_rightsizing_analysis():
    """Run automated right-sizing analysis"""
    rightsizer = ResourceRightSizer(
        prometheus_url="http://prometheus:9090",
        dry_run=False
    )
    
    # Get all deployments
    deployments = [
        ('production', 'user-service'),
        ('production', 'order-service'),
        ('production', 'payment-service'),
        ('staging', 'user-service'),
        ('staging', 'order-service'),
    ]
    
    recommendations = []
    for namespace, deployment in deployments:
        rec = rightsizer.generate_recommendations(namespace, deployment)
        recommendations.append(rec)
        
        logging.info(f"Recommendation for {deployment}:")
        logging.info(f"  Current CPU: {rec['current_resources']['requests'].get('cpu', 'N/A')}")
        logging.info(f"  Recommended CPU: {rec['recommended_resources']['cpu']}")
        logging.info(f"  Potential CPU savings: {rec['potential_savings']['cpu_percent']:.1f}%")
        logging.info(f"  Confidence: {rec['confidence']:.2f}")
    
    # Apply recommendations with high confidence
    rightsizer.apply_recommendations(
        recommendations, 
        min_confidence=0.8
    )

if __name__ == "__main__":
    run_rightsizing_analysis()
```

### Resource Governance

#### 1. Resource Policy Enforcement

**Open Policy Agent (OPA) Resource Policies:**
```rego
# resource-policies.rego
package kubernetes.admission

# Deny pods without resource requests
deny[msg] {
    input.request.kind.kind == "Pod"
    input.request.object.spec.containers[_]
    not input.request.object.spec.containers[_].resources.requests
    msg := "Pods must specify resource requests"
}

# Enforce resource limits
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.resources.limits
    msg := "Pods must specify resource limits"
}

# Enforce CPU limits are reasonable
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    cpu_limit := container.resources.limits.cpu
    cpu_limit_millicores := parse_cpu(cpu_limit)
    cpu_limit_millicores > 8000  # 8 cores
    msg := sprintf("CPU limit %v exceeds maximum allowed (8 cores)", [cpu_limit])
}

# Enforce memory limits are reasonable
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    memory_limit := container.resources.limits.memory
    memory_limit_bytes := parse_memory(memory_limit)
    memory_limit_bytes > 34359738368  # 32GB
    msg := sprintf("Memory limit %v exceeds maximum allowed (32GB)", [memory_limit])
}

# Require appropriate QoS class for production
deny[msg] {
    input.request.kind.kind == "Pod"
    input.request.namespace == "production"
    not guaranteed_qos(input.request.object)
    not input.request.object.metadata.labels["qos-class"] == "burstable-approved"
    msg := "Production pods must have Guaranteed QoS or approved Burstable QoS"
}

# Helper functions
guaranteed_qos(pod) {
    container := pod.spec.containers[_]
    container.resources.requests.cpu == container.resources.limits.cpu
    container.resources.requests.memory == container.resources.limits.memory
}

parse_cpu(cpu_str) = millicores {
    endswith(cpu_str, "m")
    millicores := to_number(substring(cpu_str, 0, count(cpu_str) - 1))
}

parse_cpu(cpu_str) = millicores {
    not endswith(cpu_str, "m")
    millicores := to_number(cpu_str) * 1000
}

parse_memory(memory_str) = bytes {
    endswith(memory_str, "Mi")
    mebibytes := to_number(substring(memory_str, 0, count(memory_str) - 2))
    bytes := mebibytes * 1024 * 1024
}

parse_memory(memory_str) = bytes {
    endswith(memory_str, "Gi")
    gibibytes := to_number(substring(memory_str, 0, count(memory_str) - 2))
    bytes := gibibytes * 1024 * 1024 * 1024
}
```

**Gatekeeper Constraints:**
```yaml
# gatekeeper-resource-constraints.yaml
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredresources
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredResources
      validation:
        properties:
          exemptImages:
            type: array
            items:
              type: string
          maxCPU:
            type: string
          maxMemory:
            type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredresources
        
        violation[{"msg": msg}] {
            container := input.review.object.spec.containers[_]
            not container.resources.requests
            msg := "Container must specify resource requests"
        }
        
        violation[{"msg": msg}] {
            container := input.review.object.spec.containers[_]
            not container.resources.limits
            msg := "Container must specify resource limits"
        }
        
        violation[{"msg": msg}] {
            container := input.review.object.spec.containers[_]
            cpu_limit := container.resources.limits.cpu
            max_cpu := input.parameters.maxCPU
            cpu_exceeds_limit(cpu_limit, max_cpu)
            msg := sprintf("CPU limit %v exceeds maximum %v", [cpu_limit, max_cpu])
        }
        
        cpu_exceeds_limit(limit, max) {
            limit_millicores := parse_cpu(limit)
            max_millicores := parse_cpu(max)
            limit_millicores > max_millicores
        }

---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredResources
metadata:
  name: must-have-resources
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    excludedNamespaces: ["kube-system", "gatekeeper-system"]
  parameters:
    maxCPU: "8"
    maxMemory: "32Gi"
    exemptImages: 
      - "busybox"
      - "alpine"
```

#### 2. Resource Monitoring and Alerting

**Comprehensive Resource Monitoring:**
```yaml
# resource-monitoring.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: resource-monitoring-config
  namespace: monitoring
data:
  resource-alerts.yml: |
    groups:
    - name: resource-utilization
      rules:
      # Node resource alerts
      - alert: NodeHighCPUUtilization
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU utilization on node {{ $labels.instance }}"
          description: "CPU utilization is {{ $value }}%"
          
      - alert: NodeHighMemoryUtilization
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory utilization on node {{ $labels.instance }}"
          description: "Memory utilization is {{ $value }}%"
          
      # Pod resource alerts
      - alert: PodHighCPUUtilization
        expr: rate(container_cpu_usage_seconds_total[5m]) / on(pod) group_left kube_pod_container_resource_limits{resource="cpu"} > 0.9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Pod {{ $labels.pod }} high CPU utilization"
          description: "Pod is using {{ $value | humanizePercentage }} of CPU limit"
          
      - alert: PodHighMemoryUtilization
        expr: container_memory_usage_bytes / on(pod) group_left kube_pod_container_resource_limits{resource="memory"} > 0.9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Pod {{ $labels.pod }} high memory utilization"
          description: "Pod is using {{ $value | humanizePercentage }} of memory limit"
          
      # Resource waste alerts
      - alert: PodLowResourceUtilization
        expr: |
          (
            avg_over_time(rate(container_cpu_usage_seconds_total[5m])[1h:1m]) / 
            on(pod) group_left kube_pod_container_resource_requests{resource="cpu"} < 0.1
          ) and (
            avg_over_time(container_memory_usage_bytes[1h:1m]) / 
            on(pod) group_left kube_pod_container_resource_requests{resource="memory"} < 0.3
          )
        for: 2h
        labels:
          severity: info
        annotations:
          summary: "Pod {{ $labels.pod }} low resource utilization"
          description: "Pod is using much less than requested resources"
          
      # Quota alerts
      - alert: NamespaceQuotaExceeded
        expr: kube_resourcequota{type="used"} / kube_resourcequota{type="hard"} > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Namespace {{ $labels.namespace }} quota almost exceeded"
          description: "Resource {{ $labels.resource }} usage is {{ $value | humanizePercentage }} of quota"
          
  resource-dashboard.json: |
    {
      "dashboard": {
        "title": "Resource Management Dashboard",
        "panels": [
          {
            "title": "Cluster Resource Utilization",
            "type": "stat",
            "targets": [
              {
                "expr": "sum(rate(container_cpu_usage_seconds_total[5m])) / sum(kube_node_status_allocatable{resource=\"cpu\"}) * 100",
                "legendFormat": "CPU Utilization %"
              },
              {
                "expr": "sum(container_memory_usage_bytes) / sum(kube_node_status_allocatable{resource=\"memory\"}) * 100",
                "legendFormat": "Memory Utilization %"
              }
            ]
          },
          {
            "title": "Resource Requests vs Limits",
            "type": "timeseries",
            "targets": [
              {
                "expr": "sum(kube_pod_container_resource_requests) by (resource)",
                "legendFormat": "Requests - {{resource}}"
              },
              {
                "expr": "sum(kube_pod_container_resource_limits) by (resource)",
                "legendFormat": "Limits - {{resource}}"
              }
            ]
          },
          {
            "title": "Namespace Resource Usage",
            "type": "table",
            "targets": [
              {
                "expr": "sum by (namespace) (kube_pod_container_resource_requests{resource=\"cpu\"})",
                "legendFormat": "CPU Requests"
              },
              {
                "expr": "sum by (namespace) (kube_pod_container_resource_requests{resource=\"memory\"})",
                "legendFormat": "Memory Requests"
              }
            ]
          }
        ]
      }
    }
```

### Implementation Guidelines

#### 1. Resource Management Automation

**Automated Resource Management Pipeline:**
```bash
#!/bin/bash
# resource-management-automation.sh

set -e

echo "Starting automated resource management tasks..."

# 1. Resource utilization analysis
echo "Analyzing resource utilization..."
python3 /scripts/resource-analysis.py --days 7 --output /reports/utilization-report.json

# 2. Right-sizing recommendations
echo "Generating right-sizing recommendations..."
python3 /scripts/rightsizing.py --confidence-threshold 0.8 --dry-run false

# 3. Cost optimization analysis
echo "Running cost optimization analysis..."
python3 /scripts/cost-optimizer.py --target-savings 15 --output /reports/cost-optimization.json

# 4. Resource quota adjustments
echo "Checking resource quota utilization..."
kubectl get resourcequota --all-namespaces -o json | \
    jq '.items[] | select(.status.used.cpu != null) | 
        {namespace: .metadata.namespace, 
         cpu_used: .status.used.cpu, 
         cpu_hard: .status.hard.cpu}' > /reports/quota-usage.json

# 5. Policy compliance check
echo "Checking policy compliance..."
opa test /policies/resource-policies.rego

# 6. Generate recommendations report
echo "Generating resource management report..."
python3 /scripts/generate-report.py \
    --utilization /reports/utilization-report.json \
    --cost-optimization /reports/cost-optimization.json \
    --quota-usage /reports/quota-usage.json \
    --output /reports/resource-management-report.html

echo "Resource management automation completed!"
```

This rule establishes comprehensive resource management standards ensuring optimal allocation, utilization, and governance of all infrastructure resources while maintaining cost efficiency and performance requirements. 
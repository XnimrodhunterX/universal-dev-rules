# Rule 11A: Cloud Platform Standards

<!-- CURSOR: highlight: Multi-cloud architecture with vendor-specific optimizations and cloud-native integrations -->

## Purpose & Scope

Cloud platform standards ensure consistent, secure, and cost-effective utilization of cloud services across multiple providers. This rule establishes comprehensive guidelines for multi-cloud architecture, vendor-specific optimizations, cloud-native service integration, and platform governance to maximize cloud investment while maintaining portability and avoiding vendor lock-in.

<!-- CURSOR: complexity: Advanced -->

## Core Standards

### Multi-Cloud Architecture Framework

#### 1. Cloud Strategy and Governance

**Multi-Cloud Decision Matrix:**
```yaml
# cloud-strategy.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cloud-strategy
  namespace: platform-governance
data:
  provider-matrix: |
    primary_cloud: "aws"
    secondary_cloud: "azure"
    specialized_providers:
      ai_ml: "gcp"
      edge_computing: "aws"
      government: "aws-gov"
    
    workload_placement:
      production:
        primary: "aws"
        dr: "azure"
      development: "aws"
      ml_training: "gcp"
      edge_services: "aws"
    
    cost_optimization:
      reserved_instances: true
      spot_instances: true
      auto_scaling: true
      rightsizing: true
      
  governance_policies: |
    data_residency:
      - region: "us-east-1"
        compliance: ["SOC2", "PCI-DSS"]
      - region: "eu-west-1"
        compliance: ["GDPR", "SOC2"]
    
    security_baselines:
      encryption_at_rest: "required"
      encryption_in_transit: "required"
      key_management: "customer_managed"
      network_isolation: "vpc_required"
    
    cost_controls:
      budget_alerts: true
      resource_tagging: "mandatory"
      unused_resource_cleanup: "automated"
      cost_allocation: "project_based"
```

**Cloud Provider Selection Criteria:**
```yaml
# provider-selection.yaml
criteria:
  technical:
    service_availability:
      compute: ["ec2", "virtual-machines", "compute-engine"]
      storage: ["s3", "blob-storage", "cloud-storage"]
      database: ["rds", "sql-database", "cloud-sql"]
      networking: ["vpc", "vnet", "vpc"]
    
    performance_requirements:
      latency: "<100ms"
      throughput: ">10Gbps"
      availability: "99.99%"
    
    integration_capabilities:
      kubernetes: "native_support"
      monitoring: "prometheus_compatible"
      logging: "centralized_aggregation"
      
  compliance:
    certifications: ["SOC2", "ISO27001", "PCI-DSS", "HIPAA"]
    data_residency: "configurable"
    audit_logging: "comprehensive"
    
  cost:
    pricing_model: "pay_as_you_go"
    reserved_capacity: "available"
    volume_discounts: "negotiable"
    
  operational:
    api_maturity: "rest_and_sdk"
    terraform_support: "official_provider"
    support_tiers: "enterprise_available"
```

#### 2. Cloud Abstraction Layer

**Infrastructure Abstraction:**
```hcl
# cloud-abstraction/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# Universal compute module
module "compute_cluster" {
  source = "./modules/compute"
  
  provider_type = var.cloud_provider
  region        = var.region
  instance_type = var.instance_type
  min_size      = var.min_size
  max_size      = var.max_size
  
  # Universal tags
  tags = {
    Environment = var.environment
    Project     = var.project
    Owner       = var.owner
    CostCenter  = var.cost_center
    Compliance  = var.compliance_level
  }
}

# Universal storage module
module "object_storage" {
  source = "./modules/storage"
  
  provider_type   = var.cloud_provider
  bucket_name     = var.bucket_name
  versioning      = var.enable_versioning
  encryption      = var.encryption_config
  lifecycle_rules = var.lifecycle_config
  
  tags = local.common_tags
}

# Universal database module
module "managed_database" {
  source = "./modules/database"
  
  provider_type    = var.cloud_provider
  engine           = var.db_engine
  instance_class   = var.db_instance_class
  allocated_storage = var.db_storage
  
  backup_config = {
    retention_period = var.backup_retention
    backup_window   = var.backup_window
    maintenance_window = var.maintenance_window
  }
  
  tags = local.common_tags
}
```

**Provider-Specific Implementations:**
```hcl
# modules/compute/aws.tf
resource "aws_autoscaling_group" "cluster" {
  count = var.provider_type == "aws" ? 1 : 0
  
  name                = "${var.cluster_name}-asg"
  vpc_zone_identifier = var.subnet_ids
  target_group_arns   = var.target_group_arns
  health_check_type   = "ELB"
  health_check_grace_period = 300
  
  min_size         = var.min_size
  max_size         = var.max_size
  desired_capacity = var.desired_capacity
  
  launch_template {
    id      = aws_launch_template.cluster[0].id
    version = "$Latest"
  }
  
  # Instance refresh for rolling updates
  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
      instance_warmup        = 300
    }
    triggers = ["tag"]
  }
  
  dynamic "tag" {
    for_each = var.tags
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }
}

# modules/compute/azure.tf
resource "azurerm_virtual_machine_scale_set" "cluster" {
  count = var.provider_type == "azure" ? 1 : 0
  
  name                = "${var.cluster_name}-vmss"
  location            = var.region
  resource_group_name = var.resource_group_name
  upgrade_policy_mode = "Rolling"
  
  sku {
    name     = var.instance_type
    tier     = "Standard"
    capacity = var.desired_capacity
  }
  
  storage_profile_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }
  
  storage_profile_os_disk {
    name              = ""
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Premium_LRS"
  }
  
  os_profile {
    computer_name_prefix = var.cluster_name
    admin_username       = var.admin_username
    custom_data          = base64encode(var.user_data)
  }
  
  network_profile {
    name    = "${var.cluster_name}-network-profile"
    primary = true
    
    ip_configuration {
      name                                   = "internal"
      primary                                = true
      subnet_id                              = var.subnet_id
      load_balancer_backend_address_pool_ids = var.backend_pool_ids
    }
  }
  
  tags = var.tags
}
```

### AWS-Specific Optimizations

#### 1. AWS Well-Architected Framework Implementation

**Operational Excellence:**
```yaml
# aws-operational-excellence.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-operational-excellence
  namespace: aws-config
data:
  automation-config: |
    cloudformation:
      stack_policies: true
      change_sets: true
      drift_detection: true
    
    systems_manager:
      patch_management: true
      configuration_compliance: true
      session_manager: true
    
    cloudwatch:
      custom_metrics: true
      log_insights: true
      dashboards: true
      alarms: true
    
  deployment-automation: |
    codepipeline:
      multi_stage: true
      approval_gates: true
      rollback_triggers: true
    
    codedeploy:
      blue_green: true
      canary: true
      linear: true
    
    lambda_functions:
      error_handling: true
      dead_letter_queues: true
      x_ray_tracing: true
```

**Security Best Practices:**
```json
{
  "aws_security_config": {
    "iam": {
      "principle_of_least_privilege": true,
      "role_based_access": true,
      "mfa_enforcement": "required",
      "access_key_rotation": "90_days",
      "password_policy": {
        "minimum_length": 14,
        "require_symbols": true,
        "require_numbers": true,
        "require_uppercase": true,
        "require_lowercase": true,
        "password_reuse_prevention": 24
      }
    },
    "vpc": {
      "flow_logs": "enabled",
      "private_subnets": "required",
      "nat_gateways": "multi_az",
      "network_acls": "restrictive",
      "security_groups": "minimal_access"
    },
    "encryption": {
      "ebs_encryption": "enabled",
      "s3_encryption": "sse_s3",
      "rds_encryption": "enabled",
      "kms_key_rotation": "annual"
    },
    "monitoring": {
      "cloudtrail": "all_regions",
      "config": "enabled",
      "guardduty": "enabled",
      "security_hub": "enabled",
      "inspector": "enabled"
    }
  }
}
```

**Cost Optimization:**
```hcl
# aws-cost-optimization.tf
# Reserved Instance management
resource "aws_ec2_reserved_instances" "production" {
  instance_type     = "m5.large"
  availability_zone = "us-west-2a"
  instance_count    = 10
  offering_class    = "standard"
  offering_type     = "All Upfront"
  duration          = 31536000  # 1 year
  
  tags = {
    Name        = "Production Reserved Instances"
    Environment = "production"
    CostCenter  = "engineering"
  }
}

# Spot instance configuration
resource "aws_launch_template" "spot_instances" {
  name_prefix   = "spot-template-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "m5.large"
  
  # Spot instance configuration
  instance_market_options {
    market_type = "spot"
    spot_options {
      max_price                      = "0.05"
      spot_instance_type            = "one-time"
      instance_interruption_behavior = "terminate"
    }
  }
  
  # Mixed instance policy for Auto Scaling
  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "Spot Instance"
      Type = "spot"
    }
  }
}

# S3 lifecycle management
resource "aws_s3_bucket_lifecycle_configuration" "cost_optimization" {
  bucket = aws_s3_bucket.data_bucket.id
  
  rule {
    id     = "cost_optimization"
    status = "Enabled"
    
    # Transition to IA after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    # Transition to Glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    
    # Transition to Deep Archive after 365 days
    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }
    
    # Delete after 7 years
    expiration {
      days = 2555
    }
  }
}

# CloudWatch cost optimization
resource "aws_cloudwatch_metric_alarm" "high_cost_alert" {
  alarm_name          = "high-cost-alert"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "86400"  # 24 hours
  statistic           = "Maximum"
  threshold           = "1000"
  alarm_description   = "This metric monitors monthly estimated charges"
  alarm_actions       = [aws_sns_topic.cost_alerts.arn]
  
  dimensions = {
    Currency = "USD"
  }
}
```

#### 2. AWS Native Services Integration

**EKS Cluster Configuration:**
```yaml
# aws-eks-cluster.yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: production-cluster
  region: us-west-2
  version: "1.28"

# VPC configuration
vpc:
  id: "vpc-12345678"
  subnets:
    private:
      us-west-2a:
        id: "subnet-12345678"
      us-west-2b:
        id: "subnet-87654321"
      us-west-2c:
        id: "subnet-11223344"
    public:
      us-west-2a:
        id: "subnet-44332211"
      us-west-2b:
        id: "subnet-55443322"
      us-west-2c:
        id: "subnet-66554433"

# IAM configuration
iam:
  withOIDC: true
  serviceAccounts:
  - metadata:
      name: aws-load-balancer-controller
      namespace: kube-system
    wellKnownPolicies:
      awsLoadBalancerController: true
  - metadata:
      name: cluster-autoscaler
      namespace: kube-system
    wellKnownPolicies:
      autoScaler: true
  - metadata:
      name: external-dns
      namespace: kube-system
    wellKnownPolicies:
      externalDNS: true

# Managed node groups
managedNodeGroups:
- name: system-nodes
  instanceType: m5.large
  minSize: 3
  maxSize: 6
  desiredCapacity: 3
  volumeSize: 100
  ssh:
    publicKeyName: my-key
  labels:
    node-type: system
  taints:
    - key: dedicated
      value: system
      effect: NoSchedule
  tags:
    nodegroup-role: system
    k8s.io/cluster-autoscaler/enabled: "true"
    k8s.io/cluster-autoscaler/production-cluster: "owned"

- name: application-nodes
  instanceTypes: ["m5.large", "m5.xlarge", "m4.large"]
  spot: true
  minSize: 2
  maxSize: 20
  desiredCapacity: 5
  volumeSize: 100
  ssh:
    publicKeyName: my-key
  labels:
    node-type: application
  tags:
    nodegroup-role: application
    k8s.io/cluster-autoscaler/enabled: "true"
    k8s.io/cluster-autoscaler/production-cluster: "owned"

# Add-ons
addons:
- name: vpc-cni
  version: latest
- name: coredns
  version: latest
- name: kube-proxy
  version: latest
- name: aws-ebs-csi-driver
  version: latest

# CloudWatch logging
cloudWatch:
  clusterLogging:
    enableTypes: ["api", "audit", "authenticator", "controllerManager", "scheduler"]
```

**RDS Multi-AZ Configuration:**
```hcl
# aws-rds-production.tf
resource "aws_db_instance" "production" {
  identifier = "production-database"
  
  # Engine configuration
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.r6g.xlarge"
  
  # Storage configuration
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id           = aws_kms_key.rds.arn
  
  # Database configuration
  db_name  = "production"
  username = "dbadmin"
  password = random_password.db_password.result
  port     = 5432
  
  # High availability
  multi_az               = true
  availability_zone     = "us-west-2a"
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  # Security
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.production.name
  
  # Monitoring
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn
  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  # Performance Insights
  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.rds.arn
  
  # Deletion protection
  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "production-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  
  tags = {
    Name        = "Production Database"
    Environment = "production"
    Backup      = "required"
  }
}

# Read replica for read-heavy workloads
resource "aws_db_instance" "read_replica" {
  count = 2
  
  identifier = "production-read-replica-${count.index + 1}"
  
  # Replica configuration
  replicate_source_db = aws_db_instance.production.identifier
  instance_class      = "db.r6g.large"
  
  # Placement
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  # Monitoring
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn
  
  # Performance Insights
  performance_insights_enabled = true
  
  tags = {
    Name        = "Production Read Replica ${count.index + 1}"
    Environment = "production"
    Role        = "read-replica"
  }
}
```

### Azure-Specific Optimizations

#### 1. Azure Well-Architected Framework

**Reliability and Availability:**
```yaml
# azure-reliability.yaml
azure_reliability_config:
  availability_zones: true
  availability_sets: false  # Use zones instead
  
  # Traffic Manager for global load balancing
  traffic_manager:
    routing_method: "Performance"
    endpoints:
      - region: "East US"
        priority: 1
      - region: "West Europe"
        priority: 2
        
  # Application Gateway for regional load balancing
  application_gateway:
    tier: "WAF_v2"
    autoscaling:
      min_capacity: 2
      max_capacity: 10
    
  # Azure Site Recovery
  site_recovery:
    enabled: true
    target_region: "West US 2"
    recovery_vault: "production-recovery-vault"
```

**Security Configuration:**
```json
{
  "azure_security": {
    "azure_ad": {
      "conditional_access": "enabled",
      "mfa_enforcement": "required",
      "privileged_identity_management": "enabled",
      "identity_protection": "enabled"
    },
    "key_vault": {
      "soft_delete": "enabled",
      "purge_protection": "enabled",
      "access_policies": "rbac_based",
      "network_access": "private_endpoint"
    },
    "network_security": {
      "network_security_groups": "required",
      "application_security_groups": "enabled",
      "azure_firewall": "premium",
      "ddos_protection": "enabled"
    },
    "security_center": {
      "tier": "standard",
      "auto_provisioning": "enabled",
      "security_contacts": "configured",
      "workflow_automation": "enabled"
    }
  }
}
```

#### 2. AKS Configuration

**Azure Kubernetes Service Setup:**
```hcl
# azure-aks-cluster.tf
resource "azurerm_kubernetes_cluster" "production" {
  name                = "production-aks"
  location            = azurerm_resource_group.production.location
  resource_group_name = azurerm_resource_group.production.name
  dns_prefix          = "production-aks"
  kubernetes_version  = "1.28.0"
  
  # System node pool
  default_node_pool {
    name                = "system"
    node_count          = 3
    vm_size             = "Standard_DS2_v2"
    type                = "VirtualMachineScaleSets"
    availability_zones  = ["1", "2", "3"]
    enable_auto_scaling = true
    min_count          = 3
    max_count          = 6
    
    # Node pool configuration
    os_disk_size_gb = 100
    os_disk_type    = "Premium_LRS"
    
    # Taints for system workloads
    node_taints = ["CriticalAddonsOnly=true:NoSchedule"]
    
    tags = {
      Environment = "production"
      NodePool    = "system"
    }
  }
  
  # Service principal
  service_principal {
    client_id     = var.sp_client_id
    client_secret = var.sp_client_secret
  }
  
  # RBAC configuration
  role_based_access_control {
    enabled = true
    
    azure_active_directory {
      managed                = true
      admin_group_object_ids = [var.aad_admin_group_id]
      azure_rbac_enabled     = true
    }
  }
  
  # Network configuration
  network_profile {
    network_plugin    = "azure"
    network_policy    = "azure"
    dns_service_ip    = "10.2.0.10"
    docker_bridge_cidr = "172.17.0.1/16"
    service_cidr      = "10.2.0.0/24"
  }
  
  # Add-ons
  addon_profile {
    oms_agent {
      enabled                    = true
      log_analytics_workspace_id = azurerm_log_analytics_workspace.production.id
    }
    
    azure_policy {
      enabled = true
    }
    
    http_application_routing {
      enabled = false
    }
    
    kube_dashboard {
      enabled = false
    }
  }
  
  # Auto-scaler profile
  auto_scaler_profile {
    balance_similar_node_groups      = false
    expander                        = "random"
    max_graceful_termination_sec    = "600"
    max_node_provisioning_time      = "15m"
    max_unready_nodes              = 3
    max_unready_percentage         = 45
    new_pod_scale_up_delay         = "10s"
    scale_down_delay_after_add     = "10m"
    scale_down_delay_after_delete  = "10s"
    scale_down_delay_after_failure = "3m"
    scan_interval                  = "10s"
    scale_down_threshold           = "0.5"
    scale_down_unneeded_time       = "10m"
    scale_down_utilization_threshold = "0.5"
    skip_nodes_with_local_storage   = false
    skip_nodes_with_system_pods     = true
  }
  
  tags = {
    Environment = "production"
    Team        = "platform"
  }
}

# Additional node pool for applications
resource "azurerm_kubernetes_cluster_node_pool" "applications" {
  name                  = "applications"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.production.id
  vm_size              = "Standard_DS3_v2"
  availability_zones   = ["1", "2", "3"]
  
  # Scaling configuration
  enable_auto_scaling = true
  min_count          = 2
  max_count          = 20
  node_count         = 5
  
  # Storage configuration
  os_disk_size_gb = 100
  os_disk_type    = "Premium_LRS"
  
  # Spot instances for cost optimization
  priority        = "Spot"
  eviction_policy = "Delete"
  spot_max_price  = 0.1
  
  # Node labels
  node_labels = {
    "workload-type" = "application"
    "cost-profile"  = "spot"
  }
  
  tags = {
    Environment = "production"
    NodePool    = "applications"
    CostProfile = "spot"
  }
}
```

### Google Cloud Platform Optimizations

#### 1. GCP Well-Architected Principles

**Performance and Scalability:**
```yaml
# gcp-performance.yaml
gcp_performance_config:
  compute_engine:
    # Custom machine types for optimal resource allocation
    custom_machine_types: true
    preemptible_instances: true
    sustained_use_discounts: true
    
  # Global load balancing
  load_balancing:
    type: "global_http_https"
    cdn_enabled: true
    ssl_certificates: "google_managed"
    
  # Cloud SQL configuration
  cloud_sql:
    high_availability: true
    read_replicas: 2
    point_in_time_recovery: true
    automated_backups: true
    
  # Cloud Storage
  cloud_storage:
    multi_regional: true
    lifecycle_management: true
    object_versioning: true
```

#### 2. GKE Configuration

**Google Kubernetes Engine Setup:**
```hcl
# gcp-gke-cluster.tf
resource "google_container_cluster" "production" {
  name     = "production-gke"
  location = "us-central1"
  
  # Cluster configuration
  min_master_version = "1.28.0"
  network            = google_compute_network.vpc.name
  subnetwork         = google_compute_subnetwork.private.name
  
  # Remove default node pool
  remove_default_node_pool = true
  initial_node_count       = 1
  
  # Networking configuration
  ip_allocation_policy {
    cluster_secondary_range_name  = "pod-range"
    services_secondary_range_name = "service-range"
  }
  
  # Network policy
  network_policy {
    enabled = true
  }
  
  # Private cluster configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
  
  # Master authorized networks
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "10.0.0.0/8"
      display_name = "internal"
    }
  }
  
  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
  
  # Add-ons
  addons_config {
    http_load_balancing {
      disabled = false
    }
    
    horizontal_pod_autoscaling {
      disabled = false
    }
    
    network_policy_config {
      disabled = false
    }
    
    istio_config {
      disabled = false
      auth     = "AUTH_MUTUAL_TLS"
    }
    
    cloudrun_config {
      disabled = false
    }
  }
  
  # Binary authorization
  enable_binary_authorization = true
  
  # Shielded nodes
  enable_shielded_nodes = true
  
  # Logging and monitoring
  logging_service    = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"
  
  # Maintenance policy
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }
}

# System node pool
resource "google_container_node_pool" "system_nodes" {
  name       = "system-node-pool"
  location   = "us-central1"
  cluster    = google_container_cluster.production.name
  node_count = 3
  
  # Node configuration
  node_config {
    preemptible  = false
    machine_type = "e2-standard-4"
    
    # Google service account
    service_account = google_service_account.gke_nodes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/devstorage.read_only"
    ]
    
    # Shielded instance config
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
    
    # Workload metadata config
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
    
    # Taints for system workloads
    taint {
      key    = "dedicated"
      value  = "system"
      effect = "NO_SCHEDULE"
    }
    
    labels = {
      role = "system"
    }
    
    tags = ["gke-node", "system-node"]
  }
  
  # Autoscaling
  autoscaling {
    min_node_count = 3
    max_node_count = 6
  }
  
  # Management
  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# Application node pool with spot instances
resource "google_container_node_pool" "spot_nodes" {
  name       = "spot-node-pool"
  location   = "us-central1"
  cluster    = google_container_cluster.production.name
  
  # Node configuration
  node_config {
    spot         = true
    machine_type = "e2-standard-2"
    
    # Google service account
    service_account = google_service_account.gke_nodes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/devstorage.read_only"
    ]
    
    # Shielded instance config
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
    
    # Workload metadata config
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
    
    labels = {
      role         = "application"
      cost-profile = "spot"
    }
    
    tags = ["gke-node", "spot-node"]
  }
  
  # Autoscaling
  autoscaling {
    min_node_count = 0
    max_node_count = 20
  }
  
  # Management
  management {
    auto_repair  = true
    auto_upgrade = true
  }
}
```

### Cloud-Native Service Integration

#### 1. Service Mesh Integration

**Multi-Cloud Service Mesh:**
```yaml
# multi-cloud-service-mesh.yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: multi-cloud-mesh
spec:
  values:
    global:
      meshID: mesh1
      multiCluster:
        clusterName: ${CLUSTER_NAME}
      network: ${NETWORK_NAME}
      
    pilot:
      env:
        EXTERNAL_ISTIOD: true
        ENABLE_CROSS_CLUSTER_WORKLOAD_ENTRY: true
        
  components:
    pilot:
      k8s:
        env:
          - name: ENABLE_WORKLOAD_ENTRY_AUTOREGISTRATION
            value: "true"
            
---
# Cross-cluster service discovery
apiVersion: networking.istio.io/v1alpha3
kind: WorkloadEntry
metadata:
  name: aws-service
  namespace: production
spec:
  address: 10.1.1.100
  ports:
    http: 8080
  labels:
    app: user-service
    region: aws-us-west-2
    
---
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: cross-cloud-service
  namespace: production
spec:
  hosts:
  - user-service.production.svc.cluster.local
  location: MESH_EXTERNAL
  ports:
  - number: 8080
    name: http
    protocol: HTTP
  resolution: DNS
  addresses:
  - 240.0.0.1  # Virtual IP for load balancing
  endpoints:
  - address: 10.1.1.100  # AWS endpoint
    ports:
      http: 8080
  - address: 10.2.1.100  # Azure endpoint
    ports:
      http: 8080
```

#### 2. Database as a Service Integration

**Multi-Cloud Database Strategy:**
```yaml
# database-abstraction.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: database-config
  namespace: production
data:
  database-routing: |
    primary_database:
      provider: "aws"
      service: "rds"
      endpoint: "production.cluster-xyz.us-west-2.rds.amazonaws.com"
      
    read_replicas:
      - provider: "azure"
        service: "sql_database"
        endpoint: "production-replica.database.windows.net"
      - provider: "gcp"
        service: "cloud_sql"
        endpoint: "production-replica.sql.gcp.internal"
        
    cache_layer:
      provider: "aws"
      service: "elasticache"
      endpoint: "production-cache.abc123.cache.amazonaws.com"
      
    search_engine:
      provider: "gcp"
      service: "elasticsearch"
      endpoint: "https://production-search.elasticsearch.gcp.cloud"
```

**Database Connection Pool Configuration:**
```yaml
# database-connection-pool.yaml
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
        env:
        - name: DATABASES_HOST
          value: "production.cluster-xyz.us-west-2.rds.amazonaws.com"
        - name: DATABASES_PORT
          value: "5432"
        - name: DATABASES_USER
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: username
        - name: DATABASES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: password
        - name: POOL_MODE
          value: "transaction"
        - name: MAX_CLIENT_CONN
          value: "1000"
        - name: DEFAULT_POOL_SIZE
          value: "20"
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
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

### Cost Optimization Across Clouds

#### 1. Multi-Cloud Cost Management

**Cost Optimization Framework:**
```yaml
# cost-optimization-framework.yaml
cost_optimization:
  strategies:
    compute:
      - reserved_instances: "1_year_all_upfront"
      - spot_instances: "development_staging"
      - right_sizing: "automated_recommendations"
      - auto_scaling: "predictive_scaling"
      
    storage:
      - lifecycle_policies: "automated"
      - compression: "enabled"
      - deduplication: "enabled"
      - tiered_storage: "intelligent"
      
    networking:
      - cdn_optimization: "global_distribution"
      - data_transfer_optimization: "regional_peering"
      - bandwidth_pooling: "shared_limits"
      
  monitoring:
    budget_alerts:
      - threshold: "80%"
        action: "notify_team"
      - threshold: "90%"
        action: "restrict_non_critical"
      - threshold: "100%"
        action: "emergency_shutdown"
        
    cost_allocation:
      - by_team: "department_tags"
      - by_project: "project_tags"
      - by_environment: "environment_tags"
      
  automation:
    unused_resources: "daily_cleanup"
    right_sizing: "weekly_analysis"
    commitment_optimization: "monthly_review"
```

**Cost Monitoring Dashboard:**
```json
{
  "cost_dashboard": {
    "widgets": [
      {
        "type": "cost_trend",
        "timeframe": "30_days",
        "breakdown": ["service", "region", "environment"]
      },
      {
        "type": "budget_tracking",
        "budgets": ["monthly", "quarterly", "annual"],
        "alerts": "enabled"
      },
      {
        "type": "optimization_opportunities",
        "categories": ["compute", "storage", "networking"],
        "potential_savings": "percentage"
      },
      {
        "type": "cost_allocation",
        "dimensions": ["team", "project", "environment"],
        "visualization": "tree_map"
      }
    ]
  }
}
```

### Disaster Recovery and Business Continuity

#### 1. Multi-Cloud Disaster Recovery

**DR Strategy Configuration:**
```yaml
# disaster-recovery-strategy.yaml
disaster_recovery:
  rto_targets:
    critical_services: "< 1 hour"
    business_services: "< 4 hours"
    development_services: "< 24 hours"
    
  rpo_targets:
    critical_data: "< 15 minutes"
    business_data: "< 1 hour"
    development_data: "< 24 hours"
    
  multi_cloud_strategy:
    primary_region: "aws-us-west-2"
    dr_region: "azure-west-us-2"
    backup_region: "gcp-us-central1"
    
  replication:
    database:
      primary_to_dr: "synchronous"
      primary_to_backup: "asynchronous"
      frequency: "continuous"
      
    storage:
      primary_to_dr: "real_time"
      primary_to_backup: "daily"
      retention: "30_days"
      
    applications:
      deployment_automation: "terraform"
      configuration_sync: "git_ops"
      secrets_replication: "vault_replication"
      
  failover_automation:
    health_checks: "multi_layer"
    decision_criteria: "automated_with_approval"
    rollback_capability: "one_click"
    communication: "automated_notifications"
```

**Cross-Cloud Backup Strategy:**
```hcl
# cross-cloud-backup.tf
# AWS S3 primary backup
resource "aws_s3_bucket" "primary_backup" {
  bucket = "production-backup-primary"
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    enabled = true
    
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

# Azure Blob Storage DR backup
resource "azurerm_storage_account" "dr_backup" {
  name                     = "productiondrbackup"
  resource_group_name      = azurerm_resource_group.dr.name
  location                 = "West US 2"
  account_tier             = "Standard"
  account_replication_type = "GRS"
  
  blob_properties {
    versioning_enabled = true
    
    delete_retention_policy {
      days = 30
    }
  }
}

# Google Cloud Storage tertiary backup
resource "google_storage_bucket" "tertiary_backup" {
  name     = "production-backup-tertiary"
  location = "US-CENTRAL1"
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
}
```

## Implementation Guidelines

### Cloud Migration Strategy

1. **Assessment and Planning:**
```bash
#!/bin/bash
# cloud-assessment.sh

echo "Starting cloud readiness assessment..."

# Assess current infrastructure
terraform show > current_infrastructure.json

# Analyze dependencies
dependency_analyzer --input current_infrastructure.json \
                   --output dependency_graph.json

# Cost estimation
cloud_cost_estimator --aws --azure --gcp \
                    --input dependency_graph.json \
                    --output cost_comparison.json

# Security assessment
security_scanner --infrastructure current_infrastructure.json \
                --compliance "SOC2,PCI-DSS,GDPR" \
                --output security_report.json

echo "Assessment complete. Review reports before proceeding."
```

2. **Phased Migration Approach:**
```yaml
# migration-phases.yaml
migration_strategy:
  phase_1_foundation:
    duration: "2_weeks"
    components:
      - networking_setup
      - identity_and_access_management
      - security_baseline
      - monitoring_and_logging
      
  phase_2_data_services:
    duration: "4_weeks"
    components:
      - database_migration
      - storage_migration
      - backup_and_recovery
      - data_synchronization
      
  phase_3_applications:
    duration: "6_weeks"
    components:
      - containerization
      - kubernetes_deployment
      - service_mesh_integration
      - load_balancing
      
  phase_4_optimization:
    duration: "2_weeks"
    components:
      - performance_tuning
      - cost_optimization
      - security_hardening
      - disaster_recovery_testing
```

### Monitoring and Observability

```yaml
# multi-cloud-monitoring.yaml
observability_stack:
  metrics:
    prometheus:
      federation: "hierarchical"
      retention: "30d"
      ha_configuration: "active_active"
      
    cloud_native_metrics:
      aws_cloudwatch: "enabled"
      azure_monitor: "enabled"
      gcp_monitoring: "enabled"
      
  logging:
    centralized_logging:
      platform: "elastic_stack"
      retention: "90d"
      encryption: "at_rest_and_transit"
      
    log_forwarding:
      aws_cloudtrail: "enabled"
      azure_activity_logs: "enabled"
      gcp_audit_logs: "enabled"
      
  tracing:
    distributed_tracing:
      platform: "jaeger"
      sampling_rate: "1%"
      retention: "7d"
      
    service_mesh_tracing:
      istio_tracing: "enabled"
      envoy_access_logs: "enabled"
      
  alerting:
    notification_channels:
      - slack
      - pagerduty
      - email
      
    alert_groups:
      - infrastructure
      - applications
      - security
      - cost
```

This rule provides comprehensive cloud platform standards ensuring optimal utilization of multi-cloud environments while maintaining security, cost-effectiveness, and operational excellence across all major cloud providers. 
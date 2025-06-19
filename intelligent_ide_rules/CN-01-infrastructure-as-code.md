---
description: "Infrastructure as Code: Terraform, CloudFormation, resource management, infrastructure automation. Comprehensive IaC standards and best practices."
globs: ["**/*"]
alwaysApply: true
---

# 🏗️ Infrastructure as Code Standards

<!-- CURSOR: highlight: infrastructure:code -->
<!-- CURSOR: context: terraform, cloudformation, aws, kubernetes, automation -->
<!-- CURSOR: complexity: advanced -->
<!-- CURSOR: priority: high -->

## 1. IaC Platform Standards

### Core Requirements
- **MUST** use Infrastructure as Code for all infrastructure provisioning
- **MUST** version control all infrastructure definitions
- **MUST** implement automated infrastructure testing and validation
- **MUST** use modular, reusable infrastructure components

### Platform Selection Matrix
```yaml
# iac-platform-matrix.yaml
platform_selection:
  terraform:
    use_cases:
      - "Multi-cloud deployments"
      - "Complex infrastructure topologies"
      - "Custom resource management"
    advantages:
      - "Provider agnostic"
      - "Rich ecosystem"
      - "Advanced state management"
    file_extensions: [".tf", ".tfvars"]
    
  cloudformation:
    use_cases:
      - "AWS-native deployments"
      - "AWS service integration"
      - "CloudFormation-specific features"
    advantages:
      - "Native AWS integration"
      - "Built-in rollback capabilities"
      - "CloudWatch integration"
    file_extensions: [".yaml", ".yml", ".json"]
    
  pulumi:
    use_cases:
      - "Complex logic in infrastructure"
      - "Existing application code reuse"
      - "Type-safe infrastructure"
    advantages:
      - "General-purpose languages"
      - "Strong typing"
      - "Code reuse"
    file_extensions: [".ts", ".py", ".go", ".cs"]

  cdk:
    use_cases:
      - "AWS cloud-native applications"
      - "Developer-friendly abstractions"
      - "TypeScript/Python preferences"
    advantages:
      - "Higher-level constructs"
      - "IDE support"
      - "Unit testing capabilities"
    file_extensions: [".ts", ".py", ".java", ".cs"]
```

## 2. Terraform Standards

### Project Structure
```
infrastructure/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── production/
├── modules/
│   ├── networking/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── compute/
│   ├── database/
│   └── monitoring/
├── shared/
│   ├── data.tf
│   ├── providers.tf
│   └── versions.tf
├── scripts/
│   ├── plan.sh
│   ├── apply.sh
│   └── destroy.sh
└── tests/
    ├── unit/
    ├── integration/
    └── compliance/
```

### Terraform Module Template
```hcl
# modules/compute/main.tf
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Local values for resource naming and tagging
locals {
  name_prefix = "${var.environment}-${var.service_name}"
  
  common_tags = merge(var.additional_tags, {
    Environment     = var.environment
    Service         = var.service_name
    ManagedBy      = "terraform"
    CreatedAt      = timestamp()
    Owner          = var.owner
    CostCenter     = var.cost_center
  })
  
  # Security group rules
  ingress_rules = [
    for rule in var.ingress_rules : {
      from_port   = rule.from_port
      to_port     = rule.to_port
      protocol    = rule.protocol
      cidr_blocks = rule.cidr_blocks
      description = rule.description
    }
  ]
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${local.name_prefix}-alb"
  internal           = var.internal_load_balancer
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = var.subnet_ids

  enable_deletion_protection = var.enable_deletion_protection

  dynamic "access_logs" {
    for_each = var.access_logs_enabled ? [1] : []
    content {
      bucket  = var.access_logs_bucket
      prefix  = var.access_logs_prefix
      enabled = true
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb"
    Type = "load-balancer"
  })
}

# Security Group for ALB
resource "aws_security_group" "alb" {
  name_prefix = "${local.name_prefix}-alb-"
  vpc_id      = var.vpc_id
  description = "Security group for ${local.name_prefix} ALB"

  dynamic "ingress" {
    for_each = local.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
      description = ingress.value.description
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb-sg"
    Type = "security-group"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"

  setting {
    name  = "containerInsights"
    value = var.enable_container_insights ? "enabled" : "disabled"
  }

  dynamic "configuration" {
    for_each = var.enable_execute_command ? [1] : []
    content {
      execute_command_configuration {
        logging = "DEFAULT"
      }
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-cluster"
    Type = "ecs-cluster"
  })
}

# ECS Service
resource "aws_ecs_service" "main" {
  name            = "${local.name_prefix}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.desired_count

  deployment_configuration {
    maximum_percent         = var.max_capacity_percent
    minimum_healthy_percent = var.min_capacity_percent
    
    deployment_circuit_breaker {
      enable   = true
      rollback = true
    }
  }

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets         = var.private_subnet_ids
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.main.arn
    container_name   = var.container_name
    container_port   = var.container_port
  }

  dynamic "service_registries" {
    for_each = var.service_discovery_enabled ? [1] : []
    content {
      registry_arn = aws_service_discovery_service.main[0].arn
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-service"
    Type = "ecs-service"
  })

  depends_on = [aws_lb_listener.main]
}

# Auto Scaling
resource "aws_appautoscaling_target" "ecs_target" {
  count              = var.enable_autoscaling ? 1 : 0
  max_capacity       = var.autoscaling_max_capacity
  min_capacity       = var.autoscaling_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.main.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  tags = local.common_tags
}

resource "aws_appautoscaling_policy" "ecs_policy_cpu" {
  count              = var.enable_autoscaling ? 1 : 0
  name               = "${local.name_prefix}-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target[0].resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target[0].service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = var.autoscaling_cpu_target
  }
}
```

### Terraform Variables
```hcl
# modules/compute/variables.tf
variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production."
  }
}

variable "service_name" {
  description = "Name of the service"
  type        = string
  validation {
    condition     = length(var.service_name) > 0 && length(var.service_name) <= 32
    error_message = "Service name must be between 1 and 32 characters."
  }
}

variable "vpc_id" {
  description = "VPC ID where resources will be created"
  type        = string
  validation {
    condition     = can(regex("^vpc-[a-z0-9]+$", var.vpc_id))
    error_message = "VPC ID must be a valid AWS VPC identifier."
  }
}

variable "subnet_ids" {
  description = "List of subnet IDs for load balancer"
  type        = list(string)
  validation {
    condition     = length(var.subnet_ids) >= 2
    error_message = "At least 2 subnet IDs must be provided for high availability."
  }
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for ECS tasks"
  type        = list(string)
  validation {
    condition     = length(var.private_subnet_ids) >= 2
    error_message = "At least 2 private subnet IDs must be provided."
  }
}

variable "container_image" {
  description = "Docker image URI for the container"
  type        = string
  validation {
    condition     = can(regex("^[a-zA-Z0-9][a-zA-Z0-9._/-]*:[a-zA-Z0-9._-]+$", var.container_image))
    error_message = "Container image must be a valid Docker image URI with tag."
  }
}

variable "container_port" {
  description = "Port exposed by the container"
  type        = number
  default     = 8080
  validation {
    condition     = var.container_port > 0 && var.container_port <= 65535
    error_message = "Container port must be between 1 and 65535."
  }
}

variable "desired_count" {
  description = "Desired number of tasks"
  type        = number
  default     = 2
  validation {
    condition     = var.desired_count >= 1
    error_message = "Desired count must be at least 1."
  }
}

variable "cpu" {
  description = "CPU units for the task (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 512
  validation {
    condition     = contains([256, 512, 1024, 2048, 4096], var.cpu)
    error_message = "CPU must be one of: 256, 512, 1024, 2048, 4096."
  }
}

variable "memory" {
  description = "Memory for the task in MB"
  type        = number
  default     = 1024
  validation {
    condition     = var.memory >= 512 && var.memory <= 30720
    error_message = "Memory must be between 512 and 30720 MB."
  }
}

variable "enable_autoscaling" {
  description = "Enable auto scaling for the ECS service"
  type        = bool
  default     = true
}

variable "autoscaling_min_capacity" {
  description = "Minimum number of tasks for auto scaling"
  type        = number
  default     = 1
}

variable "autoscaling_max_capacity" {
  description = "Maximum number of tasks for auto scaling"
  type        = number
  default     = 10
}

variable "autoscaling_cpu_target" {
  description = "Target CPU utilization for auto scaling"
  type        = number
  default     = 70
  validation {
    condition     = var.autoscaling_cpu_target >= 10 && var.autoscaling_cpu_target <= 90
    error_message = "CPU target must be between 10 and 90 percent."
  }
}

variable "additional_tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "owner" {
  description = "Owner of the resources (team or individual)"
  type        = string
}

variable "cost_center" {
  description = "Cost center for billing purposes"
  type        = string
}
```

### Terraform Outputs
```hcl
# modules/compute/outputs.tf
output "cluster_id" {
  description = "ECS cluster ID"
  value       = aws_ecs_cluster.main.id
}

output "cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.main.name
}

output "service_arn" {
  description = "ECS service ARN"
  value       = aws_ecs_service.main.id
}

output "load_balancer_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "load_balancer_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "load_balancer_arn" {
  description = "ARN of the load balancer"
  value       = aws_lb.main.arn
}

output "target_group_arn" {
  description = "ARN of the target group"
  value       = aws_lb_target_group.main.arn
}

output "security_group_id" {
  description = "Security group ID for ECS tasks"
  value       = aws_security_group.ecs_tasks.id
}

output "log_group_name" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.main.name
}

# Sensitive outputs
output "task_execution_role_arn" {
  description = "ARN of the task execution role"
  value       = aws_iam_role.ecs_task_execution_role.arn
  sensitive   = false
}

output "task_role_arn" {
  description = "ARN of the task role"
  value       = aws_iam_role.ecs_task_role.arn
  sensitive   = false
}
```

## 3. Terraform State Management

### Remote State Configuration
```hcl
# shared/backend.tf
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "services/${var.service_name}/${var.environment}/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
    
    # Enable versioning and lifecycle policies
    versioning {
      enabled = true
    }
    
    # Server-side encryption
    server_side_encryption_configuration {
      rule {
        apply_server_side_encryption_by_default {
          sse_algorithm = "AES256"
        }
      }
    }
  }
}

# Data source for remote state
data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "company-terraform-state"
    key    = "network/${var.environment}/terraform.tfstate"
    region = "us-west-2"
  }
}

data "terraform_remote_state" "shared" {
  backend = "s3"
  config = {
    bucket = "company-terraform-state"
    key    = "shared/${var.environment}/terraform.tfstate"
    region = "us-west-2"
  }
}
```

### State Lock with DynamoDB
```hcl
# shared/state-lock.tf
resource "aws_dynamodb_table" "terraform_state_lock" {
  name           = "terraform-state-lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "Terraform State Lock"
    Environment = "shared"
    Purpose     = "terraform-state-locking"
    ManagedBy   = "terraform"
  }
}

# S3 bucket for Terraform state
resource "aws_s3_bucket" "terraform_state" {
  bucket = "company-terraform-state"

  tags = {
    Name        = "Terraform State"
    Environment = "shared"
    Purpose     = "terraform-state-storage"
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

## 4. Infrastructure Testing

### Terratest Implementation
```go
// tests/integration/compute_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/gruntwork-io/terratest/modules/aws"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestComputeModule(t *testing.T) {
    t.Parallel()

    // Pick a random AWS region to test in
    awsRegion := aws.GetRandomStableRegion(t, nil, nil)

    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        // Path to the Terraform code that will be tested
        TerraformDir: "../../modules/compute",

        // Variables to pass to our Terraform code using -var options
        Vars: map[string]interface{}{
            "environment":          "test",
            "service_name":         "test-service",
            "vpc_id":              getTestVPCId(t, awsRegion),
            "subnet_ids":          getTestSubnetIds(t, awsRegion),
            "private_subnet_ids":  getTestPrivateSubnetIds(t, awsRegion),
            "container_image":     "nginx:latest",
            "container_port":      80,
            "desired_count":       1,
            "owner":               "test",
            "cost_center":         "engineering",
        },

        // Environment variables to set when running Terraform
        EnvVars: map[string]string{
            "AWS_DEFAULT_REGION": awsRegion,
        },
    })

    // Clean up resources with "terraform destroy" at the end of the test
    defer terraform.Destroy(t, terraformOptions)

    // Run "terraform init" and "terraform apply"
    terraform.InitAndApply(t, terraformOptions)

    // Run validations
    validateECSCluster(t, terraformOptions, awsRegion)
    validateLoadBalancer(t, terraformOptions, awsRegion)
    validateSecurityGroups(t, terraformOptions, awsRegion)
    validateAutoScaling(t, terraformOptions, awsRegion)
}

func validateECSCluster(t *testing.T, terraformOptions *terraform.Options, region string) {
    clusterName := terraform.Output(t, terraformOptions, "cluster_name")
    
    // Verify ECS cluster exists
    cluster := aws.GetEcsCluster(t, region, clusterName)
    assert.Equal(t, "ACTIVE", *cluster.Status)
    assert.True(t, *cluster.RegisteredContainerInstancesCount >= 0)
    
    // Verify ECS service exists and is stable
    serviceName := terraform.Output(t, terraformOptions, "service_name")
    service := aws.GetEcsService(t, region, clusterName, serviceName)
    assert.Equal(t, "ACTIVE", *service.Status)
    assert.Equal(t, int64(1), *service.DesiredCount)
}

func validateLoadBalancer(t *testing.T, terraformOptions *terraform.Options, region string) {
    lbArn := terraform.Output(t, terraformOptions, "load_balancer_arn")
    
    // Verify load balancer exists and is active
    lb := aws.GetApplicationLoadBalancer(t, region, lbArn)
    assert.Equal(t, "active", *lb.State.Code)
    assert.Equal(t, "application", *lb.Type)
    
    // Verify target group is healthy
    tgArn := terraform.Output(t, terraformOptions, "target_group_arn")
    targetGroup := aws.GetTargetGroup(t, region, tgArn)
    assert.Equal(t, "HTTP", *targetGroup.Protocol)
    assert.Equal(t, int64(80), *targetGroup.Port)
}

func validateSecurityGroups(t *testing.T, terraformOptions *terraform.Options, region string) {
    sgId := terraform.Output(t, terraformOptions, "security_group_id")
    
    // Verify security group rules
    sg := aws.GetSecurityGroupById(t, sgId, region)
    assert.NotEmpty(t, sg.GroupId)
    
    // Check that ingress rules are properly configured
    hasHTTPRule := false
    for _, rule := range sg.IpPermissions {
        if *rule.FromPort == 80 && *rule.ToPort == 80 {
            hasHTTPRule = true
            break
        }
    }
    assert.True(t, hasHTTPRule, "Security group should allow HTTP traffic on port 80")
}

func validateAutoScaling(t *testing.T, terraformOptions *terraform.Options, region string) {
    serviceName := terraform.Output(t, terraformOptions, "service_name")
    clusterName := terraform.Output(t, terraformOptions, "cluster_name")
    
    // Verify auto scaling target exists
    resourceId := fmt.Sprintf("service/%s/%s", clusterName, serviceName)
    targets := aws.GetAppAutoScalingTargets(t, region, "ecs", resourceId)
    
    require.NotEmpty(t, targets, "Auto scaling target should exist")
    assert.Equal(t, int64(1), *targets[0].MinCapacity)
    assert.Equal(t, int64(10), *targets[0].MaxCapacity)
}
```

### Infrastructure Compliance Testing
```go
// tests/compliance/security_test.go
package compliance

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestSecurityCompliance(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "../../environments/dev",
    }

    // Initialize without applying
    terraform.Init(t, terraformOptions)

    // Generate plan
    plan := terraform.InitAndPlan(t, terraformOptions)

    t.Run("EncryptionCompliance", func(t *testing.T) {
        testEncryptionCompliance(t, plan)
    })

    t.Run("NetworkSecurityCompliance", func(t *testing.T) {
        testNetworkSecurityCompliance(t, plan)
    })

    t.Run("AccessControlCompliance", func(t *testing.T) {
        testAccessControlCompliance(t, plan)
    })

    t.Run("LoggingCompliance", func(t *testing.T) {
        testLoggingCompliance(t, plan)
    })
}

func testEncryptionCompliance(t *testing.T, plan string) {
    // Test that all S3 buckets have encryption enabled
    assert.Contains(t, plan, "server_side_encryption_configuration")
    
    // Test that all EBS volumes are encrypted
    assert.Contains(t, plan, "encrypted = true")
    
    // Test that RDS instances have encryption enabled
    assert.Contains(t, plan, "storage_encrypted = true")
}

func testNetworkSecurityCompliance(t *testing.T, plan string) {
    // Test that security groups don't allow 0.0.0.0/0 on sensitive ports
    assert.NotContains(t, plan, `cidr_blocks = ["0.0.0.0/0"].*port.*= 22`)
    assert.NotContains(t, plan, `cidr_blocks = ["0.0.0.0/0"].*port.*= 3389`)
    
    // Test that resources are deployed in private subnets
    assert.Contains(t, plan, "private_subnet")
}

func testAccessControlCompliance(t *testing.T, plan string) {
    // Test that IAM policies follow least privilege
    assert.NotContains(t, plan, `"Effect": "Allow".*"Action": "*"`)
    assert.NotContains(t, plan, `"Resource": "*"`)
}

func testLoggingCompliance(t *testing.T, plan string) {
    // Test that CloudTrail is enabled
    assert.Contains(t, plan, "aws_cloudtrail")
    
    // Test that VPC Flow Logs are enabled
    assert.Contains(t, plan, "aws_flow_log")
    
    // Test that load balancer access logging is enabled
    assert.Contains(t, plan, "access_logs")
}
```

## 5. CI/CD Pipeline for Infrastructure

### CI pipeline Terraform Workflow
```yaml
# .github/workflows/infrastructure.yml
name: Infrastructure CI/CD

on:
  push:
    branches: [main]
    paths: ['infrastructure/**']
  pull_request:
    branches: [main]
    paths: ['infrastructure/**']
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'dev'
        type: choice
        options: ['dev', 'staging', 'production']
      action:
        description: 'Action to perform'
        required: true
        default: 'plan'
        type: choice
        options: ['plan', 'apply', 'destroy']

env:
  TF_VERSION: '1.5.0'
  AWS_REGION: 'us-west-2'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Format Check
        run: |
          cd infrastructure
          terraform fmt -check -recursive

      - name: Terraform Validate
        run: |
          cd infrastructure
          find . -name "*.tf" -exec dirname {} \; | sort -u | while read dir; do
            echo "Validating $dir"
            cd "$dir"
            terraform init -backend=false
            terraform validate
            cd - > /dev/null
          done

      - name: Security Scan with tfsec
        uses: aquasecurity/tfsec-action@v1.0.3
        with:
          working_directory: infrastructure
          format: sarif
          output: tfsec.sarif

      - name: Upload security scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: tfsec.sarif

  plan:
    needs: validate
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [dev, staging, production]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Terraform Init
        run: |
          cd infrastructure/environments/${{ matrix.environment }}
          terraform init

      - name: Terraform Plan
        id: plan
        run: |
          cd infrastructure/environments/${{ matrix.environment }}
          terraform plan -out=tfplan -detailed-exitcode
        continue-on-error: true

      - name: Save Plan
        uses: actions/upload-artifact@v4
        with:
          name: tfplan-${{ matrix.environment }}
          path: infrastructure/environments/${{ matrix.environment }}/tfplan

      - name: Comment PR with Plan
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const output = `
            ## Terraform Plan Results for ${{ matrix.environment }}
            
            #### Terraform Initialization ⚙️ \`${{ steps.init.outcome }}\`
            #### Terraform Plan 📖 \`${{ steps.plan.outcome }}\`
            
            <details><summary>Show Plan</summary>
            
            \`\`\`terraform
            ${{ steps.plan.outputs.stdout }}
            \`\`\`
            
            </details>
            
            *Pusher: @${{ github.actor }}, Action: \`${{ github.event_name }}\`*
            `;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            })

  apply:
    needs: [validate, plan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment: 
      name: ${{ github.event.inputs.environment || 'dev' }}
      url: ${{ steps.apply.outputs.url }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Download Plan
        uses: actions/download-artifact@v4
        with:
          name: tfplan-${{ github.event.inputs.environment || 'dev' }}
          path: infrastructure/environments/${{ github.event.inputs.environment || 'dev' }}

      - name: Terraform Apply
        id: apply
        run: |
          cd infrastructure/environments/${{ github.event.inputs.environment || 'dev' }}
          terraform init
          terraform apply tfplan

      - name: Run Infrastructure Tests
        run: |
          cd infrastructure/tests
          go test -v -timeout 30m ./...

      - name: Update Infrastructure Documentation
        run: |
          cd infrastructure
          terraform-docs markdown table . > ../docs/infrastructure.md
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add ../docs/infrastructure.md
          git diff --staged --quiet || git commit -m "Update infrastructure documentation"
          git push

  drift-detection:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    strategy:
      matrix:
        environment: [dev, staging, production]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Detect Configuration Drift
        run: |
          cd infrastructure/environments/${{ matrix.environment }}
          terraform init
          terraform plan -detailed-exitcode
        continue-on-error: true
        id: drift

      - name: Report Drift
        if: steps.drift.outputs.exitcode == 2
        uses: 8398a7/action-slack@v3
        with:
          status: warning
          text: |
            🚨 **Infrastructure Drift Detected**
            
            Environment: ${{ matrix.environment }}
            Drift detected in Terraform configuration.
            Please review and reconcile the infrastructure state.
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## 6. Quality Gates & Monitoring

### Infrastructure Quality Gates
```yaml
# Quality gates for Infrastructure as Code
infrastructure_quality_gates:
  terraform_validation:
    description: "All Terraform configurations pass validation"
    metric: "terraform_validation_success_rate"
    threshold: 100
    blocking: true

  security_compliance:
    description: "Security scans pass without critical findings"
    metric: "security_scan_critical_findings"
    threshold: 0
    blocking: true

  drift_detection:
    description: "Infrastructure drift detection and remediation"
    metric: "infrastructure_drift_incidents"
    threshold: 2  # per month
    blocking: false

  module_reusability:
    description: "Percentage of infrastructure using reusable modules"
    metric: "infrastructure_module_usage_percentage"
    threshold: 80
    blocking: false

  cost_optimization:
    description: "Infrastructure cost optimization metrics"
    metric: "monthly_cost_increase_percentage"
    threshold: 10
    blocking: false
```

---

## 📋 **Implementation Checklist**

### Terraform Setup
- [ ] Set up Terraform project structure with modules
- [ ] Configure remote state backend with S3 and DynamoDB
- [ ] Implement state locking and encryption
- [ ] Create reusable modules for common resources

### Infrastructure Testing
- [ ] Set up Terratest for integration testing
- [ ] Implement compliance testing with security checks
- [ ] Create unit tests for Terraform modules
- [ ] Set up drift detection and monitoring

### CI/CD Pipeline
- [ ] Configure CI pipeline for Terraform workflows
- [ ] Implement automated security scanning
- [ ] Set up plan review and approval processes
- [ ] Create automated documentation generation

### Monitoring & Governance
- [ ] Implement infrastructure cost monitoring
- [ ] Set up drift detection and alerting
- [ ] Create infrastructure compliance reporting
- [ ] Establish module governance and versioning

### Security & Compliance
- [ ] Implement least privilege IAM policies
- [ ] Enable encryption for all data at rest and in transit
- [ ] Set up network security with proper segmentation
- [ ] Configure logging and monitoring for all resources

---

## 🎯 **Success Metrics**

- **Infrastructure Automation:** 100% of infrastructure managed through IaC
- **Deployment Success Rate:** 99% of infrastructure deployments succeed without manual intervention
- **Security Compliance:** Zero critical security findings in automated scans
- **Module Reusability:** 80% of infrastructure uses standardized, reusable modules
- **Mean Time to Provision:** <30 minutes for complete environment setup 
# Rule 17B: Microservices Governance

## Overview
Comprehensive governance framework for microservices architecture ensuring proper service boundaries, communication patterns, data consistency, and operational excellence across distributed systems.

## Core Principles

### Service Design Governance
- Domain-driven service boundaries
- Single responsibility per service
- Independent deployment and scaling
- Decentralized data management

### Governance Framework
```yaml
# microservices-governance.yaml
governance_framework:
  service_design:
    boundary_strategy: "domain_driven_design"
    ownership_model: "team_owned"
    lifecycle_management: "independent"
    data_ownership: "service_exclusive"
  
  communication:
    synchronous: "REST/GraphQL for queries"
    asynchronous: "events for state changes"
    discovery: "service_registry"
    routing: "api_gateway"
  
  data_management:
    consistency: "eventual_consistency"
    transactions: "saga_pattern"
    sharing: "api_contracts_only"
    storage: "database_per_service"
  
  operational:
    monitoring: "distributed_tracing"
    logging: "correlation_ids"
    security: "zero_trust"
    deployment: "independent_pipelines"
```

## Implementation Standards

### 1. Service Boundary Definition

#### Domain-Driven Service Design
```typescript
// governance/ServiceBoundaryAnalyzer.ts
export interface ServiceBoundary {
  serviceName: string;
  domain: string;
  subdomain: string;
  responsibilities: string[];
  dataOwnership: string[];
  dependencies: ServiceDependency[];
  teamOwnership: string;
}

export interface ServiceDependency {
  targetService: string;
  dependencyType: 'synchronous' | 'asynchronous' | 'data';
  criticality: 'high' | 'medium' | 'low';
  sla: ServiceLevelAgreement;
}

export interface ServiceLevelAgreement {
  availability: string;
  responseTime: string;
  throughput: string;
  errorRate: string;
}

/**
 * Service boundary analyzer for governance validation
 */
export class ServiceBoundaryAnalyzer {
  private services: Map<string, ServiceBoundary> = new Map();

  registerService(boundary: ServiceBoundary): void {
    this.validateServiceBoundary(boundary);
    this.services.set(boundary.serviceName, boundary);
  }

  private validateServiceBoundary(boundary: ServiceBoundary): void {
    // Single responsibility validation
    if (boundary.responsibilities.length > 5) {
      throw new Error(`Service ${boundary.serviceName} has too many responsibilities (${boundary.responsibilities.length}). Consider splitting.`);
    }

    this.validateDataOwnership(boundary);
    this.validateDependencies(boundary);
  }

  private validateDataOwnership(boundary: ServiceBoundary): void {
    const conflictingOwnership = boundary.dataOwnership.filter(data => {
      return Array.from(this.services.values()).some(service => 
        service.serviceName !== boundary.serviceName && 
        service.dataOwnership.includes(data)
      );
    });

    if (conflictingOwnership.length > 0) {
      throw new Error(`Service ${boundary.serviceName} has conflicting data ownership: ${conflictingOwnership.join(', ')}`);
    }
  }

  private validateDependencies(boundary: ServiceBoundary): void {
    const synchronousDeps = boundary.dependencies.filter(dep => dep.dependencyType === 'synchronous');
    
    if (synchronousDeps.length > 3) {
      console.warn(`Service ${boundary.serviceName} has many synchronous dependencies (${synchronousDeps.length}). Consider asynchronous patterns.`);
    }

    this.detectCircularDependencies(boundary);
  }

  private detectCircularDependencies(boundary: ServiceBoundary): void {
    const visited = new Set<string>();
    const recursionStack = new Set<string>();

    const hasCircularDependency = (serviceName: string): boolean => {
      if (recursionStack.has(serviceName)) {
        return true;
      }

      if (visited.has(serviceName)) {
        return false;
      }

      visited.add(serviceName);
      recursionStack.add(serviceName);

      const service = this.services.get(serviceName);
      if (service) {
        for (const dep of service.dependencies) {
          if (hasCircularDependency(dep.targetService)) {
            return true;
          }
        }
      }

      recursionStack.delete(serviceName);
      return false;
    };

    if (hasCircularDependency(boundary.serviceName)) {
      throw new Error(`Circular dependency detected involving service: ${boundary.serviceName}`);
    }
  }

  generateDependencyGraph(): string {
    let graph = 'digraph ServiceDependencies {\n';
    graph += '  rankdir=LR;\n';
    graph += '  node [shape=<provider>];\n\n';

    for (const service of this.services.values()) {
      for (const dep of service.dependencies) {
        const style = dep.dependencyType === 'synchronous' ? 'solid' : 'dashed';
        const color = dep.criticality === 'high' ? 'red' : dep.criticality === 'medium' ? 'orange' : 'green';
        
        graph += `  "${service.serviceName}" -> "${dep.targetService}" [style=${style}, color=${color}];\n`;
      }
    }

    graph += '}';
    return graph;
  }

  analyzeCoupling(): ServiceCouplingReport {
    const report: ServiceCouplingReport = {
      totalServices: this.services.size,
      averageDependencies: 0,
      highCouplingServices: [],
      isolatedServices: [],
      recommendations: []
    };

    let totalDependencies = 0;

    for (const service of this.services.values()) {
      const dependencyCount = service.dependencies.length;
      totalDependencies += dependencyCount;

      if (dependencyCount > 5) {
        report.highCouplingServices.push({
          serviceName: service.serviceName,
          dependencyCount,
          recommendation: 'Consider splitting service or reducing dependencies'
        });
      }

      if (dependencyCount === 0) {
        report.isolatedServices.push(service.serviceName);
      }
    }

    report.averageDependencies = totalDependencies / this.services.size;

    if (report.averageDependencies > 3) {
      report.recommendations.push('Average service coupling is high. Consider domain restructuring.');
    }

    if (report.highCouplingServices.length > this.services.size * 0.2) {
      report.recommendations.push('More than 20% of services are highly coupled. Review service boundaries.');
    }

    return report;
  }
}

export interface ServiceCouplingReport {
  totalServices: number;
  averageDependencies: number;
  highCouplingServices: Array<{
    serviceName: string;
    dependencyCount: number;
    recommendation: string;
  }>;
  isolatedServices: string[];
  recommendations: string[];
}
```

### 2. Communication Governance

#### Service Contract Management
```typescript
// governance/CommunicationGovernance.ts
export interface ServiceContract {
  serviceName: string;
  version: string;
  endpoints: EndpointDefinition[];
  events: EventDefinition[];
  schema: any;
  backwardCompatibility: boolean;
}

export interface EndpointDefinition {
  path: string;
  method: string;
  purpose: string;
  inputSchema: any;
  outputSchema: any;
  deprecationDate?: Date;
}

export interface EventDefinition {
  eventType: string;
  version: string;
  schema: any;
  frequency: string;
  consumers: string[];
}

export class CommunicationGovernance {
  private contracts: Map<string, ServiceContract> = new Map();

  registerContract(contract: ServiceContract): void {
    this.validateContract(contract);
    this.contracts.set(contract.serviceName, contract);
  }

  private validateContract(contract: ServiceContract): void {
    // Validate endpoint naming conventions
    for (const endpoint of contract.endpoints) {
      if (!this.isValidEndpointPath(endpoint.path)) {
        throw new Error(`Invalid endpoint path: ${endpoint.path}. Must follow REST conventions.`);
      }
    }

    // Validate event definitions
    for (const event of contract.events) {
      if (!this.isValidEventType(event.eventType)) {
        throw new Error(`Invalid event type: ${event.eventType}. Must follow naming conventions.`);
      }
    }

    if (contract.backwardCompatibility) {
      this.validateBackwardCompatibility(contract);
    }
  }

  private isValidEndpointPath(path: string): boolean {
    const pathPattern = /^\/api\/v\d+\/[a-z-]+(\/{[a-zA-Z0-9_-]+})*$/;
    return pathPattern.test(path);
  }

  private isValidEventType(eventType: string): boolean {
    const eventPattern = /^[A-Z][a-zA-Z]+[A-Z][a-z]+$/;
    return eventPattern.test(eventType);
  }

  private validateBackwardCompatibility(contract: ServiceContract): void {
    const existingContract = this.contracts.get(contract.serviceName);
    if (!existingContract) return;

    for (const existingEndpoint of existingContract.endpoints) {
      const newEndpoint = contract.endpoints.find(e => 
        e.path === existingEndpoint.path && e.method === existingEndpoint.method
      );

      if (!newEndpoint) {
        throw new Error(`Breaking change: Endpoint ${existingEndpoint.method} ${existingEndpoint.path} was removed`);
      }

      if (!this.isSchemaCompatible(existingEndpoint.inputSchema, newEndpoint.inputSchema)) {
        throw new Error(`Breaking change: Input schema for ${existingEndpoint.path} is not backward compatible`);
      }
    }
  }

  private isSchemaCompatible(oldSchema: any, newSchema: any): boolean {
    if (!oldSchema || !newSchema) return true;

    if (oldSchema.required && newSchema.required) {
      return oldSchema.required.every((field: string) => newSchema.required.includes(field));
    }

    return true;
  }

  generateApiDocumentation(): string {
    let documentation = '# Service API Documentation\n\n';

    for (const contract of this.contracts.values()) {
      documentation += `## ${contract.serviceName} (v${contract.version})\n\n`;

      if (contract.endpoints.length > 0) {
        documentation += '### Endpoints\n\n';
        for (const endpoint of contract.endpoints) {
          documentation += `#### ${endpoint.method} ${endpoint.path}\n`;
          documentation += `**Purpose:** ${endpoint.purpose}\n\n`;
          
          if (endpoint.deprecationDate) {
            documentation += `**⚠️ Deprecated:** This endpoint will be removed on ${endpoint.deprecationDate.toISOString()}\n\n`;
          }
        }
      }

      if (contract.events.length > 0) {
        documentation += '### Events\n\n';
        for (const event of contract.events) {
          documentation += `#### ${event.eventType} (v${event.version})\n`;
          documentation += `**Frequency:** ${event.frequency}\n`;
          documentation += `**Consumers:** ${event.consumers.join(', ')}\n\n`;
        }
      }

      documentation += '---\n\n';
    }

    return documentation;
  }
}
```

### 3. Saga Pattern for Distributed Transactions

#### Saga Orchestrator
```typescript
// governance/SagaOrchestrator.ts
export interface SagaStep {
  stepId: string;
  serviceName: string;
  action: string;
  compensationAction: string;
  timeout: number;
  retryPolicy: RetryPolicy;
}

export interface RetryPolicy {
  maxAttempts: number;
  backoffStrategy: 'fixed' | 'exponential' | 'linear';
  baseDelay: number;
  maxDelay: number;
}

export interface SagaDefinition {
  sagaId: string;
  sagaType: string;
  steps: SagaStep[];
  timeout: number;
  compensationOrder: 'reverse' | 'custom';
}

export interface SagaExecution {
  executionId: string;
  sagaId: string;
  status: 'running' | 'completed' | 'failed' | 'compensating' | 'compensated';
  currentStep: number;
  completedSteps: string[];
  failedStep?: string;
  startTime: Date;
  endTime?: Date;
  context: any;
}

export class SagaOrchestrator {
  private sagaDefinitions: Map<string, SagaDefinition> = new Map();
  private activeExecutions: Map<string, SagaExecution> = new Map();
  private stepHandlers: Map<string, SagaStepHandler> = new Map();

  registerSaga(definition: SagaDefinition): void {
    this.validateSagaDefinition(definition);
    this.sagaDefinitions.set(definition.sagaId, definition);
  }

  registerStepHandler(serviceName: string, handler: SagaStepHandler): void {
    this.stepHandlers.set(serviceName, handler);
  }

  async startSaga(sagaId: string, context: any): Promise<string> {
    const definition = this.sagaDefinitions.get(sagaId);
    if (!definition) {
      throw new Error(`Saga definition not found: ${sagaId}`);
    }

    const executionId = this.generateExecutionId();
    const execution: SagaExecution = {
      executionId,
      sagaId,
      status: 'running',
      currentStep: 0,
      completedSteps: [],
      startTime: new Date(),
      context
    };

    this.activeExecutions.set(executionId, execution);

    this.executeSaga(execution).catch(error => {
      console.error(`Saga execution failed: ${executionId}`, error);
    });

    return executionId;
  }

  private async executeSaga(execution: SagaExecution): Promise<void> {
    const definition = this.sagaDefinitions.get(execution.sagaId)!;

    try {
      for (let i = execution.currentStep; i < definition.steps.length; i++) {
        const step = definition.steps[i];
        execution.currentStep = i;

        await this.executeStep(execution, step);
        execution.completedSteps.push(step.stepId);
      }

      execution.status = 'completed';
      execution.endTime = new Date();
    } catch (error) {
      execution.status = 'failed';
      execution.failedStep = definition.steps[execution.currentStep].stepId;
      
      await this.compensateSaga(execution);
    }
  }

  private async executeStep(execution: SagaExecution, step: SagaStep): Promise<void> {
    const handler = this.stepHandlers.get(step.serviceName);
    if (!handler) {
      throw new Error(`No handler found for service: ${step.serviceName}`);
    }

    const retryPolicy = step.retryPolicy;
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= retryPolicy.maxAttempts; attempt++) {
      try {
        await Promise.race([
          handler.executeAction(step.action, execution.context),
          this.createTimeout(step.timeout)
        ]);
        
        return;
      } catch (error) {
        lastError = error as Error;
        
        if (attempt < retryPolicy.maxAttempts) {
          const delay = this.calculateRetryDelay(retryPolicy, attempt);
          await this.delay(delay);
        }
      }
    }

    throw lastError;
  }

  private async compensateSaga(execution: SagaExecution): Promise<void> {
    execution.status = 'compensating';
    const definition = this.sagaDefinitions.get(execution.sagaId)!;

    const stepsToCompensate = [...execution.completedSteps].reverse();

    for (const stepId of stepsToCompensate) {
      const step = definition.steps.find(s => s.stepId === stepId)!;
      const handler = this.stepHandlers.get(step.serviceName);

      if (handler) {
        try {
          await handler.executeCompensation(step.compensationAction, execution.context);
        } catch (error) {
          console.error(`Compensation failed for step ${stepId}:`, error);
        }
      }
    }

    execution.status = 'compensated';
    execution.endTime = new Date();
  }

  private calculateRetryDelay(policy: RetryPolicy, attempt: number): number {
    let delay: number;

    switch (policy.backoffStrategy) {
      case 'fixed':
        delay = policy.baseDelay;
        break;
      case 'linear':
        delay = policy.baseDelay * attempt;
        break;
      case 'exponential':
        delay = policy.baseDelay * Math.pow(2, attempt - 1);
        break;
    }

    return Math.min(delay, policy.maxDelay);
  }

  private createTimeout(timeoutMs: number): Promise<never> {
    return new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Step timeout')), timeoutMs);
    });
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private generateExecutionId(): string {
    return `saga_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private validateSagaDefinition(definition: SagaDefinition): void {
    if (definition.steps.length === 0) {
      throw new Error('Saga must have at least one step');
    }

    for (const step of definition.steps) {
      if (!step.stepId || !step.serviceName || !step.action || !step.compensationAction) {
        throw new Error(`Invalid step definition: ${step.stepId}`);
      }
    }
  }

  getExecutionStatus(executionId: string): SagaExecution | null {
    return this.activeExecutions.get(executionId) || null;
  }
}

export interface SagaStepHandler {
  executeAction(action: string, context: any): Promise<void>;
  executeCompensation(action: string, context: any): Promise<void>;
}
```

### 4. Service Registry

#### Service Discovery Implementation
```typescript
// governance/ServiceRegistry.ts
export interface ServiceInstance {
  serviceId: string;
  serviceName: string;
  version: string;
  host: string;
  port: number;
  protocol: string;
  healthCheckUrl: string;
  metadata: Record<string, string>;
  registrationTime: Date;
  lastHeartbeat: Date;
  status: 'healthy' | 'unhealthy' | 'unknown';
}

export class ServiceRegistry {
  private services: Map<string, ServiceInstance[]> = new Map();
  private healthCheckInterval: NodeJS.Timeout;

  constructor(private healthCheckIntervalMs: number = 30000) {
    this.healthCheckInterval = setInterval(() => {
      this.performHealthChecks();
    }, healthCheckIntervalMs);
  }

  async registerService(instance: ServiceInstance): Promise<void> {
    this.validateServiceInstance(instance);

    if (!this.services.has(instance.serviceName)) {
      this.services.set(instance.serviceName, []);
    }

    const instances = this.services.get(instance.serviceName)!;
    
    const existingIndex = instances.findIndex(s => s.serviceId === instance.serviceId);
    if (existingIndex >= 0) {
      instances.splice(existingIndex, 1);
    }

    instances.push({
      ...instance,
      registrationTime: new Date(),
      lastHeartbeat: new Date(),
      status: 'unknown'
    });

    console.log(`Service registered: ${instance.serviceName} (${instance.serviceId})`);
  }

  async discoverService(serviceName: string): Promise<ServiceInstance[]> {
    const instances = this.services.get(serviceName) || [];
    return instances.filter(instance => instance.status === 'healthy');
  }

  private async performHealthChecks(): Promise<void> {
    for (const [serviceName, instances] of this.services.entries()) {
      for (const instance of instances) {
        try {
          const healthCheck = await this.checkServiceHealth(instance);
          instance.status = healthCheck.status;
          instance.lastHeartbeat = healthCheck.timestamp;

          if (healthCheck.status === 'unhealthy') {
            console.warn(`Service unhealthy: ${serviceName} (${instance.serviceId})`);
          }
        } catch (error) {
          instance.status = 'unhealthy';
          console.error(`Health check failed for ${serviceName} (${instance.serviceId}):`, error);
        }
      }
    }

    this.removeStaleInstances();
  }

  private async checkServiceHealth(instance: ServiceInstance): Promise<ServiceHealthCheck> {
    const startTime = Date.now();
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(instance.healthCheckUrl, {
        signal: controller.signal,
        method: 'GET'
      });

      clearTimeout(timeoutId);
      const responseTime = Date.now() - startTime;

      return {
        serviceId: instance.serviceId,
        status: response.ok ? 'healthy' : 'unhealthy',
        timestamp: new Date(),
        responseTime
      };
    } catch (error) {
      return {
        serviceId: instance.serviceId,
        status: 'unhealthy',
        timestamp: new Date(),
        responseTime: Date.now() - startTime
      };
    }
  }

  private removeStaleInstances(): void {
    const staleThreshold = 5 * 60 * 1000; // 5 minutes
    const now = Date.now();

    for (const [serviceName, instances] of this.services.entries()) {
      const activeInstances = instances.filter(instance => {
        const timeSinceHeartbeat = now - instance.lastHeartbeat.getTime();
        return timeSinceHeartbeat < staleThreshold;
      });

      if (activeInstances.length !== instances.length) {
        const removedCount = instances.length - activeInstances.length;
        console.log(`Removed ${removedCount} stale instances of ${serviceName}`);
      }

      if (activeInstances.length === 0) {
        this.services.delete(serviceName);
      } else {
        this.services.set(serviceName, activeInstances);
      }
    }
  }

  private validateServiceInstance(instance: ServiceInstance): void {
    if (!instance.serviceId || !instance.serviceName) {
      throw new Error('Service ID and name are required');
    }

    if (!instance.host || !instance.port) {
      throw new Error('Host and port are required');
    }

    if (!instance.healthCheckUrl) {
      throw new Error('Health check URL is required');
    }

    if (!instance.version) {
      throw new Error('Service version is required');
    }
  }

  destroy(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
  }
}

export interface ServiceHealthCheck {
  serviceId: string;
  status: 'healthy' | 'unhealthy';
  timestamp: Date;
  responseTime: number;
}
```

## CI/CD Integration

### Governance Pipeline
```yaml
# .github/workflows/microservices-governance.yml
name: Microservices Governance

on:
  push:
    paths:
      - 'services/**'
      - 'governance/**'

jobs:
  governance-validation:
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
      
      - name: Validate service boundaries
        run: npm run validate:service-boundaries
      
      - name: Check service contracts
        run: npm run validate:service-contracts
      
      - name: Analyze service coupling
        run: npm run analyze:coupling
      
      - name: Generate governance report
        run: npm run generate:governance-report

  integration-tests:
    runs-on: ubuntu-latest
    needs: governance-validation
    steps:
      - uses: actions/checkout@v3
      
      - name: Start service dependencies
        run: docker-compose up -d
      
      - name: Run integration tests
        run: npm run test:integration
      
      - name: Test saga patterns
        run: npm run test:saga

  deploy:
    needs: [governance-validation, integration-tests]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy service registry
        run: |
          kubectl apply -f k8s/service-registry.yaml
          kubectl rollout status deployment/service-registry
```

## Enforcement Mechanisms

### Quality Gates
```yaml
# quality-gates/microservices-governance.yml
microservices_governance_gates:
  service_design:
    max_responsibilities_per_service: 5
    max_synchronous_dependencies: 3
    data_ownership_conflicts: 0
    circular_dependencies: 0
  
  communication:
    contract_backward_compatibility: true
    endpoint_naming_compliance: 100%
    event_naming_compliance: 100%
  
  operational:
    service_availability: ">= 99.9%"
    saga_completion_rate: ">= 99%"
    service_discovery_latency: "< 10ms"

validation_rules:
  - name: "Service boundary validation"
    command: "npm run validate:service-boundaries"
    fail_on_error: true
  
  - name: "Contract compatibility check"
    command: "npm run validate:contracts"
    fail_on_error: true
  
  - name: "Coupling analysis"
    command: "npm run analyze:coupling"
    threshold: "average_dependencies < 3"
```

## Success Criteria

- ✅ Service boundaries follow domain-driven design principles
- ✅ No circular dependencies between services
- ✅ Data ownership clearly defined with no conflicts
- ✅ Service contracts maintain backward compatibility
- ✅ Communication patterns follow governance policies
- ✅ Saga patterns handle distributed transactions reliably
- ✅ Service discovery provides sub-10ms response times
- ✅ Health checks maintain 99.5% success rate
- ✅ Average service coupling below 3 dependencies
- ✅ 100% service contract documentation coverage 
# CN-04: Comprehensive Monitoring & Observability

## Purpose & Scope

Comprehensive monitoring and observability framework covering metrics collection, structured logging, distributed tracing, security monitoring, and alerting. This rule establishes unified standards for complete system observability, SRE practices, log aggregation, security event monitoring, and incident response to ensure production reliability and security visibility.

## Core Standards

### 1. Metrics Collection & Instrumentation Framework

#### Application Metrics Excellence

**Core Monitoring Requirements:**
- **RED Methodology**: Rate, Errors, Duration for request-driven services
- **USE Methodology**: Utilization, Saturation, Errors for resource monitoring
- **SLI/SLO Framework**: Service Level Indicators and Objectives with error budgets
- **Distributed Tracing**: End-to-end request flow visibility

**Comprehensive Metrics Collection:**
```typescript
// src/monitoring/metrics-collector.ts
import prometheus from 'prom-client';
import { Request, Response, NextFunction } from 'express';

export interface MetricsConfig {
  serviceName: string;
  version: string;
  environment: string;
  instanceId?: string;
  customLabels?: Record<string, string>;
}

export class ComprehensiveMetricsCollector {
  private static instance: ComprehensiveMetricsCollector;
  private registry: prometheus.Registry;
  private config: MetricsConfig;
  
  // RED Metrics (Rate, Errors, Duration)
  private httpRequestsTotal: prometheus.Counter;
  private httpRequestDuration: prometheus.Histogram;
  private httpRequestsErrors: prometheus.Counter;
  
  // USE Metrics (Utilization, Saturation, Errors)
  private cpuUtilization: prometheus.Gauge;
  private memoryUtilization: prometheus.Gauge;
  private diskUtilization: prometheus.Gauge;
  private networkConnections: prometheus.Gauge;
  private queueDepth: prometheus.Gauge;
  
  // Business & Application Metrics
  private businessMetrics: Map<string, prometheus.Counter | prometheus.Gauge | prometheus.Histogram>;
  private customMetrics: Map<string, any>;
  
  // Security Metrics
  private securityEvents: prometheus.Counter;
  private authenticationAttempts: prometheus.Counter;
  private authorizationFailures: prometheus.Counter;

  constructor(config: MetricsConfig) {
    this.config = config;
    this.registry = new prometheus.Registry();
    this.businessMetrics = new Map();
    this.customMetrics = new Map();
    this.setupDefaultMetrics();
    this.setupApplicationMetrics();
    this.setupSecurityMetrics();
  }

  static getInstance(config?: MetricsConfig): ComprehensiveMetricsCollector {
    if (!ComprehensiveMetricsCollector.instance) {
      if (!config) {
        throw new Error('MetricsConfig required for first initialization');
      }
      ComprehensiveMetricsCollector.instance = new ComprehensiveMetricsCollector(config);
    }
    return ComprehensiveMetricsCollector.instance;
  }

  private setupDefaultMetrics(): void {
    // Default Node.js metrics with custom labels
    prometheus.collectDefaultMetrics({ 
      register: this.registry,
      labels: {
        service: this.config.serviceName,
        version: this.config.version,
        environment: this.config.environment,
        ...this.config.customLabels
      }
    });
  }

  private setupApplicationMetrics(): void {
    const defaultLabels = {
      service: this.config.serviceName,
      version: this.config.version,
      environment: this.config.environment
    };

    // HTTP Request metrics (RED)
    this.httpRequestsTotal = new prometheus.Counter({
      name: 'http_requests_total',
      help: 'Total number of HTTP requests',
      labelNames: ['method', 'route', 'status_code', 'service', 'version', 'environment'],
      registers: [this.registry]
    });

    this.httpRequestDuration = new prometheus.Histogram({
      name: 'http_request_duration_seconds',
      help: 'Duration of HTTP requests in seconds',
      labelNames: ['method', 'route', 'status_code', 'service', 'version', 'environment'],
      buckets: [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30],
      registers: [this.registry]
    });

    this.httpRequestsErrors = new prometheus.Counter({
      name: 'http_requests_errors_total',
      help: 'Total number of HTTP request errors',
      labelNames: ['method', 'route', 'error_type', 'error_code', 'service', 'version', 'environment'],
      registers: [this.registry]
    });

    // System metrics (USE)
    this.cpuUtilization = new prometheus.Gauge({
      name: 'system_cpu_utilization_percent',
      help: 'CPU utilization percentage',
      labelNames: ['service', 'version', 'environment', 'instance'],
      registers: [this.registry]
    });

    this.memoryUtilization = new prometheus.Gauge({
      name: 'system_memory_utilization_percent',
      help: 'Memory utilization percentage',
      labelNames: ['service', 'version', 'environment', 'instance'],
      registers: [this.registry]
    });

    this.diskUtilization = new prometheus.Gauge({
      name: 'system_disk_utilization_percent',
      help: 'Disk utilization percentage',
      labelNames: ['service', 'version', 'environment', 'instance', 'mount_point'],
      registers: [this.registry]
    });

    this.networkConnections = new prometheus.Gauge({
      name: 'network_connections_active',
      help: 'Number of active network connections',
      labelNames: ['service', 'version', 'environment', 'instance', 'connection_type'],
      registers: [this.registry]
    });

    this.queueDepth = new prometheus.Gauge({
      name: 'queue_depth_current',
      help: 'Current queue depth',
      labelNames: ['service', 'version', 'environment', 'queue_name', 'queue_type'],
      registers: [this.registry]
    });
  }

  private setupSecurityMetrics(): void {
    this.securityEvents = new prometheus.Counter({
      name: 'security_events_total',
      help: 'Total number of security events',
      labelNames: ['event_type', 'severity', 'source', 'service', 'version', 'environment'],
      registers: [this.registry]
    });

    this.authenticationAttempts = new prometheus.Counter({
      name: 'authentication_attempts_total',
      help: 'Total number of authentication attempts',
      labelNames: ['outcome', 'method', 'source_ip', 'user_agent', 'service', 'version', 'environment'],
      registers: [this.registry]
    });

    this.authorizationFailures = new prometheus.Counter({
      name: 'authorization_failures_total',
      help: 'Total number of authorization failures',
      labelNames: ['resource', 'action', 'user_id', 'reason', 'service', 'version', 'environment'],
      registers: [this.registry]
    });
  }

  // HTTP Metrics Recording
  recordHttpRequest(method: string, route: string, statusCode: number, duration: number, errorDetails?: any): void {
    const baseLabels = {
      method,
      route,
      status_code: statusCode.toString(),
      service: this.config.serviceName,
      version: this.config.version,
      environment: this.config.environment
    };
    
    this.httpRequestsTotal.inc(baseLabels);
    this.httpRequestDuration.observe(baseLabels, duration / 1000); // Convert to seconds
    
    if (statusCode >= 400) {
      this.httpRequestsErrors.inc({
        ...baseLabels,
        error_type: statusCode >= 500 ? 'server_error' : 'client_error',
        error_code: statusCode.toString()
      });
    }
  }

  // Security Metrics Recording
  recordSecurityEvent(eventType: string, severity: 'low' | 'medium' | 'high' | 'critical', source: string, details?: any): void {
    this.securityEvents.inc({
      event_type: eventType,
      severity,
      source,
      service: this.config.serviceName,
      version: this.config.version,
      environment: this.config.environment
    });
  }

  recordAuthenticationAttempt(outcome: 'success' | 'failure', method: string, sourceIp: string, userAgent: string): void {
    this.authenticationAttempts.inc({
      outcome,
      method,
      source_ip: sourceIp,
      user_agent: userAgent,
      service: this.config.serviceName,
      version: this.config.version,
      environment: this.config.environment
    });
  }

  recordAuthorizationFailure(resource: string, action: string, userId: string, reason: string): void {
    this.authorizationFailures.inc({
      resource,
      action,
      user_id: userId,
      reason,
      service: this.config.serviceName,
      version: this.config.version,
      environment: this.config.environment
    });
  }

  // Business Metrics Factory
  createBusinessCounter(name: string, help: string, labelNames: string[] = []): prometheus.Counter {
    const counter = new prometheus.Counter({
      name,
      help,
      labelNames: [...labelNames, 'service', 'version', 'environment'],
      registers: [this.registry]
    });
    
    this.businessMetrics.set(name, counter);
    return counter;
  }

  createBusinessGauge(name: string, help: string, labelNames: string[] = []): prometheus.Gauge {
    const gauge = new prometheus.Gauge({
      name,
      help,
      labelNames: [...labelNames, 'service', 'version', 'environment'],
      registers: [this.registry]
    });
    
    this.businessMetrics.set(name, gauge);
    return gauge;
  }

  createBusinessHistogram(name: string, help: string, labelNames: string[] = [], buckets?: number[]): prometheus.Histogram {
    const histogram = new prometheus.Histogram({
      name,
      help,
      labelNames: [...labelNames, 'service', 'version', 'environment'],
      buckets: buckets || prometheus.exponentialBuckets(0.001, 2, 15),
      registers: [this.registry]
    });
    
    this.businessMetrics.set(name, histogram);
    return histogram;
  }

  // System Metrics Updates
  updateSystemMetrics(): void {
    const usage = process.cpuUsage();
    const memUsage = process.memoryUsage();
    
    // CPU utilization calculation
    const cpuPercent = (usage.user + usage.system) / 1000000; // Convert to seconds
    this.cpuUtilization.set({
      service: this.config.serviceName,
      version: this.config.version,
      environment: this.config.environment,
      instance: this.config.instanceId || process.pid.toString()
    }, cpuPercent);
    
    // Memory utilization
    const totalMemory = memUsage.heapTotal + memUsage.external;
    const usedMemory = memUsage.heapUsed;
    const memoryPercent = (usedMemory / totalMemory) * 100;
    
    this.memoryUtilization.set({
      service: this.config.serviceName,
      version: this.config.version,
      environment: this.config.environment,
      instance: this.config.instanceId || process.pid.toString()
    }, memoryPercent);
  }

  // Export metrics
  async getMetrics(): Promise<string> {
    this.updateSystemMetrics();
    return this.registry.metrics();
  }

  getRegistry(): prometheus.Registry {
    return this.registry;
  }
}

// Express Middleware Integration
export function metricsMiddleware() {
  const metrics = ComprehensiveMetricsCollector.getInstance();
  
  return (req: Request, res: Response, next: NextFunction) => {
    const startTime = Date.now();
    
    res.on('finish', () => {
      const duration = Date.now() - startTime;
      const route = req.route?.path || req.path;
      
      metrics.recordHttpRequest(
        req.method,
        route,
        res.statusCode,
        duration
      );
    });
    
    next();
  };
}
```

### 2. Comprehensive Structured Logging Framework

#### Enterprise Logging Standards

**Logging Architecture Requirements:**
- **Structured Logging**: JSON format with consistent schema
- **Contextual Enrichment**: Request tracing, user context, correlation IDs
- **Security-First**: No sensitive data exposure, audit trail compliance
- **Centralized Aggregation**: ELK, Datadog, or equivalent SIEM integration

**Advanced Structured Logger:**
```typescript
// src/logging/comprehensive-logger.ts
import winston from 'winston';
import { Request } from 'express';

export interface LogContext {
  requestId?: string;
  correlationId?: string;
  userId?: string;
  sessionId?: string;
  operation?: string;
  component?: string;
  version?: string;
  environment?: string;
  traceId?: string;
  spanId?: string;
  parentSpanId?: string;
  tags?: Record<string, string>;
  metadata?: Record<string, any>;
}

export interface SecurityLogContext extends LogContext {
  sourceIp?: string;
  userAgent?: string;
  resource?: string;
  action?: string;
  outcome?: 'success' | 'failure' | 'denied';
  riskScore?: number;
  geolocation?: string;
  deviceFingerprint?: string;
}

export enum LogLevel {
  ERROR = 'error',
  WARN = 'warn',
  INFO = 'info',
  HTTP = 'http',
  DEBUG = 'debug',
  TRACE = 'trace'
}

export interface LoggerConfig {
  serviceName: string;
  version: string;
  environment: string;
  instanceId?: string;
  level?: LogLevel;
  console?: {
    enabled: boolean;
    colorize?: boolean;
  };
  file?: {
    enabled: boolean;
    path: string;
    maxSize?: number;
    maxFiles?: number;
    rotationPattern?: string;
  };
  http?: {
    enabled: boolean;
    host: string;
    port: number;
    path?: string;
    ssl?: boolean;
    headers?: Record<string, string>;
  };
  elasticsearch?: {
    enabled: boolean;
    host: string;
    port: number;
    index: string;
    auth?: {
      username: string;
      password: string;
    };
  };
}

export class ComprehensiveLogger {
  private winston: winston.Logger;
  private defaultContext: LogContext;
  private config: LoggerConfig;
  private sensitiveFields: Set<string>;

  constructor(config: LoggerConfig) {
    this.config = config;
    this.defaultContext = {
      service: config.serviceName,
      version: config.version,
      environment: config.environment,
      instance: config.instanceId || this.generateInstanceId()
    };

    this.sensitiveFields = new Set([
      'password', 'token', 'secret', 'apikey', 'authorization',
      'cookie', 'session', 'ssn', 'creditcard', 'cvv'
    ]);

    this.winston = winston.createLogger({
      level: config.level || LogLevel.INFO,
      format: this.createLogFormat(),
      transports: this.createTransports(config),
      defaultMeta: this.defaultContext,
      exitOnError: false
    });
  }

  private createLogFormat(): winston.Logform.Format {
    return winston.format.combine(
      winston.format.timestamp({
        format: 'YYYY-MM-DDTHH:mm:ss.SSSZ'
      }),
      winston.format.errors({ stack: true }),
      winston.format.json(),
      winston.format.printf((info) => {
        const log = {
          '@timestamp': info.timestamp,
          level: info.level,
          message: this.sanitizeMessage(info.message),
          service: {
            name: info.service,
            version: info.version,
            environment: info.environment,
            instance: info.instance
          },
          ...this.extractStructuredData(info)
        };

        // Add error details if present
        if (info.stack) {
          log.error = {
            name: info.name,
            message: this.sanitizeMessage(info.message),
            stack: info.stack,
            type: info.constructor?.name || 'Error'
          };
        }

        // Add tracing information if present
        if (info.traceId || info.spanId) {
          log.trace = {
            traceId: info.traceId,
            spanId: info.spanId,
            parentSpanId: info.parentSpanId
          };
        }

        return JSON.stringify(log);
      })
    );
  }

  private sanitizeMessage(message: string): string {
    if (!message) return message;
    
    // Remove sensitive data patterns
    let sanitized = message;
    
    // Common sensitive patterns
    sanitized = sanitized.replace(/password[=:]\s*[^\s,}]+/gi, 'password=***');
    sanitized = sanitized.replace(/token[=:]\s*[^\s,}]+/gi, 'token=***');
    sanitized = sanitized.replace(/api[_-]?key[=:]\s*[^\s,}]+/gi, 'apikey=***');
    sanitized = sanitized.replace(/authorization[=:]\s*[^\s,}]+/gi, 'authorization=***');
    
    // Credit card patterns
    sanitized = sanitized.replace(/\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g, '****-****-****-****');
    
    // SSN patterns
    sanitized = sanitized.replace(/\b\d{3}-\d{2}-\d{4}\b/g, '***-**-****');
    
    return sanitized;
  }

  private extractStructuredData(info: any): Record<string, any> {
    const excluded = [
      '@timestamp', 'timestamp', 'level', 'message', 'service', 'version', 
      'environment', 'instance', 'stack', 'name', 'traceId', 'spanId', 'parentSpanId'
    ];
    const structured: Record<string, any> = {};

    Object.keys(info).forEach(key => {
      if (!excluded.includes(key)) {
        structured[key] = this.sanitizeData(info[key]);
      }
    });

    return structured;
  }

  private sanitizeData(data: any): any {
    if (typeof data === 'string') {
      return this.sanitizeMessage(data);
    }
    
    if (Array.isArray(data)) {
      return data.map(item => this.sanitizeData(item));
    }
    
    if (data && typeof data === 'object') {
      const sanitized: any = {};
      Object.keys(data).forEach(key => {
        if (this.sensitiveFields.has(key.toLowerCase())) {
          sanitized[key] = '***';
        } else {
          sanitized[key] = this.sanitizeData(data[key]);
        }
      });
      return sanitized;
    }
    
    return data;
  }

  private createTransports(config: LoggerConfig): winston.transport[] {
    const transports: winston.transport[] = [];

    // Console transport
    if (config.console?.enabled) {
      transports.push(new winston.transports.Console({
        format: config.environment === 'development' && config.console.colorize ? 
          winston.format.combine(
            winston.format.colorize(),
            winston.format.simple()
          ) : 
          winston.format.json()
      }));
    }

    // File transport with rotation
    if (config.file?.enabled) {
      transports.push(new winston.transports.File({
        filename: config.file.path,
        maxsize: config.file.maxSize || 50 * 1024 * 1024, // 50MB
        maxFiles: config.file.maxFiles || 10,
        tailable: true
      }));
    }

    // HTTP transport for centralized logging
    if (config.http?.enabled) {
      transports.push(new winston.transports.Http({
        host: config.http.host,
        port: config.http.port,
        path: config.http.path || '/logs',
        ssl: config.http.ssl || false,
        headers: config.http.headers || {}
      }));
    }

    return transports;
  }

  private generateInstanceId(): string {
    return `${process.pid}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private enrichContext(context: LogContext = {}): LogContext {
    return {
      ...this.defaultContext,
      ...context,
      timestamp: new Date().toISOString()
    };
  }

  // Core logging methods
  error(message: string, context: LogContext = {}): void {
    this.winston.error(message, this.enrichContext(context));
  }

  warn(message: string, context: LogContext = {}): void {
    this.winston.warn(message, this.enrichContext(context));
  }

  info(message: string, context: LogContext = {}): void {
    this.winston.info(message, this.enrichContext(context));
  }

  http(message: string, context: LogContext = {}): void {
    this.winston.http(message, this.enrichContext(context));
  }

  debug(message: string, context: LogContext = {}): void {
    this.winston.debug(message, this.enrichContext(context));
  }

  trace(message: string, context: LogContext = {}): void {
    this.winston.log('trace', message, this.enrichContext(context));
  }

  // Specialized logging methods
  audit(action: string, resource: string, context: LogContext = {}): void {
    this.info(`Audit: ${action} on ${resource}`, {
      ...context,
      category: 'audit',
      audit: {
        action,
        resource,
        timestamp: new Date().toISOString()
      }
    });
  }

  security(event: string, severity: 'low' | 'medium' | 'high' | 'critical', context: SecurityLogContext = {}): void {
    this.error(`Security: ${event}`, {
      ...context,
      category: 'security',
      security: {
        event,
        severity,
        sourceIp: context.sourceIp,
        userAgent: context.userAgent,
        riskScore: context.riskScore,
        outcome: context.outcome,
        timestamp: new Date().toISOString()
      }
    });
  }

  performance(operation: string, durationMs: number, context: LogContext = {}): void {
    this.info(`Performance: ${operation} completed in ${durationMs}ms`, {
      ...context,
      category: 'performance',
      performance: {
        operation,
        duration: durationMs,
        threshold: context.metadata?.threshold || null,
        status: durationMs > (context.metadata?.threshold || 1000) ? 'slow' : 'normal'
      }
    });
  }

  business(event: string, data: Record<string, any>, context: LogContext = {}): void {
    this.info(`Business: ${event}`, {
      ...context,
      category: 'business',
      business: {
        event,
        data: this.sanitizeData(data),
        timestamp: new Date().toISOString()
      }
    });
  }
}

// Express Middleware Integration
export function loggingMiddleware(logger: ComprehensiveLogger) {
  return (req: Request, res: Response, next: NextFunction) => {
    const startTime = Date.now();
    const requestId = req.headers['x-request-id'] || generateRequestId();
    
    // Add request context to req object
    (req as any).logger = logger;
    (req as any).requestId = requestId;
    
    // Log incoming request
    logger.http('Incoming request', {
      requestId,
      method: req.method,
      url: req.url,
      userAgent: req.headers['user-agent'],
      sourceIp: req.ip || req.connection.remoteAddress,
      headers: sanitizeHeaders(req.headers)
    });
    
    res.on('finish', () => {
      const duration = Date.now() - startTime;
      
      logger.http('Request completed', {
        requestId,
        method: req.method,
        url: req.url,
        statusCode: res.statusCode,
        duration,
        responseSize: res.get('content-length') || 0
      });
    });
    
    next();
  };
}

function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function sanitizeHeaders(headers: any): any {
  const sanitized = { ...headers };
  const sensitiveHeaders = ['authorization', 'cookie', 'x-api-key', 'x-auth-token'];
  
  sensitiveHeaders.forEach(header => {
    if (sanitized[header]) {
      sanitized[header] = '***';
    }
  });
  
  return sanitized;
}
```

### 3. Security Event Monitoring & SIEM Integration

#### Security Observability Framework

**Security Monitoring Requirements:**
- **Event Classification**: Authentication, authorization, data access, system events
- **Real-time Alerting**: Critical security events trigger immediate alerts
- **SIEM Integration**: Centralized security information and event management
- **Compliance Logging**: Audit trail for regulatory requirements

**Security Event Categories:**
```yaml
# security-events-taxonomy.yaml
security_event_categories:
  authentication:
    events:
      - login_success
      - login_failure
      - password_changes
      - account_lockouts
      - session_creation
      - session_termination
      - multi_factor_authentication
      - password_reset_requests
    severity_mapping:
      login_failure: "medium"
      account_lockouts: "high"
      password_changes: "medium"
      session_termination: "low"
    
  authorization:
    events:
      - permission_grants
      - permission_denials
      - privilege_escalations
      - role_changes
      - resource_access_attempts
      - admin_access_granted
    severity_mapping:
      permission_denials: "medium"
      privilege_escalations: "critical"
      admin_access_granted: "high"
    
  data_access:
    events:
      - sensitive_data_access
      - data_modifications
      - bulk_data_downloads
      - unauthorized_access_attempts
      - data_exports
      - pii_access
    severity_mapping:
      bulk_data_downloads: "high"
      unauthorized_access_attempts: "critical"
      pii_access: "high"
    
  system_events:
    events:
      - configuration_changes
      - security_policy_modifications
      - service_starts_stops
      - file_integrity_violations
      - network_anomalies
      - resource_exhaustion
    severity_mapping:
      security_policy_modifications: "critical"
      file_integrity_violations: "high"
      configuration_changes: "medium"

alerting_rules:
  authentication_anomalies:
    multiple_failed_logins:
      threshold: 5
      timeframe: "5m"
      severity: "medium"
      action: "alert_security_team"
    
    impossible_travel:
      distance_threshold: "500km"
      timeframe: "1h"
      severity: "high"
      action: "immediate_investigation"
    
    brute_force_detection:
      threshold: 20
      timeframe: "10m"
      severity: "high"
      action: "auto_block_ip"
  
  data_access_anomalies:
    bulk_download:
      threshold: "100MB"
      timeframe: "10m"
      severity: "high"
      action: "alert_data_owner"
    
    off_hours_access:
      time_range: "22:00-06:00"
      sensitivity: "confidential"
      severity: "medium"
      action: "log_and_monitor"
    
    unusual_data_volume:
      threshold_multiplier: 5  # 5x normal volume
      baseline_period: "7d"
      severity: "medium"
      action: "alert_security_team"

  privilege_escalation:
    admin_access_granted:
      alerting: "immediate"
      severity: "critical"
      action: "immediate_investigation"
    
    sudo_usage:
      user_whitelist: ["devops", "admin", "sre"]
      severity: "medium"
      action: "log_and_review"
    
    service_account_usage:
      expected_sources: ["ci_cd", "automation"]
      severity: "high"
      action: "verify_legitimacy"
```

**Security Monitoring Implementation:**
```typescript
// src/security/security-monitor.ts
import { ComprehensiveLogger, SecurityLogContext } from '../logging/comprehensive-logger';
import { ComprehensiveMetricsCollector } from '../monitoring/metrics-collector';

export interface SecurityEvent {
  eventType: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  userId?: string;
  sourceIp?: string;
  userAgent?: string;
  resource?: string;
  action?: string;
  outcome: 'success' | 'failure' | 'denied';
  riskScore?: number;
  metadata?: Record<string, any>;
}

export interface SecurityAlertRule {
  name: string;
  condition: (events: SecurityEvent[]) => boolean;
  threshold?: number;
  timeframe?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  action: string;
}

export class SecurityMonitor {
  private logger: ComprehensiveLogger;
  private metrics: ComprehensiveMetricsCollector;
  private eventBuffer: SecurityEvent[] = [];
  private alertRules: SecurityAlertRule[] = [];
  private alertHandlers: Map<string, (event: SecurityEvent) => void> = new Map();

  constructor(logger: ComprehensiveLogger, metrics: ComprehensiveMetricsCollector) {
    this.logger = logger;
    this.metrics = metrics;
    this.setupDefaultAlertRules();
    this.setupDefaultAlertHandlers();
  }

  private setupDefaultAlertRules(): void {
    this.alertRules = [
      {
        name: 'multiple_failed_logins',
        condition: (events) => {
          const recentFailures = events.filter(e => 
            e.eventType === 'login_failure' && 
            Date.now() - new Date(e.metadata?.timestamp || 0).getTime() < 5 * 60 * 1000 // 5 minutes
          );
          return recentFailures.length >= 5;
        },
        threshold: 5,
        timeframe: '5m',
        severity: 'medium',
        action: 'alert_security_team'
      },
      {
        name: 'privilege_escalation',
        condition: (events) => {
          return events.some(e => e.eventType === 'privilege_escalation');
        },
        severity: 'critical',
        action: 'immediate_investigation'
      },
      {
        name: 'bulk_data_access',
        condition: (events) => {
          const bulkAccess = events.filter(e => 
            e.eventType === 'data_access' && 
            (e.metadata?.dataVolume || 0) > 100 * 1024 * 1024 // 100MB
          );
          return bulkAccess.length > 0;
        },
        severity: 'high',
        action: 'alert_data_owner'
      }
    ];
  }

  private setupDefaultAlertHandlers(): void {
    this.alertHandlers.set('alert_security_team', (event) => {
      this.logger.security(`Security Alert: ${event.eventType}`, 'high', {
        userId: event.userId,
        sourceIp: event.sourceIp,
        resource: event.resource,
        action: event.action,
        outcome: event.outcome,
        riskScore: event.riskScore,
        metadata: { alertAction: 'security_team_notified', ...event.metadata }
      });
    });

    this.alertHandlers.set('immediate_investigation', (event) => {
      this.logger.security(`CRITICAL Security Event: ${event.eventType}`, 'critical', {
        userId: event.userId,
        sourceIp: event.sourceIp,
        resource: event.resource,
        action: event.action,
        outcome: event.outcome,
        riskScore: event.riskScore,
        metadata: { alertAction: 'immediate_investigation_required', ...event.metadata }
      });
    });

    this.alertHandlers.set('alert_data_owner', (event) => {
      this.logger.security(`Data Access Alert: ${event.eventType}`, 'high', {
        userId: event.userId,
        sourceIp: event.sourceIp,
        resource: event.resource,
        metadata: { alertAction: 'data_owner_notified', ...event.metadata }
      });
    });
  }

  recordSecurityEvent(event: SecurityEvent): void {
    // Add timestamp if not present
    if (!event.metadata?.timestamp) {
      event.metadata = { ...event.metadata, timestamp: new Date().toISOString() };
    }

    // Record metrics
    this.metrics.recordSecurityEvent(event.eventType, event.severity, event.source, event.metadata);

    // Log the event
    this.logger.security(`Security Event: ${event.eventType}`, event.severity, {
      userId: event.userId,
      sourceIp: event.sourceIp,
      userAgent: event.userAgent,
      resource: event.resource,
      action: event.action,
      outcome: event.outcome,
      riskScore: event.riskScore,
      metadata: event.metadata
    });

    // Add to event buffer
    this.eventBuffer.push(event);
    
    // Clean old events (keep last 1000 or events from last hour)
    const oneHourAgo = Date.now() - 60 * 60 * 1000;
    this.eventBuffer = this.eventBuffer
      .filter(e => new Date(e.metadata?.timestamp || 0).getTime() > oneHourAgo)
      .slice(-1000);

    // Check alert rules
    this.checkAlertRules(event);
  }

  private checkAlertRules(triggerEvent: SecurityEvent): void {
    for (const rule of this.alertRules) {
      if (rule.condition(this.eventBuffer)) {
        const handler = this.alertHandlers.get(rule.action);
        if (handler) {
          handler(triggerEvent);
        }
      }
    }
  }

  // Convenience methods for common security events
  recordAuthenticationEvent(outcome: 'success' | 'failure', userId: string, sourceIp: string, userAgent?: string, metadata?: any): void {
    const eventType = outcome === 'success' ? 'login_success' : 'login_failure';
    const severity = outcome === 'failure' ? 'medium' : 'low';
    
    this.recordSecurityEvent({
      eventType,
      severity,
      source: 'authentication_service',
      userId,
      sourceIp,
      userAgent,
      outcome,
      riskScore: outcome === 'failure' ? 5 : 1,
      metadata
    });

    // Record authentication metrics
    this.metrics.recordAuthenticationAttempt(outcome, 'password', sourceIp, userAgent || 'unknown');
  }

  recordAuthorizationEvent(outcome: 'success' | 'denied', userId: string, resource: string, action: string, sourceIp?: string, metadata?: any): void {
    const severity = outcome === 'denied' ? 'medium' : 'low';
    
    this.recordSecurityEvent({
      eventType: 'authorization_check',
      severity,
      source: 'authorization_service',
      userId,
      sourceIp,
      resource,
      action,
      outcome,
      riskScore: outcome === 'denied' ? 3 : 1,
      metadata
    });

    // Record authorization metrics
    if (outcome === 'denied') {
      this.metrics.recordAuthorizationFailure(resource, action, userId, metadata?.reason || 'unknown');
    }
  }

  recordDataAccessEvent(userId: string, resource: string, action: string, dataVolume?: number, sourceIp?: string, metadata?: any): void {
    const severity = dataVolume && dataVolume > 100 * 1024 * 1024 ? 'high' : 'low'; // 100MB threshold
    
    this.recordSecurityEvent({
      eventType: 'data_access',
      severity,
      source: 'data_service',
      userId,
      sourceIp,
      resource,
      action,
      outcome: 'success',
      riskScore: severity === 'high' ? 7 : 2,
      metadata: { dataVolume, ...metadata }
    });
  }
}
```

### 4. SLI/SLO Framework & Error Budget Management

#### Service Level Management

**SLI/SLO Configuration:**
```yaml
# sli-slo-configuration.yaml
service_level_objectives:
  api_service:
    availability:
      sli: "http_requests_total{status_code!~'5..'} / http_requests_total"
      slo: 99.9  # 99.9% availability
      error_budget: 0.1  # 0.1% error budget
      measurement_window: "30d"
      alerting_threshold: 0.05  # Alert when 50% of error budget consumed
      
    latency:
      sli: "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
      slo: 0.5  # 95th percentile < 500ms
      measurement_window: "30d"
      alerting_threshold: 0.4  # Alert when latency > 400ms
      
    throughput:
      sli: "rate(http_requests_total[5m])"
      slo: 1000  # Minimum 1000 RPS
      measurement_window: "24h"
      alerting_threshold: 800  # Alert when throughput < 800 RPS

  worker_service:
    processing_success:
      sli: "job_success_total / job_total"
      slo: 99.5  # 99.5% job success rate
      error_budget: 0.5
      measurement_window: "30d"
      
    processing_latency:
      sli: "histogram_quantile(0.90, job_duration_seconds_bucket)"
      slo: 300  # 90th percentile < 5 minutes
      measurement_window: "7d"

alerting_rules:
  slo_burn_rate:
    fast_burn:
      lookback_window: "1h"
      burn_rate_threshold: 14.4  # Burns through error budget in 2 days
      severity: "critical"
      
    slow_burn:
      lookback_window: "6h"  
      burn_rate_threshold: 6  # Burns through error budget in 5 days
      severity: "warning"
```

### 5. Distributed Tracing & APM Integration

#### Application Performance Monitoring

**OpenTelemetry Integration:**
```typescript
// src/tracing/distributed-tracing.ts
import { NodeSDK } from '@opentelemetry/sdk-node';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { JaegerExporter } from '@opentelemetry/exporter-jaeger';
import { PrometheusExporter } from '@opentelemetry/exporter-prometheus';

export class DistributedTracing {
  private sdk: NodeSDK;

  constructor(config: TracingConfig) {
    this.sdk = new NodeSDK({
      resource: new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: config.serviceName,
        [SemanticResourceAttributes.SERVICE_VERSION]: config.version,
        [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: config.environment,
      }),
      traceExporter: new JaegerExporter({
        endpoint: config.jaegerEndpoint,
      }),
      metricReader: new PrometheusExporter({
        port: config.metricsPort || 9090,
      }),
    });
  }

  start(): void {
    this.sdk.start();
  }

  shutdown(): Promise<void> {
    return this.sdk.shutdown();
  }
}
```

## Implementation Requirements

### 1. Infrastructure & Deployment

```yaml
# monitoring-infrastructure.yaml
monitoring_stack:
  metrics:
    prometheus:
      retention: "30d"
      scrape_interval: "15s"
      evaluation_interval: "15s"
      external_labels:
        cluster: "production"
        region: "us-west-2"
    
    grafana:
      dashboards:
        - "RED metrics dashboard"
        - "USE metrics dashboard"
        - "SLI/SLO dashboard"
        - "Security events dashboard"
      
  logging:
    elasticsearch:
      retention: "90d"
      shards: 3
      replicas: 1
      index_template: "logs-*"
    
    kibana:
      dashboards:
        - "Application logs"
        - "Security events"
        - "Performance analytics"
    
  alerting:
    alertmanager:
      routing:
        group_by: ['alertname', 'cluster', 'service']
        group_wait: "10s"
        group_interval: "10s"
        repeat_interval: "1h"
      
      receivers:
        - name: "security-team"
          slack_configs:
            - channel: "#security-alerts"
              title: "Security Alert"
        - name: "sre-team"
          pagerduty_configs:
            - service_key: "sre-service-key"

deployment_requirements:
  high_availability: true
  backup_strategy: "daily"
  disaster_recovery: "cross_region"
  monitoring_monitoring: true  # Monitor the monitoring system
```

## Quality Standards & Success Metrics

### Observability Excellence Checklist
- ✅ **100% service metrics coverage** (RED/USE methodologies)
- ✅ **Structured logging** with consistent JSON schema
- ✅ **Security event monitoring** with real-time alerting
- ✅ **SLI/SLO tracking** with error budget management
- ✅ **Distributed tracing** for request flow visibility
- ✅ **SIEM integration** for security compliance
- ✅ **Automated alerting** with intelligent routing
- ✅ **Dashboard standardization** across all services

### Performance & Reliability Targets
- **Metrics Collection Latency**: < 15 seconds
- **Log Processing Latency**: < 30 seconds  
- **Alert Response Time**: < 5 minutes
- **Dashboard Load Time**: < 3 seconds
- **Monitoring System Availability**: 99.95%
- **Data Retention Compliance**: 100%
- **Security Event Detection Rate**: 99%

This comprehensive monitoring and observability rule consolidates metrics collection, structured logging, and security monitoring into unified guidance for building observable, secure, and reliable systems with complete visibility into application behavior and security posture.
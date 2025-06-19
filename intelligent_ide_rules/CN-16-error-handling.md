---
description: "Universal error handling: error types, error propagation, error recovery. Comprehensive error management and resilience patterns."
globs: ["**/*"]
alwaysApply: true
---

# 🚨 Universal Error Handling

## 1. Error Classification & Types

### Error Handling Requirements
- **DEFINE:** Clear error hierarchies and error types
- **IMPLEMENT:** Consistent error propagation and recovery
- **PROVIDE:** Rich error context and debugging information
- **ENSURE:** Graceful degradation and user-friendly error messages

### Error Type Hierarchy
```typescript
// src/errors/base-error.ts
export abstract class BaseError extends Error {
  abstract readonly name: string;
  abstract readonly statusCode: number;
  abstract readonly severity: ErrorSeverity;
  readonly isOperational: boolean = true;
  readonly timestamp: Date;
  readonly correlationId: string;
  readonly context: Record<string, any>;

  constructor(
    message: string,
    context: Record<string, any> = {},
    correlationId?: string
  ) {
    super(message);
    this.timestamp = new Date();
    this.correlationId = correlationId || this.generateCorrelationId();
    this.context = context;
    
    // Maintains proper stack trace for V8
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }

  private generateCorrelationId(): string {
    return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  toJSON(): ErrorJSON {
    return {
      name: this.name,
      message: this.message,
      statusCode: this.statusCode,
      severity: this.severity,
      timestamp: this.timestamp.toISOString(),
      correlationId: this.correlationId,
      context: this.context,
      stack: this.stack
    };
  }

  toPublicJSON(): PublicErrorJSON {
    return {
      name: this.name,
      message: this.getPublicMessage(),
      statusCode: this.statusCode,
      correlationId: this.correlationId,
      timestamp: this.timestamp.toISOString()
    };
  }

  protected getPublicMessage(): string {
    return this.message;
  }
}

export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export interface ErrorJSON {
  name: string;
  message: string;
  statusCode: number;
  severity: ErrorSeverity;
  timestamp: string;
  correlationId: string;
  context: Record<string, any>;
  stack?: string;
}

export interface PublicErrorJSON {
  name: string;
  message: string;
  statusCode: number;
  correlationId: string;
  timestamp: string;
}
```

### Business Logic Errors
```typescript
// src/errors/business-errors.ts
export class ValidationError extends BaseError {
  readonly name = 'ValidationError';
  readonly statusCode = 400;
  readonly severity = ErrorSeverity.LOW;

  constructor(
    field: string,
    value: any,
    constraint: string,
    context: Record<string, any> = {}
  ) {
    const message = `Validation failed for field '${field}': ${constraint}`;
    super(message, { field, value, constraint, ...context });
  }
}

export class BusinessRuleError extends BaseError {
  readonly name = 'BusinessRuleError';
  readonly statusCode = 422;
  readonly severity = ErrorSeverity.MEDIUM;

  constructor(
    rule: string,
    message: string,
    context: Record<string, any> = {}
  ) {
    super(message, { rule, ...context });
  }
}

export class ConflictError extends BaseError {
  readonly name = 'ConflictError';
  readonly statusCode = 409;
  readonly severity = ErrorSeverity.MEDIUM;

  constructor(
    resource: string,
    identifier: string,
    context: Record<string, any> = {}
  ) {
    const message = `Conflict: ${resource} with identifier '${identifier}' already exists`;
    super(message, { resource, identifier, ...context });
  }
}

export class NotFoundError extends BaseError {
  readonly name = 'NotFoundError';
  readonly statusCode = 404;
  readonly severity = ErrorSeverity.LOW;

  constructor(
    resource: string,
    identifier: string,
    context: Record<string, any> = {}
  ) {
    const message = `${resource} with identifier '${identifier}' not found`;
    super(message, { resource, identifier, ...context });
  }

  protected getPublicMessage(): string {
    return `${this.context.resource} not found`;
  }
}
```

### Technical Errors
```typescript
// src/errors/technical-errors.ts
export class DatabaseError extends BaseError {
  readonly name = 'DatabaseError';
  readonly statusCode = 500;
  readonly severity = ErrorSeverity.HIGH;

  constructor(
    operation: string,
    originalError: Error,
    context: Record<string, any> = {}
  ) {
    const message = `Database operation '${operation}' failed: ${originalError.message}`;
    super(message, { operation, originalError: originalError.message, ...context });
  }

  protected getPublicMessage(): string {
    return 'A database error occurred. Please try again later.';
  }
}

export class ExternalServiceError extends BaseError {
  readonly name = 'ExternalServiceError';
  readonly statusCode = 502;
  readonly severity = ErrorSeverity.HIGH;

  constructor(
    service: string,
    operation: string,
    statusCode: number,
    context: Record<string, any> = {}
  ) {
    const message = `External service '${service}' failed during '${operation}' with status ${statusCode}`;
    super(message, { service, operation, externalStatusCode: statusCode, ...context });
  }

  protected getPublicMessage(): string {
    return `Service temporarily unavailable. Please try again later.`;
  }
}

export class TimeoutError extends BaseError {
  readonly name = 'TimeoutError';
  readonly statusCode = 408;
  readonly severity = ErrorSeverity.MEDIUM;

  constructor(
    operation: string,
    timeoutMs: number,
    context: Record<string, any> = {}
  ) {
    const message = `Operation '${operation}' timed out after ${timeoutMs}ms`;
    super(message, { operation, timeoutMs, ...context });
  }
}

export class RateLimitError extends BaseError {
  readonly name = 'RateLimitError';
  readonly statusCode = 429;
  readonly severity = ErrorSeverity.MEDIUM;

  constructor(
    limit: number,
    windowMs: number,
    context: Record<string, any> = {}
  ) {
    const message = `Rate limit exceeded: ${limit} requests per ${windowMs}ms`;
    super(message, { limit, windowMs, ...context });
  }
}
```

### Authorization Errors
```typescript
// src/errors/auth-errors.ts
export class AuthenticationError extends BaseError {
  readonly name = 'AuthenticationError';
  readonly statusCode = 401;
  readonly severity = ErrorSeverity.MEDIUM;

  constructor(
    reason: string,
    context: Record<string, any> = {}
  ) {
    super(`Authentication failed: ${reason}`, context);
  }

  protected getPublicMessage(): string {
    return 'Authentication required. Please log in.';
  }
}

export class AuthorizationError extends BaseError {
  readonly name = 'AuthorizationError';
  readonly statusCode = 403;
  readonly severity = ErrorSeverity.MEDIUM;

  constructor(
    resource: string,
    action: string,
    context: Record<string, any> = {}
  ) {
    const message = `Access denied: insufficient permissions for '${action}' on '${resource}'`;
    super(message, { resource, action, ...context });
  }

  protected getPublicMessage(): string {
    return 'Access denied. You do not have permission to perform this action.';
  }
}

export class TokenExpiredError extends BaseError {
  readonly name = 'TokenExpiredError';
  readonly statusCode = 401;
  readonly severity = ErrorSeverity.LOW;

  constructor(
    tokenType: string,
    expiredAt: Date,
    context: Record<string, any> = {}
  ) {
    const message = `${tokenType} token expired at ${expiredAt.toISOString()}`;
    super(message, { tokenType, expiredAt: expiredAt.toISOString(), ...context });
  }

  protected getPublicMessage(): string {
    return 'Your session has expired. Please log in again.';
  }
}
```

## 2. Error Propagation & Context

### Error Context Enrichment
```typescript
// src/errors/error-context.ts
export class ErrorContext {
  private static context: Map<string, any> = new Map();

  static setContext(key: string, value: any): void {
    this.context.set(key, value);
  }

  static getContext(): Record<string, any> {
    return Object.fromEntries(this.context);
  }

  static clearContext(): void {
    this.context.clear();
  }

  static withContext<T>(
    contextData: Record<string, any>,
    fn: () => T
  ): T {
    const originalContext = new Map(this.context);
    
    try {
      // Add new context
      Object.entries(contextData).forEach(([key, value]) => {
        this.context.set(key, value);
      });
      
      return fn();
    } finally {
      // Restore original context
      this.context = originalContext;
    }
  }

  static enhanceError(error: Error): Error {
    if (error instanceof BaseError) {
      // Add current context to existing error context
      const currentContext = this.getContext();
      Object.assign(error.context, currentContext);
    }
    
    return error;
  }
}

// Middleware for adding request context
export function addRequestContext(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  const requestContext = {
    requestId: req.headers['x-request-id'] || generateRequestId(),
    userId: req.user?.id,
    ip: req.ip,
    userAgent: req.headers['user-agent'],
    method: req.method,
    url: req.url,
    timestamp: new Date().toISOString()
  };

  ErrorContext.withContext(requestContext, () => {
    next();
  });
}
```

### Error Propagation Patterns
```typescript
// src/patterns/error-propagation.ts
export class ErrorPropagator {
  static async wrapAsync<T>(
    operation: () => Promise<T>,
    errorMapper?: (error: Error) => BaseError
  ): Promise<T> {
    try {
      return await operation();
    } catch (error) {
      const enhancedError = ErrorContext.enhanceError(error);
      
      if (errorMapper && !(error instanceof BaseError)) {
        throw errorMapper(enhancedError);
      }
      
      throw enhancedError;
    }
  }

  static wrapSync<T>(
    operation: () => T,
    errorMapper?: (error: Error) => BaseError
  ): T {
    try {
      return operation();
    } catch (error) {
      const enhancedError = ErrorContext.enhanceError(error);
      
      if (errorMapper && !(error instanceof BaseError)) {
        throw errorMapper(enhancedError);
      }
      
      throw enhancedError;
    }
  }

  static async retryWithBackoff<T>(
    operation: () => Promise<T>,
    options: RetryOptions = {}
  ): Promise<T> {
    const {
      maxRetries = 3,
      baseDelayMs = 1000,
      maxDelayMs = 10000,
      backoffMultiplier = 2,
      retryableErrors = [TimeoutError, ExternalServiceError]
    } = options;

    let lastError: Error;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error;
        
        // Check if error is retryable
        const isRetryable = retryableErrors.some(ErrorClass => 
          error instanceof ErrorClass
        );
        
        if (!isRetryable || attempt === maxRetries) {
          throw error;
        }
        
        // Calculate delay with exponential backoff
        const delay = Math.min(
          baseDelayMs * Math.pow(backoffMultiplier, attempt - 1),
          maxDelayMs
        );
        
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    throw lastError!;
  }
}

export interface RetryOptions {
  maxRetries?: number;
  baseDelayMs?: number;
  maxDelayMs?: number;
  backoffMultiplier?: number;
  retryableErrors?: Array<new (...args: any[]) => BaseError>;
}
```

## 3. Error Recovery & Resilience

### Circuit Breaker Pattern
```typescript
// src/resilience/circuit-breaker.ts
export enum CircuitState {
  CLOSED = 'closed',
  OPEN = 'open',
  HALF_OPEN = 'half-open'
}

export class CircuitBreaker<T> {
  private state: CircuitState = CircuitState.CLOSED;
  private failureCount: number = 0;
  private successCount: number = 0;
  private lastFailureTime: number = 0;
  private nextAttemptTime: number = 0;

  constructor(
    private options: CircuitBreakerOptions
  ) {}

  async execute(operation: () => Promise<T>): Promise<T> {
    if (this.state === CircuitState.OPEN) {
      if (Date.now() < this.nextAttemptTime) {
        throw new CircuitBreakerOpenError(
          this.options.name,
          this.nextAttemptTime - Date.now()
        );
      }
      
      // Transition to half-open
      this.state = CircuitState.HALF_OPEN;
      this.successCount = 0;
    }

    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure(error);
      throw error;
    }
  }

  private onSuccess(): void {
    this.failureCount = 0;
    
    if (this.state === CircuitState.HALF_OPEN) {
      this.successCount++;
      
      if (this.successCount >= this.options.successThreshold) {
        this.state = CircuitState.CLOSED;
      }
    }
  }

  private onFailure(error: Error): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    
    if (this.failureCount >= this.options.failureThreshold) {
      this.state = CircuitState.OPEN;
      this.nextAttemptTime = Date.now() + this.options.timeoutMs;
    }
  }

  getState(): CircuitBreakerState {
    return {
      state: this.state,
      failureCount: this.failureCount,
      successCount: this.successCount,
      nextAttemptTime: this.nextAttemptTime
    };
  }
}

export interface CircuitBreakerOptions {
  name: string;
  failureThreshold: number;
  successThreshold: number;
  timeoutMs: number;
}

export interface CircuitBreakerState {
  state: CircuitState;
  failureCount: number;
  successCount: number;
  nextAttemptTime: number;
}

export class CircuitBreakerOpenError extends BaseError {
  readonly name = 'CircuitBreakerOpenError';
  readonly statusCode = 503;
  readonly severity = ErrorSeverity.HIGH;

  constructor(
    circuitName: string,
    retryAfterMs: number,
    context: Record<string, any> = {}
  ) {
    const message = `Circuit breaker '${circuitName}' is open. Retry after ${retryAfterMs}ms`;
    super(message, { circuitName, retryAfterMs, ...context });
  }
}
```

### Fallback Patterns
```typescript
// src/resilience/fallback.ts
export class FallbackHandler<T> {
  private fallbacks: Array<() => Promise<T>> = [];

  constructor(
    private primaryOperation: () => Promise<T>
  ) {}

  addFallback(fallback: () => Promise<T>): this {
    this.fallbacks.push(fallback);
    return this;
  }

  async execute(): Promise<T> {
    const operations = [this.primaryOperation, ...this.fallbacks];
    let lastError: Error;

    for (let i = 0; i < operations.length; i++) {
      try {
        const result = await operations[i]();
        
        if (i > 0) {
          // Log fallback usage
          console.warn(`Fallback ${i} used successfully`, {
            operation: 'fallback_executed',
            fallbackIndex: i,
            lastError: lastError?.message
          });
        }
        
        return result;
      } catch (error) {
        lastError = error;
        
        if (i === operations.length - 1) {
          // All operations failed
          throw new FallbackExhaustedError(
            operations.length,
            lastError,
            { attempts: operations.length }
          );
        }
      }
    }

    throw lastError!;
  }
}

export class FallbackExhaustedError extends BaseError {
  readonly name = 'FallbackExhaustedError';
  readonly statusCode = 503;
  readonly severity = ErrorSeverity.HIGH;

  constructor(
    attemptCount: number,
    lastError: Error,
    context: Record<string, any> = {}
  ) {
    const message = `All ${attemptCount} fallback attempts failed. Last error: ${lastError.message}`;
    super(message, { attemptCount, lastError: lastError.message, ...context });
  }
}
```

## 4. Error Monitoring & Alerting

### Error Tracking
```typescript
// src/monitoring/error-tracker.ts
export class ErrorTracker {
  private errorCounts: Map<string, number> = new Map();
  private errorWindows: Map<string, number[]> = new Map();

  constructor(
    private options: ErrorTrackerOptions
  ) {}

  trackError(error: BaseError): void {
    const errorKey = this.getErrorKey(error);
    const now = Date.now();

    // Increment error count
    this.errorCounts.set(errorKey, (this.errorCounts.get(errorKey) || 0) + 1);

    // Add to time window
    const window = this.errorWindows.get(errorKey) || [];
    window.push(now);
    
    // Remove old entries outside the window
    const cutoff = now - this.options.windowMs;
    const recentErrors = window.filter(timestamp => timestamp > cutoff);
    this.errorWindows.set(errorKey, recentErrors);

    // Check for threshold breaches
    this.checkThresholds(errorKey, recentErrors.length, error);

    // Report to external systems
    this.reportError(error, {
      count: this.errorCounts.get(errorKey),
      recentCount: recentErrors.length
    });
  }

  private getErrorKey(error: BaseError): string {
    return `${error.name}:${error.severity}`;
  }

  private checkThresholds(
    errorKey: string,
    recentCount: number,
    error: BaseError
  ): void {
    const threshold = this.getThreshold(error.severity);
    
    if (recentCount >= threshold) {
      this.sendAlert({
        errorKey,
        count: recentCount,
        threshold,
        severity: error.severity,
        windowMs: this.options.windowMs,
        latestError: error
      });
    }
  }

  private getThreshold(severity: ErrorSeverity): number {
    switch (severity) {
      case ErrorSeverity.CRITICAL:
        return 1;
      case ErrorSeverity.HIGH:
        return 5;
      case ErrorSeverity.MEDIUM:
        return 20;
      case ErrorSeverity.LOW:
        return 50;
      default:
        return 100;
    }
  }

  private async reportError(
    error: BaseError,
    metadata: { count?: number; recentCount?: number }
  ): Promise<void> {
    // Report to APM systems
    if (this.options.apmClient) {
      this.options.apmClient.captureError(error, {
        custom: {
          ...error.context,
          ...metadata
        }
      });
    }

    // Report to logging system
    if (this.options.logger) {
      this.options.logger.error('Error tracked', {
        error: error.toJSON(),
        metadata
      });
    }
  }

  private async sendAlert(alert: ErrorAlert): Promise<void> {
    if (this.options.alertingClient) {
      await this.options.alertingClient.sendAlert({
        title: `Error threshold breached: ${alert.errorKey}`,
        message: `${alert.count} errors in ${alert.windowMs}ms (threshold: ${alert.threshold})`,
        severity: alert.severity,
        metadata: {
          errorKey: alert.errorKey,
          count: alert.count,
          threshold: alert.threshold,
          latestError: alert.latestError.toJSON()
        }
      });
    }
  }
}

export interface ErrorTrackerOptions {
  windowMs: number;
  apmClient?: APMClient;
  logger?: Logger;
  alertingClient?: AlertingClient;
}

export interface ErrorAlert {
  errorKey: string;
  count: number;
  threshold: number;
  severity: ErrorSeverity;
  windowMs: number;
  latestError: BaseError;
}
```

## 5. Error Handling Middleware

### Express Error Middleware
```typescript
// src/middleware/error-handler.ts
export function errorHandler(
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
): void {
  // Enhance error with request context
  const enhancedError = ErrorContext.enhanceError(error);
  
  // Track error for monitoring
  if (enhancedError instanceof BaseError) {
    errorTracker.trackError(enhancedError);
  }

  // Log error details
  logger.error('Request error', {
    error: enhancedError instanceof BaseError ? 
      enhancedError.toJSON() : 
      { name: error.name, message: error.message, stack: error.stack },
    request: {
      method: req.method,
      url: req.url,
      headers: sanitizeHeaders(req.headers),
      body: sanitizeBody(req.body)
    }
  });

  // Send appropriate response
  if (enhancedError instanceof BaseError) {
    res.status(enhancedError.statusCode).json({
      error: enhancedError.toPublicJSON()
    });
  } else {
    // Unknown error - don't expose details
    res.status(500).json({
      error: {
        name: 'InternalServerError',
        message: 'An unexpected error occurred',
        statusCode: 500,
        correlationId: generateCorrelationId(),
        timestamp: new Date().toISOString()
      }
    });
  }
}

function sanitizeHeaders(headers: any): any {
  const sensitiveHeaders = ['authorization', 'cookie', 'x-api-key'];
  const sanitized = { ...headers };
  
  sensitiveHeaders.forEach(header => {
    if (sanitized[header]) {
      sanitized[header] = '[REDACTED]';
    }
  });
  
  return sanitized;
}

function sanitizeBody(body: any): any {
  if (!body || typeof body !== 'object') {
    return body;
  }
  
  const sensitiveFields = ['password', 'token', 'secret', 'key'];
  const sanitized = { ...body };
  
  sensitiveFields.forEach(field => {
    if (sanitized[field]) {
      sanitized[field] = '[REDACTED]';
    }
  });
  
  return sanitized;
}
```

## 6. Testing Error Scenarios

### Error Testing Utilities
```typescript
// tests/utils/error-testing.ts
export class ErrorTestingUtils {
  static expectErrorType<T extends BaseError>(
    errorClass: new (...args: any[]) => T
  ) {
    return {
      toBeThrown: async (operation: () => Promise<any>) => {
        try {
          await operation();
          throw new Error(`Expected ${errorClass.name} to be thrown`);
        } catch (error) {
          expect(error).toBeInstanceOf(errorClass);
          return error as T;
        }
      },
      
      toBeThrownSync: (operation: () => any) => {
        try {
          operation();
          throw new Error(`Expected ${errorClass.name} to be thrown`);
        } catch (error) {
          expect(error).toBeInstanceOf(errorClass);
          return error as T;
        }
      }
    };
  }

  static expectErrorWithContext(
    expectedContext: Record<string, any>
  ) {
    return {
      toBeThrown: async (operation: () => Promise<any>) => {
        try {
          await operation();
          throw new Error('Expected error to be thrown');
        } catch (error) {
          expect(error).toBeInstanceOf(BaseError);
          const baseError = error as BaseError;
          
          Object.entries(expectedContext).forEach(([key, value]) => {
            expect(baseError.context[key]).toEqual(value);
          });
          
          return baseError;
        }
      }
    };
  }

  static createMockError(
    errorClass: new (...args: any[]) => BaseError,
    ...args: any[]
  ): BaseError {
    return new errorClass(...args);
  }

  static simulateErrorScenarios<T>(
    scenarios: ErrorScenario<T>[]
  ): Array<{ scenario: string; test: () => Promise<void> }> {
    return scenarios.map(scenario => ({
      scenario: scenario.description,
      test: async () => {
        const error = await ErrorTestingUtils.expectErrorType(scenario.errorClass)
          .toBeThrown(scenario.operation);
        
        if (scenario.expectedContext) {
          Object.entries(scenario.expectedContext).forEach(([key, value]) => {
            expect(error.context[key]).toEqual(value);
          });
        }
        
        if (scenario.expectedStatusCode) {
          expect(error.statusCode).toBe(scenario.expectedStatusCode);
        }
      }
    }));
  }
}

export interface ErrorScenario<T> {
  description: string;
  errorClass: new (...args: any[]) => BaseError;
  operation: () => Promise<T>;
  expectedContext?: Record<string, any>;
  expectedStatusCode?: number;
}
```

## 7. Enforcement & Validation

### Error Handling Lint Rules
```typescript
// .eslintrc.js - Custom rules for error handling
module.exports = {
  rules: {
    // Require proper error handling in async functions
    '@typescript-eslint/promise-function-async': 'error',
    '@typescript-eslint/await-thenable': 'error',
    
    // Require error types to extend BaseError
    'custom/require-base-error': 'error',
    
    // Require error context in error constructors
    'custom/require-error-context': 'warn',
    
    // Prevent generic Error throwing
    'custom/no-generic-error': 'error'
  }
};
```

### Metrics & SLIs
```yaml
# Error handling metrics configuration
error_handling_metrics:
  error_rate:
    description: "Percentage of requests resulting in errors"
    query: "sum(rate(http_requests_total{status=~'4..|5..'}[5m])) / sum(rate(http_requests_total[5m])) * 100"
    threshold: 1.0  # 1% error rate
    severity: "high"

  error_response_time:
    description: "Time to return error responses"
    query: "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{status=~'4..|5..'}[5m]))"
    threshold: 0.5  # 500ms
    severity: "medium"

  unhandled_errors:
    description: "Count of unhandled errors"
    query: "sum(rate(unhandled_errors_total[5m]))"
    threshold: 0  # Zero tolerance
    severity: "critical"

  error_recovery_time:
    description: "Time to recover from errors"
    query: "histogram_quantile(0.95, rate(error_recovery_duration_seconds_bucket[5m]))"
    threshold: 30.0  # 30 seconds
    severity: "high"
```

### Quality Gates
```yaml
# Quality gates for error handling
quality_gates:
  error_handling_coverage:
    description: "Percentage of error scenarios covered by tests"
    metric: "error_scenario_coverage"
    threshold: 90
    blocking: true

  error_documentation:
    description: "All custom errors must be documented"
    metric: "documented_errors_percentage"
    threshold: 100
    blocking: true

  error_context_completeness:
    description: "All errors must include relevant context"
    metric: "errors_with_context_percentage"
    threshold: 95
    blocking: false
```

---

## 📋 **Implementation Checklist**

### Error Classification
- [ ] Define error hierarchy with BaseError
- [ ] Create business logic error types
- [ ] Create technical error types  
- [ ] Create authorization error types
- [ ] Implement error serialization methods

### Error Propagation
- [ ] Implement error context enrichment
- [ ] Create error propagation patterns
- [ ] Add retry mechanisms with backoff
- [ ] Implement error correlation IDs

### Resilience Patterns
- [ ] Implement circuit breaker pattern
- [ ] Create fallback mechanisms
- [ ] Add timeout handling
- [ ] Implement graceful degradation

### Monitoring & Alerting
- [ ] Set up error tracking and metrics
- [ ] Configure error rate thresholds
- [ ] Implement alert escalation
- [ ] Create error dashboards

### Testing
- [ ] Write error scenario tests
- [ ] Test error propagation
- [ ] Test resilience patterns
- [ ] Validate error context

---

## 🎯 **Success Metrics**

- **Error Classification Coverage:** 100% of application errors use proper error types
- **Error Context Completeness:** 95% of errors include relevant debugging context
- **Error Recovery Time:** 95th percentile under 30 seconds
- **Unhandled Error Rate:** 0% tolerance for unhandled errors
- **Error Documentation:** 100% of custom errors documented with examples 
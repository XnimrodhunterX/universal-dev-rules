# Rule 16A: Microservices Architecture Standards

<!-- CURSOR: highlight: Service decomposition patterns, communication protocols, distributed system design, and microservices governance with resilience patterns -->

## Purpose & Scope

Microservices architecture standards establish guidelines for designing, implementing, and operating distributed systems through service decomposition, communication patterns, data management, and governance frameworks. This rule provides standards for service boundaries, inter-service communication, distributed data management, resilience patterns, and operational considerations to enable scalable and maintainable microservices architectures.

<!-- CURSOR: complexity: Advanced -->

## Core Standards

### Service Design Patterns

#### 1. Domain-Driven Design Service Boundaries

**Service Decomposition Strategy:**
```typescript
// src/domain/user-management/bounded-context.ts
/**
 * User Management Bounded Context
 * Responsible for user identity, profiles, and authentication
 */

export interface UserAggregate {
  id: UserId;
  profile: UserProfile;
  authentication: AuthenticationInfo;
  preferences: UserPreferences;
}

export class UserId {
  constructor(private readonly value: string) {
    if (!this.isValid(value)) {
      throw new Error('Invalid user ID format');
    }
  }
  
  private isValid(value: string): boolean {
    return /^user_[a-zA-Z0-9]{16}$/.test(value);
  }
  
  toString(): string {
    return this.value;
  }
}

export class UserProfile {
  constructor(
    private readonly firstName: string,
    private readonly lastName: string,
    private readonly email: EmailAddress,
    private readonly createdAt: Date,
    private readonly lastModified: Date
  ) {}
  
  updateProfile(firstName: string, lastName: string): UserProfile {
    return new UserProfile(
      firstName,
      lastName,
      this.email,
      this.createdAt,
      new Date()
    );
  }
  
  getDisplayName(): string {
    return `${this.firstName} ${this.lastName}`;
  }
}

export class EmailAddress {
  constructor(private readonly value: string) {
    if (!this.isValid(value)) {
      throw new Error('Invalid email address format');
    }
  }
  
  private isValid(value: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
  }
  
  toString(): string {
    return this.value;
  }
}

// Domain Events
export abstract class DomainEvent {
  abstract eventType: string;
  abstract aggregateId: string;
  abstract timestamp: Date;
  abstract version: number;
}

export class UserRegisteredEvent extends DomainEvent {
  eventType = 'UserRegistered';
  
  constructor(
    public readonly aggregateId: string,
    public readonly userProfile: UserProfile,
    public readonly timestamp: Date = new Date(),
    public readonly version: number = 1
  ) {
    super();
  }
}

export class UserProfileUpdatedEvent extends DomainEvent {
  eventType = 'UserProfileUpdated';
  
  constructor(
    public readonly aggregateId: string,
    public readonly updatedProfile: UserProfile,
    public readonly timestamp: Date = new Date(),
    public readonly version: number = 1
  ) {
    super();
  }
}

// Domain Service
export class UserDomainService {
  constructor(
    private readonly userRepository: UserRepository,
    private readonly eventPublisher: DomainEventPublisher
  ) {}
  
  async registerUser(
    firstName: string,
    lastName: string,
    email: string,
    password: string
  ): Promise<UserId> {
    // Check if user already exists
    const existingUser = await this.userRepository.findByEmail(new EmailAddress(email));
    if (existingUser) {
      throw new Error('User with this email already exists');
    }
    
    // Create new user
    const userId = new UserId(`user_${this.generateId()}`);
    const userProfile = new UserProfile(
      firstName,
      lastName,
      new EmailAddress(email),
      new Date(),
      new Date()
    );
    
    const authInfo = new AuthenticationInfo(password);
    
    const user: UserAggregate = {
      id: userId,
      profile: userProfile,
      authentication: authInfo,
      preferences: new UserPreferences()
    };
    
    // Save user
    await this.userRepository.save(user);
    
    // Publish domain event
    const event = new UserRegisteredEvent(
      userId.toString(),
      userProfile
    );
    
    await this.eventPublisher.publish(event);
    
    return userId;
  }
  
  private generateId(): string {
    return Array.from({ length: 16 }, () => 
      Math.random().toString(36)[2]
    ).join('');
  }
}

// Repository Interface (Port)
export interface UserRepository {
  save(user: UserAggregate): Promise<void>;
  findById(id: UserId): Promise<UserAggregate | null>;
  findByEmail(email: EmailAddress): Promise<UserAggregate | null>;
  update(user: UserAggregate): Promise<void>;
  delete(id: UserId): Promise<void>;
}

// Event Publisher Interface (Port)
export interface DomainEventPublisher {
  publish(event: DomainEvent): Promise<void>;
  publishBatch(events: DomainEvent[]): Promise<void>;
}
```

#### 2. Service Communication Patterns

**API Gateway Implementation:**
```typescript
// src/gateway/api-gateway.ts
import express, { Request, Response, NextFunction } from 'express';
import httpProxy from 'http-proxy-middleware';
import jwt from 'jsonwebtoken';
import rateLimit from 'express-rate-limit';
import helmet from 'helmet';
import cors from 'cors';
import { createProxyMiddleware } from 'http-proxy-middleware';
import { CircuitBreaker } from './circuit-breaker';
import { ServiceRegistry } from './service-registry';
import { MetricsCollector } from './metrics-collector';

interface ServiceRoute {
  serviceName: string;
  path: string;
  target: string;
  authentication: boolean;
  rateLimit?: {
    windowMs: number;
    maxRequests: number;
  };
  circuitBreaker?: {
    failureThreshold: number;
    recoveryTimeout: number;
  };
}

export class APIGateway {
  private app: express.Application;
  private serviceRegistry: ServiceRegistry;
  private circuitBreakers: Map<string, CircuitBreaker>;
  private metricsCollector: MetricsCollector;
  
  constructor(
    serviceRegistry: ServiceRegistry,
    metricsCollector: MetricsCollector
  ) {
    this.app = express();
    this.serviceRegistry = serviceRegistry;
    this.circuitBreakers = new Map();
    this.metricsCollector = metricsCollector;
    
    this.setupMiddleware();
    this.setupRoutes();
  }
  
  private setupMiddleware(): void {
    // Security middleware
    this.app.use(helmet());
    this.app.use(cors({
      origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
      credentials: true
    }));
    
    // Request parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));
    
    // Request logging and metrics
    this.app.use((req: Request, res: Response, next: NextFunction) => {
      const startTime = Date.now();
      
      res.on('finish', () => {
        const duration = Date.now() - startTime;
        this.metricsCollector.recordRequest(
          req.method,
          req.path,
          res.statusCode,
          duration
        );
      });
      
      next();
    });
  }
  
  private setupRoutes(): void {
    const routes: ServiceRoute[] = [
      {
        serviceName: 'user-service',
        path: '/api/users',
        target: 'http://user-service:8080',
        authentication: true,
        rateLimit: { windowMs: 60000, maxRequests: 100 }
      },
      {
        serviceName: 'order-service',
        path: '/api/orders',
        target: 'http://order-service:8080',
        authentication: true,
        rateLimit: { windowMs: 60000, maxRequests: 50 },
        circuitBreaker: { failureThreshold: 5, recoveryTimeout: 30000 }
      },
      {
        serviceName: 'catalog-service',
        path: '/api/catalog',
        target: 'http://catalog-service:8080',
        authentication: false,
        rateLimit: { windowMs: 60000, maxRequests: 200 }
      },
      {
        serviceName: 'payment-service',
        path: '/api/payments',
        target: 'http://payment-service:8080',
        authentication: true,
        rateLimit: { windowMs: 60000, maxRequests: 20 },
        circuitBreaker: { failureThreshold: 3, recoveryTimeout: 60000 }
      }
    ];
    
    routes.forEach(route => this.setupServiceRoute(route));
    
    // Health check endpoint
    this.app.get('/health', (req: Request, res: Response) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        services: Array.from(this.circuitBreakers.entries()).map(([name, cb]) => ({
          name,
          status: cb.getState()
        }))
      });
    });
  }
  
  private setupServiceRoute(route: ServiceRoute): void {
    const router = express.Router();
    
    // Rate limiting
    if (route.rateLimit) {
      const limiter = rateLimit({
        windowMs: route.rateLimit.windowMs,
        max: route.rateLimit.maxRequests,
        message: {
          error: 'Too many requests',
          retryAfter: route.rateLimit.windowMs / 1000
        },
        standardHeaders: true,
        legacyHeaders: false
      });
      router.use(limiter);
    }
    
    // Authentication middleware
    if (route.authentication) {
      router.use(this.authenticationMiddleware);
    }
    
    // Circuit breaker setup
    if (route.circuitBreaker) {
      const circuitBreaker = new CircuitBreaker(
        route.serviceName,
        route.circuitBreaker.failureThreshold,
        route.circuitBreaker.recoveryTimeout
      );
      this.circuitBreakers.set(route.serviceName, circuitBreaker);
    }
    
    // Service discovery and load balancing
    const proxyMiddleware = createProxyMiddleware({
      target: route.target,
      changeOrigin: true,
      pathRewrite: (path, req) => {
        // Remove the route prefix
        return path.replace(route.path, '');
      },
      router: async (req) => {
        // Dynamic service discovery
        const instances = await this.serviceRegistry.getHealthyInstances(route.serviceName);
        if (instances.length === 0) {
          throw new Error(`No healthy instances for service ${route.serviceName}`);
        }
        
        // Simple round-robin load balancing
        const instance = instances[Math.floor(Math.random() * instances.length)];
        return `http://${instance.host}:${instance.port}`;
      },
      onProxyReq: (proxyReq, req, res) => {
        // Add tracing headers
        proxyReq.setHeader('X-Trace-Id', req.headers['x-trace-id'] || this.generateTraceId());
        proxyReq.setHeader('X-Request-Id', this.generateRequestId());
        
        // Add service context
        proxyReq.setHeader('X-Service-Name', route.serviceName);
        proxyReq.setHeader('X-Gateway-Timestamp', new Date().toISOString());
        
        // Forward user context if authenticated
        if (req.user) {
          proxyReq.setHeader('X-User-Id', (req.user as any).id);
          proxyReq.setHeader('X-User-Roles', JSON.stringify((req.user as any).roles));
        }
      },
      onProxyRes: (proxyRes, req, res) => {
        // Add security headers
        proxyRes.headers['X-Content-Type-Options'] = 'nosniff';
        proxyRes.headers['X-Frame-Options'] = 'DENY';
        
        // Record metrics
        this.metricsCollector.recordServiceResponse(
          route.serviceName,
          req.method,
          proxyRes.statusCode || 0
        );
      },
      onError: (err, req, res) => {
        console.error(`Proxy error for ${route.serviceName}:`, err);
        
        // Check circuit breaker
        const circuitBreaker = this.circuitBreakers.get(route.serviceName);
        if (circuitBreaker) {
          circuitBreaker.recordFailure();
          
          if (circuitBreaker.getState() === 'OPEN') {
            res.status(503).json({
              error: 'Service temporarily unavailable',
              message: 'Circuit breaker is open',
              serviceName: route.serviceName
            });
            return;
          }
        }
        
        res.status(502).json({
          error: 'Bad Gateway',
          message: 'Service is currently unavailable',
          serviceName: route.serviceName
        });
      }
    });
    
    // Apply proxy middleware with circuit breaker
    router.use('*', async (req: Request, res: Response, next: NextFunction) => {
      const circuitBreaker = this.circuitBreakers.get(route.serviceName);
      
      if (circuitBreaker && circuitBreaker.getState() === 'OPEN') {
        res.status(503).json({
          error: 'Service temporarily unavailable',
          message: 'Circuit breaker is open',
          serviceName: route.serviceName
        });
        return;
      }
      
      proxyMiddleware(req, res, next);
    });
    
    this.app.use(route.path, router);
  }
  
  private authenticationMiddleware = async (
    req: Request,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    try {
      const token = this.extractToken(req);
      
      if (!token) {
        res.status(401).json({ error: 'Authentication required' });
        return;
      }
      
      const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;
      req.user = decoded;
      
      next();
    } catch (error) {
      res.status(401).json({ error: 'Invalid token' });
    }
  };
  
  private extractToken(req: Request): string | null {
    const authHeader = req.headers.authorization;
    
    if (authHeader && authHeader.startsWith('Bearer ')) {
      return authHeader.substring(7);
    }
    
    return null;
  }
  
  private generateTraceId(): string {
    return Array.from({ length: 32 }, () =>
      Math.floor(Math.random() * 16).toString(16)
    ).join('');
  }
  
  private generateRequestId(): string {
    return Array.from({ length: 16 }, () =>
      Math.floor(Math.random() * 16).toString(16)
    ).join('');
  }
  
  public start(port: number = 3000): void {
    this.app.listen(port, () => {
      console.log(`API Gateway listening on port ${port}`);
    });
  }
}
```

#### 3. Circuit Breaker Pattern

**Resilient Service Communication:**
```typescript
// src/gateway/circuit-breaker.ts
export enum CircuitBreakerState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN',
  HALF_OPEN = 'HALF_OPEN'
}

export interface CircuitBreakerConfig {
  failureThreshold: number;
  recoveryTimeout: number;
  monitoringWindow: number;
  minimumThroughput: number;
}

export class CircuitBreaker {
  private state: CircuitBreakerState = CircuitBreakerState.CLOSED;
  private failures: number = 0;
  private successes: number = 0;
  private requests: number = 0;
  private lastFailureTime: number = 0;
  private requestLog: Array<{ timestamp: number; success: boolean }> = [];
  
  constructor(
    private readonly serviceName: string,
    private readonly config: CircuitBreakerConfig
  ) {}
  
  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === CircuitBreakerState.OPEN) {
      if (this.shouldAttemptReset()) {
        this.state = CircuitBreakerState.HALF_OPEN;
        console.log(`Circuit breaker for ${this.serviceName} is now HALF_OPEN`);
      } else {
        throw new Error(`Circuit breaker is OPEN for service ${this.serviceName}`);
      }
    }
    
    this.requests++;
    
    try {
      const result = await operation();
      this.recordSuccess();
      return result;
    } catch (error) {
      this.recordFailure();
      throw error;
    }
  }
  
  recordSuccess(): void {
    this.successes++;
    this.addToRequestLog(true);
    
    if (this.state === CircuitBreakerState.HALF_OPEN) {
      this.state = CircuitBreakerState.CLOSED;
      this.failures = 0;
      console.log(`Circuit breaker for ${this.serviceName} is now CLOSED`);
    }
  }
  
  recordFailure(): void {
    this.failures++;
    this.lastFailureTime = Date.now();
    this.addToRequestLog(false);
    
    if (this.shouldOpenCircuit()) {
      this.state = CircuitBreakerState.OPEN;
      console.log(`Circuit breaker for ${this.serviceName} is now OPEN`);
    }
  }
  
  private shouldOpenCircuit(): boolean {
    if (this.state === CircuitBreakerState.OPEN) {
      return false;
    }
    
    // Check if we have enough requests to make a decision
    if (this.requests < this.config.minimumThroughput) {
      return false;
    }
    
    // Calculate failure rate in the monitoring window
    const now = Date.now();
    const windowStart = now - this.config.monitoringWindow;
    
    const recentRequests = this.requestLog.filter(
      req => req.timestamp >= windowStart
    );
    
    if (recentRequests.length === 0) {
      return false;
    }
    
    const failures = recentRequests.filter(req => !req.success).length;
    const failureRate = failures / recentRequests.length;
    
    return failureRate >= this.config.failureThreshold;
  }
  
  private shouldAttemptReset(): boolean {
    return Date.now() - this.lastFailureTime >= this.config.recoveryTimeout;
  }
  
  private addToRequestLog(success: boolean): void {
    const now = Date.now();
    this.requestLog.push({ timestamp: now, success });
    
    // Clean up old entries outside monitoring window
    const windowStart = now - this.config.monitoringWindow;
    this.requestLog = this.requestLog.filter(
      req => req.timestamp >= windowStart
    );
  }
  
  getState(): CircuitBreakerState {
    return this.state;
  }
  
  getMetrics(): {
    state: CircuitBreakerState;
    failures: number;
    successes: number;
    requests: number;
    failureRate: number;
  } {
    const now = Date.now();
    const windowStart = now - this.config.monitoringWindow;
    
    const recentRequests = this.requestLog.filter(
      req => req.timestamp >= windowStart
    );
    
    const recentFailures = recentRequests.filter(req => !req.success).length;
    const failureRate = recentRequests.length > 0 ? 
      recentFailures / recentRequests.length : 0;
    
    return {
      state: this.state,
      failures: this.failures,
      successes: this.successes,
      requests: this.requests,
      failureRate: Math.round(failureRate * 100) / 100
    };
  }
  
  reset(): void {
    this.state = CircuitBreakerState.CLOSED;
    this.failures = 0;
    this.successes = 0;
    this.requests = 0;
    this.lastFailureTime = 0;
    this.requestLog = [];
    console.log(`Circuit breaker for ${this.serviceName} has been reset`);
  }
}

// Service Registry for Dynamic Discovery
export interface ServiceInstance {
  id: string;
  host: string;
  port: number;
  healthy: boolean;
  metadata: Record<string, string>;
  lastHealthCheck: Date;
}

export class ServiceRegistry {
  private services: Map<string, ServiceInstance[]> = new Map();
  private healthCheckInterval: NodeJS.Timeout;
  
  constructor(private readonly healthCheckIntervalMs: number = 30000) {
    this.healthCheckInterval = setInterval(
      () => this.performHealthChecks(),
      healthCheckIntervalMs
    );
  }
  
  registerService(
    serviceName: string,
    instance: Omit<ServiceInstance, 'lastHealthCheck'>
  ): void {
    const serviceInstances = this.services.get(serviceName) || [];
    
    const fullInstance: ServiceInstance = {
      ...instance,
      lastHealthCheck: new Date()
    };
    
    // Remove existing instance with same id
    const filteredInstances = serviceInstances.filter(
      inst => inst.id !== instance.id
    );
    
    filteredInstances.push(fullInstance);
    this.services.set(serviceName, filteredInstances);
    
    console.log(`Registered service instance: ${serviceName}:${instance.id}`);
  }
  
  deregisterService(serviceName: string, instanceId: string): void {
    const serviceInstances = this.services.get(serviceName) || [];
    const filteredInstances = serviceInstances.filter(
      inst => inst.id !== instanceId
    );
    
    this.services.set(serviceName, filteredInstances);
    console.log(`Deregistered service instance: ${serviceName}:${instanceId}`);
  }
  
  async getHealthyInstances(serviceName: string): Promise<ServiceInstance[]> {
    const instances = this.services.get(serviceName) || [];
    return instances.filter(instance => instance.healthy);
  }
  
  getAllServices(): Map<string, ServiceInstance[]> {
    return new Map(this.services);
  }
  
  private async performHealthChecks(): Promise<void> {
    for (const [serviceName, instances] of this.services.entries()) {
      const healthCheckPromises = instances.map(instance => 
        this.checkInstanceHealth(serviceName, instance)
      );
      
      await Promise.allSettled(healthCheckPromises);
    }
  }
  
  private async checkInstanceHealth(
    serviceName: string,
    instance: ServiceInstance
  ): Promise<void> {
    try {
      const response = await fetch(
        `http://${instance.host}:${instance.port}/health`,
        {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          signal: AbortSignal.timeout(5000) // 5 second timeout
        }
      );
      
      instance.healthy = response.ok;
      instance.lastHealthCheck = new Date();
      
      if (!response.ok) {
        console.warn(
          `Health check failed for ${serviceName}:${instance.id} - Status: ${response.status}`
        );
      }
    } catch (error) {
      instance.healthy = false;
      instance.lastHealthCheck = new Date();
      console.error(
        `Health check error for ${serviceName}:${instance.id}:`,
        error
      );
    }
  }
  
  destroy(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
  }
}
```

This represents the first part of Rule 16A covering microservices architecture with domain-driven design, API gateway patterns, circuit breakers, and service discovery. The implementation continues with distributed data management, event-driven communication, and microservices governance patterns. 
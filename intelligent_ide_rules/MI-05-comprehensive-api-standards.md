# MI-05: Comprehensive API Standards & Management

## Purpose & Scope

Comprehensive API standards covering the complete API lifecycle from design through documentation to versioning and deprecation. This rule establishes unified standards for RESTful API design, OpenAPI documentation, semantic versioning, and lifecycle management to ensure consistent, maintainable, and well-documented APIs across all services.

## Core Standards

### 1. RESTful API Design Principles

#### REST Architecture Standards

**Resource-Based Design:**
```typescript
// api/standards/resource-patterns.ts
export interface ResourceController<T> {
  // GET /api/v1/resources - List resources with pagination
  list(req: ListRequest): Promise<PaginatedResponse<T>>;
  
  // GET /api/v1/resources/:id - Get single resource
  get(req: GetRequest): Promise<T>;
  
  // POST /api/v1/resources - Create new resource
  create(req: CreateRequest<T>): Promise<T>;
  
  // PUT /api/v1/resources/:id - Update entire resource
  update(req: UpdateRequest<T>): Promise<T>;
  
  // PATCH /api/v1/resources/:id - Partial update
  patch(req: PatchRequest<T>): Promise<T>;
  
  // DELETE /api/v1/resources/:id - Delete resource
  delete(req: DeleteRequest): Promise<void>;
}

// Standard resource URL patterns
export const API_URL_PATTERNS = {
  // Collection operations
  collection: '/api/{version}/{resources}',
  
  // Resource operations  
  resource: '/api/{version}/{resources}/{id}',
  
  // Nested resources
  nested: '/api/{version}/{parent_resources}/{parent_id}/{child_resources}',
  
  // Resource actions (avoid when possible)
  action: '/api/{version}/{resources}/{id}/{action}',
  
  // Search and filtering
  search: '/api/{version}/{resources}?filter={criteria}&sort={fields}&page={num}'
};
```

#### HTTP Method Standards

**Method Usage Guidelines:**
```yaml
# http-method-standards.yaml
http_methods:
  GET:
    purpose: "Retrieve resource(s)"
    safe: true
    idempotent: true
    cacheable: true
    body_allowed: false
    response_codes: [200, 404, 304, 400, 401, 403, 500]
    
  POST:
    purpose: "Create new resource or non-idempotent operations"
    safe: false
    idempotent: false
    cacheable: false
    body_required: true
    response_codes: [201, 200, 400, 401, 403, 409, 422, 500]
    
  PUT:
    purpose: "Create or completely replace resource"
    safe: false
    idempotent: true
    cacheable: false
    body_required: true
    response_codes: [200, 201, 204, 400, 401, 403, 404, 409, 422, 500]
    
  PATCH:
    purpose: "Partial update of resource"
    safe: false
    idempotent: false
    cacheable: false
    body_required: true
    response_codes: [200, 204, 400, 401, 403, 404, 409, 422, 500]
    
  DELETE:
    purpose: "Remove resource"
    safe: false
    idempotent: true
    cacheable: false
    body_allowed: false
    response_codes: [200, 204, 404, 400, 401, 403, 500]
```

#### Status Code Standards

**HTTP Response Codes:**
```typescript
// api/standards/status-codes.ts
export const HTTP_STATUS_CODES = {
  // Success 2xx
  SUCCESS: {
    OK: 200,                    // GET, PUT, PATCH success
    CREATED: 201,               // POST success with resource creation
    ACCEPTED: 202,              // Async operation accepted
    NO_CONTENT: 204,            // DELETE, PUT success without response body
    PARTIAL_CONTENT: 206        // Partial GET (range requests)
  },
  
  // Client Error 4xx
  CLIENT_ERROR: {
    BAD_REQUEST: 400,           // Invalid request syntax
    UNAUTHORIZED: 401,          // Authentication required
    FORBIDDEN: 403,             // Insufficient permissions
    NOT_FOUND: 404,             // Resource not found
    METHOD_NOT_ALLOWED: 405,    // HTTP method not supported
    NOT_ACCEPTABLE: 406,        // Cannot produce requested content type
    CONFLICT: 409,              // Resource conflict
    GONE: 410,                  // Resource permanently deleted
    LENGTH_REQUIRED: 411,       // Content-Length header missing
    PRECONDITION_FAILED: 412,   // Conditional request failed
    PAYLOAD_TOO_LARGE: 413,     // Request body too large
    UNSUPPORTED_MEDIA_TYPE: 415, // Content-Type not supported
    UNPROCESSABLE_ENTITY: 422,  // Validation errors
    TOO_MANY_REQUESTS: 429      // Rate limit exceeded
  },
  
  // Server Error 5xx
  SERVER_ERROR: {
    INTERNAL_SERVER_ERROR: 500, // Generic server error
    NOT_IMPLEMENTED: 501,       // Functionality not implemented
    BAD_GATEWAY: 502,           // Invalid upstream response
    SERVICE_UNAVAILABLE: 503,   // Service temporarily unavailable
    GATEWAY_TIMEOUT: 504,       // Upstream timeout
    VERSION_NOT_SUPPORTED: 505  // HTTP version not supported
  }
};
```

### 2. Comprehensive API Documentation

#### OpenAPI Specification Standards

**Complete API Documentation:**
```yaml
# openapi-template.yaml
openapi: 3.0.3
info:
  title: "{Service Name} API"
  description: |
    {Comprehensive service description}
    
    ## Authentication
    This API uses JWT Bearer tokens for authentication.
    Include the token in the Authorization header:
    ```
    Authorization: Bearer <your-jwt-token>
    ```
    
    ## Rate Limiting
    API requests are rate limited. Current limits:
    - Authenticated users: 1000 requests/hour
    - Anonymous users: 100 requests/hour
    
    Rate limit information is included in response headers.
    
    ## Error Handling
    All errors follow RFC 9457 (Problem Details) format.
    
  version: "{semantic.version}"
  contact:
    name: "{Team Name}"
    url: "https://example.com/support"
    email: "{team}@example.com"
  license:
    name: "MIT"
    url: "https://opensource.org/licenses/MIT"

servers:
  - url: "https://api.example.com/{version}"
    description: "Production server"
  - url: "https://staging-api.example.com/{version}"
    description: "Staging server"
  - url: "http://localhost:{port}/api/{version}"
    description: "Development server"

security:
  - BearerAuth: []

paths:
  "/resources":
    get:
      summary: "List resources"
      description: |
        Retrieve a paginated list of resources with optional filtering and sorting.
        
        ### Filtering
        Use query parameters to filter results:
        - `status=active` - Filter by status
        - `type=premium` - Filter by type
        - `created_since=2024-01-01` - Filter by creation date
        
        ### Sorting
        Use the `sort` parameter with field:direction format:
        - `sort=name:asc` - Sort by name ascending
        - `sort=created_at:desc` - Sort by creation date descending
        - `sort=name:asc,created_at:desc` - Multiple sort fields
        
      operationId: "listResources"
      tags: ["Resources"]
      parameters:
        - $ref: "#/components/parameters/PageParam"
        - $ref: "#/components/parameters/LimitParam" 
        - $ref: "#/components/parameters/SortParam"
        - $ref: "#/components/parameters/FilterParam"
      responses:
        "200":
          description: "Successfully retrieved resources"
          headers:
            X-Total-Count:
              description: "Total number of resources"
              schema:
                type: integer
            X-Rate-Limit-Remaining:
              description: "Requests remaining in current window"
              schema:
                type: integer
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ResourceListResponse"
              examples:
                success:
                  summary: "Successful response"
                  value:
                    data: 
                      - id: "123e4567-e89b-12d3-a456-426614174000"
                        name: "Sample Resource"
                        status: "active"
                        created_at: "2024-01-15T10:30:00Z"
                    pagination:
                      page: 1
                      limit: 20
                      total: 150
                      pages: 8
        "400":
          $ref: "#/components/responses/BadRequest"
        "401":
          $ref: "#/components/responses/Unauthorized"
        "403":
          $ref: "#/components/responses/Forbidden"
        "429":
          $ref: "#/components/responses/RateLimitExceeded"
        "500":
          $ref: "#/components/responses/InternalServerError"

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      
  parameters:
    PageParam:
      name: page
      in: query
      description: "Page number (1-based)"
      schema:
        type: integer
        minimum: 1
        default: 1
      example: 1
      
    LimitParam:
      name: limit
      in: query
      description: "Items per page"
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20
      example: 20
      
  responses:
    BadRequest:
      description: "Bad Request - Invalid request parameters"
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetails"
          example:
            type: "https://api.example.com/problems/bad-request"
            title: "Bad Request"
            status: 400
            detail: "The request parameters are invalid"
            
    Unauthorized:
      description: "Unauthorized - Authentication required"
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetails"
          example:
            type: "https://api.example.com/problems/unauthorized"
            title: "Unauthorized"
            status: 401
            detail: "Authentication is required to access this resource"
            
  schemas:
    ProblemDetails:
      type: object
      required: [type, title, status]
      properties:
        type:
          type: string
          format: uri
          description: "URI identifying the problem type"
        title:
          type: string
          description: "Human-readable summary of the problem"
        status:
          type: integer
          description: "HTTP status code"
        detail:
          type: string
          description: "Human-readable explanation of the problem"
        instance:
          type: string
          format: uri
          description: "URI identifying the specific occurrence"
```

#### Documentation Automation

**Code-First Documentation:**
```typescript
// api/documentation/swagger-generator.ts
export class SwaggerDocumentationGenerator {
  private readonly decorators = {
    controller: (path: string, tags: string[]) => {
      return (target: any) => {
        Reflect.defineMetadata('path', path, target);
        Reflect.defineMetadata('tags', tags, target);
      };
    },
    
    operation: (method: string, path: string, summary: string) => {
      return (target: any, propertyKey: string, descriptor: PropertyDescriptor) => {
        Reflect.defineMetadata('method', method, target, propertyKey);
        Reflect.defineMetadata('path', path, target, propertyKey);
        Reflect.defineMetadata('summary', summary, target, propertyKey);
      };
    },
    
    response: (status: number, description: string, schema?: any) => {
      return (target: any, propertyKey: string, descriptor: PropertyDescriptor) => {
        const responses = Reflect.getMetadata('responses', target, propertyKey) || {};
        responses[status] = { description, schema };
        Reflect.defineMetadata('responses', responses, target, propertyKey);
      };
    },
    
    parameter: (name: string, location: 'query' | 'path' | 'header', schema: any) => {
      return (target: any, propertyKey: string, descriptor: PropertyDescriptor) => {
        const parameters = Reflect.getMetadata('parameters', target, propertyKey) || [];
        parameters.push({ name, in: location, schema });
        Reflect.defineMetadata('parameters', parameters, target, propertyKey);
      };
    }
  };
  
  generateOpenAPISpec(controllers: any[]): OpenAPIObject {
    const spec: OpenAPIObject = {
      openapi: '3.0.3',
      info: this.getApiInfo(),
      servers: this.getServers(),
      paths: {},
      components: {
        schemas: {},
        responses: this.getStandardResponses(),
        parameters: this.getStandardParameters(),
        securitySchemes: this.getSecuritySchemes()
      }
    };
    
    // Generate paths from controllers
    controllers.forEach(controller => {
      this.addControllerToSpec(spec, controller);
    });
    
    return spec;
  }
  
  private addControllerToSpec(spec: OpenAPIObject, controller: any): void {
    const controllerPath = Reflect.getMetadata('path', controller);
    const controllerTags = Reflect.getMetadata('tags', controller);
    
    const methods = Object.getOwnPropertyNames(controller.prototype)
      .filter(name => name !== 'constructor');
    
    methods.forEach(methodName => {
      const method = Reflect.getMetadata('method', controller.prototype, methodName);
      const path = Reflect.getMetadata('path', controller.prototype, methodName);
      const summary = Reflect.getMetadata('summary', controller.prototype, methodName);
      
      if (method && path) {
        const fullPath = controllerPath + path;
        
        if (!spec.paths[fullPath]) {
          spec.paths[fullPath] = {};
        }
        
        spec.paths[fullPath][method.toLowerCase()] = {
          summary,
          tags: controllerTags,
          parameters: Reflect.getMetadata('parameters', controller.prototype, methodName) || [],
          responses: Reflect.getMetadata('responses', controller.prototype, methodName) || {}
        };
      }
    });
  }
}
```

### 3. API Versioning & Lifecycle Management

#### Semantic Versioning Strategy

**Version Management Framework:**
```typescript
// api/versioning/version-manager.ts
export interface ApiVersion {
  major: number;
  minor: number;
  patch: number;
  status: 'development' | 'active' | 'deprecated' | 'sunset';
  releaseDate: Date;
  deprecationDate?: Date;
  sunsetDate?: Date;
  breakingChanges: BreakingChange[];
  features: Feature[];
  supportLevel: 'full' | 'security_only' | 'none';
}

export interface BreakingChange {
  type: 'removed' | 'modified' | 'moved';
  component: string;
  description: string;
  migrationGuide: string;
}

export interface Feature {
  name: string;
  description: string;
  endpoints: string[];
}

export class ApiVersionManager {
  private versions: Map<string, ApiVersion> = new Map();
  private supportMatrix: Map<string, SupportPolicy> = new Map();
  
  constructor() {
    this.initializeVersions();
  }
  
  private initializeVersions(): void {
    // Version 1.0 - Initial stable release
    this.versions.set('v1.0', {
      major: 1,
      minor: 0,
      patch: 0,
      status: 'deprecated',
      releaseDate: new Date('2023-01-01'),
      deprecationDate: new Date('2024-01-01'),
      sunsetDate: new Date('2024-06-01'),
      supportLevel: 'security_only',
      breakingChanges: [],
      features: [
        {
          name: 'Core API',
          description: 'Basic CRUD operations',
          endpoints: ['/users', '/resources']
        }
      ]
    });
    
    // Version 2.0 - Major architectural changes
    this.versions.set('v2.0', {
      major: 2,
      minor: 0,
      patch: 0,
      status: 'active',
      releaseDate: new Date('2024-01-01'),
      supportLevel: 'full',
      breakingChanges: [
        {
          type: 'modified',
          component: 'User ID format',
          description: 'Changed from integer to UUID',
          migrationGuide: 'https://docs.example.com/migration/v1-to-v2#user-ids'
        },
        {
          type: 'removed',
          component: '/users/search endpoint',
          description: 'Deprecated search endpoint removed',
          migrationGuide: 'Use /users with query parameters instead'
        }
      ],
      features: [
        {
          name: 'Enhanced Authentication',
          description: 'JWT-based authentication with refresh tokens',
          endpoints: ['/auth/login', '/auth/refresh', '/auth/logout']
        },
        {
          name: 'Advanced Filtering',
          description: 'Complex query capabilities',
          endpoints: ['/users', '/resources']
        }
      ]
    });
  }
  
  // Version validation and routing
  extractVersionFromRequest(req: Request): string {
    // Priority: path > header > query > default
    return this.extractVersionFromPath(req.path) ||
           this.extractVersionFromHeader(req.get('Accept')) ||
           (req.query.version as string) ||
           this.getDefaultVersion();
  }
  
  private extractVersionFromPath(path: string): string | null {
    const match = path.match(/^\/api\/(v\d+(?:\.\d+)?)\//);
    return match ? match[1] : null;
  }
  
  validateVersion(version: string): boolean {
    const apiVersion = this.versions.get(version);
    return apiVersion ? apiVersion.status !== 'sunset' : false;
  }
  
  getVersionInfo(version: string): ApiVersion | undefined {
    return this.versions.get(version);
  }
  
  getDeprecationHeaders(version: string): Record<string, string> {
    const versionInfo = this.versions.get(version);
    if (!versionInfo || versionInfo.status !== 'deprecated') {
      return {};
    }
    
    const headers: Record<string, string> = {
      'Deprecation': versionInfo.deprecationDate?.toISOString() || 'true',
      'API-Version': version,
      'API-Supported-Versions': this.getSupportedVersions().join(', ')
    };
    
    if (versionInfo.sunsetDate) {
      headers['Sunset'] = versionInfo.sunsetDate.toISOString();
    }
    
    const latestVersion = this.getLatestVersion();
    if (latestVersion !== version) {
      headers['Link'] = `</api/${latestVersion}>; rel="successor-version"`;
    }
    
    return headers;
  }
}
```

#### Backward Compatibility Management

**Compatibility Strategy:**
```yaml
# compatibility-strategy.yaml
compatibility_rules:
  major_version_changes:
    allowed:
      - "Remove deprecated endpoints (after 6+ months notice)"
      - "Change response format structure"
      - "Change authentication mechanism"
      - "Modify URL patterns"
      - "Change default behaviors"
    
    not_allowed:
      - "Remove endpoints without deprecation period"  
      - "Change data types without migration path"
      - "Modify core business logic unexpectedly"
      
  minor_version_changes:
    allowed:
      - "Add new endpoints"
      - "Add new optional parameters"
      - "Add new response fields"
      - "Enhance existing functionality"
      - "Add new optional headers"
    
    not_allowed:
      - "Remove any existing functionality"
      - "Change existing response formats"
      - "Make optional parameters required"
      - "Change default values"
      
  patch_version_changes:
    allowed:
      - "Bug fixes"
      - "Security updates"
      - "Performance improvements"
      - "Documentation updates"
    
    not_allowed:
      - "Add new functionality"
      - "Change any external interfaces"
      - "Modify behavior visibly"

deprecation_policy:
  notice_period:
    major_breaking_changes: "12 months"
    minor_breaking_changes: "6 months"
    endpoint_removal: "6 months"
    parameter_changes: "3 months"
    
  communication_channels:
    - "API changelog"
    - "Developer newsletter"
    - "API response headers"
    - "Developer portal announcements"
    - "Direct customer notification for major changes"
    
  migration_support:
    documentation_required: true
    code_examples_required: true
    migration_scripts_provided: true
    support_team_training: true
```

### 4. API Quality & Standards

#### Request/Response Standards

**Standardized Patterns:**
```typescript
// api/standards/request-response-patterns.ts
export interface StandardRequest {
  // Common headers
  'Content-Type': string;
  'Accept': string;
  'Authorization'?: string;
  'X-Request-ID': string;
  'User-Agent': string;
}

export interface StandardResponse<T> {
  data: T;
  meta: ResponseMeta;
  links?: ResponseLinks;
}

export interface ResponseMeta {
  timestamp: string;
  version: string;
  requestId: string;
  pagination?: PaginationMeta;
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  pages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface ResponseLinks {
  self: string;
  first?: string;
  last?: string;
  next?: string;
  prev?: string;
}

// Error response following RFC 9457
export interface ProblemDetails {
  type: string;          // URI identifying the problem type
  title: string;         // Human-readable summary
  status: number;        // HTTP status code
  detail: string;        // Human-readable explanation
  instance?: string;     // URI identifying this occurrence
  [key: string]: any;    // Additional problem-specific fields
}
```

#### Validation & Security Standards

**Input Validation:**
```typescript
// api/validation/request-validator.ts
export class ApiRequestValidator {
  // Content-Type validation
  static validateContentType(req: Request, allowedTypes: string[]): void {
    const contentType = req.get('Content-Type');
    if (!contentType || !allowedTypes.some(type => contentType.includes(type))) {
      throw new UnsupportedMediaTypeError(
        `Content-Type must be one of: ${allowedTypes.join(', ')}`
      );
    }
  }
  
  // Request size limits
  static validateRequestSize(req: Request, maxSize: number): void {
    const contentLength = parseInt(req.get('Content-Length') || '0');
    if (contentLength > maxSize) {
      throw new PayloadTooLargeError(
        `Request body too large. Maximum size: ${maxSize} bytes`
      );
    }
  }
  
  // Rate limiting
  static async validateRateLimit(req: Request, limits: RateLimitConfig): Promise<void> {
    const identifier = this.getRateLimitIdentifier(req);
    const current = await this.getCurrentRequestCount(identifier);
    
    if (current >= limits.maxRequests) {
      const resetTime = await this.getRateLimitReset(identifier);
      throw new TooManyRequestsError(
        'Rate limit exceeded',
        { retryAfter: resetTime }
      );
    }
  }
  
  // Schema validation
  static validateSchema(data: any, schema: JSONSchema): ValidationResult {
    const validator = new JSONSchemaValidator();
    return validator.validate(data, schema);
  }
}
```

## Implementation Requirements

### 1. Development Workflow Integration

```yaml
# api-development-workflow.yaml
development_lifecycle:
  design_phase:
    - "Create OpenAPI specification first"
    - "Review API design with stakeholders"
    - "Validate against existing APIs for consistency"
    - "Plan versioning strategy"
    
  implementation_phase:
    - "Generate code from OpenAPI spec"
    - "Implement with validation and error handling"
    - "Add comprehensive tests"
    - "Set up monitoring and logging"
    
  testing_phase:
    - "Unit tests for all endpoints"
    - "Integration tests with real data"
    - "Contract tests against OpenAPI spec"
    - "Performance and load testing"
    
  deployment_phase:
    - "Deploy to staging with full OpenAPI docs"
    - "Run automated API tests"
    - "Update API documentation portal"
    - "Monitor deployment metrics"
    
  maintenance_phase:
    - "Monitor API usage and performance"
    - "Collect feedback from API consumers"
    - "Plan deprecation of old versions"
    - "Regular security updates"
```

### 2. Monitoring & Observability

```yaml
# api-monitoring-standards.yaml  
monitoring_requirements:
  metrics:
    - name: "api_requests_total"
      labels: ["method", "endpoint", "status_code", "version"]
      
    - name: "api_request_duration_seconds"
      labels: ["method", "endpoint", "version"]
      
    - name: "api_errors_total"
      labels: ["method", "endpoint", "error_type", "version"]
      
    - name: "api_rate_limit_hits_total"
      labels: ["endpoint", "client_id"]
      
  logging:
    request_logging:
      - "timestamp"
      - "request_id"
      - "method"
      - "endpoint"
      - "version"
      - "client_id"
      - "user_id"
      - "status_code"
      - "response_time_ms"
      
    error_logging:
      - "error_type"
      - "error_message"
      - "stack_trace"
      - "request_context"
      
  alerting:
    critical_alerts:
      - "Error rate > 5% for 5 minutes"
      - "Response time p95 > 2 seconds"
      - "API endpoint returning 5xx errors"
      
    warning_alerts:
      - "Rate limit hit rate > 10%"
      - "Deprecated API version usage > 20%"
      - "Request validation error rate > 2%"
```

## Quality Gates & Best Practices

### API Design Checklist
- ✅ RESTful resource-based URLs
- ✅ Proper HTTP methods and status codes
- ✅ Consistent naming conventions
- ✅ Comprehensive error handling
- ✅ Input validation and sanitization
- ✅ Rate limiting implementation
- ✅ Authentication and authorization
- ✅ Request/response logging

### Documentation Requirements
- ✅ Complete OpenAPI 3.0+ specification
- ✅ Interactive API documentation
- ✅ Code examples for all endpoints
- ✅ Error response documentation
- ✅ Authentication examples
- ✅ Rate limiting information
- ✅ Versioning and deprecation notices

### Versioning Standards
- ✅ Semantic versioning (major.minor.patch)
- ✅ URL path versioning (/api/v2/)
- ✅ Backward compatibility within major versions
- ✅ Deprecation notices and timelines
- ✅ Migration guides for breaking changes
- ✅ Support policy documentation

This comprehensive API standards rule consolidates design principles, documentation requirements, and versioning strategies into unified guidance for building maintainable, well-documented APIs throughout their entire lifecycle. 
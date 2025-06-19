---
description: "Universal environment configuration: environment variables, configuration validation, environment-specific settings. Configuration management standards and security."
globs: ["**/*"]
alwaysApply: true
---

# ⚙️ Universal Environment Configuration

## 1. Environment Variable Management

### Environment Configuration Requirements
- **USE:** Structured environment variable naming with consistent prefixes
- **VALIDATE:** All environment variables with schema validation
- **SEPARATE:** Configuration by environment (dev, staging, production)
- **SECURE:** Sensitive values through secrets management, never in plain text

### Environment Variable Schema
```typescript
// config/env-schema.ts
import { z } from 'zod';

export const envSchema = z.object({
  // Application settings
  NODE_ENV: z.enum(['development', 'staging', 'production']).default('development'),
  APP_NAME: z.string().min(1),
  APP_VERSION: z.string().min(1),
  APP_PORT: z.coerce.number().int().positive().default(3000),
  APP_HOST: z.string().default('0.0.0.0'),
  
  // Database configuration
  DATABASE_URL: z.string().url(),
  DATABASE_MAX_CONNECTIONS: z.coerce.number().int().positive().default(20),
  DATABASE_CONNECTION_TIMEOUT: z.coerce.number().int().positive().default(30000),
  DATABASE_SSL_MODE: z.enum(['disable', 'require', 'verify-ca', 'verify-full']).default('require'),
  
  // Redis configuration
  REDIS_URL: z.string().url().optional(),
  REDIS_MAX_RETRIES: z.coerce.number().int().positive().default(3),
  REDIS_RETRY_DELAY: z.coerce.number().int().positive().default(1000),
  
  // Authentication & Security
  JWT_SECRET: z.string().min(32),
  JWT_EXPIRES_IN: z.string().default('24h'),
  CORS_ORIGINS: z.string().transform(val => val.split(',')).default(''),
  RATE_LIMIT_WINDOW_MS: z.coerce.number().int().positive().default(900000), // 15 minutes
  RATE_LIMIT_MAX_REQUESTS: z.coerce.number().int().positive().default(100),
  
  // External services
  AWS_REGION: z.string().optional(),
  AWS_ACCESS_KEY_ID: z.string().optional(),
  AWS_SECRET_ACCESS_KEY: z.string().optional(),
  
  // Monitoring & Observability
  LOG_LEVEL: z.enum(['error', 'warn', 'info', 'debug']).default('info'),
  METRICS_ENABLED: z.coerce.boolean().default(true),
  TRACING_ENABLED: z.coerce.boolean().default(false),
  HEALTH_CHECK_INTERVAL: z.coerce.number().int().positive().default(30000),
  
  // Feature flags
  FEATURE_NEW_API: z.coerce.boolean().default(false),
  FEATURE_ANALYTICS: z.coerce.boolean().default(true),
  
  // Performance settings
  BODY_PARSER_LIMIT: z.string().default('10mb'),
  REQUEST_TIMEOUT: z.coerce.number().int().positive().default(30000),
  
  // Email configuration
  SMTP_HOST: z.string().optional(),
  SMTP_PORT: z.coerce.number().int().positive().optional(),
  SMTP_USER: z.string().optional(),
  SMTP_PASSWORD: z.string().optional(),
});

export type Environment = z.infer<typeof envSchema>;

// Validate and export parsed environment
export const env = envSchema.parse(process.env);
```

### Configuration Loader
```typescript
// config/config-loader.ts
import { env } from './env-schema';
import { readFileSync } from 'fs';
import { join } from 'path';

export interface AppConfig {
  app: {
    name: string;
    version: string;
    port: number;
    host: string;
    environment: string;
  };
  database: {
    url: string;
    maxConnections: number;
    connectionTimeout: number;
    sslMode: string;
  };
  redis?: {
    url: string;
    maxRetries: number;
    retryDelay: number;
  };
  auth: {
    jwtSecret: string;
    jwtExpiresIn: string;
  };
  security: {
    corsOrigins: string[];
    rateLimit: {
      windowMs: number;
      maxRequests: number;
    };
  };
  monitoring: {
    logLevel: string;
    metricsEnabled: boolean;
    tracingEnabled: boolean;
    healthCheckInterval: number;
  };
  features: {
    newApi: boolean;
    analytics: boolean;
  };
}

export class ConfigLoader {
  private static instance: ConfigLoader;
  private config: AppConfig;
  
  private constructor() {
    this.config = this.loadConfiguration();
    this.validateConfiguration();
  }
  
  static getInstance(): ConfigLoader {
    if (!ConfigLoader.instance) {
      ConfigLoader.instance = new ConfigLoader();
    }
    return ConfigLoader.instance;
  }
  
  getConfig(): AppConfig {
    return this.config;
  }
  
  private loadConfiguration(): AppConfig {
    // Load base configuration from environment
    const baseConfig: AppConfig = {
      app: {
        name: env.APP_NAME,
        version: env.APP_VERSION,
        port: env.APP_PORT,
        host: env.APP_HOST,
        environment: env.NODE_ENV,
      },
      database: {
        url: env.DATABASE_URL,
        maxConnections: env.DATABASE_MAX_CONNECTIONS,
        connectionTimeout: env.DATABASE_CONNECTION_TIMEOUT,
        sslMode: env.DATABASE_SSL_MODE,
      },
      auth: {
        jwtSecret: env.JWT_SECRET,
        jwtExpiresIn: env.JWT_EXPIRES_IN,
      },
      security: {
        corsOrigins: env.CORS_ORIGINS,
        rateLimit: {
          windowMs: env.RATE_LIMIT_WINDOW_MS,
          maxRequests: env.RATE_LIMIT_MAX_REQUESTS,
        },
      },
      monitoring: {
        logLevel: env.LOG_LEVEL,
        metricsEnabled: env.METRICS_ENABLED,
        tracingEnabled: env.TRACING_ENABLED,
        healthCheckInterval: env.HEALTH_CHECK_INTERVAL,
      },
      features: {
        newApi: env.FEATURE_NEW_API,
        analytics: env.FEATURE_ANALYTICS,
      },
    };
    
    // Add Redis configuration if URL is provided
    if (env.REDIS_URL) {
      baseConfig.redis = {
        url: env.REDIS_URL,
        maxRetries: env.REDIS_MAX_RETRIES,
        retryDelay: env.REDIS_RETRY_DELAY,
      };
    }
    
    // Load environment-specific overrides
    const envOverrides = this.loadEnvironmentOverrides();
    return this.mergeConfigurations(baseConfig, envOverrides);
  }
  
  private loadEnvironmentOverrides(): Partial<AppConfig> {
    const envConfigPath = join(process.cwd(), 'config', `${env.NODE_ENV}.json`);
    
    try {
      const envConfigFile = readFileSync(envConfigPath, 'utf-8');
      return JSON.parse(envConfigFile);
    } catch (error) {
      console.warn(`No environment-specific config found at ${envConfigPath}`);
      return {};
    }
  }
  
  private mergeConfigurations(base: AppConfig, override: Partial<AppConfig>): AppConfig {
    return {
      ...base,
      ...override,
      app: { ...base.app, ...override.app },
      database: { ...base.database, ...override.database },
      redis: base.redis ? { ...base.redis, ...override.redis } : override.redis,
      auth: { ...base.auth, ...override.auth },
      security: { 
        ...base.security, 
        ...override.security,
        rateLimit: { ...base.security.rateLimit, ...override.security?.rateLimit }
      },
      monitoring: { ...base.monitoring, ...override.monitoring },
      features: { ...base.features, ...override.features },
    };
  }
  
  private validateConfiguration(): void {
    // Validate critical configuration
    if (env.NODE_ENV === 'production') {
      this.validateProductionConfig();
    }
    
    // Validate service dependencies
    this.validateServiceConnections();
  }
  
  private validateProductionConfig(): void {
    const requiredProdSettings = [
      { key: 'JWT_SECRET', value: env.JWT_SECRET, minLength: 32 },
      { key: 'DATABASE_URL', value: env.DATABASE_URL },
      { key: 'LOG_LEVEL', value: env.LOG_LEVEL, allowed: ['error', 'warn', 'info'] },
    ];
    
    for (const setting of requiredProdSettings) {
      if (!setting.value) {
        throw new Error(`${setting.key} is required in production`);
      }
      
      if (setting.minLength && setting.value.length < setting.minLength) {
        throw new Error(`${setting.key} must be at least ${setting.minLength} characters in production`);
      }
      
      if (setting.allowed && !setting.allowed.includes(setting.value)) {
        throw new Error(`${setting.key} must be one of: ${setting.allowed.join(', ')}`);
      }
    }
    
    // Validate security settings
    if (env.NODE_ENV === 'production' && env.DATABASE_SSL_MODE === 'disable') {
      throw new Error('SSL must be enabled for database connections in production');
    }
  }
  
  private async validateServiceConnections(): Promise<void> {
    // This would typically validate connections to external services
    // Implementation depends on your specific services
  }
}
```

## 2. Environment-Specific Configuration

### Environment Configuration Files
```json
// config/development.json
{
  "app": {
    "port": 3000
  },
  "database": {
    "maxConnections": 5,
    "sslMode": "disable"
  },
  "monitoring": {
    "logLevel": "debug",
    "tracingEnabled": true
  },
  "features": {
    "newApi": true,
    "analytics": false
  }
}
```

```json
// config/staging.json
{
  "app": {
    "port": 8080
  },
  "database": {
    "maxConnections": 10,
    "sslMode": "require"
  },
  "monitoring": {
    "logLevel": "info",
    "tracingEnabled": true
  },
  "features": {
    "newApi": true,
    "analytics": true
  }
}
```

```json
// config/production.json
{
  "app": {
    "port": 8080
  },
  "database": {
    "maxConnections": 20,
    "sslMode": "verify-full"
  },
  "monitoring": {
    "logLevel": "warn",
    "tracingEnabled": false
  },
  "features": {
    "newApi": false,
    "analytics": true
  },
  "security": {
    "rateLimit": {
      "windowMs": 900000,
      "maxRequests": 50
    }
  }
}
```

### Docker Environment Configuration
```dockerfile
# Multi-stage Docker configuration with environment support
FROM node:18-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM base AS development
RUN npm ci
ENV NODE_ENV=development
ENV LOG_LEVEL=debug
COPY . .
CMD ["npm", "run", "dev"]

FROM base AS staging
ENV NODE_ENV=staging
ENV LOG_LEVEL=info
COPY . .
RUN npm run build
CMD ["npm", "start"]

FROM base AS production
ENV NODE_ENV=production
ENV LOG_LEVEL=warn
COPY . .
RUN npm run build
USER node
CMD ["npm", "start"]
```

```yaml
# docker-compose.yml - Environment-specific configurations
version: '3.8'

services:
  app-development:
    build:
      context: .
      target: development
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://dev:dev@postgres:5432/myapp_dev
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=debug
    volumes:
      - .:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    depends_on:
      - postgres
      - redis

  app-staging:
    build:
      context: .
      target: staging
    environment:
      - NODE_ENV=staging
      - DATABASE_URL=postgresql://staging:${STAGING_DB_PASSWORD}@postgres:5432/myapp_staging
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${STAGING_JWT_SECRET}
    ports:
      - "8080:8080"

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_MULTIPLE_DATABASES=myapp_dev,myapp_test,myapp_staging
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-databases.sh:/docker-entrypoint-initdb.d/init-databases.sh

volumes:
  postgres_data:
```

## 3. Configuration Validation & Security

### Runtime Configuration Validation
```typescript
// config/validation-middleware.ts
export class ConfigurationValidator {
  static validateStartup(): void {
    const config = ConfigLoader.getInstance().getConfig();
    
    // Validate required services are accessible
    this.validateDatabaseConnection(config.database);
    
    if (config.redis) {
      this.validateRedisConnection(config.redis);
    }
    
    // Validate security configuration
    this.validateSecurityConfig(config.security, config.app.environment);
    
    // Validate feature flags
    this.validateFeatureFlags(config.features);
  }
  
  private static async validateDatabaseConnection(dbConfig: any): Promise<void> {
    try {
      const client = new DatabaseClient(dbConfig);
      await client.query('SELECT 1');
      await client.close();
      console.log('✓ Database connection validated');
    } catch (error) {
      throw new Error(`Database connection failed: ${error.message}`);
    }
  }
  
  private static validateSecurityConfig(security: any, environment: string): void {
    if (environment === 'production') {
      if (!security.corsOrigins || security.corsOrigins.length === 0) {
        throw new Error('CORS origins must be configured in production');
      }
      
      if (security.rateLimit.maxRequests > 1000) {
        console.warn('⚠️  High rate limit detected in production');
      }
    }
  }
  
  private static validateFeatureFlags(features: any): void {
    const flagValidations = {
      newApi: (value: boolean, env: string) => {
        if (value && env === 'production') {
          console.warn('⚠️  New API feature enabled in production');
        }
      },
      analytics: (value: boolean, env: string) => {
        if (!value && env === 'production') {
          console.warn('⚠️  Analytics disabled in production');
        }
      },
    };
    
    Object.entries(features).forEach(([flag, value]) => {
      const validation = flagValidations[flag as keyof typeof flagValidations];
      if (validation) {
        validation(value as boolean, process.env.NODE_ENV!);
      }
    });
  }
}
```

### Configuration Hot Reloading
```typescript
// config/hot-reload.ts
import { watchFile } from 'fs';
import { EventEmitter } from 'events';

export class ConfigurationWatcher extends EventEmitter {
  private configPath: string;
  private currentConfig: any;
  
  constructor(configPath: string) {
    super();
    this.configPath = configPath;
    this.currentConfig = this.loadConfig();
    this.startWatching();
  }
  
  private startWatching(): void {
    watchFile(this.configPath, (curr, prev) => {
      if (curr.mtime !== prev.mtime) {
        this.reloadConfiguration();
      }
    });
  }
  
  private reloadConfiguration(): void {
    try {
      const newConfig = this.loadConfig();
      const changes = this.detectChanges(this.currentConfig, newConfig);
      
      if (changes.length > 0) {
        this.currentConfig = newConfig;
        this.emit('configChanged', { config: newConfig, changes });
        console.log('Configuration reloaded:', changes);
      }
    } catch (error) {
      this.emit('configError', error);
      console.error('Failed to reload configuration:', error);
    }
  }
  
  private detectChanges(old: any, updated: any): string[] {
    const changes: string[] = [];
    
    const traverse = (oldObj: any, newObj: any, path: string = '') => {
      Object.keys({ ...oldObj, ...newObj }).forEach(key => {
        const fullPath = path ? `${path}.${key}` : key;
        
        if (oldObj[key] !== newObj[key]) {
          changes.push(`${fullPath}: ${oldObj[key]} -> ${newObj[key]}`);
        }
        
        if (typeof oldObj[key] === 'object' && typeof newObj[key] === 'object') {
          traverse(oldObj[key], newObj[key], fullPath);
        }
      });
    };
    
    traverse(old, updated);
    return changes;
  }
  
  private loadConfig(): any {
    delete require.cache[require.resolve(this.configPath)];
    return require(this.configPath);
  }
}
```

## 4. Secrets Management Integration

### Secrets Provider Interface
```typescript
// config/secrets-provider.ts
export interface SecretsProvider {
  getSecret(key: string): Promise<string>;
  setSecret(key: string, value: string): Promise<void>;
  deleteSecret(key: string): Promise<void>;
  listSecrets(): Promise<string[]>;
}

export class HashiCorpVaultProvider implements SecretsProvider {
  private client: VaultClient;
  private mountPath: string;
  
  constructor(vaultConfig: VaultConfig) {
    this.client = new VaultClient(vaultConfig);
    this.mountPath = vaultConfig.mountPath || 'secret';
  }
  
  async getSecret(key: string): Promise<string> {
    const result = await this.client.read(`${this.mountPath}/data/${key}`);
    return result?.data?.data?.value;
  }
  
  async setSecret(key: string, value: string): Promise<void> {
    await this.client.write(`${this.mountPath}/data/${key}`, {
      data: { value }
    });
  }
  
  async deleteSecret(key: string): Promise<void> {
    await this.client.delete(`${this.mountPath}/data/${key}`);
  }
  
  async listSecrets(): Promise<string[]> {
    const result = await this.client.list(`${this.mountPath}/metadata`);
    return result?.data?.keys || [];
  }
}

export class AWSSecretsManagerProvider implements SecretsProvider {
  private client: SecretsManagerClient;
  
  constructor(region: string) {
    this.client = new SecretsManagerClient({ region });
  }
  
  async getSecret(key: string): Promise<string> {
    const command = new GetSecretValueCommand({ SecretId: key });
    const result = await this.client.send(command);
    return result.SecretString!;
  }
  
  async setSecret(key: string, value: string): Promise<void> {
    const command = new CreateSecretCommand({
      Name: key,
      SecretString: value
    });
    await this.client.send(command);
  }
  
  async deleteSecret(key: string): Promise<void> {
    const command = new DeleteSecretCommand({ SecretId: key });
    await this.client.send(command);
  }
  
  async listSecrets(): Promise<string[]> {
    const command = new ListSecretsCommand({});
    const result = await this.client.send(command);
    return result.SecretList?.map(s => s.Name!) || [];
  }
}
```

---

## 🛠️ Enforcement & Tooling

### Required CI Checks
- [ ] Environment schema validation and type checking
- [ ] Configuration file syntax validation (JSON/YAML)
- [ ] Environment-specific configuration completeness
- [ ] Secrets management integration testing
- [ ] Production configuration security validation

### Repository Requirements
- [ ] `/config/` directory with environment-specific configurations
- [ ] Environment variable schema definition and validation
- [ ] Docker environment configuration for all environments
- [ ] Secrets management setup and documentation
- [ ] Configuration validation and hot-reload implementation

### Recommended Tools
- **Schema Validation:** Zod, Joi, Yup, JSON Schema
- **Configuration Management:** dotenv, config, node-config
- **Secrets Management:** HashiCorp Vault, AWS Secrets Manager, Azure Key Vault
- **Environment Management:** Docker Compose, Kubernetes ConfigMaps/Secrets
- **Validation:** TypeScript, runtime validation libraries

### Configuration Management Metrics & KPIs
- **Configuration Errors:** Zero configuration-related deployment failures
- **Validation Coverage:** 100% of environment variables validated with schema
- **Secrets Security:** 100% of secrets managed through secure providers
- **Environment Parity:** Consistent configuration across all environments
- **Hot Reload Time:** < 1 second for configuration updates
- **Validation Time:** < 100ms for startup configuration validation

---

*This rule focuses on environment configuration management. See also: CN-15-secrets-management.md for advanced secrets handling and MI-03-service-metadata-roles.md for service configuration standards.* 
---
description: "Universal secrets management: secret stores, rotation, access control, audit. Advanced secrets handling and security standards."
globs: ["**/*"]
alwaysApply: true
---

# 🔐 Universal Secrets Management

## 1. Secret Store Integration

### Secrets Management Requirements
- **USE:** Dedicated secret management systems (Vault, AWS Secrets Manager, Azure Key Vault)
- **IMPLEMENT:** Automatic secret rotation with zero-downtime updates
- **ENFORCE:** Least-privilege access to secrets with comprehensive audit logging
- **MONITOR:** Secret access patterns and rotation compliance

### Multi-Provider Secret Store
```typescript
// secrets/secret-store.ts
export interface SecretMetadata {
  name: string;
  version: string;
  rotationFrequency: string;
  lastRotated: Date;
  nextRotation: Date;
  accessPolicy: string[];
  tags: Record<string, string>;
}

export interface SecretStore {
  get(key: string, version?: string): Promise<string>;
  set(key: string, value: string, metadata?: Partial<SecretMetadata>): Promise<void>;
  delete(key: string): Promise<void>;
  list(): Promise<string[]>;
  getMetadata(key: string): Promise<SecretMetadata>;
  rotate(key: string): Promise<void>;
}

export class UnifiedSecretStore implements SecretStore {
  private providers: Map<string, SecretStore> = new Map();
  private routingConfig: SecretRoutingConfig;
  
  constructor(config: SecretStoreConfig) {
    this.routingConfig = config.routing;
    this.initializeProviders(config);
  }
  
  private initializeProviders(config: SecretStoreConfig): void {
    // HashiCorp Vault
    if (config.vault) {
      this.providers.set('vault', new VaultSecretStore(config.vault));
    }
    
    // AWS Secrets Manager
    if (config.aws) {
      this.providers.set('aws', new AWSSecretsStore(config.aws));
    }
    
    // Azure Key Vault
    if (config.azure) {
      this.providers.set('azure', new AzureKeyVaultStore(config.azure));
    }
    
    // Kubernetes Secrets
    if (config.kubernetes) {
      this.providers.set('k8s', new KubernetesSecretStore(config.kubernetes));
    }
  }
  
  async get(key: string, version?: string): Promise<string> {
    const provider = this.getProviderForSecret(key);
    const store = this.providers.get(provider);
    
    if (!store) {
      throw new Error(`Secret store provider not found: ${provider}`);
    }
    
    try {
      const value = await store.get(key, version);
      await this.auditSecretAccess(key, 'read', provider);
      return value;
    } catch (error) {
      await this.auditSecretAccess(key, 'read_failed', provider, error.message);
      throw error;
    }
  }
  
  async set(key: string, value: string, metadata?: Partial<SecretMetadata>): Promise<void> {
    const provider = this.getProviderForSecret(key);
    const store = this.providers.get(provider);
    
    if (!store) {
      throw new Error(`Secret store provider not found: ${provider}`);
    }
    
    // Add default metadata
    const fullMetadata: Partial<SecretMetadata> = {
      lastRotated: new Date(),
      nextRotation: this.calculateNextRotation(metadata?.rotationFrequency || '90d'),
      tags: {
        environment: process.env.NODE_ENV || 'development',
        service: process.env.SERVICE_NAME || 'unknown',
        ...metadata?.tags
      },
      ...metadata
    };
    
    try {
      await store.set(key, value, fullMetadata);
      await this.auditSecretAccess(key, 'write', provider);
    } catch (error) {
      await this.auditSecretAccess(key, 'write_failed', provider, error.message);
      throw error;
    }
  }
  
  async rotate(key: string): Promise<void> {
    const provider = this.getProviderForSecret(key);
    const store = this.providers.get(provider);
    
    if (!store) {
      throw new Error(`Secret store provider not found: ${provider}`);
    }
    
    try {
      await store.rotate(key);
      await this.auditSecretAccess(key, 'rotated', provider);
      
      // Notify dependent services
      await this.notifySecretRotation(key);
    } catch (error) {
      await this.auditSecretAccess(key, 'rotation_failed', provider, error.message);
      throw error;
    }
  }
  
  private getProviderForSecret(key: string): string {
    // Route secrets to appropriate providers based on configuration
    for (const rule of this.routingConfig.rules) {
      if (this.matchesRoutingRule(key, rule)) {
        return rule.provider;
      }
    }
    return this.routingConfig.defaultProvider;
  }
  
  private matchesRoutingRule(key: string, rule: RoutingRule): boolean {
    if (rule.keyPattern) {
      const regex = new RegExp(rule.keyPattern);
      return regex.test(key);
    }
    
    if (rule.keyPrefix) {
      return key.startsWith(rule.keyPrefix);
    }
    
    return false;
  }
  
  private async auditSecretAccess(
    key: string, 
    action: string, 
    provider: string, 
    error?: string
  ): Promise<void> {
    const auditEntry = {
      timestamp: new Date().toISOString(),
      secretKey: key,
      action,
      provider,
      service: process.env.SERVICE_NAME,
      environment: process.env.NODE_ENV,
      success: !error,
      error,
      metadata: {
        userAgent: process.env.USER_AGENT,
        requestId: process.env.REQUEST_ID
      }
    };
    
    // Send to audit logging system
    await this.sendAuditLog(auditEntry);
  }
}
```

### Provider Implementations
```typescript
// secrets/providers/vault-store.ts
export class VaultSecretStore implements SecretStore {
  private client: VaultApi;
  private mountPath: string;
  
  constructor(config: VaultConfig) {
    this.client = new VaultApi({
      apiVersion: 'v1',
      endpoint: config.endpoint,
      token: config.token
    });
    this.mountPath = config.mountPath || 'secret';
  }
  
  async get(key: string, version?: string): Promise<string> {
    const path = `${this.mountPath}/data/${key}`;
    const options = version ? { version: parseInt(version) } : {};
    
    const result = await this.client.read(path, options);
    
    if (!result?.data?.data?.value) {
      throw new Error(`Secret not found: ${key}`);
    }
    
    return result.data.data.value;
  }
  
  async set(key: string, value: string, metadata?: Partial<SecretMetadata>): Promise<void> {
    const dataPath = `${this.mountPath}/data/${key}`;
    const metadataPath = `${this.mountPath}/metadata/${key}`;
    
    // Store the secret value
    await this.client.write(dataPath, {
      data: { value },
      options: {
        cas: 0 // Create new version
      }
    });
    
    // Store metadata if provided
    if (metadata) {
      await this.client.write(metadataPath, {
        custom_metadata: metadata,
        max_versions: 10,
        delete_version_after: '365d'
      });
    }
  }
  
  async rotate(key: string): Promise<void> {
    const metadata = await this.getMetadata(key);
    const newValue = await this.generateSecret(metadata);
    
    // Create new version
    await this.set(key, newValue, {
      ...metadata,
      lastRotated: new Date(),
      nextRotation: this.calculateNextRotation(metadata.rotationFrequency)
    });
  }
  
  private async generateSecret(metadata: SecretMetadata): Promise<string> {
    // Generate appropriate secret based on type
    const secretType = metadata.tags?.type || 'random';
    
    switch (secretType) {
      case 'api-key':
        return this.generateApiKey();
      case 'password':
        return this.generatePassword();
      case 'jwt-secret':
        return this.generateJwtSecret();
      default:
        return this.generateRandomSecret(32);
    }
  }
  
  private generateApiKey(): string {
    return `ak_${crypto.randomBytes(32).toString('hex')}`;
  }
  
  private generatePassword(): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < 24; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
  }
  
  private generateJwtSecret(): string {
    return crypto.randomBytes(64).toString('base64');
  }
  
  private generateRandomSecret(length: number): string {
    return crypto.randomBytes(length).toString('hex');
  }
}

// secrets/providers/aws-secrets-store.ts
export class AWSSecretsStore implements SecretStore {
  private client: SecretsManagerClient;
  
  constructor(config: AWSSecretsConfig) {
    this.client = new SecretsManagerClient({
      region: config.region,
      credentials: config.credentials
    });
  }
  
  async get(key: string, version?: string): Promise<string> {
    const command = new GetSecretValueCommand({
      SecretId: key,
      VersionId: version
    });
    
    try {
      const result = await this.client.send(command);
      return result.SecretString!;
    } catch (error) {
      if (error.name === 'ResourceNotFoundException') {
        throw new Error(`Secret not found: ${key}`);
      }
      throw error;
    }
  }
  
  async set(key: string, value: string, metadata?: Partial<SecretMetadata>): Promise<void> {
    try {
      // Try to update existing secret
      const updateCommand = new UpdateSecretCommand({
        SecretId: key,
        SecretString: value,
        Description: metadata?.name || `Secret: ${key}`
      });
      
      await this.client.send(updateCommand);
    } catch (error) {
      if (error.name === 'ResourceNotFoundException') {
        // Create new secret
        const createCommand = new CreateSecretCommand({
          Name: key,
          SecretString: value,
          Description: metadata?.name || `Secret: ${key}`,
          Tags: this.metadataToTags(metadata)
        });
        
        await this.client.send(createCommand);
      } else {
        throw error;
      }
    }
  }
  
  private metadataToTags(metadata?: Partial<SecretMetadata>): Tag[] {
    if (!metadata?.tags) return [];
    
    return Object.entries(metadata.tags).map(([key, value]) => ({
      Key: key,
      Value: value
    }));
  }
}
```

## 2. Secret Rotation Management

### Automated Rotation System
```typescript
// secrets/rotation-manager.ts
export class SecretRotationManager {
  private secretStore: UnifiedSecretStore;
  private scheduler: CronScheduler;
  private notificationService: NotificationService;
  
  constructor(
    secretStore: UnifiedSecretStore,
    notificationService: NotificationService
  ) {
    this.secretStore = secretStore;
    this.notificationService = notificationService;
    this.scheduler = new CronScheduler();
  }
  
  async initializeRotationSchedule(): Promise<void> {
    // Check for secrets needing rotation every hour
    this.scheduler.schedule('0 * * * *', async () => {
      await this.checkAndRotateSecrets();
    });
    
    // Generate rotation report daily
    this.scheduler.schedule('0 8 * * *', async () => {
      await this.generateRotationReport();
    });
  }
  
  async checkAndRotateSecrets(): Promise<void> {
    try {
      const secrets = await this.secretStore.list();
      const rotationTasks: Promise<void>[] = [];
      
      for (const secretKey of secrets) {
        rotationTasks.push(this.checkSecretRotation(secretKey));
      }
      
      await Promise.allSettled(rotationTasks);
    } catch (error) {
      console.error('Error in rotation check:', error);
      await this.notificationService.sendAlert(
        'Secret Rotation Check Failed',
        `Failed to check secret rotations: ${error.message}`
      );
    }
  }
  
  private async checkSecretRotation(secretKey: string): Promise<void> {
    try {
      const metadata = await this.secretStore.getMetadata(secretKey);
      
      if (this.needsRotation(metadata)) {
        console.log(`Rotating secret: ${secretKey}`);
        await this.rotateSecretWithValidation(secretKey, metadata);
      }
    } catch (error) {
      console.error(`Failed to check rotation for ${secretKey}:`, error);
    }
  }
  
  private needsRotation(metadata: SecretMetadata): boolean {
    const now = new Date();
    return metadata.nextRotation && now >= metadata.nextRotation;
  }
  
  private async rotateSecretWithValidation(
    secretKey: string,
    metadata: SecretMetadata
  ): Promise<void> {
    try {
      // 1. Create new secret version
      await this.secretStore.rotate(secretKey);
      
      // 2. Wait for propagation
      await this.waitForPropagation();
      
      // 3. Validate new secret works
      await this.validateSecretRotation(secretKey);
      
      // 4. Send success notification
      await this.notificationService.sendInfo(
        'Secret Rotated Successfully',
        `Secret ${secretKey} has been rotated successfully`
      );
      
    } catch (error) {
      // Rollback if possible and alert
      await this.handleRotationFailure(secretKey, error);
    }
  }
  
  private async validateSecretRotation(secretKey: string): Promise<void> {
    // Get the new secret value
    const newValue = await this.secretStore.get(secretKey);
    
    // Perform validation based on secret type
    const metadata = await this.secretStore.getMetadata(secretKey);
    const secretType = metadata.tags?.type || 'random';
    
    switch (secretType) {
      case 'database-password':
        await this.validateDatabaseConnection(newValue);
        break;
      case 'api-key':
        await this.validateApiKey(newValue);
        break;
      case 'jwt-secret':
        await this.validateJwtSecret(newValue);
        break;
      default:
        // Basic validation - ensure secret is not empty
        if (!newValue || newValue.length < 8) {
          throw new Error('Generated secret is too short or empty');
        }
    }
  }
  
  private async validateDatabaseConnection(password: string): Promise<void> {
    // Test database connection with new password
    const testConfig = {
      ...this.getDatabaseConfig(),
      password
    };
    
    const testClient = new DatabaseClient(testConfig);
    try {
      await testClient.query('SELECT 1');
      await testClient.close();
    } catch (error) {
      throw new Error(`Database connection failed with new password: ${error.message}`);
    }
  }
  
  private async validateApiKey(apiKey: string): Promise<void> {
    // Test API key with a simple request
    const response = await fetch(`${process.env.API_BASE_URL}/health`, {
      headers: {
        'Authorization': `Bearer ${apiKey}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`API key validation failed: ${response.status}`);
    }
  }
  
  private async generateRotationReport(): Promise<void> {
    const secrets = await this.secretStore.list();
    const report = {
      timestamp: new Date().toISOString(),
      totalSecrets: secrets.length,
      secretsNeedingRotation: 0,
      secretsRotatedToday: 0,
      rotationCompliance: 0
    };
    
    let needingRotation = 0;
    let rotatedToday = 0;
    
    for (const secretKey of secrets) {
      const metadata = await this.secretStore.getMetadata(secretKey);
      
      if (this.needsRotation(metadata)) {
        needingRotation++;
      }
      
      if (this.wasRotatedToday(metadata)) {
        rotatedToday++;
      }
    }
    
    report.secretsNeedingRotation = needingRotation;
    report.secretsRotatedToday = rotatedToday;
    report.rotationCompliance = ((secrets.length - needingRotation) / secrets.length) * 100;
    
    await this.notificationService.sendReport('Secret Rotation Report', report);
  }
}
```

## 3. Access Control & Audit

### Secret Access Control
```typescript
// secrets/access-control.ts
export interface SecretAccessPolicy {
  secretPattern: string;
  principals: string[];
  actions: SecretAction[];
  conditions?: AccessCondition[];
  effect: 'allow' | 'deny';
}

export type SecretAction = 'read' | 'write' | 'delete' | 'rotate' | 'list';

export interface AccessCondition {
  type: 'ip-range' | 'time-window' | 'environment' | 'service';
  value: string;
}

export class SecretAccessController {
  private policies: SecretAccessPolicy[] = [];
  private auditLogger: AuditLogger;
  
  constructor(auditLogger: AuditLogger) {
    this.auditLogger = auditLogger;
    this.loadPolicies();
  }
  
  async checkAccess(
    principal: string,
    secretKey: string,
    action: SecretAction,
    context: AccessContext
  ): Promise<boolean> {
    const applicable = this.findApplicablePolicies(principal, secretKey, action);
    
    // Default deny if no policies match
    if (applicable.length === 0) {
      await this.auditLogger.logAccessDenied(principal, secretKey, action, 'no-policy');
      return false;
    }
    
    // Evaluate policies (deny takes precedence)
    for (const policy of applicable) {
      if (policy.effect === 'deny' && this.evaluateConditions(policy.conditions, context)) {
        await this.auditLogger.logAccessDenied(principal, secretKey, action, 'explicit-deny');
        return false;
      }
    }
    
    // Check for explicit allow
    for (const policy of applicable) {
      if (policy.effect === 'allow' && this.evaluateConditions(policy.conditions, context)) {
        await this.auditLogger.logAccessGranted(principal, secretKey, action);
        return true;
      }
    }
    
    await this.auditLogger.logAccessDenied(principal, secretKey, action, 'no-allow');
    return false;
  }
  
  private findApplicablePolicies(
    principal: string,
    secretKey: string,
    action: SecretAction
  ): SecretAccessPolicy[] {
    return this.policies.filter(policy => {
      // Check if principal matches
      const principalMatches = policy.principals.some(p => 
        p === principal || p === '*' || this.matchesPattern(principal, p)
      );
      
      // Check if secret pattern matches
      const secretMatches = this.matchesPattern(secretKey, policy.secretPattern);
      
      // Check if action is allowed
      const actionMatches = policy.actions.includes(action) || policy.actions.includes('*' as SecretAction);
      
      return principalMatches && secretMatches && actionMatches;
    });
  }
  
  private evaluateConditions(conditions: AccessCondition[] = [], context: AccessContext): boolean {
    return conditions.every(condition => {
      switch (condition.type) {
        case 'ip-range':
          return this.isIpInRange(context.sourceIp, condition.value);
        case 'time-window':
          return this.isInTimeWindow(new Date(), condition.value);
        case 'environment':
          return context.environment === condition.value;
        case 'service':
          return context.serviceName === condition.value;
        default:
          return false;
      }
    });
  }
  
  private matchesPattern(value: string, pattern: string): boolean {
    if (pattern === '*') return true;
    
    // Convert glob pattern to regex
    const regexPattern = pattern
      .replace(/\*/g, '.*')
      .replace(/\?/g, '.');
    
    return new RegExp(`^${regexPattern}$`).test(value);
  }
}
```

### Audit Logging
```typescript
// secrets/audit-logger.ts
export class SecretAuditLogger {
  private logger: Logger;
  private auditStore: AuditStore;
  
  constructor(logger: Logger, auditStore: AuditStore) {
    this.logger = logger;
    this.auditStore = auditStore;
  }
  
  async logAccessGranted(
    principal: string,
    secretKey: string,
    action: SecretAction,
    context?: AccessContext
  ): Promise<void> {
    const auditEvent = {
      eventType: 'secret-access-granted',
      timestamp: new Date().toISOString(),
      principal,
      secretKey: this.hashSecretKey(secretKey), // Don't log actual secret keys
      action,
      result: 'granted',
      context: {
        sourceIp: context?.sourceIp,
        userAgent: context?.userAgent,
        environment: context?.environment,
        serviceName: context?.serviceName
      }
    };
    
    this.logger.info('Secret access granted', auditEvent);
    await this.auditStore.store(auditEvent);
  }
  
  async logAccessDenied(
    principal: string,
    secretKey: string,
    action: SecretAction,
    reason: string,
    context?: AccessContext
  ): Promise<void> {
    const auditEvent = {
      eventType: 'secret-access-denied',
      timestamp: new Date().toISOString(),
      principal,
      secretKey: this.hashSecretKey(secretKey),
      action,
      result: 'denied',
      reason,
      context: {
        sourceIp: context?.sourceIp,
        userAgent: context?.userAgent,
        environment: context?.environment,
        serviceName: context?.serviceName
      }
    };
    
    this.logger.warn('Secret access denied', auditEvent);
    await this.auditStore.store(auditEvent);
  }
  
  async logSecretRotation(secretKey: string, success: boolean, error?: string): Promise<void> {
    const auditEvent = {
      eventType: 'secret-rotation',
      timestamp: new Date().toISOString(),
      secretKey: this.hashSecretKey(secretKey),
      result: success ? 'success' : 'failure',
      error
    };
    
    if (success) {
      this.logger.info('Secret rotated successfully', auditEvent);
    } else {
      this.logger.error('Secret rotation failed', auditEvent);
    }
    
    await this.auditStore.store(auditEvent);
  }
  
  private hashSecretKey(secretKey: string): string {
    return crypto
      .createHash('sha256')
      .update(secretKey)
      .digest('hex')
      .substring(0, 16); // First 16 chars for identification
  }
}
```

---

## 🛠️ Enforcement & Tooling

### Required CI Checks
- [ ] Secret store configuration validation
- [ ] Secret rotation policy compliance
- [ ] Access control policy validation
- [ ] Audit logging functionality testing
- [ ] Secret leakage scanning in code and configurations

### Repository Requirements
- [ ] `/secrets/` directory with secret management configuration
- [ ] Secret rotation schedules and policies
- [ ] Access control policies and RBAC configuration
- [ ] Audit logging setup and retention policies
- [ ] Secret scanning and monitoring automation

### Recommended Tools
- **Secret Stores:** HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, Google Secret Manager
- **Rotation:** AWS Secrets Manager auto-rotation, Vault dynamic secrets
- **Scanning:** GitLeaks, TruffleHog, detect-secrets, git-secrets
- **Monitoring:** Vault audit logs, CloudTrail, Azure Monitor
- **Access Control:** OPA (Open Policy Agent), AWS IAM, Azure RBAC

### Secrets Management Metrics & KPIs
- **Rotation Compliance:** 100% of secrets rotated within policy timeframes
- **Access Audit:** 100% of secret access events logged and monitored
- **Secret Leakage:** Zero secrets detected in code repositories or logs
- **Availability:** 99.9% uptime for secret store services
- **Access Response Time:** < 100ms for secret retrieval operations
- **Rotation Success Rate:** 99.5% successful automatic rotations

---

*This rule focuses on advanced secrets management. See also: CN-14-environment-configuration.md for basic configuration and CN-13-security-encryption.md for encryption standards.* 
---
description: "Universal security and encryption: encryption standards, secrets management, vulnerability scanning, security monitoring. Comprehensive security controls."
globs: ["**/*"]
alwaysApply: true
---

# 🔒 Universal Security & Encryption

## 1. Encryption Standards

### Encryption Requirements
- **USE:** AES-256 for symmetric encryption, RSA-4096 or ECDSA P-384 for asymmetric
- **IMPLEMENT:** Encryption at rest for all sensitive data storage
- **ENFORCE:** TLS 1.3+ for all data in transit
- **ROTATE:** Encryption keys regularly with automated key management

### Encryption Implementation Template
```typescript
// encryption-service.ts
import crypto from 'crypto';

export class EncryptionService {
  private algorithm = 'aes-256-gcm';
  private keyLength = 32; // 256 bits
  
  async encryptData(data: string, key?: Buffer): Promise<{
    encrypted: string;
    iv: string;
    authTag: string;
    keyId?: string;
  }> {
    const encryptionKey = key || await this.getActiveKey();
    const iv = crypto.randomBytes(16);
    
    const cipher = crypto.createCipher(this.algorithm, encryptionKey);
    cipher.setAAD(Buffer.from('additional-auth-data'));
    
    let encrypted = cipher.update(data, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return {
      encrypted,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex'),
      keyId: await this.getActiveKeyId()
    };
  }
  
  async decryptData(encryptedData: {
    encrypted: string;
    iv: string;
    authTag: string;
    keyId?: string;
  }): Promise<string> {
    const key = await this.getKey(encryptedData.keyId);
    const decipher = crypto.createDecipher(this.algorithm, key);
    
    decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));
    decipher.setAAD(Buffer.from('additional-auth-data'));
    
    let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }
  
  async generateKey(): Promise<Buffer> {
    return crypto.randomBytes(this.keyLength);
  }
  
  private async getActiveKey(): Promise<Buffer> {
    // Get from key management service
    return crypto.randomBytes(this.keyLength);
  }
  
  private async getKey(keyId?: string): Promise<Buffer> {
    // Get specific key from key management service
    return crypto.randomBytes(this.keyLength);
  }
  
  private async getActiveKeyId(): Promise<string> {
    // Get current active key ID
    return 'key-2024-01';
  }
}
```

### Database Encryption
```sql
-- PostgreSQL encryption at rest example
-- Enable transparent data encryption
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/path/to/server.crt';
ALTER SYSTEM SET ssl_key_file = '/path/to/server.key';

-- Column-level encryption for sensitive data
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive columns
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL,
  encrypted_ssn BYTEA,  -- Store encrypted
  created_at TIMESTAMP DEFAULT NOW()
);

-- Insert with encryption
INSERT INTO users (email, encrypted_ssn) 
VALUES ('user@example.com', pgp_sym_encrypt('123-45-6789', 'encryption-key'));

-- Query with decryption
SELECT id, email, pgp_sym_decrypt(encrypted_ssn, 'encryption-key') as ssn 
FROM users WHERE id = $1;
```

## 2. Secrets Management

### Secrets Management Requirements
- **USE:** Dedicated secrets management systems (Vault, AWS Secrets Manager, K8s Secrets)
- **NEVER:** Store secrets in code, configuration files, or environment variables in repos
- **IMPLEMENT:** Automatic secret rotation with zero-downtime updates
- **ENFORCE:** Least-privilege access to secrets with audit logging

### Secrets Management Implementation
```typescript
// secrets-manager.ts
export interface SecretMetadata {
  name: string;
  version: string;
  rotationFrequency: string;
  lastRotated: Date;
  nextRotation: Date;
  accessPolicy: string[];
}

export class SecretsManager {
  private vault: VaultClient;
  
  constructor(vaultConfig: VaultConfig) {
    this.vault = new VaultClient(vaultConfig);
  }
  
  async getSecret(secretName: string, version?: string): Promise<string> {
    try {
      const secret = await this.vault.read(`secret/data/${secretName}`, {
        version
      });
      
      await this.auditSecretAccess(secretName, 'read');
      return secret.data.data.value;
    } catch (error) {
      await this.auditSecretAccess(secretName, 'read_failed');
      throw new Error(`Failed to retrieve secret: ${secretName}`);
    }
  }
  
  async setSecret(
    secretName: string, 
    value: string, 
    metadata?: Partial<SecretMetadata>
  ): Promise<void> {
    try {
      await this.vault.write(`secret/data/${secretName}`, {
        data: { value },
        options: {
          cas: 0  // Create new version
        }
      });
      
      if (metadata) {
        await this.vault.write(`secret/metadata/${secretName}`, metadata);
      }
      
      await this.auditSecretAccess(secretName, 'write');
    } catch (error) {
      await this.auditSecretAccess(secretName, 'write_failed');
      throw new Error(`Failed to store secret: ${secretName}`);
    }
  }
  
  async rotateSecret(secretName: string): Promise<void> {
    const metadata = await this.getSecretMetadata(secretName);
    const newSecret = await this.generateSecret(metadata);
    
    // Store new version
    await this.setSecret(secretName, newSecret);
    
    // Update applications using the secret
    await this.notifySecretRotation(secretName);
    
    await this.auditSecretAccess(secretName, 'rotated');
  }
  
  private async generateSecret(metadata: SecretMetadata): Promise<string> {
    // Generate new secret based on type
    if (metadata.name.includes('api-key')) {
      return crypto.randomBytes(32).toString('hex');
    } else if (metadata.name.includes('password')) {
      return this.generateStrongPassword();
    }
    return crypto.randomBytes(32).toString('base64');
  }
  
  private generateStrongPassword(): string {
    const length = 32;
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let password = '';
    
    for (let i = 0; i < length; i++) {
      password += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    
    return password;
  }
  
  private async auditSecretAccess(
    secretName: string, 
    action: string
  ): Promise<void> {
    // Log to audit system
    console.log(`Secret access: ${action} on ${secretName} at ${new Date()}`);
  }
  
  private async getSecretMetadata(secretName: string): Promise<SecretMetadata> {
    const metadata = await this.vault.read(`secret/metadata/${secretName}`);
    return metadata.data;
  }
  
  private async notifySecretRotation(secretName: string): Promise<void> {
    // Notify applications about secret rotation
    // This could trigger redeployment or config reload
  }
}
```

### Kubernetes Secrets Management
```yaml
# external-secrets-operator.yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-secret-store
  namespace: default
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "external-secrets"

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-secret-store
    kind: SecretStore
  target:
    name: database-secret
    creationPolicy: Owner
  data:
    - secretKey: username
      remoteRef:
        key: database/credentials
        property: username
    - secretKey: password
      remoteRef:
        key: database/credentials
        property: password
```

## 3. Vulnerability Scanning

### Vulnerability Scanning Requirements
- **IMPLEMENT:** Automated vulnerability scanning in CI/CD pipelines
- **SCAN:** Container images, dependencies, and infrastructure as code
- **BLOCK:** Deployments with HIGH or CRITICAL vulnerabilities
- **TRACK:** Vulnerability remediation with SLA enforcement

### Container Security Scanning
```yaml
# .github/workflows/security-scan.yml
name: Security Scanning
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  vulnerability-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t ${{ github.repository }}:${{ github.sha }} .
        
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ github.repository }}:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'  # Fail on critical/high
          
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'
          
      - name: Run Grype vulnerability scanner
        uses: anchore/scan-action@v3
        with:
          image: ${{ github.repository }}:${{ github.sha }}
          severity-cutoff: high
          fail-build: true
          
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
          
      - name: Run npm audit
        run: |
          npm audit --audit-level high
          npm audit fix --dry-run
          
  sast-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/owasp-top-ten
          publishToken: ${{ secrets.SEMGREP_APP_TOKEN }}
          
      - name: Run CodeQL Analysis
        uses: github/codeql-action/analyze@v2
        with:
          languages: typescript, javascript
```

### Infrastructure Security Scanning
```yaml
# infrastructure-security.yml
name: Infrastructure Security
on:
  push:
    paths: ['infrastructure/**', 'terraform/**', 'k8s/**']

jobs:
  iac-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: terraform,kubernetes
          soft_fail: false
          download_external_modules: true
          
      - name: Run Terrascan
        uses: accurics/terrascan-action@main
        with:
          iac_type: 'terraform'
          iac_version: 'v14'
          policy_type: 'aws'
          only_warn: false
          
      - name: Run kube-score
        run: |
          wget https://github.com/zegl/kube-score/releases/latest/download/kube-score_linux_amd64 -O kube-score
          chmod +x kube-score
          ./kube-score score k8s/*.yaml --output-format ci
```

## 4. Security Monitoring

### Security Monitoring Requirements
- **IMPLEMENT:** Real-time security event monitoring and alerting
- **COLLECT:** Security logs from all services and infrastructure
- **DETECT:** Suspicious activities and potential security incidents
- **RESPOND:** Automated incident response for common security events

### Security Event Collection
```typescript
// security-monitor.ts
export interface SecurityEvent {
  timestamp: Date;
  eventType: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  source: string;
  userId?: string;
  ipAddress: string;
  userAgent?: string;
  details: Record<string, any>;
}

export class SecurityMonitor {
  private eventCollector: EventCollector;
  
  async logSecurityEvent(event: SecurityEvent): Promise<void> {
    // Enrich event with additional context
    const enrichedEvent = await this.enrichEvent(event);
    
    // Store event
    await this.eventCollector.collect(enrichedEvent);
    
    // Check for immediate response needed
    if (event.severity === 'CRITICAL') {
      await this.triggerIncidentResponse(enrichedEvent);
    }
    
    // Check for patterns
    await this.checkSecurityPatterns(enrichedEvent);
  }
  
  private async enrichEvent(event: SecurityEvent): Promise<SecurityEvent> {
    return {
      ...event,
      details: {
        ...event.details,
        geolocation: await this.getGeolocation(event.ipAddress),
        threatIntelligence: await this.checkThreatIntel(event.ipAddress),
        userContext: event.userId ? await this.getUserContext(event.userId) : null
      }
    };
  }
  
  private async checkSecurityPatterns(event: SecurityEvent): Promise<void> {
    // Check for brute force attacks
    if (event.eventType === 'failed_login') {
      const recentFailures = await this.getRecentFailedLogins(
        event.ipAddress, 
        event.userId
      );
      
      if (recentFailures.length > 5) {
        await this.logSecurityEvent({
          timestamp: new Date(),
          eventType: 'brute_force_detected',
          severity: 'HIGH',
          source: 'security_monitor',
          ipAddress: event.ipAddress,
          details: {
            failureCount: recentFailures.length,
            timeWindow: '5m'
          }
        });
      }
    }
    
    // Check for unusual access patterns
    if (event.eventType === 'resource_access') {
      const isUnusual = await this.checkUnusualAccess(event);
      if (isUnusual) {
        await this.logSecurityEvent({
          timestamp: new Date(),
          eventType: 'unusual_access_pattern',
          severity: 'MEDIUM',
          source: 'security_monitor',
          ipAddress: event.ipAddress,
          userId: event.userId,
          details: {
            originalEvent: event,
            reason: 'access_outside_normal_hours'
          }
        });
      }
    }
  }
  
  private async triggerIncidentResponse(event: SecurityEvent): Promise<void> {
    // Create incident ticket
    const incident = await this.createIncident(event);
    
    // Notify security team
    await this.notifySecurityTeam(incident);
    
    // Auto-remediation for known threats
    if (event.eventType === 'malicious_ip_detected') {
      await this.blockIpAddress(event.ipAddress);
    }
  }
  
  private async getGeolocation(ipAddress: string): Promise<any> {
    // Get geolocation data
    return {};
  }
  
  private async checkThreatIntel(ipAddress: string): Promise<any> {
    // Check against threat intelligence feeds
    return {};
  }
  
  private async getUserContext(userId: string): Promise<any> {
    // Get user context and recent activity
    return {};
  }
  
  private async getRecentFailedLogins(
    ipAddress: string, 
    userId?: string
  ): Promise<SecurityEvent[]> {
    // Query recent failed login attempts
    return [];
  }
  
  private async checkUnusualAccess(event: SecurityEvent): Promise<boolean> {
    // Machine learning-based anomaly detection
    return false;
  }
  
  private async createIncident(event: SecurityEvent): Promise<string> {
    // Create incident in incident management system
    return 'INC-' + Date.now();
  }
  
  private async notifySecurityTeam(incidentId: string): Promise<void> {
    // Send alert to security team
  }
  
  private async blockIpAddress(ipAddress: string): Promise<void> {
    // Add IP to firewall block list
  }
}
```

## 5. Security Headers & Policies

### Security Headers Requirements
- **IMPLEMENT:** Comprehensive security headers for all HTTP responses
- **CONFIGURE:** Content Security Policy (CSP) with strict rules
- **ENABLE:** HTTP Strict Transport Security (HSTS)
- **SET:** Appropriate security headers for API responses

### Security Headers Implementation
```typescript
// security-headers.ts
export function securityHeaders() {
  return (req: Request, res: Response, next: NextFunction) => {
    // Strict Transport Security
    res.setHeader(
      'Strict-Transport-Security',
      'max-age=31536000; includeSubDomains; preload'
    );
    
    // Content Security Policy
    res.setHeader(
      'Content-Security-Policy',
      "default-src 'self'; " +
      "script-src 'self' 'unsafe-inline'; " +
      "style-src 'self' 'unsafe-inline'; " +
      "img-src 'self' data: https:; " +
      "font-src 'self'; " +
      "connect-src 'self'; " +
      "frame-ancestors 'none';"
    );
    
    // X-Frame-Options
    res.setHeader('X-Frame-Options', 'DENY');
    
    // X-Content-Type-Options
    res.setHeader('X-Content-Type-Options', 'nosniff');
    
    // X-XSS-Protection
    res.setHeader('X-XSS-Protection', '1; mode=block');
    
    // Referrer Policy
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    
    // Permissions Policy
    res.setHeader(
      'Permissions-Policy',
      'geolocation=(), microphone=(), camera=()'
    );
    
    // Remove server information
    res.removeHeader('X-Powered-By');
    
    next();
  };
}
```

---

## 🛠️ Enforcement & Tooling

### Required CI Checks
- [ ] Vulnerability scanning (container, dependencies, SAST)
- [ ] Secrets detection and validation
- [ ] Security headers configuration verification
- [ ] Encryption implementation testing
- [ ] Security policy compliance checking

### Repository Requirements
- [ ] Vulnerability scanning configuration
- [ ] Secrets management setup
- [ ] Security monitoring implementation
- [ ] Encryption service implementation
- [ ] Security headers middleware

### Recommended Tools
- **Vulnerability Scanning:** Trivy, Grype, Snyk, Semgrep
- **Secrets Management:** HashiCorp Vault, AWS Secrets Manager, External Secrets Operator
- **Security Monitoring:** Falco, Grafana, Elasticsearch, Splunk
- **Encryption:** OpenSSL, AWS KMS, Google Cloud KMS, Azure Key Vault

### Security Metrics
- **Vulnerability Management:** Mean time to remediation, vulnerability count by severity
- **Secrets Security:** Secret rotation frequency, unauthorized access attempts
- **Security Monitoring:** Security event volume, incident response time
- **Encryption Coverage:** Percentage of sensitive data encrypted at rest and in transit

---

*This rule focuses on security and encryption standards. See also: CN-11-authentication-systems.md for authentication and CN-12-authorization-rbac.md for authorization and access control.* 
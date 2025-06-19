# SEC-04: Comprehensive Identity & Access Management

## Purpose & Scope

Comprehensive identity and access management ensures secure authentication, authorization, and access control through integrated systems covering OAuth2/OIDC, RBAC, multi-factor authentication, and session management. This rule establishes unified standards for the complete identity lifecycle from authentication to access control to security hardening.

## Core Standards

### 1. Authentication Foundation

#### OAuth2 & OpenID Connect Implementation

**Enterprise Authentication Architecture:**
```yaml
# enterprise-auth-config.yaml
authentication_framework:
  oauth2_oidc:
    authorization_server:
      issuer: "https://auth.example.com"
      authorization_endpoint: "https://auth.example.com/oauth2/authorize"
      token_endpoint: "https://auth.example.com/oauth2/token"
      userinfo_endpoint: "https://auth.example.com/oauth2/userinfo"
      jwks_uri: "https://auth.example.com/.well-known/jwks.json"
      
    security_configuration:
      require_pkce: true
      require_state: true
      enforce_https: true
      token_binding_enabled: true
      
    client_configurations:
      web_application:
        client_type: "confidential"
        grant_types: ["authorization_code", "refresh_token"]
        response_types: ["code"]
        redirect_uris: ["https://app.example.com/callback"]
        scope: "openid profile email"
        token_endpoint_auth_method: "client_secret_jwt"
        
      single_page_app:
        client_type: "public"
        grant_types: ["authorization_code", "refresh_token"]
        response_types: ["code"]
        redirect_uris: ["https://spa.example.com/callback"]
        scope: "openid profile email"
        pkce_required: true
        
      mobile_application:
        client_type: "public"
        grant_types: ["authorization_code", "refresh_token"]
        response_types: ["code"]
        redirect_uris: ["com.example.app://callback"]
        scope: "openid profile email offline_access"
        pkce_required: true
        
      service_to_service:
        client_type: "confidential"
        grant_types: ["client_credentials"]
        scope: "api:read api:write"
        token_endpoint_auth_method: "private_key_jwt"

    token_management:
      access_token:
        lifetime: "15m"
        type: "JWT"
        signing_algorithm: "RS256"
        audience_validation: true
        
      refresh_token:
        lifetime: "7d"
        rotation_enabled: true
        absolute_lifetime: "30d"
        reuse_detection: true
        
      id_token:
        lifetime: "1h"
        signing_algorithm: "RS256"
        nonce_required: true
```

#### JWT Implementation Standards

**Secure JWT Processing:**
```typescript
// comprehensive-jwt-service.ts
export interface EnterpriseJWTPayload {
  // Standard Claims (RFC 7519)
  iss: string;      // Issuer
  aud: string[];    // Audience  
  sub: string;      // Subject (user ID)
  iat: number;      // Issued At
  exp: number;      // Expiration Time
  nbf?: number;     // Not Before
  jti?: string;     // JWT ID
  
  // Authentication Context
  auth_time?: number;       // Authentication timestamp
  acr?: string;            // Authentication Context Class Reference
  amr?: string[];          // Authentication Methods References
  azp?: string;            // Authorized Party
  
  // Authorization Claims
  roles: string[];         // User roles
  permissions: string[];   // Specific permissions
  scope?: string;          // OAuth2 scopes
  groups?: string[];       // User groups
  
  // Organizational Context
  tenant?: string;         // Multi-tenant identifier
  organization?: string;   // Organization identifier
  department?: string;     // Department/division
  cost_center?: string;    // Financial allocation
  
  // Session Management
  session_id?: string;     // Session identifier
  session_state?: string;  // Session state for logout
  
  // Security Context
  security_level?: number; // Security clearance level
  data_classification?: string; // Data access classification
  ip_address?: string;     // Source IP (for audit)
  user_agent_hash?: string; // User agent fingerprint
}

export class EnterpriseJWTService {
  private jwksClient: jwksClient.JwksClient;
  private securityConfig: SecurityConfig;
  
  constructor(config: {
    issuer: string;
    audience: string[];
    jwksUri: string;
    securityConfig: SecurityConfig;
  }) {
    this.jwksClient = jwksClient({
      jwksUri: config.jwksUri,
      cache: true,
      cacheMaxAge: 600000, // 10 minutes
      rateLimit: true,
      jwksRequestsPerMinute: 10,
      timeout: 30000
    });
    
    this.securityConfig = config.securityConfig;
  }
  
  async validateToken(token: string, requiredScopes?: string[]): Promise<EnterpriseJWTPayload> {
    try {
      // Validate JWT structure and signature
      const payload = await this.verifyJWTSignature(token);
      
      // Validate security context
      await this.validateSecurityContext(payload);
      
      // Validate scopes if required
      if (requiredScopes && !this.validateScopes(payload, requiredScopes)) {
        throw new Error('Insufficient scope');
      }
      
      // Check for revocation
      await this.checkRevocation(payload);
      
      return payload;
      
    } catch (error) {
      throw new Error(`JWT validation failed: ${error.message}`);
    }
  }
  
  private async verifyJWTSignature(token: string): Promise<EnterpriseJWTPayload> {
    return new Promise((resolve, reject) => {
      jwt.verify(token, this.getSigningKey.bind(this), {
        issuer: this.config.issuer,
        audience: this.config.audience,
        algorithms: ['RS256', 'RS384', 'RS512'],
        clockTolerance: 30, // 30 seconds clock skew tolerance
        maxAge: '1h' // Maximum token age
      }, (err, decoded) => {
        if (err) {
          reject(err);
        } else {
          resolve(decoded as EnterpriseJWTPayload);
        }
      });
    });
  }
  
  private async validateSecurityContext(payload: EnterpriseJWTPayload): Promise<void> {
    // Validate authentication time
    if (payload.auth_time && Date.now() / 1000 - payload.auth_time > this.securityConfig.maxAuthAge) {
      throw new Error('Authentication too old');
    }
    
    // Validate session
    if (payload.session_id && !(await this.validateSession(payload.session_id))) {
      throw new Error('Invalid session');
    }
    
    // Validate IP restrictions if configured
    if (this.securityConfig.ipRestrictions && payload.ip_address) {
      if (!this.validateIPRestriction(payload.ip_address)) {
        throw new Error('IP address not authorized');
      }
    }
  }
  
  private validateScopes(payload: EnterpriseJWTPayload, requiredScopes: string[]): boolean {
    const userScopes = payload.scope?.split(' ') || [];
    return requiredScopes.every(scope => userScopes.includes(scope));
  }
}
```

### 2. Authorization & Access Control

#### Enterprise RBAC Framework

**Comprehensive Role-Based Access Control:**
```yaml
# enterprise-rbac-framework.yaml
rbac_framework:
  version: "2.0"
  last_updated: "2024-01-15"
  
  organizational_hierarchy:
    root_organization:
      name: "enterprise"
      type: "organization"
      children: ["business_units"]
      
    business_units:
      engineering:
        name: "Engineering Division"
        type: "division"
        children: ["teams"]
        
      finance:
        name: "Finance Division" 
        type: "division"
        children: ["teams"]
        
    teams:
      platform_engineering:
        name: "Platform Engineering"
        parent: "engineering"
        type: "team"
        
      security_engineering:
        name: "Security Engineering"
        parent: "engineering"
        type: "team"

  role_definitions:
    # Executive Roles
    global_admin:
      description: "Global administrative access across all systems"
      permissions: ["*:*:*"]
      max_assignments: 3
      approval_required: true
      mfa_required: true
      session_timeout: "30m"
      audit_level: "high"
      
    organization_admin:
      description: "Administrative access within organization scope"
      permissions:
        - "users:*:org:{organization}"
        - "groups:*:org:{organization}"
        - "resources:*:org:{organization}"
      scoped_to: "organization"
      max_assignments: 5
      approval_required: true
      mfa_required: true
      
    # Operational Roles
    platform_engineer:
      description: "Platform infrastructure management"
      permissions:
        - "infrastructure:*:*"
        - "deployments:*:*"
        - "monitoring:read:*"
        - "logs:read:*"
        - "secrets:read:env:{environment}"
      environments: ["development", "staging", "production"]
      max_assignments: 20
      inherits_from: ["base_engineer"]
      
    security_engineer:
      description: "Security tools and policy management"
      permissions:
        - "security:*:*"
        - "policies:*:*"
        - "audit:read:*"
        - "compliance:*:*"
        - "vulnerabilities:*:*"
      max_assignments: 10
      inherits_from: ["base_engineer"]
      mfa_required: true
      
    # Developer Roles
    senior_developer:
      description: "Senior development with deployment rights"
      permissions:
        - "code:*:project:{project}"
        - "deployments:create:env:development"
        - "deployments:create:env:staging"
        - "monitoring:read:project:{project}"
        - "logs:read:project:{project}"
      scoped_to: "project"
      max_assignments: 50
      inherits_from: ["developer"]
      
    developer:
      description: "Standard development access"
      permissions:
        - "code:read:project:{project}"
        - "code:write:project:{project}"
        - "deployments:read:env:development"
        - "monitoring:read:project:{project}"
      scoped_to: "project"
      max_assignments: 200
      
    # Service Roles
    service_account:
      description: "Automated service access"
      permissions:
        - "api:read:service:{service}"
        - "api:write:service:{service}"
        - "metrics:write:service:{service}"
      scoped_to: "service"
      certificate_based: true
      no_interactive_login: true

  permission_catalog:
    "users:create":
      description: "Create new user accounts"
      resources: ["user"]
      sensitive: true
      
    "users:read":
      description: "View user information"
      resources: ["user", "profile"]
      
    "deployments:create":
      description: "Create new deployments"
      resources: ["deployment", "environment"]
      sensitive: true
      requires_approval: ["production"]
      
    "secrets:read":
      description: "Access secret values"
      resources: ["secret", "credential"]
      sensitive: true
      audit_required: true

  access_policies:
    environment_separation:
      description: "Enforce environment-based access separation"
      rules:
        - "production access requires senior+ role"
        - "production deployments require approval"
        - "cross-environment access prohibited"
        
    data_classification:
      description: "Enforce data classification access controls"
      rules:
        - "confidential data requires security clearance"
        - "pii access requires privacy training"
        - "financial data requires finance role"
        
    temporal_controls:
      description: "Time-based access restrictions"
      rules:
        - "administrative access limited to business hours"
        - "emergency access available 24/7 with approval"
        - "scheduled access for maintenance windows"
```

#### Dynamic Authorization Policies

**Policy-Based Access Control:**
```yaml
# opa-authorization-policies.rego
package enterprise.authorization

import rego.v1

# Default deny policy
default allow = false

# Allow access if user has required permission
allow if {
    user_has_permission(input.user, input.action, input.resource)
}

# Allow access if user has required role
allow if {
    user_has_role(input.user, required_role)
    role_has_permission(required_role, input.action, input.resource)
}

# Allow emergency access with proper justification
allow if {
    input.emergency_access == true
    input.justification != ""
    user_has_emergency_role(input.user)
}

# Helper functions
user_has_permission(user, action, resource) if {
    permission := sprintf("%s:%s", [action, resource])
    permission in data.users[user].permissions
}

user_has_role(user, role) if {
    role in data.users[user].roles
}

role_has_permission(role, action, resource) if {
    permission := sprintf("%s:%s", [action, resource])
    permission in data.roles[role].permissions
}

# Environment-specific rules
allow if {
    input.environment == "development"
    user_has_role(input.user, "developer")
}

allow if {
    input.environment == "production"
    user_has_role(input.user, "senior_developer")
    time.now_ns() > data.users[input.user].last_security_training
}

# Data classification rules
allow if {
    input.data_classification == "public"
}

allow if {
    input.data_classification == "internal"
    user_belongs_to_organization(input.user)
}

allow if {
    input.data_classification == "confidential"
    user_has_security_clearance(input.user, "confidential")
}

allow if {
    input.data_classification == "restricted"
    user_has_security_clearance(input.user, "restricted")
    mfa_recently_verified(input.user)
}
```

### 3. Multi-Factor Authentication & Hardening

#### Comprehensive MFA Implementation

**Enterprise MFA Framework:**
```yaml
# enterprise-mfa-config.yaml
mfa_framework:
  policy_configuration:
    global_requirements:
      admin_accounts: "required"
      privileged_operations: "required"
      sensitive_data_access: "required"
      production_environment: "required"
      
    user_tier_requirements:
      executives:
        methods: ["hardware_token", "biometric", "totp"]
        backup_methods: ["recovery_codes"]
        verification_frequency: "8h"
        
      administrators:
        methods: ["hardware_token", "totp", "webauthn"]
        backup_methods: ["recovery_codes", "admin_recovery"]
        verification_frequency: "4h"
        
      developers:
        methods: ["totp", "webauthn", "sms"]
        backup_methods: ["recovery_codes"]
        verification_frequency: "24h"
        
      standard_users:
        methods: ["totp", "sms", "email"]
        backup_methods: ["recovery_codes"]
        verification_frequency: "7d"

  authentication_methods:
    hardware_tokens:
      yubikey:
        protocols: ["FIDO2", "U2F", "OTP"]
        required_for: ["admin", "executive"]
        enrollment_required: true
        
      smart_cards:
        protocols: ["PIV", "PKI"]
        required_for: ["government", "high_security"]
        certificate_required: true
        
    software_tokens:
      totp:
        algorithms: ["SHA1", "SHA256", "SHA512"]
        time_step: 30
        window: 1
        backup_codes: 10
        
      push_notifications:
        providers: ["duo", "okta", "azure_mfa"]
        timeout: "60s"
        fallback_enabled: true
        
    biometric_authentication:
      fingerprint:
        enabled: true
        quality_threshold: "high"
        liveness_detection: true
        
      facial_recognition:
        enabled: true
        anti_spoofing: true
        privacy_compliant: true

  risk_based_authentication:
    risk_factors:
      location_based:
        new_location: "high_risk"
        impossible_travel: "critical_risk"
        vpn_usage: "medium_risk"
        
      device_based:
        new_device: "high_risk"
        unmanaged_device: "high_risk"
        mobile_device: "medium_risk"
        
      behavioral_based:
        unusual_access_time: "medium_risk"
        unusual_access_pattern: "medium_risk"
        failed_attempts: "high_risk"
        
    adaptive_responses:
      low_risk:
        action: "allow"
        logging: "standard"
        
      medium_risk:
        action: "require_mfa"
        logging: "enhanced"
        
      high_risk:
        action: "require_additional_mfa"
        logging: "detailed"
        admin_notification: true
        
      critical_risk:
        action: "block_and_alert"
        logging: "full_audit"
        security_team_alert: true
        user_notification: true
```

#### Session Security & Management

**Advanced Session Controls:**
```typescript
// enterprise-session-management.ts
export interface SessionSecurity {
  sessionId: string;
  userId: string;
  deviceFingerprint: string;
  ipAddress: string;
  userAgent: string;
  authenticationLevel: number;
  mfaVerified: boolean;
  lastActivity: Date;
  expiresAt: Date;
  securityContext: SecurityContext;
}

export interface SecurityContext {
  dataClassification: string[];
  environmentAccess: string[];
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  authenticationMethods: string[];
  deviceTrust: 'trusted' | 'unknown' | 'untrusted';
  locationTrust: 'trusted' | 'known' | 'unknown' | 'suspicious';
}

export class EnterpriseSessionManager {
  private sessionStore: SessionStore;
  private securityPolicies: SecurityPolicies;
  
  async createSession(authResult: AuthenticationResult): Promise<SessionSecurity> {
    const session: SessionSecurity = {
      sessionId: this.generateSecureSessionId(),
      userId: authResult.userId,
      deviceFingerprint: authResult.deviceFingerprint,
      ipAddress: authResult.ipAddress,
      userAgent: authResult.userAgent,
      authenticationLevel: this.calculateAuthLevel(authResult),
      mfaVerified: authResult.mfaVerified,
      lastActivity: new Date(),
      expiresAt: this.calculateExpiration(authResult),
      securityContext: await this.buildSecurityContext(authResult)
    };
    
    // Apply security policies
    await this.enforceSessionPolicies(session);
    
    // Store session securely
    await this.sessionStore.store(session);
    
    // Audit session creation
    await this.auditService.logSessionEvent('session_created', session);
    
    return session;
  }
  
  async validateSession(sessionId: string, request: Request): Promise<SessionSecurity> {
    const session = await this.sessionStore.get(sessionId);
    
    if (!session) {
      throw new Error('Session not found');
    }
    
    // Check expiration
    if (session.expiresAt < new Date()) {
      await this.terminateSession(sessionId, 'expired');
      throw new Error('Session expired');
    }
    
    // Validate device fingerprint
    if (session.deviceFingerprint !== request.deviceFingerprint) {
      await this.terminateSession(sessionId, 'device_mismatch');
      throw new Error('Device fingerprint mismatch');
    }
    
    // Check for suspicious activity
    await this.detectSuspiciousActivity(session, request);
    
    // Update last activity
    session.lastActivity = new Date();
    await this.sessionStore.update(session);
    
    // Apply continuous authentication
    await this.applyContinuousAuthentication(session, request);
    
    return session;
  }
  
  private async enforceSessionPolicies(session: SessionSecurity): Promise<void> {
    const policies = await this.securityPolicies.getForUser(session.userId);
    
    // Enforce concurrent session limits
    const activeSessions = await this.sessionStore.getActiveForUser(session.userId);
    if (activeSessions.length >= policies.maxConcurrentSessions) {
      // Terminate oldest session
      const oldestSession = activeSessions.sort((a, b) => 
        a.lastActivity.getTime() - b.lastActivity.getTime()
      )[0];
      await this.terminateSession(oldestSession.sessionId, 'session_limit');
    }
    
    // Enforce authentication level requirements
    if (session.authenticationLevel < policies.minimumAuthLevel) {
      throw new Error('Insufficient authentication level');
    }
    
    // Enforce MFA requirements
    if (policies.requireMFA && !session.mfaVerified) {
      throw new Error('MFA required for this user');
    }
  }
  
  private async applyContinuousAuthentication(
    session: SessionSecurity, 
    request: Request
  ): Promise<void> {
    // Risk-based re-authentication
    const riskScore = await this.calculateRiskScore(session, request);
    
    if (riskScore > this.securityPolicies.riskThresholds.high) {
      // Require immediate re-authentication
      session.authenticationLevel = 0;
      await this.sessionStore.update(session);
      throw new Error('Re-authentication required due to high risk');
    }
    
    // Time-based re-authentication
    const timeSinceAuth = Date.now() - session.lastActivity.getTime();
    const maxAuthAge = this.securityPolicies.getMaxAuthAge(session.securityContext);
    
    if (timeSinceAuth > maxAuthAge) {
      session.authenticationLevel = Math.max(0, session.authenticationLevel - 1);
      await this.sessionStore.update(session);
    }
  }
}
```

### 4. Session Security & Management

#### Advanced Session Controls

**Secure Session Management:**
```typescript
// enterprise-session-management.ts
export interface SessionSecurity {
  sessionId: string;
  userId: string;
  deviceFingerprint: string;
  ipAddress: string;
  authenticationLevel: number;
  mfaVerified: boolean;
  lastActivity: Date;
  expiresAt: Date;
  securityContext: SecurityContext;
}

export class EnterpriseSessionManager {
  async createSession(authResult: AuthenticationResult): Promise<SessionSecurity> {
    const session: SessionSecurity = {
      sessionId: this.generateSecureSessionId(),
      userId: authResult.userId,
      deviceFingerprint: authResult.deviceFingerprint,
      ipAddress: authResult.ipAddress,
      authenticationLevel: this.calculateAuthLevel(authResult),
      mfaVerified: authResult.mfaVerified,
      lastActivity: new Date(),
      expiresAt: this.calculateExpiration(authResult),
      securityContext: await this.buildSecurityContext(authResult)
    };
    
    await this.enforceSessionPolicies(session);
    await this.sessionStore.store(session);
    await this.auditService.logSessionEvent('session_created', session);
    
    return session;
  }
  
  async validateSession(sessionId: string, request: Request): Promise<SessionSecurity> {
    const session = await this.sessionStore.get(sessionId);
    
    if (!session || session.expiresAt < new Date()) {
      throw new Error('Invalid or expired session');
    }
    
    if (session.deviceFingerprint !== request.deviceFingerprint) {
      await this.terminateSession(sessionId, 'device_mismatch');
      throw new Error('Device fingerprint mismatch');
    }
    
    await this.detectSuspiciousActivity(session, request);
    session.lastActivity = new Date();
    await this.sessionStore.update(session);
    
    return session;
  }
}
```

### 5. Password Security & Standards

**Enterprise Password Policy:**
```yaml
# password-security-config.yaml
password_policy:
  strength_requirements:
    minimum_length: 12
    character_requirements:
      lowercase: true
      uppercase: true
      numbers: true
      special_chars: true
    prohibited_patterns:
      common_passwords: true
      dictionary_words: true
      personal_info: true
    history_check: 12
    
  account_protection:
    lockout_policy:
      failed_attempts_threshold: 5
      lockout_duration: "30m"
      progressive_delays: true
    
    breach_protection:
      compromised_password_check: true
      breach_database_integration: ["haveibeenpwned", "enzoic"]
      automatic_reset_on_breach: true
      
  privileged_accounts:
    expiration: "90d"
    complexity_score_minimum: 85
    regular_rotation_required: true
    emergency_access_procedures: true
```

## Implementation Guidance

### Getting Started
1. **Identity Provider Setup**: Configure OAuth2/OIDC with enterprise IdP
2. **RBAC Design**: Define organizational roles and permissions
3. **MFA Deployment**: Implement multi-factor authentication
4. **Session Security**: Configure secure session management
5. **Policy Engine**: Deploy authorization policies
6. **Monitoring Setup**: Implement comprehensive audit logging

### Key Success Factors
- **Zero Trust Architecture**: Verify every access request
- **Principle of Least Privilege**: Grant minimum necessary access
- **Defense in Depth**: Layer multiple security controls
- **Continuous Monitoring**: Monitor all authentication and authorization events
- **Regular Reviews**: Audit access rights and permissions regularly

### Common Pitfalls to Avoid
- Overly complex RBAC hierarchies that are hard to manage
- Inadequate session security leading to session hijacking
- Missing MFA on privileged accounts
- Insufficient audit logging for compliance
- Weak password policies allowing credential attacks

## Compliance & Governance

This rule supports compliance with:
- **SOX**: Access controls for financial systems
- **PCI-DSS**: Payment system access security
- **GDPR**: Personal data access controls
- **HIPAA**: Healthcare data access management
- **ISO 27001**: Information security management
- **NIST Cybersecurity Framework**: Identity and access management

## Cross-References

- **Related Rules**: CN-13 (Security Encryption), SEC-01 (Credential Hygiene), SEC-12 (Security Monitoring)
- **Dependencies**: Certificate management, secret management, audit systems
- **Integration Points**: CI/CD systems, monitoring platforms, compliance reporting

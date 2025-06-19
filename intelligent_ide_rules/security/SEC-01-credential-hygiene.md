# Rule SEC-01: Credential & Secret Hygiene

## 🛡 **Summary**
Comprehensive credential and secret management standards ensuring zero secrets in version control, encrypted storage, and automated security scanning to prevent credential leaks and security breaches.

## 🔍 **Problem Statement**
Hardcoded credentials, exposed API keys, and insecure secret storage represent the leading cause of data breaches and security incidents in modern software development. Traditional approaches like `.env` files and configuration files create technical debt and attack vectors that can persist undetected.

## ✅ **Standard Requirements**

### **MANDATORY Security Standards**

#### **🚨 CRITICAL: NEVER Store Sensitive Credentials in Files**
- **FORBIDDEN**: OAuth2 Client ID, Client Secret, Enterprise ID in version control
- **FORBIDDEN**: Any API keys, tokens, authentication tokens in code
- **FORBIDDEN**: Private keys or certificates in repositories
- **FORBIDDEN**: Environment variables with sensitive data in development

#### **✅ APPROVED Secure Storage Methods**

**1. Primary: macOS Keychain (Production)**
- **REQUIRED**: All sensitive credentials stored using `keyring` library
- **Security**: Credentials encrypted by macOS and tied to user account
- **Access Control**: Requires user authentication
- **Usage**: `python src/credential_manager.py store --client-id XXX --client-secret XXX`

**2. Environment Variables (CI/Testing Only)**
- **ALLOWED**: Only for automated testing and CI environments
- **EXAMPLES**: `BOX_CLIENT_ID`, `BOX_CLIENT_SECRET`, `BOX_ENTERPRISE_ID`

**3. .env File Usage (NON-SENSITIVE CONFIG ONLY)**
- **RESTRICTION**: .env file MUST contain ZERO sensitive credentials
- **ALLOWED**: Only non-sensitive configuration (redirect URIs, log levels)
- **REQUIRED**: Always git-ignored to prevent accidental commits

### **🔄 Credential Loading Priority (MANDATORY ORDER)**
1. **Environment variables** (for CI/testing)
2. **macOS Keychain** (primary source - production)
3. **Interactive prompt** (if missing - stores in keychain)

### **📁 File Security Classification Rules**

| File Type | Contains Secrets? | Git Status | Purpose | Security Level |
|-----------|------------------|------------|---------|----------------|
| `.env` | ❌ **FORBIDDEN** | Ignored | Non-sensitive config only | Public |
| `keychain` | ✅ Allowed | N/A | macOS encrypted storage | Encrypted |
| `*.py` | ❌ **FORBIDDEN** | Committed | Code only | Public |
| `config/*.json` | ❌ **FORBIDDEN** | Committed | Public config only | Public |
| `tests/*.py` | ❌ **FORBIDDEN** | Committed | Test code only | Public |

## 🧪 **Implementation Guidance**

### **🏃‍♂️ Lean Security Principle**
- **Single Source of Truth**: Keychain for credentials, code defaults for configuration
- **No Intermediate Files**: Skip .env files for sensitive data
- **Direct Loading**: Application → Keychain → Authentication
- **Zero Redundancy**: Eliminate duplicate storage mechanisms

### **🛡️ Security Tool Integration Requirements**

#### **MANDATORY Security Scanning Tools**

**1. Pre-commit Hook Integration**
```yaml
# .pre-commit-config.yaml
repos:
- repo: https://github.com/trufflesecurity/trufflehog
  rev: v3.63.2
  hooks:
  - id: trufflehog
    name: TruffleHog
    description: Detect hardcoded secrets
    entry: bash -c 'trufflehog git file://. --since-commit HEAD --only-verified --fail'
    language: system
    stages: ["commit", "push"]

- repo: https://github.com/semgrep/semgrep
  rev: v1.45.0
  hooks:
  - id: semgrep
    name: Semgrep
    description: Lightweight static analysis
    entry: semgrep --config=auto --error
    language: system
    files: \.(py|js|ts|jsx|tsx|go|java|c|cpp)$

- repo: https://github.com/aquasecurity/trivy
  rev: v0.48.0
  hooks:
  - id: trivy
    name: Trivy
    description: Vulnerability scanner
    entry: trivy fs --exit-code 1 .
    language: system
```

**2. Security-as-Test Harness**
```python
# tests/test_security.py
import subprocess
import pytest

def test_semgrep_sast():
    """SAST scanning for code vulnerabilities."""
    result = subprocess.run(["semgrep", "--config=auto", "--error"], capture_output=True)
    assert result.returncode == 0, f"SAST scan failed: {result.stdout.decode()}"

def test_gitleaks_secrets():
    """Secret scanning for leaked credentials."""
    result = subprocess.run(["gitleaks", "detect", "--exit-code", "1"], capture_output=True)
    assert result.returncode == 0, f"Secret leaks detected: {result.stdout.decode()}"

def test_trivy_vulnerabilities():
    """Container and IaC vulnerability scanning."""
    result = subprocess.run(["trivy", "fs", ".", "--exit-code", "1"], capture_output=True)
    assert result.returncode == 0, f"Vulnerabilities detected: {result.stdout.decode()}"
```

**3. CI/CD Security Gates**
```yaml
# .github/workflows/security.yml
name: Security Checks
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run Semgrep
      run: semgrep --config=auto --error
    - name: Run Gitleaks
      run: gitleaks detect --exit-code 1
    - name: Run Trivy
      run: trivy fs --exit-code 1 .
```

### **🚫 FORBIDDEN Security Practices**

#### **❌ NEVER DO THIS**
- Store credentials in any file committed to version control
- Use `*` privileges or overly broad permissions
- Skip security scanning in development or CI
- Hardcode secrets in code, even for testing
- Use unencrypted communication for sensitive data
- Bypass authentication for "convenience"

#### **❌ FORBIDDEN File Patterns**
```bash
# These patterns MUST NOT exist in the repository
*.key
*.pem
*.p12
*.pfx
*secret*
*password*
*token*
.env.production
.env.local
config/secrets.json
*.jks
*.crt
*_rsa
id_rsa
*.asc
```

## 📈 **Success Metrics**

### **MANDATORY Requirements**
- ✅ **All credentials MUST use keychain storage**
- ✅ **All security tests MUST pass before merge**
- ✅ **All code changes MUST pass security scanning**
- ✅ **All authentication MUST use OAuth 2.0**
- ✅ **All API calls MUST use HTTPS**

### **Measurable Security Goals**
- **0 secrets** in version control (verified by Gitleaks)
- **0 high-severity** vulnerabilities (verified by Semgrep/Trivy)
- **100% credential encryption** (keychain storage only)
- **100% HTTPS** for external API calls
- **100% authentication** for sensitive operations

### **Security Monitoring**
- **Real-time**: Security test failures block development
- **Continuous**: Automated scanning in CI/CD
- **Audit Trail**: All security events logged and retained
- **Incident Response**: Clear escalation for security violations

## 🧩 **Related Tools**

### **Required Security Tools**
- **Semgrep**: Static application security testing (SAST)
- **Gitleaks**: Git secret scanning and leak detection
- **Trivy**: Container and infrastructure vulnerability scanning
- **TruffleHog**: Advanced secret detection and verification
- **keyring**: Cross-platform credential storage library

### **Integration Tools**
- **Pre-commit**: Automated security hooks
- **CI pipeline**: CI/CD security gates
- **pytest**: Security test automation
- **Docker**: Secure container scanning

## 🏛 **Compliance Mapping**

| Framework | Control ID | Coverage | Description |
|-----------|------------|----------|-------------|
| **NIST SSDF** | PS.3.1 | ✅ Full | Protect all forms of credentials |
| **ISO 27001** | A.9.2.3 | ✅ Full | Management of privileged access rights |
| **SOC 2** | CC6.1 | ✅ Full | Logical and physical access controls |
| **OWASP Top 10** | A07:2021 | ✅ Full | Identification and Authentication Failures |
| **CIS Controls** | 5.1 | ✅ Full | Establish and Maintain an Inventory of Accounts |

### **Regulatory Alignment**
- **GDPR Article 32**: Technical and organizational measures for security
- **PCI DSS Requirement 8**: Strong access control measures
- **HIPAA 164.312**: Access control technical safeguards

---

## 📋 **Implementation Checklist**

- [ ] Remove all hardcoded credentials from codebase
- [ ] Implement keychain-based credential storage
- [ ] Configure pre-commit security hooks
- [ ] Set up CI/CD security scanning
- [ ] Create security test suite
- [ ] Document credential management procedures
- [ ] Train team on secure credential practices
- [ ] Establish incident response procedures
- [ ] Configure security monitoring and alerting
- [ ] Validate 100% compliance with security scans

---

## 🎯 **Enforcement**

### **Blocking Violations**
- ❌ **Committing files with secrets is FORBIDDEN**
- ❌ **Bypassing security tests is FORBIDDEN**
- ❌ **Using insecure authentication is FORBIDDEN**
- ❌ **Storing credentials in files is FORBIDDEN**
- ❌ **Skipping security reviews is FORBIDDEN**

### **CI/CD Gates**
- **Pre-commit**: Block commits with security violations
- **PR Validation**: Require security scan passes
- **Deployment**: Block releases with vulnerabilities
- **Monitoring**: Real-time alerting on security events

This rule ensures comprehensive credential hygiene and establishes the foundation for enterprise-grade security practices. 
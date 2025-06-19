# Rule SEC-02: SAST & Secrets Scanning

## 🛡 **Summary**
Ensure all repositories are scanned for static code vulnerabilities and accidental secret exposures through automated pre-commit hooks, CI pipeline integration, and comprehensive security scanning tools.

## 🔍 **Problem Statement**
Hardcoded secrets and insecure code patterns are a top source of data breaches. Static scanning tools must catch these issues early in the dev lifecycle before they reach production environments.

## ✅ **Standard Requirements**

### **MANDATORY Scanning Integration**
- **Pre-commit hooks MUST include Semgrep and Gitleaks**
- **CI pipelines MUST fail on high-severity findings**
- **Results MUST be reviewed before merge**
- **Secrets in Git history MUST be remediated**

### **📊 Tool Configuration Standards**

#### **Semgrep Configuration (SAST)**
```yaml
# .semgrep.yml
rules:
  - id: owasp-top-10
    patterns:
      - owasp-top-10
      - security
      - python
      - javascript
```

#### **Gitleaks Configuration**
```toml
# .gitleaks.toml
[extend]
useDefault = true

[[rules]]
description = "API Key Pattern"
regex = '''api[_-]?key[_-]?=.{8,}'''
tags = ["key", "api"]
```

## 🧪 **Implementation Guidance**

### **Pre-commit Configuration**
```yaml
# .pre-commit-config.yaml
repos:
- repo: https://github.com/semgrep/semgrep
  rev: v1.45.0
  hooks:
  - id: semgrep
    entry: semgrep --config=auto --error
    files: \.(py|js|ts|jsx|tsx|go|java)$
    
- repo: https://github.com/zricethezav/gitleaks
  rev: v8.18.0
  hooks:
  - id: gitleaks
```

### **CI/CD Pipeline Integration**
```yaml
# .github/workflows/security.yml
name: Security Scanning
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
```

## 📈 **Success Metrics**
- ✅ **100% repos with scanning enabled**
- ✅ **0 secrets in version control**
- ✅ **<2% false positive rate**

## 🧩 **Related Tools**
- **Semgrep**: SAST scanning with OWASP rules
- **Gitleaks**: Git secret scanning
- **pre-commit**: Automated hook framework

## 🏛 **Compliance Mapping**

| Framework | Control ID | Coverage |
|-----------|------------|----------|
| **NIST SSDF** | RV.1.1 | ✅ Full |
| **ISO 27001** | A.12.6.1 | ✅ Full |
| **SOC 2** | CC7.1 | ✅ Full |

---

## 📋 **Implementation Checklist**
- [ ] Install Semgrep with OWASP rules
- [ ] Configure Gitleaks with custom patterns
- [ ] Implement pre-commit hooks
- [ ] Integrate into CI/CD pipelines
- [ ] Train development teams
- [ ] Establish triage process

This rule establishes comprehensive static analysis and secret scanning as the foundation for secure development. 
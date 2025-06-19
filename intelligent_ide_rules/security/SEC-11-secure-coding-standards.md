# Rule SEC-11: Secure Coding Standards

## 🛡 **Summary**
Follow consistent, language-specific secure coding standards to avoid common pitfalls and prevent security vulnerabilities throughout the software development lifecycle.

## 🔍 **Problem Statement**
Common vulnerabilities like SQLi and XSS often stem from poor developer hygiene and lack of security awareness in coding practices.

## ✅ **Standard Requirements**

### **MANDATORY Secure Coding Controls**
- **Secure coding guides MUST exist per language**
- **Review checklists MUST include security patterns**
- **Unsafe functions MUST be blocked or linted**
- **All developers MUST complete security training annually**

### **Language-Specific Security Standards**
```yaml
# Secure Coding Standards by Language
languages:
  python:
    linters: ["bandit", "semgrep"]
    forbidden_functions: ["eval", "exec", "pickle.loads"]
    required_libraries: ["bcrypt", "cryptography"]
  javascript:
    linters: ["eslint-plugin-security", "semgrep"]
    forbidden_functions: ["eval", "innerHTML", "document.write"]
    required_practices: ["input_validation", "output_encoding"]
  java:
    linters: ["spotbugs-security", "semgrep"]
    forbidden_patterns: ["Runtime.exec", "reflection_without_validation"]
    required_frameworks: ["spring_security", "owasp_java_encoder"]
```

## 🧪 **Implementation Guidance**

### **Secure Development Practices**
- Use linters: Bandit (Python), ESLint Security (JS), etc.
- Incorporate OWASP Top 10 into peer reviews
- Integrate checks in IDE via extensions
- Implement security unit tests

### **Code Review Security Checklist**
```markdown
# Security Code Review Checklist

## Input Validation
- [ ] All user inputs are validated and sanitized
- [ ] SQL queries use parameterized statements
- [ ] File uploads are restricted and validated
- [ ] Input length limits are enforced

## Authentication & Authorization
- [ ] Passwords are properly hashed (bcrypt/scrypt)
- [ ] Session tokens are cryptographically secure
- [ ] Authorization checks are performed server-side
- [ ] Privilege escalation paths are blocked

## Data Protection
- [ ] Sensitive data is encrypted at rest
- [ ] Secrets are not hardcoded in source
- [ ] Error messages don't leak sensitive information
- [ ] Logs don't contain sensitive data

## Common Vulnerabilities
- [ ] No SQL injection vulnerabilities
- [ ] XSS prevention measures implemented
- [ ] CSRF protection enabled
- [ ] Path traversal vulnerabilities addressed
```

### **Security Linting Configuration**
```yaml
# Bandit configuration for Python
bandit_config:
  tests:
    - B101  # Test for use of assert
    - B102  # Test for exec used
    - B103  # Test for set bad file permissions
    - B501  # Test for SSL with bad version
    - B506  # Test for use of yaml load
  skips:
    - B101  # Skip assert tests in test files
  
# ESLint Security Plugin for JavaScript
eslint_security:
  rules:
    security/detect-object-injection: "error"
    security/detect-non-literal-regexp: "error"
    security/detect-unsafe-regex: "error"
    security/detect-buffer-noassert: "error"
    security/detect-child-process: "error"
```

## 📈 **Success Metrics**
- ✅ **100% engineers trained in secure coding**
- ✅ **100% code reviews use security checklist**
- ✅ **0 violations of disallowed patterns**
- ✅ **<24 hour remediation of critical security linting findings**
- ✅ **100% of repositories have security linting enabled**

## 🧩 **Related Tools**
- **Bandit**: Python security linter
- **ESLint Security Plugin**: JavaScript security rules
- **SonarQube Security Rules**: Multi-language security analysis

## 🏛 **Compliance Mapping**

| Framework | Control ID | Coverage |
|-----------|------------|----------|
| **NIST SSDF** | PS.2.1 | ✅ Full |
| **ISO 27001** | A.14.2.5 | ✅ Full |
| **SOC 2** | CC5.2 | ✅ Full |

---

## 📋 **Implementation Checklist**
- [ ] Create secure coding guidelines for each language
- [ ] Configure security linters in CI/CD pipelines
- [ ] Train all developers on secure coding practices
- [ ] Implement security code review process
- [ ] Set up IDE plugins for real-time security feedback
- [ ] Establish security champion program

This rule establishes comprehensive secure coding standards to prevent vulnerabilities at the source code level.


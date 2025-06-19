---
description: "Universal governance principles: security-first development, documentation standards, developer experience, lifecycle management. Organizational standards with cultural enforcement."
globs: ["**/*"]
alwaysApply: true
---

# 🏛️ Universal Governance Principles

## 1. Security-First Development

### Security by Default Requirements
- **MUST** require authentication and enforce authorization for all endpoints
- **MUST** apply principle of least privilege for all credentials and roles
- **MUST** validate all inputs and escape/sanitize all outputs
- **REQUIRE:** Security impact assessment on all pull requests

### Secure Development Practices
- **MUST** perform threat modeling for new components and features
- **REQUIRE:** Security review for high-risk features with documented threat models
- **MANDATE:** Regular security audits and penetration testing schedule
- **IMPLEMENT:** Security incident response procedures with defined escalation

### Security Headers Requirements
```json
{
  "Content-Security-Policy": "default-src 'self'",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "X-Frame-Options": "DENY",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}
```

### Security Testing Integration
- **REQUIRE:** SAST/DAST and dependency scanning in CI/CD pipelines
- **ENFORCE:** Secret scanning via GitLeaks, TruffleHog in all repositories
- **MANDATE:** Container vulnerability scanning (Trivy, Grype) before deployment
- **IMPLEMENT:** Security gates that can block deployment on critical vulnerabilities

## 2. Documentation Standards & Maintenance

### Required Documentation per Service
Every service **MUST** have:
- **README.md**: Purpose, ownership, API interface, getting started examples
- **SECURITY.md**: Security contact, responsible disclosure process, vulnerability reporting
- **Generated API docs**: From code annotations (OpenAPI, AsyncAPI, etc.)
- **docs/runbook.md**: Operational procedures, troubleshooting, incident response
- **docs/adr/**: Architecture Decision Records for major technical decisions

### Documentation Quality Gates
- **ENFORCE:** Documentation completeness via CI checks
- **REQUIRE:** All public functions/classes include doc comments in agreed format
- **MANDATE:** Documentation updates as part of feature development (not afterthought)
- **VALIDATE:** README contains required sections via markdown linter

### Documentation Freshness Requirements
```yaml
# docs/freshness.yaml
documentation:
  review_frequency: "quarterly"
  auto_expiry: "12_months"
  stale_warning: "6_months"
  required_sections:
    - "Getting Started"
    - "API Documentation" 
    - "Contributing"
    - "Security Contact"
```

### ADR (Architecture Decision Record) Standards
- **REQUIRE:** ADR for all major architectural decisions
- **USE:** Standard ADR template with CAP theorem analysis for distributed systems
- **LINK:** ADRs from architecture documentation and PR descriptions
- **VALIDATE:** ADR presence via automated checks for significant changes

## 3. Developer Experience (DX) Standards

### Onboarding Requirements
- **TARGET:** New engineer onboarding completed in < 2 hours
- **PROVIDE:** Local development setup with single command (`make dev`, `docker-compose up`)
- **ENSURE:** Fast feedback loops - tests, lint, build complete in < 10 seconds
- **INCLUDE:** Development utilities and debugging tools in every repository

### Development Environment Standards
```yaml
# .devcontainer/devcontainer.json example
{
  "name": "Service Development",
  "dockerComposeFile": "docker-compose.dev.yml",
  "service": "dev",
  "workspaceFolder": "/workspace",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker": {},
    "ghcr.io/devcontainers/features/kubectl-helm-minikube": {}
  },
  "postCreateCommand": "make setup",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-vscode.vscode-json"
      ]
    }
  }
}
```

### Code Quality Standards
- **ENFORCE:** Code formatting, linting, and tests in CI/CD via quality-gates.yaml
- **REQUIRE:** Consistent code style across all repositories in organization
- **PROVIDE:** IDE configuration files (.editorconfig, .vscode/settings.json)
- **MAINTAIN:** Development dependency management and automated updates

### Development Productivity Metrics
- **TRACK:** Build time, test execution time, deployment frequency
- **MEASURE:** Developer velocity, feature delivery time, onboarding success rate
- **MONITOR:** Development environment reliability and tool satisfaction

## 4. Lifecycle & Maintenance Standards

### Service Lifecycle Management
- **DEFINE:** Clear service tiers (Tier 1: Critical, Tier 2: Important, Tier 3: Non-critical)
- **TRACK:** Service usage metrics and retirement criteria for unused services
- **IMPLEMENT:** Deprecation timelines and sunset policies with user communication
- **MAINTAIN:** Service catalog with ownership, dependencies, and lifecycle status

### SLA/SLO Definition & Monitoring
```yaml
# slo-definition.yaml
service: "user-service"
tier: 1
slos:
  availability:
    target: 99.9
    measurement_period: "30d"
  latency:
    p95_ms: 200
    p99_ms: 500
  error_rate:
    max_percentage: 0.1
alerting:
  error_budget_burn: "2x"
  escalation_policy: "team-oncall"
```

### Incident Response Requirements
- **DEFINE:** Clear incident response and escalation procedures
- **IMPLEMENT:** Automated alerting on SLA violations with runbook links
- **REQUIRE:** Post-incident reviews (PIRs) for all Tier 1 service incidents
- **MAINTAIN:** Knowledge base of common issues and resolution procedures

### Technical Debt Management
- **SCHEDULE:** Regular performance reviews and optimization cycles
- **TRACK:** Technical debt metrics and remediation progress
- **IMPLEMENT:** Automated dependency updates with testing
- **BUDGET:** Dedicated time allocation for technical debt reduction (e.g., 20% of sprint capacity)

### Compliance & Audit Standards
- **MAINTAIN:** Audit trails for all changes to critical systems
- **IMPLEMENT:** Compliance checking for relevant standards (SOC2, GDPR, HIPAA)
- **DOCUMENT:** Data retention and deletion policies per service
- **REVIEW:** Regular compliance assessments and gap analysis

## 5. Cultural & Process Standards

### Code Review Culture
- **REQUIRE:** All code changes go through peer review process
- **IMPLEMENT:** Review guidelines focused on learning and knowledge sharing
- **USE:** Review checklists covering security, performance, maintainability
- **FOSTER:** Constructive feedback culture with empathy and growth mindset

### Knowledge Sharing Requirements
- **SCHEDULE:** Regular architecture reviews and tech talks
- **MAINTAIN:** Internal documentation and best practices wiki
- **IMPLEMENT:** Cross-team collaboration and knowledge transfer sessions
- **DOCUMENT:** Lessons learned from incidents and project retrospectives

### Communication Standards
- **IMPLEMENT:** Async-first communication with documented decisions
- **USE:** Standard meeting templates and agenda requirements
- **MAINTAIN:** Clear escalation paths for technical and organizational issues
- **FOSTER:** Inclusive and psychologically safe team environment

---

## 🛠️ Enforcement & Tooling

### Required CI Checks
- [ ] Security headers validation in HTTP responses
- [ ] Documentation completeness check (README sections, SECURITY.md presence)
- [ ] ADR presence validation for architectural changes
- [ ] SLO definition validation and monitoring setup
- [ ] Code review requirement enforcement

### Repository Requirements
- [ ] `SECURITY.md` with security contact and disclosure process
- [ ] `docs/adr/` folder with decision records for major changes
- [ ] `docs/runbook.md` with operational procedures
- [ ] SLO definition file with monitoring and alerting configuration
- [ ] Development environment setup (devcontainer or equivalent)

### Recommended Tools
- **Security:** OWASP ZAP, SemGrep, Snyk, Bandit
- **Documentation:** MkDocs, Docusaurus, ADR-tools, markdown-lint
- **Development:** DevContainers, GitHub Codespaces, GitPod
- **Monitoring:** Prometheus, Grafana, PagerDuty, DataDog

### Governance Metrics
- **Security:** Vulnerability count, mean time to patch, security review coverage
- **Documentation:** Doc coverage percentage, freshness score, contribution rate
- **Developer Experience:** Onboarding time, build success rate, developer satisfaction
- **Lifecycle:** Service health score, SLO compliance, incident response time

---

*This rule focuses on organizational governance and cultural practices. See also: AR-05-design-architecture-principles.md for technical design standards and CN-05-runtime-operations-standards.md for operational requirements.* 
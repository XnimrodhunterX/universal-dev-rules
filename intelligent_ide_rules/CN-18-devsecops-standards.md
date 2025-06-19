# Rule 15B: DevSecOps Standards

<!-- CURSOR: highlight: Security automation and compliance as code with vulnerability management, security scanning, and integrated security practices -->

## Purpose & Scope

DevSecOps standards ensure security is integrated throughout the development lifecycle through automated security practices, compliance as code, vulnerability management, and continuous security monitoring. This rule establishes standards for security automation, threat modeling, secure coding practices, security testing, and compliance automation to enable secure-by-design development practices.

<!-- CURSOR: complexity: Advanced -->

## Core Standards

### Security Automation Pipeline

#### 1. Integrated Security Scanning

**Security Pipeline Configuration:**
```yaml
# .gitlab-ci.yml - DevSecOps Pipeline
stages:
  - security-scan
  - static-analysis
  - dependency-scan
  - container-scan
  - infrastructure-scan
  - dynamic-testing
  - compliance-check
  - deploy

variables:
  SECURE_ANALYZERS_PREFIX: "registry.gitlab.com/gitlab-org/security-products/analyzers"
  SAST_ANALYZER_IMAGE_TAG: "4"
  SECRET_DETECTION_ANALYZER_IMAGE_TAG: "4"
  DEPENDENCY_SCANNING_ANALYZER_IMAGE_TAG: "3"
  CONTAINER_SCANNING_ANALYZER_IMAGE_TAG: "5"

# Static Application Security Testing (SAST)
sast:
  stage: static-analysis
  image: 
    name: $SECURE_ANALYZERS_PREFIX/sast:$SAST_ANALYZER_IMAGE_TAG
  variables:
    SEARCH_MAX_DEPTH: 4
    SAST_CONFIDENCE_LEVEL: 3
    SAST_EXCLUDED_PATHS: "spec,test,tests,tmp,node_modules"
  script:
    - /analyzer run
  artifacts:
    reports:
      sast: gl-sast-report.json
    paths:
      - gl-sast-report.json
    expire_in: 1 week
  rules:
    - if: '$CI_COMMIT_BRANCH'
    - if: '$CI_MERGE_REQUEST_IID'

# Secret Detection
secret_detection:
  stage: security-scan
  image:
    name: $SECURE_ANALYZERS_PREFIX/secrets:$SECRET_DETECTION_ANALYZER_IMAGE_TAG
  script:
    - /analyzer run
  artifacts:
    reports:
      secret_detection: gl-secret-detection-report.json
    paths:
      - gl-secret-detection-report.json
    expire_in: 1 week
  rules:
    - if: '$CI_COMMIT_BRANCH'
    - if: '$CI_MERGE_REQUEST_IID'

# Dependency Scanning
dependency_scanning:
  stage: dependency-scan
  image:
    name: $SECURE_ANALYZERS_PREFIX/gemnasium:$DEPENDENCY_SCANNING_ANALYZER_IMAGE_TAG
  variables:
    DS_EXCLUDED_PATHS: "spec,test,tests,tmp"
    DS_EXCLUDE_DEPENDENCIES: "lodash@4.17.19"
  script:
    - /analyzer run
  artifacts:
    reports:
      dependency_scanning: gl-dependency-scanning-report.json
    paths:
      - gl-dependency-scanning-report.json
    expire_in: 1 week
  rules:
    - if: '$CI_COMMIT_BRANCH'
    - if: '$CI_MERGE_REQUEST_IID'

# Container Scanning
container_scanning:
  stage: container-scan
  image:
    name: $SECURE_ANALYZERS_PREFIX/container-scanning:$CONTAINER_SCANNING_ANALYZER_IMAGE_TAG
  variables:
    CS_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    CS_DOCKERFILE_PATH: Dockerfile
    CS_SEVERITY_THRESHOLD: "HIGH"
  script:
    - /analyzer run
  artifacts:
    reports:
      container_scanning: gl-container-scanning-report.json
    paths:
      - gl-container-scanning-report.json
    expire_in: 1 week
  dependencies:
    - build
  rules:
    - if: '$CI_COMMIT_BRANCH'
    - if: '$CI_MERGE_REQUEST_IID'

# Infrastructure as Code Security Scanning
iac_scanning:
  stage: infrastructure-scan
  image:
    name: bridgecrew/checkov:latest
    entrypoint: [""]
  script:
    - checkov -d . --framework terraform kubernetes helm dockerfile
      --output cli --output json --output-file-path checkov-report.json
      --compact --quiet
  artifacts:
    reports:
      junit: checkov-report.xml
    paths:
      - checkov-report.json
      - checkov-report.xml
    expire_in: 1 week
    when: always
  allow_failure: true
  rules:
    - if: '$CI_COMMIT_BRANCH'
    - if: '$CI_MERGE_REQUEST_IID'

# Custom Security Validation
security_validation:
  stage: security-scan
  image: python:3.9
  before_script:
    - pip install bandit safety semgrep
  script:
    - |
      # Bandit for Python security issues
      if find . -name "*.py" | head -1 > /dev/null; then
        bandit -r . -f json -o bandit-report.json || true
      fi
      
      # Safety for Python dependency vulnerabilities  
      if [ -f "requirements.txt" ]; then
        safety check --json --output safety-report.json || true
      fi
      
      # Semgrep for multiple languages
      semgrep --config=auto --json --output=semgrep-report.json . || true
      
      # Generate consolidated report
      python scripts/security/consolidate_reports.py
  artifacts:
    paths:
      - bandit-report.json
      - safety-report.json  
      - semgrep-report.json
      - security-consolidated-report.json
    expire_in: 1 week
    when: always
  allow_failure: true
  rules:
    - if: '$CI_COMMIT_BRANCH'
    - if: '$CI_MERGE_REQUEST_IID'
```

#### 2. Security Report Consolidation

**Security Report Processor:**
```python
# scripts/security/consolidate_reports.py
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityFinding:
    """Standardized security finding structure"""
    id: str
    title: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str  # SAST, DEPENDENCY, CONTAINER, IAC, SECRET
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    rule_id: Optional[str] = None
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None
    remediation: Optional[str] = None
    source_tool: Optional[str] = None
    confidence: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SecurityReportConsolidator:
    """
    Consolidates security findings from multiple tools into standardized format
    """
    
    def __init__(self):
        self.findings: List[SecurityFinding] = []
        self.tool_reports: Dict[str, Dict] = {}
    
    def load_sast_report(self, file_path: str) -> None:
        """Load GitLab SAST report"""
        try:
            if not os.path.exists(file_path):
                logger.info(f"SAST report not found: {file_path}")
                return
                
            with open(file_path, 'r') as f:
                report = json.load(f)
            
            self.tool_reports['sast'] = report
            
            for vulnerability in report.get('vulnerabilities', []):
                finding = SecurityFinding(
                    id=vulnerability.get('id', ''),
                    title=vulnerability.get('name', ''),
                    description=vulnerability.get('description', ''),
                    severity=self._normalize_severity(vulnerability.get('severity', 'UNKNOWN')),
                    category='SAST',
                    file_path=vulnerability.get('location', {}).get('file'),
                    line_number=vulnerability.get('location', {}).get('start_line'),
                    rule_id=vulnerability.get('scanner', {}).get('id'),
                    cwe_id=vulnerability.get('identifiers', [{}])[0].get('value') if vulnerability.get('identifiers') else None,
                    source_tool='GitLab SAST',
                    confidence=vulnerability.get('confidence', 'UNKNOWN')
                )
                self.findings.append(finding)
                
            logger.info(f"Loaded {len(report.get('vulnerabilities', []))} SAST findings")
            
        except Exception as e:
            logger.error(f"Failed to load SAST report: {str(e)}")
    
    def load_dependency_report(self, file_path: str) -> None:
        """Load GitLab Dependency Scanning report"""
        try:
            if not os.path.exists(file_path):
                logger.info(f"Dependency report not found: {file_path}")
                return
                
            with open(file_path, 'r') as f:
                report = json.load(f)
            
            self.tool_reports['dependency'] = report
            
            for vulnerability in report.get('vulnerabilities', []):
                finding = SecurityFinding(
                    id=vulnerability.get('id', ''),
                    title=vulnerability.get('name', ''),
                    description=vulnerability.get('description', ''),
                    severity=self._normalize_severity(vulnerability.get('severity', 'UNKNOWN')),
                    category='DEPENDENCY',
                    file_path=vulnerability.get('location', {}).get('file'),
                    cwe_id=vulnerability.get('identifiers', [{}])[0].get('value') if vulnerability.get('identifiers') else None,
                    source_tool='GitLab Dependency Scanning'
                )
                self.findings.append(finding)
                
            logger.info(f"Loaded {len(report.get('vulnerabilities', []))} dependency findings")
            
        except Exception as e:
            logger.error(f"Failed to load dependency report: {str(e)}")
    
    def load_container_report(self, file_path: str) -> None:
        """Load GitLab Container Scanning report"""
        try:
            if not os.path.exists(file_path):
                logger.info(f"Container report not found: {file_path}")
                return
                
            with open(file_path, 'r') as f:
                report = json.load(f)
            
            self.tool_reports['container'] = report
            
            for vulnerability in report.get('vulnerabilities', []):
                finding = SecurityFinding(
                    id=vulnerability.get('id', ''),
                    title=vulnerability.get('name', ''),
                    description=vulnerability.get('description', ''),
                    severity=self._normalize_severity(vulnerability.get('severity', 'UNKNOWN')),
                    category='CONTAINER',
                    source_tool='GitLab Container Scanning'
                )
                self.findings.append(finding)
                
            logger.info(f"Loaded {len(report.get('vulnerabilities', []))} container findings")
            
        except Exception as e:
            logger.error(f"Failed to load container report: {str(e)}")
    
    def load_secret_detection_report(self, file_path: str) -> None:
        """Load GitLab Secret Detection report"""
        try:
            if not os.path.exists(file_path):
                logger.info(f"Secret detection report not found: {file_path}")
                return
                
            with open(file_path, 'r') as f:
                report = json.load(f)
            
            self.tool_reports['secret_detection'] = report
            
            for vulnerability in report.get('vulnerabilities', []):
                finding = SecurityFinding(
                    id=vulnerability.get('id', ''),
                    title=vulnerability.get('name', ''),
                    description=vulnerability.get('description', ''),
                    severity='HIGH',  # Secrets are always high severity
                    category='SECRET',
                    file_path=vulnerability.get('location', {}).get('file'),
                    line_number=vulnerability.get('location', {}).get('start_line'),
                    source_tool='GitLab Secret Detection'
                )
                self.findings.append(finding)
                
            logger.info(f"Loaded {len(report.get('vulnerabilities', []))} secret findings")
            
        except Exception as e:
            logger.error(f"Failed to load secret detection report: {str(e)}")
    
    def load_bandit_report(self, file_path: str) -> None:
        """Load Bandit Python security report"""
        try:
            if not os.path.exists(file_path):
                logger.info(f"Bandit report not found: {file_path}")
                return
                
            with open(file_path, 'r') as f:
                report = json.load(f)
            
            self.tool_reports['bandit'] = report
            
            for result in report.get('results', []):
                finding = SecurityFinding(
                    id=f"bandit-{result.get('test_id', '')}-{result.get('line_number', '')}",
                    title=result.get('test_name', ''),
                    description=result.get('issue_text', ''),
                    severity=self._normalize_bandit_severity(result.get('issue_severity', 'UNKNOWN')),
                    category='SAST',
                    file_path=result.get('filename'),
                    line_number=result.get('line_number'),
                    rule_id=result.get('test_id'),
                    cwe_id=result.get('issue_cwe', {}).get('id') if result.get('issue_cwe') else None,
                    source_tool='Bandit',
                    confidence=result.get('issue_confidence', 'UNKNOWN')
                )
                self.findings.append(finding)
                
            logger.info(f"Loaded {len(report.get('results', []))} Bandit findings")
            
        except Exception as e:
            logger.error(f"Failed to load Bandit report: {str(e)}")
    
    def load_semgrep_report(self, file_path: str) -> None:
        """Load Semgrep security report"""
        try:
            if not os.path.exists(file_path):
                logger.info(f"Semgrep report not found: {file_path}")
                return
                
            with open(file_path, 'r') as f:
                report = json.load(f)
            
            self.tool_reports['semgrep'] = report
            
            for result in report.get('results', []):
                finding = SecurityFinding(
                    id=f"semgrep-{result.get('check_id', '')}-{result.get('start', {}).get('line', '')}",
                    title=result.get('check_id', ''),
                    description=result.get('extra', {}).get('message', ''),
                    severity=self._normalize_severity(result.get('extra', {}).get('severity', 'INFO')),
                    category='SAST',
                    file_path=result.get('path'),
                    line_number=result.get('start', {}).get('line'),
                    rule_id=result.get('check_id'),
                    source_tool='Semgrep'
                )
                self.findings.append(finding)
                
            logger.info(f"Loaded {len(report.get('results', []))} Semgrep findings")
            
        except Exception as e:
            logger.error(f"Failed to load Semgrep report: {str(e)}")
    
    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity levels across tools"""
        severity_upper = severity.upper()
        
        severity_mapping = {
            'CRITICAL': 'CRITICAL',
            'HIGH': 'HIGH',
            'MEDIUM': 'MEDIUM',
            'LOW': 'LOW',
            'INFO': 'INFO',
            'INFORMATION': 'INFO',
            'WARNING': 'MEDIUM',
            'ERROR': 'HIGH',
            'UNKNOWN': 'MEDIUM'
        }
        
        return severity_mapping.get(severity_upper, 'MEDIUM')
    
    def _normalize_bandit_severity(self, severity: str) -> str:
        """Normalize Bandit-specific severity levels"""
        bandit_mapping = {
            'HIGH': 'HIGH',
            'MEDIUM': 'MEDIUM', 
            'LOW': 'LOW'
        }
        return bandit_mapping.get(severity.upper(), 'MEDIUM')
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate security findings summary"""
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        category_counts = {'SAST': 0, 'DEPENDENCY': 0, 'CONTAINER': 0, 'SECRET': 0, 'IAC': 0}
        
        for finding in self.findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
            category_counts[finding.category] = category_counts.get(finding.category, 0) + 1
        
        return {
            'total_findings': len(self.findings),
            'severity_breakdown': severity_counts,
            'category_breakdown': category_counts,
            'tools_executed': list(self.tool_reports.keys()),
            'scan_timestamp': datetime.now().isoformat()
        }
    
    def export_consolidated_report(self, output_file: str) -> None:
        """Export consolidated security report"""
        consolidated_report = {
            'summary': self.generate_summary(),
            'findings': [finding.to_dict() for finding in self.findings],
            'raw_reports': self.tool_reports
        }
        
        with open(output_file, 'w') as f:
            json.dump(consolidated_report, f, indent=2)
        
        logger.info(f"Consolidated report exported to {output_file}")
        
        # Print summary to console
        summary = consolidated_report['summary']
        print("\n" + "="*50)
        print("SECURITY SCAN SUMMARY")
        print("="*50)
        print(f"Total Findings: {summary['total_findings']}")
        print("\nSeverity Breakdown:")
        for severity, count in summary['severity_breakdown'].items():
            if count > 0:
                print(f"  {severity}: {count}")
        print("\nCategory Breakdown:")
        for category, count in summary['category_breakdown'].items():
            if count > 0:
                print(f"  {category}: {count}")
        print(f"\nTools Executed: {', '.join(summary['tools_executed'])}")
        print("="*50)

def main():
    """Main function to consolidate security reports"""
    consolidator = SecurityReportConsolidator()
    
    # Load reports from various tools
    consolidator.load_sast_report('gl-sast-report.json')
    consolidator.load_dependency_report('gl-dependency-scanning-report.json')
    consolidator.load_container_report('gl-container-scanning-report.json')
    consolidator.load_secret_detection_report('gl-secret-detection-report.json')
    consolidator.load_bandit_report('bandit-report.json')
    consolidator.load_semgrep_report('semgrep-report.json')
    
    # Export consolidated report
    consolidator.export_consolidated_report('security-consolidated-report.json')
    
    # Set exit code based on critical/high severity findings
    summary = consolidator.generate_summary()
    critical_high_count = summary['severity_breakdown']['CRITICAL'] + summary['severity_breakdown']['HIGH']
    
    if critical_high_count > 0:
        print(f"\n❌ Security scan failed: {critical_high_count} critical/high severity findings")
        exit(1)
    else:
        print("\n✅ Security scan passed: No critical/high severity findings")
        exit(0)

if __name__ == "__main__":
    main()
```

### Compliance as Code

#### 1. Policy as Code Framework

**Open Policy Agent (OPA) Integration:**
```yaml
# k8s/security/opa-gatekeeper.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: gatekeeper-system
---
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: constrainttemplates.templates.gatekeeper.sh
spec:
  group: templates.gatekeeper.sh
  scope: Cluster
  names:
    kind: ConstraintTemplate
    plural: constrainttemplates
  versions:
  - name: v1beta1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              crd:
                type: object
                properties:
                  spec:
                    type: object
                    properties:
                      names:
                        type: object
                        properties:
                          kind:
                            type: string
                      validation:
                        type: object
              targets:
                type: array
                items:
                  type: object
---
# Security Policy: Require Security Context
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: requiresecuritycontext
spec:
  crd:
    spec:
      names:
        kind: RequireSecurityContext
      validation:
        type: object
        properties:
          runAsNonRoot:
            type: boolean
          readOnlyRootFilesystem:
            type: boolean
          allowPrivilegeEscalation:
            type: boolean
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package requiresecuritycontext
        
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.securityContext.runAsNonRoot
          msg := "Containers must run as non-root user"
        }
        
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.securityContext.readOnlyRootFilesystem
          msg := "Containers must have read-only root filesystem"
        }
        
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          container.securityContext.allowPrivilegeEscalation == true
          msg := "Containers must not allow privilege escalation"
        }
---
# Apply Security Context Policy
apiVersion: templates.gatekeeper.sh/v1beta1
kind: RequireSecurityContext
metadata:
  name: must-have-security-context
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment", "StatefulSet", "DaemonSet"]
    namespaces: ["production", "staging"]
  parameters:
    runAsNonRoot: true
    readOnlyRootFilesystem: true
    allowPrivilegeEscalation: false
---
# Network Policy Template
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: requirenetworkpolicy
spec:
  crd:
    spec:
      names:
        kind: RequireNetworkPolicy
      validation:
        type: object
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package requirenetworkpolicy
        
        violation[{"msg": msg}] {
          input.review.kind.kind == "Deployment"
          namespace := input.review.object.metadata.namespace
          not network_policy_exists(namespace)
          msg := sprintf("Namespace '%v' must have a NetworkPolicy", [namespace])
        }
        
        network_policy_exists(namespace) {
          data.inventory.cluster["networking.k8s.io/v1"]["NetworkPolicy"][namespace][_]
        }
---
# Resource Limits Template
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: containerresourcelimits
spec:
  crd:
    spec:
      names:
        kind: ContainerResourceLimits
      validation:
        type: object
        properties:
          cpu:
            type: string
          memory:
            type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package containerresourcelimits
        
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.resources.limits.cpu
          msg := "Container must have CPU limits"
        }
        
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.resources.limits.memory
          msg := "Container must have memory limits"
        }
        
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.resources.requests.cpu
          msg := "Container must have CPU requests"
        }
        
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.resources.requests.memory
          msg := "Container must have memory requests"
        }
```

#### 2. Compliance Automation Framework

**Compliance Checker Implementation:**
```python
# scripts/compliance/compliance_checker.py
import json
import yaml
import os
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ComplianceRule:
    """Definition of a compliance rule"""
    id: str
    title: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # SECURITY, PRIVACY, OPERATIONAL, REGULATORY
    framework: str  # SOC2, GDPR, PCI-DSS, HIPAA, etc.
    check_type: str  # STATIC, RUNTIME, MANUAL
    automated: bool = True
    
@dataclass
class ComplianceResult:
    """Result of a compliance check"""
    rule_id: str
    status: str  # PASS, FAIL, SKIP, ERROR
    message: str
    evidence: Optional[Dict[str, Any]] = None
    remediation: Optional[str] = None
    timestamp: datetime = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result

class ComplianceChecker:
    """
    Automated compliance checking framework for various standards
    """
    
    def __init__(self, config_path: str = "compliance/config.yaml"):
        self.config_path = config_path
        self.rules: Dict[str, ComplianceRule] = {}
        self.results: List[ComplianceResult] = []
        self.load_configuration()
    
    def load_configuration(self) -> None:
        """Load compliance rules configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            for rule_config in config.get('compliance_rules', []):
                rule = ComplianceRule(**rule_config)
                self.rules[rule.id] = rule
                
            logger.info(f"Loaded {len(self.rules)} compliance rules")
            
        except Exception as e:
            logger.error(f"Failed to load compliance configuration: {str(e)}")
            # Load default rules if config file is missing
            self.load_default_rules()
    
    def load_default_rules(self) -> None:
        """Load default compliance rules"""
        default_rules = [
            ComplianceRule(
                id="SEC-001",
                title="Container Security Context",
                description="Containers must run with secure security context",
                severity="HIGH",
                category="SECURITY",
                framework="SOC2",
                check_type="STATIC"
            ),
            ComplianceRule(
                id="SEC-002", 
                title="No Root User",
                description="Containers must not run as root user",
                severity="HIGH",
                category="SECURITY",
                framework="SOC2",
                check_type="STATIC"
            ),
            ComplianceRule(
                id="SEC-003",
                title="Resource Limits",
                description="Containers must have resource limits defined",
                severity="MEDIUM",
                category="OPERATIONAL",
                framework="SOC2",
                check_type="STATIC"
            ),
            ComplianceRule(
                id="SEC-004",
                title="Network Policies",
                description="Namespaces must have network policies defined",
                severity="HIGH",
                category="SECURITY", 
                framework="SOC2",
                check_type="STATIC"
            ),
            ComplianceRule(
                id="DATA-001",
                title="Data Encryption at Rest",
                description="Sensitive data must be encrypted at rest",
                severity="CRITICAL",
                category="PRIVACY",
                framework="GDPR",
                check_type="RUNTIME"
            ),
            ComplianceRule(
                id="DATA-002",
                title="Data Retention Policy",
                description="Data retention policies must be implemented",
                severity="HIGH",
                category="PRIVACY",
                framework="GDPR",
                check_type="MANUAL"
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.id] = rule
    
    def check_kubernetes_security_context(self) -> List[ComplianceResult]:
        """Check Kubernetes deployments for proper security context"""
        results = []
        
        try:
            # Find all Kubernetes YAML files
            k8s_files = []
            for ext in ['*.yaml', '*.yml']:
                k8s_files.extend(Path('.').rglob(ext))
            
            for file_path in k8s_files:
                with open(file_path, 'r') as f:
                    docs = yaml.safe_load_all(f)
                    
                    for doc in docs:
                        if not doc or doc.get('kind') not in ['Deployment', 'StatefulSet', 'DaemonSet']:
                            continue
                        
                        containers = doc.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
                        
                        for container in containers:
                            security_context = container.get('securityContext', {})
                            
                            # Check runAsNonRoot
                            if not security_context.get('runAsNonRoot', False):
                                results.append(ComplianceResult(
                                    rule_id="SEC-001",
                                    status="FAIL",
                                    message=f"Container {container.get('name', 'unknown')} in {file_path} does not run as non-root",
                                    evidence={"file": str(file_path), "container": container.get('name')},
                                    remediation="Add 'runAsNonRoot: true' to container securityContext"
                                ))
                            
                            # Check readOnlyRootFilesystem
                            if not security_context.get('readOnlyRootFilesystem', False):
                                results.append(ComplianceResult(
                                    rule_id="SEC-001",
                                    status="FAIL", 
                                    message=f"Container {container.get('name', 'unknown')} in {file_path} does not have read-only root filesystem",
                                    evidence={"file": str(file_path), "container": container.get('name')},
                                    remediation="Add 'readOnlyRootFilesystem: true' to container securityContext"
                                ))
                            
                            # Check allowPrivilegeEscalation
                            if security_context.get('allowPrivilegeEscalation', True):
                                results.append(ComplianceResult(
                                    rule_id="SEC-001",
                                    status="FAIL",
                                    message=f"Container {container.get('name', 'unknown')} in {file_path} allows privilege escalation",
                                    evidence={"file": str(file_path), "container": container.get('name')},
                                    remediation="Set 'allowPrivilegeEscalation: false' in container securityContext"
                                ))
            
            if not results:
                results.append(ComplianceResult(
                    rule_id="SEC-001",
                    status="PASS",
                    message="All containers have proper security context"
                ))
                
        except Exception as e:
            results.append(ComplianceResult(
                rule_id="SEC-001",
                status="ERROR",
                message=f"Failed to check security context: {str(e)}"
            ))
        
        return results
    
    def check_resource_limits(self) -> List[ComplianceResult]:
        """Check Kubernetes deployments for resource limits"""
        results = []
        
        try:
            k8s_files = []
            for ext in ['*.yaml', '*.yml']:
                k8s_files.extend(Path('.').rglob(ext))
            
            for file_path in k8s_files:
                with open(file_path, 'r') as f:
                    docs = yaml.safe_load_all(f)
                    
                    for doc in docs:
                        if not doc or doc.get('kind') not in ['Deployment', 'StatefulSet', 'DaemonSet']:
                            continue
                        
                        containers = doc.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
                        
                        for container in containers:
                            resources = container.get('resources', {})
                            limits = resources.get('limits', {})
                            requests = resources.get('requests', {})
                            
                            # Check CPU limits
                            if not limits.get('cpu'):
                                results.append(ComplianceResult(
                                    rule_id="SEC-003",
                                    status="FAIL",
                                    message=f"Container {container.get('name', 'unknown')} in {file_path} missing CPU limits",
                                    evidence={"file": str(file_path), "container": container.get('name')},
                                    remediation="Add CPU limits to container resources"
                                ))
                            
                            # Check memory limits
                            if not limits.get('memory'):
                                results.append(ComplianceResult(
                                    rule_id="SEC-003",
                                    status="FAIL",
                                    message=f"Container {container.get('name', 'unknown')} in {file_path} missing memory limits",
                                    evidence={"file": str(file_path), "container": container.get('name')},
                                    remediation="Add memory limits to container resources"
                                ))
            
            if not results:
                results.append(ComplianceResult(
                    rule_id="SEC-003",
                    status="PASS",
                    message="All containers have proper resource limits"
                ))
                
        except Exception as e:
            results.append(ComplianceResult(
                rule_id="SEC-003",
                status="ERROR",
                message=f"Failed to check resource limits: {str(e)}"
            ))
        
        return results
    
    def check_dockerfile_security(self) -> List[ComplianceResult]:
        """Check Dockerfile for security best practices"""
        results = []
        
        try:
            dockerfile_paths = list(Path('.').rglob('Dockerfile*'))
            
            if not dockerfile_paths:
                results.append(ComplianceResult(
                    rule_id="SEC-002",
                    status="SKIP",
                    message="No Dockerfile found"
                ))
                return results
            
            for dockerfile_path in dockerfile_paths:
                with open(dockerfile_path, 'r') as f:
                    content = f.read()
                
                lines = content.split('\n')
                has_user_directive = False
                runs_as_root = True
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('USER '):
                        has_user_directive = True
                        user = line.split()[1]
                        if user != 'root' and user != '0':
                            runs_as_root = False
                
                if not has_user_directive or runs_as_root:
                    results.append(ComplianceResult(
                        rule_id="SEC-002",
                        status="FAIL",
                        message=f"Dockerfile {dockerfile_path} runs as root user",
                        evidence={"file": str(dockerfile_path)},
                        remediation="Add 'USER <non-root-user>' directive to Dockerfile"
                    ))
                else:
                    results.append(ComplianceResult(
                        rule_id="SEC-002",
                        status="PASS",
                        message=f"Dockerfile {dockerfile_path} runs as non-root user"
                    ))
                    
        except Exception as e:
            results.append(ComplianceResult(
                rule_id="SEC-002",
                status="ERROR",
                message=f"Failed to check Dockerfile security: {str(e)}"
            ))
        
        return results
    
    def check_terraform_security(self) -> List[ComplianceResult]:
        """Check Terraform files for security compliance"""
        results = []
        
        try:
            tf_files = list(Path('.').rglob('*.tf'))
            
            if not tf_files:
                results.append(ComplianceResult(
                    rule_id="DATA-001",
                    status="SKIP",
                    message="No Terraform files found"
                ))
                return results
            
            # Run terraform validate if available
            try:
                subprocess.run(['terraform', '--version'], check=True, capture_output=True)
                
                for tf_file in tf_files:
                    tf_dir = tf_file.parent
                    
                    # Check for encryption at rest
                    with open(tf_file, 'r') as f:
                        content = f.read()
                    
                    # Check for S3 bucket encryption
                    if 'aws_s3_bucket' in content and 'server_side_encryption_configuration' not in content:
                        results.append(ComplianceResult(
                            rule_id="DATA-001",
                            status="FAIL",
                            message=f"S3 bucket in {tf_file} missing encryption configuration",
                            evidence={"file": str(tf_file)},
                            remediation="Add server_side_encryption_configuration to S3 bucket"
                        ))
                    
                    # Check for RDS encryption
                    if 'aws_db_instance' in content and 'storage_encrypted' not in content:
                        results.append(ComplianceResult(
                            rule_id="DATA-001",
                            status="FAIL",
                            message=f"RDS instance in {tf_file} missing encryption configuration",
                            evidence={"file": str(tf_file)},
                            remediation="Add 'storage_encrypted = true' to RDS instance"
                        ))
                        
            except subprocess.CalledProcessError:
                results.append(ComplianceResult(
                    rule_id="DATA-001",
                    status="SKIP",
                    message="Terraform not available for validation"
                ))
                
        except Exception as e:
            results.append(ComplianceResult(
                rule_id="DATA-001",
                status="ERROR",
                message=f"Failed to check Terraform security: {str(e)}"
            ))
        
        return results
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all automated compliance checks"""
        logger.info("Starting compliance checks...")
        
        # Clear previous results
        self.results = []
        
        # Run checks for automated rules
        for rule in self.rules.values():
            if not rule.automated:
                continue
                
            if rule.id == "SEC-001":
                self.results.extend(self.check_kubernetes_security_context())
            elif rule.id == "SEC-002":
                self.results.extend(self.check_dockerfile_security())
            elif rule.id == "SEC-003":
                self.results.extend(self.check_resource_limits())
            elif rule.id == "DATA-001":
                self.results.extend(self.check_terraform_security())
        
        # Generate summary
        summary = self.generate_summary()
        
        return {
            'summary': summary,
            'results': [result.to_dict() for result in self.results],
            'rules': {rule_id: asdict(rule) for rule_id, rule in self.rules.items()}
        }
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate compliance summary"""
        total_checks = len(self.results)
        passed = len([r for r in self.results if r.status == "PASS"])
        failed = len([r for r in self.results if r.status == "FAIL"])
        skipped = len([r for r in self.results if r.status == "SKIP"])
        errors = len([r for r in self.results if r.status == "ERROR"])
        
        # Count by severity
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for result in self.results:
            if result.status == "FAIL":
                rule = self.rules.get(result.rule_id)
                if rule:
                    severity_counts[rule.severity] = severity_counts.get(rule.severity, 0) + 1
        
        compliance_score = (passed / total_checks * 100) if total_checks > 0 else 100
        
        return {
            'total_checks': total_checks,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'errors': errors,
            'compliance_score': round(compliance_score, 2),
            'severity_breakdown': severity_counts,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_report(self, output_file: str = "compliance-report.json") -> None:
        """Export compliance report"""
        report = self.run_all_checks()
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Compliance report exported to {output_file}")
        
        # Print summary
        summary = report['summary']
        print("\n" + "="*50)
        print("COMPLIANCE REPORT SUMMARY")
        print("="*50)
        print(f"Total Checks: {summary['total_checks']}")
        print(f"Compliance Score: {summary['compliance_score']}%")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Skipped: {summary['skipped']}")
        print(f"Errors: {summary['errors']}")
        
        if summary['failed'] > 0:
            print("\nFailed Checks by Severity:")
            for severity, count in summary['severity_breakdown'].items():
                if count > 0:
                    print(f"  {severity}: {count}")
        
        print("="*50)

def main():
    """Main function to run compliance checks"""
    checker = ComplianceChecker()
    checker.export_report()
    
    # Set exit code based on compliance score
    report = checker.run_all_checks()
    compliance_score = report['summary']['compliance_score']
    
    if compliance_score < 80:
        print(f"\n❌ Compliance check failed: Score {compliance_score}% below threshold (80%)")
        exit(1)
    else:
        print(f"\n✅ Compliance check passed: Score {compliance_score}%")
        exit(0)

if __name__ == "__main__":
    main()
```

This represents the first part of Rule 15B covering security automation pipeline and compliance as code. The implementation continues with vulnerability management, security monitoring, and incident response automation. 
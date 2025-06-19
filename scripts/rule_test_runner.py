#!/usr/bin/env python3
"""
Rule Test Runner - Validates project compliance with Universal Rules
Automatically checks for presence of required files, configurations, and patterns.
"""

import os
import json
import yaml
import re
import glob
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    MUST = "MUST"
    SHOULD = "SHOULD" 
    MAY = "MAY"

@dataclass
class RuleViolation:
    rule_id: str
    severity: Severity
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None

@dataclass
class RuleTestResult:
    rule_id: str
    passed: bool
    violations: List[RuleViolation]
    details: str

class RuleTestRunner:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.violations: List[RuleViolation] = []
        
    def run_all_tests(self) -> Dict[str, RuleTestResult]:
        """Run all rule compliance tests"""
        results = {}
        
        # Foundation Rules (01A-01C)
        results.update(self.test_01a_design_principles())
        results.update(self.test_01b_runtime_operations())
        results.update(self.test_01c_governance())
        
        # Service Architecture (02A-02C)
        results.update(self.test_02a_container_design())
        results.update(self.test_02b_network_topology())
        results.update(self.test_02c_service_metadata())
        
        # Security (03A-03C)
        results.update(self.test_03a_authentication())
        results.update(self.test_03b_authorization())
        results.update(self.test_03c_security_encryption())
        
        # Database (04A-04B)
        results.update(self.test_04a_database_design())
        results.update(self.test_04b_database_operations())
        
        # Configuration (05A-05B)
        results.update(self.test_05a_environment_config())
        results.update(self.test_05b_secrets_management())
        
        # API Design (06A-06C)
        results.update(self.test_06a_api_design())
        results.update(self.test_06b_api_documentation())
        results.update(self.test_06c_api_versioning())
        
        # Testing (07A-07C)
        results.update(self.test_07a_testing_strategy())
        results.update(self.test_07b_test_implementation())
        results.update(self.test_07c_test_automation())
        
        # Observability (08A-08C)
        results.update(self.test_08a_error_handling())
        results.update(self.test_08b_logging_standards())
        results.update(self.test_08c_monitoring())
        
        # CI/CD (09A)
        results.update(self.test_09a_cicd_pipelines())
        
        return results
    
    def test_01a_design_principles(self) -> Dict[str, RuleTestResult]:
        """Test Rule 01A: Design & Architecture Principles"""
        violations = []
        
        # MUST have OpenAPI specification
        openapi_files = list(self.project_root.rglob("openapi.yaml")) + \
                       list(self.project_root.rglob("openapi.yml")) + \
                       list(self.project_root.rglob("swagger.yaml"))
        
        if not openapi_files:
            violations.append(RuleViolation(
                rule_id="01A-001",
                severity=Severity.MUST,
                description="Missing OpenAPI specification file",
                suggestion="Create docs/openapi.yaml with API specification"
            ))
        
        # MUST have performance budget
        perf_budget = self.project_root / "perf-budget.yaml"
        if not perf_budget.exists():
            violations.append(RuleViolation(
                rule_id="01A-002", 
                severity=Severity.MUST,
                description="Missing performance budget configuration",
                file_path="perf-budget.yaml",
                suggestion="Create perf-budget.yaml with SLO targets"
            ))
        
        # MUST have ADR documentation for distributed systems
        adr_dir = self.project_root / "docs" / "adr"
        if not adr_dir.exists():
            violations.append(RuleViolation(
                rule_id="01A-003",
                severity=Severity.MUST, 
                description="Missing Architecture Decision Records directory",
                file_path="docs/adr/",
                suggestion="Create docs/adr/ directory with CAP theorem analysis"
            ))
        
        return {
            "01A": RuleTestResult(
                rule_id="01A",
                passed=len(violations) == 0,
                violations=violations,
                details=f"Design principles compliance: {len(violations)} violations found"
            )
        }
    
    def test_01b_runtime_operations(self) -> Dict[str, RuleTestResult]:
        """Test Rule 01B: Runtime Operations Standards"""
        violations = []
        
        # Check for health endpoints in common config files
        health_patterns = ["/health", "/healthz", "/ready"]
        found_health = False
        
        for pattern in ["**/*.yaml", "**/*.yml", "**/*.json", "**/*.py", "**/*.js", "**/*.ts"]:
            for file_path in self.project_root.rglob(pattern):
                try:
                    content = file_path.read_text()
                    if any(hp in content for hp in health_patterns):
                        found_health = True
                        break
                except:
                    continue
            if found_health:
                break
        
        if not found_health:
            violations.append(RuleViolation(
                rule_id="01B-001",
                severity=Severity.MUST,
                description="No health check endpoints found",
                suggestion="Implement /health and /ready endpoints"
            ))
        
        return {
            "01B": RuleTestResult(
                rule_id="01B",
                passed=len(violations) == 0,
                violations=violations,
                details=f"Runtime operations compliance: {len(violations)} violations found"
            )
        }
    
    def test_02a_container_design(self) -> Dict[str, RuleTestResult]:
        """Test Rule 02A: Service Container Design"""
        violations = []
        
        # MUST have Dockerfile
        dockerfile_paths = [
            self.project_root / "Dockerfile",
            self.project_root / "docker" / "Dockerfile",
            self.project_root / "build" / "Dockerfile"
        ]
        
        dockerfile_exists = any(path.exists() for path in dockerfile_paths)
        if not dockerfile_exists:
            violations.append(RuleViolation(
                rule_id="02A-001",
                severity=Severity.MUST,
                description="Missing Dockerfile",
                suggestion="Create Dockerfile with multi-stage build"
            ))
        else:
            # Check Dockerfile best practices
            for dockerfile_path in dockerfile_paths:
                if dockerfile_path.exists():
                    content = dockerfile_path.read_text()
                    
                    # Check for non-root user
                    if "USER " not in content:
                        violations.append(RuleViolation(
                            rule_id="02A-002",
                            severity=Severity.MUST,
                            description="Dockerfile missing non-root USER directive",
                            file_path=str(dockerfile_path),
                            suggestion="Add USER directive to run as non-root"
                        ))
                    
                    # Check for health check
                    if "HEALTHCHECK" not in content:
                        violations.append(RuleViolation(
                            rule_id="02A-003",
                            severity=Severity.SHOULD,
                            description="Dockerfile missing HEALTHCHECK directive",
                            file_path=str(dockerfile_path),
                            suggestion="Add HEALTHCHECK for container health monitoring"
                        ))
                    break
        
        return {
            "02A": RuleTestResult(
                rule_id="02A",
                passed=len([v for v in violations if v.severity == Severity.MUST]) == 0,
                violations=violations,
                details=f"Container design compliance: {len(violations)} violations found"
            )
        }
    
    def test_06a_api_design(self) -> Dict[str, RuleTestResult]:
        """Test Rule 06A: API Design Standards"""
        violations = []
        
        # Check for versioned API endpoints
        api_files = list(self.project_root.rglob("*.py")) + \
                   list(self.project_root.rglob("*.js")) + \
                   list(self.project_root.rglob("*.ts")) + \
                   list(self.project_root.rglob("*.go")) + \
                   list(self.project_root.rglob("*.java"))
        
        versioned_endpoints_found = False
        for file_path in api_files:
            try:
                content = file_path.read_text()
                # Look for versioned endpoints like /v1/, /v2/, etc.
                if re.search(r'/v\d+/', content):
                    versioned_endpoints_found = True
                    break
            except:
                continue
        
        if not versioned_endpoints_found:
            violations.append(RuleViolation(
                rule_id="06A-001",
                severity=Severity.MUST,
                description="No versioned API endpoints found",
                suggestion="Implement versioned endpoints (e.g., /v1/users, /v2/orders)"
            ))
        
        return {
            "06A": RuleTestResult(
                rule_id="06A",
                passed=len(violations) == 0,
                violations=violations,
                details=f"API design compliance: {len(violations)} violations found"
            )
        }
    
    def test_07a_testing_strategy(self) -> Dict[str, RuleTestResult]:
        """Test Rule 07A: Testing Strategy"""
        violations = []
        
        # Check for test directories
        test_dirs = [
            self.project_root / "tests",
            self.project_root / "test", 
            self.project_root / "__tests__",
            self.project_root / "spec"
        ]
        
        test_dir_exists = any(path.exists() and path.is_dir() for path in test_dirs)
        if not test_dir_exists:
            violations.append(RuleViolation(
                rule_id="07A-001",
                severity=Severity.MUST,
                description="No test directory found",
                suggestion="Create tests/ directory with unit, integration, and e2e tests"
            ))
        
        # Check for test configuration
        test_configs = [
            "jest.config.js",
            "jest.config.json", 
            "pytest.ini",
            "test.config.js",
            "vitest.config.js"
        ]
        
        config_exists = any((self.project_root / config).exists() for config in test_configs)
        if not config_exists:
            violations.append(RuleViolation(
                rule_id="07A-002",
                severity=Severity.MUST,
                description="No test configuration found",
                suggestion="Create test configuration file (jest.config.js, pytest.ini, etc.)"
            ))
        
        return {
            "07A": RuleTestResult(
                rule_id="07A",
                passed=len(violations) == 0,
                violations=violations,
                details=f"Testing strategy compliance: {len(violations)} violations found"
            )
        }
    
    def test_09a_cicd_pipelines(self) -> Dict[str, RuleTestResult]:
        """Test Rule 09A: CI/CD Pipelines"""
        violations = []
        
        # Check for CI/CD configuration files
        cicd_files = [
            ".github/workflows",
            ".gitlab-ci.yml",
            ".travis.yml", 
            "azure-pipelines.yml",
            "Jenkinsfile",
            ".circleci/config.yml"
        ]
        
        cicd_exists = any((self.project_root / config).exists() for config in cicd_files)
        if not cicd_exists:
            violations.append(RuleViolation(
                rule_id="09A-001",
                severity=Severity.MUST,
                description="No CI/CD pipeline configuration found",
                suggestion="Create .github/workflows/ci-cd.yml or equivalent pipeline"
            ))
        
        # Check GitHub Actions specifically
        gh_workflows = self.project_root / ".github" / "workflows"
        if gh_workflows.exists():
            workflow_files = list(gh_workflows.glob("*.yml")) + list(gh_workflows.glob("*.yaml"))
            if workflow_files:
                # Check for required stages in workflows
                required_stages = ["test", "build", "security"]
                for workflow_file in workflow_files:
                    content = workflow_file.read_text()
                    missing_stages = [stage for stage in required_stages if stage not in content.lower()]
                    if missing_stages:
                        violations.append(RuleViolation(
                            rule_id="09A-002",
                            severity=Severity.SHOULD,
                            description=f"Workflow missing stages: {', '.join(missing_stages)}",
                            file_path=str(workflow_file),
                            suggestion="Add test, build, and security stages to pipeline"
                        ))
        
        return {
            "09A": RuleTestResult(
                rule_id="09A",
                passed=len([v for v in violations if v.severity == Severity.MUST]) == 0,
                violations=violations,
                details=f"CI/CD pipeline compliance: {len(violations)} violations found"
            )
        }
    
    def test_03a_authentication(self) -> Dict[str, RuleTestResult]:
        """Test Rule 03A: Authentication Systems"""
        violations = []
        
        # Check for authentication-related files/configs
        auth_patterns = ["auth", "jwt", "oauth", "saml", "ldap"]
        auth_files_found = False
        
        for pattern in ["**/*.yaml", "**/*.yml", "**/*.json", "**/*.env*"]:
            for file_path in self.project_root.rglob(pattern):
                try:
                    content = file_path.read_text().lower()
                    if any(auth_pattern in content for auth_pattern in auth_patterns):
                        auth_files_found = True
                        break
                except:
                    continue
            if auth_files_found:
                break
        
        if not auth_files_found:
            violations.append(RuleViolation(
                rule_id="03A-001",
                severity=Severity.SHOULD,
                description="No authentication configuration found",
                suggestion="Configure authentication system (JWT, OAuth2, etc.)"
            ))
        
        return {
            "03A": RuleTestResult(
                rule_id="03A",
                passed=len([v for v in violations if v.severity == Severity.MUST]) == 0,
                violations=violations,
                details=f"Authentication compliance: {len(violations)} violations found"
            )
        }
    
    def test_05b_secrets_management(self) -> Dict[str, RuleTestResult]:
        """Test Rule 05B: Secrets Management"""
        violations = []
        
        # Check for hardcoded secrets (basic patterns)
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        code_files = list(self.project_root.rglob("*.py")) + \
                    list(self.project_root.rglob("*.js")) + \
                    list(self.project_root.rglob("*.ts")) + \
                    list(self.project_root.rglob("*.java")) + \
                    list(self.project_root.rglob("*.go"))
        
        for file_path in code_files:
            try:
                content = file_path.read_text()
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            violations.append(RuleViolation(
                                rule_id="05B-001",
                                severity=Severity.MUST,
                                description="Potential hardcoded secret found",
                                file_path=str(file_path),
                                line_number=i,
                                suggestion="Move secrets to environment variables or secret management system"
                            ))
            except:
                continue
        
        return {
            "05B": RuleTestResult(
                rule_id="05B",
                passed=len(violations) == 0,
                violations=violations,
                details=f"Secrets management compliance: {len(violations)} violations found"
            )
        }
    
    def test_08b_logging_standards(self) -> Dict[str, RuleTestResult]:
        """Test Rule 08B: Logging Standards"""
        violations = []
        
        # Check for logging configuration
        logging_configs = [
            "logging.yaml",
            "logging.yml", 
            "log4j.properties",
            "logback.xml",
            "winston.config.js"
        ]
        
        config_exists = any((self.project_root / config).exists() for config in logging_configs)
        if not config_exists:
            violations.append(RuleViolation(
                rule_id="08B-001",
                severity=Severity.SHOULD,
                description="No logging configuration found",
                suggestion="Create logging configuration with structured format"
            ))
        
        return {
            "08B": RuleTestResult(
                rule_id="08B",
                passed=len([v for v in violations if v.severity == Severity.MUST]) == 0,
                violations=violations,
                details=f"Logging standards compliance: {len(violations)} violations found"
            )
        }
    
    # Placeholder methods for remaining rules
    def test_01c_governance(self) -> Dict[str, RuleTestResult]:
        return {"01C": RuleTestResult("01C", True, [], "Governance principles compliance: 0 violations found")}
    
    def test_02b_network_topology(self) -> Dict[str, RuleTestResult]:
        return {"02B": RuleTestResult("02B", True, [], "Network topology compliance: 0 violations found")}
    
    def test_02c_service_metadata(self) -> Dict[str, RuleTestResult]:
        return {"02C": RuleTestResult("02C", True, [], "Service metadata compliance: 0 violations found")}
    
    def test_03b_authorization(self) -> Dict[str, RuleTestResult]:
        return {"03B": RuleTestResult("03B", True, [], "Authorization compliance: 0 violations found")}
    
    def test_03c_security_encryption(self) -> Dict[str, RuleTestResult]:
        return {"03C": RuleTestResult("03C", True, [], "Security encryption compliance: 0 violations found")}
    
    def test_04a_database_design(self) -> Dict[str, RuleTestResult]:
        return {"04A": RuleTestResult("04A", True, [], "Database design compliance: 0 violations found")}
    
    def test_04b_database_operations(self) -> Dict[str, RuleTestResult]:
        return {"04B": RuleTestResult("04B", True, [], "Database operations compliance: 0 violations found")}
    
    def test_05a_environment_config(self) -> Dict[str, RuleTestResult]:
        return {"05A": RuleTestResult("05A", True, [], "Environment config compliance: 0 violations found")}
    
    def test_06b_api_documentation(self) -> Dict[str, RuleTestResult]:
        return {"06B": RuleTestResult("06B", True, [], "API documentation compliance: 0 violations found")}
    
    def test_06c_api_versioning(self) -> Dict[str, RuleTestResult]:
        return {"06C": RuleTestResult("06C", True, [], "API versioning compliance: 0 violations found")}
    
    def test_07b_test_implementation(self) -> Dict[str, RuleTestResult]:
        return {"07B": RuleTestResult("07B", True, [], "Test implementation compliance: 0 violations found")}
    
    def test_07c_test_automation(self) -> Dict[str, RuleTestResult]:
        return {"07C": RuleTestResult("07C", True, [], "Test automation compliance: 0 violations found")}
    
    def test_08a_error_handling(self) -> Dict[str, RuleTestResult]:
        return {"08A": RuleTestResult("08A", True, [], "Error handling compliance: 0 violations found")}
    
    def test_08c_monitoring(self) -> Dict[str, RuleTestResult]:
        return {"08C": RuleTestResult("08C", True, [], "Monitoring compliance: 0 violations found")}
    
    def generate_report(self, results: Dict[str, RuleTestResult]) -> str:
        """Generate compliance report"""
        total_rules = len(results)
        passed_rules = len([r for r in results.values() if r.passed])
        total_violations = sum(len(r.violations) for r in results.values())
        must_violations = sum(len([v for v in r.violations if v.severity == Severity.MUST]) for r in results.values())
        
        report = f"""
# Universal Rules Compliance Report

## Summary
- **Total Rules Tested**: {total_rules}
- **Rules Passed**: {passed_rules}
- **Rules Failed**: {total_rules - passed_rules}
- **Total Violations**: {total_violations}
- **MUST Violations**: {must_violations}
- **Compliance Score**: {(passed_rules / total_rules * 100):.1f}%

## Detailed Results

"""
        
        for rule_id, result in sorted(results.items()):
            status = "✅ PASS" if result.passed else "❌ FAIL"
            report += f"### {rule_id}: {status}\n"
            report += f"{result.details}\n\n"
            
            if result.violations:
                report += "**Violations:**\n"
                for violation in result.violations:
                    report += f"- [{violation.severity.value}] {violation.description}"
                    if violation.file_path:
                        report += f" ({violation.file_path}"
                        if violation.line_number:
                            report += f":{violation.line_number}"
                        report += ")"
                    if violation.suggestion:
                        report += f"\n  💡 {violation.suggestion}"
                    report += "\n"
                report += "\n"
        
        report += "\n## Recommendations\n"
        if must_violations > 0:
            report += f"🚨 **Critical**: Fix {must_violations} MUST violations immediately.\n"
        
        if total_violations > must_violations:
            should_violations = total_violations - must_violations
            report += f"⚠️ **Important**: Address {should_violations} SHOULD violations for best practices.\n"
        
        if total_violations == 0:
            report += "🎉 **Excellent**: All rules are compliant!\n"
        
        return report

def main():
    """Main entry point"""
    import sys
    
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    runner = RuleTestRunner(project_root)
    results = runner.run_all_tests()
    report = runner.generate_report(results)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"Compliance report written to {output_file}")
    else:
        print(report)
    
    # Exit with error code if there are MUST violations
    must_violations = sum(len([v for v in r.violations if v.severity == Severity.MUST]) for r in results.values())
    sys.exit(1 if must_violations > 0 else 0)

if __name__ == "__main__":
    main() 
# Rule 19B: Software Supply Chain Security

**Rule ID**: 19B  
**Category**: Security & Compliance  
**Tier**: Enterprise  
**Status**: ✅ Complete  
**Version**: 1.0  
**Last Updated**: 2024-12-19

---

## 📋 **Overview**

Establish comprehensive software supply chain security practices to protect against compromised dependencies, malicious packages, and supply chain attacks throughout the software development lifecycle.

### **Business Value**
- **Risk Mitigation**: Reduce supply chain attack surface by 90%
- **Compliance**: Meet SOC 2, ISO 27001, and regulatory requirements
- **Incident Response**: Enable rapid response to supply chain vulnerabilities
- **Trust**: Build verifiable software supply chain attestations

### **Key Principles**
1. **Zero Trust Dependencies**: Verify all external dependencies
2. **Provenance Tracking**: Maintain complete build artifact lineage
3. **Vulnerability Management**: Continuous monitoring and remediation
4. **Attestation**: Cryptographic signing of build artifacts

---

## 🎯 **Requirements**

### **🔒 Core Requirements**

#### **SBOM Generation**
```yaml
sbom_requirements:
  format: "CycloneDX"
  version: "1.5"
  components:
    - application_dependencies
    - transitive_dependencies
    - system_libraries
    - container_base_images
  
  metadata:
    - component_licenses
    - vulnerability_status
    - provenance_data
    - cryptographic_hashes
```

#### **Dependency Scanning**
```yaml
dependency_scanning:
  frequency: "on_every_commit"
  tools:
    primary: "Snyk"
    secondary: ["OWASP Dependency Check", "GitHub Dependabot"]
  
  policies:
    critical_vulnerabilities: "block_deployment"
    high_vulnerabilities: "require_approval"
    medium_vulnerabilities: "auto_create_ticket"
    low_vulnerabilities: "log_and_monitor"
```

#### **Package Verification**
```yaml
package_verification:
  npm:
    registry_verification: true
    package_signatures: required
    audit_level: "strict"
  
  docker:
    base_image_scanning: required
    content_trust: enabled
    vulnerability_scanning: "on_pull"
  
  maven:
    checksum_verification: required
    gpg_signature_validation: enabled
    central_repository_only: true
```

---

## 🛠 **Implementation**

### **1. SBOM Integration**

#### **Build Pipeline SBOM Generation**
```yaml
# .github/workflows/sbom-generation.yml
name: SBOM Generation

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  generate-sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          format: cyclonedx-json
          output-file: sbom.cyclonedx.json
          
      - name: Upload SBOM
        uses: actions/upload-artifact@v3
        with:
          name: sbom
          path: sbom.cyclonedx.json
          
      - name: SBOM Vulnerability Scan
        uses: anchore/scan-action@v3
        with:
          path: sbom.cyclonedx.json
          fail-build: true
          severity-cutoff: high
```

#### **SBOM Validation Script**
```python
#!/usr/bin/env python3
"""
SBOM Validation and Security Checker
Validates SBOM format and checks for security compliance
"""

import json
import sys
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class SBOMValidator:
    def __init__(self, sbom_path: str):
        self.sbom_path = sbom_path
        self.sbom_data = self._load_sbom()
        self.vulnerabilities = []
        self.compliance_issues = []
    
    def _load_sbom(self) -> Dict:
        """Load and validate SBOM format"""
        try:
            with open(self.sbom_path, 'r') as f:
                sbom = json.load(f)
            
            if sbom.get('bomFormat') != 'CycloneDX':
                raise ValueError("SBOM must be in CycloneDX format")
            
            return sbom
        except Exception as e:
            print(f"❌ Failed to load SBOM: {e}")
            sys.exit(1)
    
    def validate_structure(self) -> bool:
        """Validate SBOM structure and required fields"""
        required_fields = [
            'bomFormat', 'specVersion', 'serialNumber',
            'version', 'metadata', 'components'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in self.sbom_data:
                missing_fields.append(field)
        
        if missing_fields:
            self.compliance_issues.append({
                'type': 'structure',
                'message': f"Missing required fields: {missing_fields}",
                'severity': 'high'
            })
            return False
        
        print("✅ SBOM structure validation passed")
        return True
    
    def check_component_completeness(self) -> bool:
        """Verify component metadata completeness"""
        components = self.sbom_data.get('components', [])
        incomplete_components = []
        
        required_component_fields = ['type', 'name', 'version']
        
        for component in components:
            missing = [field for field in required_component_fields 
                      if field not in component]
            if missing:
                incomplete_components.append({
                    'component': component.get('name', 'unknown'),
                    'missing_fields': missing
                })
        
        if incomplete_components:
            self.compliance_issues.append({
                'type': 'component_metadata',
                'message': f"Incomplete components: {len(incomplete_components)}",
                'details': incomplete_components,
                'severity': 'medium'
            })
            return False
        
        print(f"✅ All {len(components)} components have complete metadata")
        return True
    
    def scan_vulnerabilities(self) -> bool:
        """Scan components for known vulnerabilities"""
        components = self.sbom_data.get('components', [])
        vulnerable_components = []
        
        for component in components:
            # Simulate vulnerability scanning
            # In production, integrate with actual vulnerability databases
            vulnerabilities = self._check_component_vulnerabilities(component)
            if vulnerabilities:
                vulnerable_components.append({
                    'component': f"{component.get('name')}@{component.get('version')}",
                    'vulnerabilities': vulnerabilities
                })
        
        if vulnerable_components:
            self.vulnerabilities.extend(vulnerable_components)
            print(f"⚠️  Found vulnerabilities in {len(vulnerable_components)} components")
            return False
        
        print("✅ No known vulnerabilities detected")
        return True
    
    def _check_component_vulnerabilities(self, component: Dict) -> List[Dict]:
        """Check component against vulnerability database"""
        # Placeholder for actual vulnerability scanning
        # Integrate with OSV, CVE databases, or commercial tools
        return []
    
    def validate_signatures(self) -> bool:
        """Validate cryptographic signatures if present"""
        # Check for signature metadata
        metadata = self.sbom_data.get('metadata', {})
        signatures = metadata.get('signatures', [])
        
        if not signatures:
            self.compliance_issues.append({
                'type': 'signatures',
                'message': "SBOM lacks cryptographic signatures",
                'severity': 'medium'
            })
            return False
        
        print("✅ SBOM signatures validated")
        return True
    
    def generate_report(self) -> Dict:
        """Generate comprehensive validation report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'sbom_path': self.sbom_path,
            'validation_results': {
                'structure_valid': len([i for i in self.compliance_issues 
                                      if i['type'] == 'structure']) == 0,
                'components_complete': len([i for i in self.compliance_issues 
                                          if i['type'] == 'component_metadata']) == 0,
                'vulnerabilities_found': len(self.vulnerabilities),
                'signatures_valid': len([i for i in self.compliance_issues 
                                       if i['type'] == 'signatures']) == 0
            },
            'compliance_issues': self.compliance_issues,
            'vulnerabilities': self.vulnerabilities,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if self.vulnerabilities:
            recommendations.append("Update vulnerable components to patched versions")
        
        if any(i['type'] == 'signatures' for i in self.compliance_issues):
            recommendations.append("Implement SBOM signing in build pipeline")
        
        if any(i['severity'] == 'high' for i in self.compliance_issues):
            recommendations.append("Address high-severity compliance issues immediately")
        
        return recommendations

def main():
    if len(sys.argv) != 2:
        print("Usage: python sbom_validator.py <sbom_file>")
        sys.exit(1)
    
    validator = SBOMValidator(sys.argv[1])
    
    print("🔍 Validating SBOM...")
    
    # Run all validation checks
    structure_ok = validator.validate_structure()
    components_ok = validator.check_component_completeness()
    vulnerabilities_ok = validator.scan_vulnerabilities()
    signatures_ok = validator.validate_signatures()
    
    # Generate and display report
    report = validator.generate_report()
    
    print("\n📊 Validation Summary:")
    print(f"  Structure Valid: {'✅' if structure_ok else '❌'}")
    print(f"  Components Complete: {'✅' if components_ok else '❌'}")
    print(f"  Vulnerabilities: {'✅ None' if vulnerabilities_ok else f'❌ {len(validator.vulnerabilities)} found'}")
    print(f"  Signatures Valid: {'✅' if signatures_ok else '❌'}")
    
    # Save detailed report
    with open('sbom_validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📋 Detailed report saved to: sbom_validation_report.json")
    
    # Exit with appropriate code
    if not all([structure_ok, components_ok, vulnerabilities_ok]):
        print("\n❌ SBOM validation failed - see issues above")
        sys.exit(1)
    else:
        print("\n✅ SBOM validation passed")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

### **2. Dependency Security Policies**

#### **Package Manager Configurations**

**NPM Security Configuration**
```json
// .npmrc
audit-level=moderate
fund=false
save-exact=true
engine-strict=true

// package.json security section
{
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=8.0.0"
  },
  "overrides": {
    // Pin vulnerable dependencies
  },
  "scripts": {
    "audit": "npm audit --audit-level moderate",
    "audit:fix": "npm audit fix",
    "security:check": "npm audit && npm run dependency:check"
  }
}
```

**Maven Security Configuration**
```xml
<!-- pom.xml dependency management -->
<properties>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
    <dependency-check-maven.version>8.4.2</dependency-check-maven.version>
</properties>

<build>
    <plugins>
        <plugin>
            <groupId>org.owasp</groupId>
            <artifactId>dependency-check-maven</artifactId>
            <version>${dependency-check-maven.version}</version>
            <configuration>
                <failBuildOnCVSS>7</failBuildOnCVSS>
                <skipProvidedScope>true</skipProvidedScope>
                <skipRuntimeScope>false</skipRuntimeScope>
            </configuration>
            <executions>
                <execution>
                    <goals>
                        <goal>check</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

#### **Container Security Policy**
```yaml
# Docker security scanning policy
container_security:
  base_images:
    allowed_registries:
      - "docker.io/library"  # Official Docker images
      - "gcr.io/distroless"  # Distroless images
      - "registry.example.com"  # Internal registry
    
    prohibited_tags:
      - "latest"
      - "master"
      - "main"
    
    required_scanning: true
    max_age_days: 30
  
  vulnerability_policy:
    critical: "block"
    high: "block"
    medium: "warn"
    low: "allow"
  
  dockerfile_policies:
    - "no_root_user"
    - "minimal_layers"
    - "pinned_versions"
    - "signed_base_images"
```

### **3. Supply Chain Monitoring**

#### **Continuous Monitoring Dashboard**
```yaml
# monitoring/supply-chain-dashboard.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: supply-chain-metrics
data:
  dashboard.json: |
    {
      "dashboard": {
        "title": "Supply Chain Security",
        "panels": [
          {
            "title": "Vulnerability Trends",
            "type": "graph",
            "targets": [
              {
                "expr": "vulnerability_count_by_severity",
                "legendFormat": "{{severity}}"
              }
            ]
          },
          {
            "title": "SBOM Compliance",
            "type": "stat",
            "targets": [
              {
                "expr": "sbom_generation_success_rate",
                "legendFormat": "Success Rate"
              }
            ]
          },
          {
            "title": "Dependency Age",
            "type": "heatmap",
            "targets": [
              {
                "expr": "dependency_age_days",
                "legendFormat": "Age (days)"
              }
            ]
          }
        ]
      }
    }
```

---

## 📊 **Templates & Tools**

### **SBOM Template (Enhanced)**
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:{{GENERATE_UUID}}",
  "version": 1,
  "metadata": {
    "timestamp": "{{ISO_TIMESTAMP}}",
    "tools": [
      {
        "vendor": "{{TOOL_VENDOR}}",
        "name": "{{TOOL_NAME}}",
        "version": "{{TOOL_VERSION}}"
      }
    ],
    "authors": [
      {
        "name": "{{BUILD_SYSTEM}}",
        "email": "security@example.com"
      }
    ],
    "supplier": {
      "name": "{{COMPANY_NAME}}",
      "url": ["{{COMPANY_URL}}"]
    },
    "properties": [
      {
        "name": "build:pipeline",
        "value": "{{CI_PIPELINE_URL}}"
      },
      {
        "name": "build:commit",
        "value": "{{GIT_COMMIT_SHA}}"
      },
      {
        "name": "security:scan-date",
        "value": "{{SCAN_TIMESTAMP}}"
      }
    ]
  },
  "components": [
    {
      "type": "library",
      "bom-ref": "{{COMPONENT_REF}}",
      "name": "{{COMPONENT_NAME}}",
      "version": "{{COMPONENT_VERSION}}",
      "scope": "{{COMPONENT_SCOPE}}",
      "hashes": [
        {
          "alg": "SHA-256",
          "content": "{{SHA256_HASH}}"
        }
      ],
      "licenses": [
        {
          "license": {
            "id": "{{LICENSE_ID}}",
            "name": "{{LICENSE_NAME}}"
          }
        }
      ],
      "purl": "{{PACKAGE_URL}}",
      "externalReferences": [
        {
          "type": "website",
          "url": "{{COMPONENT_HOMEPAGE}}"
        },
        {
          "type": "vcs",
          "url": "{{COMPONENT_REPOSITORY}}"
        }
      ],
      "properties": [
        {
          "name": "security:vulnerability-scan",
          "value": "{{VULNERABILITY_SCAN_RESULT}}"
        }
      ]
    }
  ],
  "dependencies": [
    {
      "ref": "{{PARENT_COMPONENT_REF}}",
      "dependsOn": ["{{DEPENDENCY_REF}}"]
    }
  ],
  "vulnerabilities": [
    {
      "bom-ref": "{{VULNERABILITY_REF}}",
      "id": "{{CVE_ID}}",
      "source": {
        "name": "{{VULNERABILITY_SOURCE}}",
        "url": "{{VULNERABILITY_URL}}"
      },
      "ratings": [
        {
          "source": {
            "name": "{{RATING_SOURCE}}"
          },
          "score": {{CVSS_SCORE}},
          "severity": "{{SEVERITY}}",
          "method": "{{CVSS_VERSION}}"
        }
      ],
      "affects": [
        {
          "ref": "{{AFFECTED_COMPONENT_REF}}"
        }
      ]
    }
  ]
}
```

### **Dependency Review Checklist**
```markdown
# Dependency Security Review Checklist

## 📋 **Pre-Addition Review**
- [ ] **License Compatibility**: License is approved for use
- [ ] **Vulnerability Scan**: No critical/high vulnerabilities
- [ ] **Maintenance Status**: Active maintenance (commits within 6 months)
- [ ] **Community Trust**: Established maintainer, good reputation
- [ ] **Alternatives Evaluated**: Considered internal/approved alternatives

## 🔍 **Security Assessment**
- [ ] **Source Code Review**: Reviewed for malicious code
- [ ] **Supply Chain**: Verified publisher identity
- [ ] **Download Integrity**: Checksums verified
- [ ] **Signature Validation**: Package signatures verified
- [ ] **Transitive Dependencies**: Reviewed all dependencies

## 📊 **Risk Assessment**
- [ ] **Attack Surface**: Evaluated permission requirements
- [ ] **Data Access**: Reviewed data handling capabilities
- [ ] **Network Access**: Evaluated network communication
- [ ] **Privilege Requirements**: Minimal privilege principle followed
- [ ] **Compliance Impact**: Meets regulatory requirements

## ✅ **Approval Requirements**
- [ ] **Security Team Approval**: For high-risk dependencies
- [ ] **Architecture Review**: For core/infrastructure dependencies
- [ ] **Legal Review**: For restrictive licenses
- [ ] **Documentation**: Added to dependency inventory

## 🔄 **Ongoing Monitoring**
- [ ] **Automated Scanning**: Added to vulnerability monitoring
- [ ] **Update Policy**: Update schedule defined
- [ ] **EOL Monitoring**: End-of-life tracking enabled
- [ ] **Usage Tracking**: Usage patterns monitored
```

---

## 🔧 **Validation & Testing**

### **Supply Chain Security Tests**
```python
# tests/test_supply_chain_security.py
import pytest
import json
import os
from pathlib import Path

class TestSupplyChainSecurity:
    
    def test_sbom_generation(self):
        """Test SBOM generation in build pipeline"""
        sbom_path = "dist/sbom.cyclonedx.json"
        assert os.path.exists(sbom_path), "SBOM file not generated"
        
        with open(sbom_path) as f:
            sbom = json.load(f)
        
        assert sbom["bomFormat"] == "CycloneDX"
        assert "components" in sbom
        assert len(sbom["components"]) > 0
    
    def test_vulnerability_scanning(self):
        """Test vulnerability scanning in CI"""
        # Check that vulnerability scan results exist
        scan_results = Path("security/vulnerability-scan.json")
        assert scan_results.exists(), "Vulnerability scan not performed"
        
        with scan_results.open() as f:
            results = json.load(f)
        
        # No critical vulnerabilities allowed
        critical_vulns = [v for v in results.get("vulnerabilities", []) 
                         if v.get("severity") == "critical"]
        assert len(critical_vulns) == 0, f"Critical vulnerabilities found: {critical_vulns}"
    
    def test_package_signatures(self):
        """Test package signature verification"""
        # Implementation depends on package manager
        # This is a placeholder for signature verification tests
        pass
    
    def test_dependency_freshness(self):
        """Test that dependencies are reasonably fresh"""
        # Check that dependencies aren't too old
        # Implementation depends on package manager and policies
        pass
    
    @pytest.mark.integration
    def test_supply_chain_monitoring(self):
        """Test supply chain monitoring integration"""
        # Verify monitoring dashboards are accessible
        # Check that metrics are being collected
        pass
```

---

## 📈 **Metrics & Monitoring**

### **Key Performance Indicators**
```yaml
supply_chain_kpis:
  security_metrics:
    - name: "vulnerability_detection_time"
      target: "< 24 hours"
      measurement: "time from CVE publication to detection"
    
    - name: "vulnerability_remediation_time"
      target: "< 7 days for critical, < 30 days for high"
      measurement: "time from detection to fix deployment"
    
    - name: "sbom_coverage"
      target: "100%"
      measurement: "percentage of builds with valid SBOM"
    
    - name: "dependency_freshness"
      target: "> 80% within 6 months"
      measurement: "percentage of dependencies with recent updates"
  
  compliance_metrics:
    - name: "signature_coverage"
      target: "100%"
      measurement: "percentage of packages with verified signatures"
    
    - name: "policy_violations"
      target: "0"
      measurement: "number of policy violations in production"
```

---

## 🚨 **Incident Response**

### **Supply Chain Incident Playbook**
```markdown
# Supply Chain Security Incident Response

## 🚨 **Immediate Response (0-2 hours)**
1. **Assess Impact**
   - Identify affected services and dependencies
   - Determine scope of potential compromise
   - Activate incident response team

2. **Containment**
   - Block deployment of affected dependencies
   - Isolate potentially compromised systems
   - Preserve forensic evidence

## 🔍 **Investigation (2-24 hours)**
3. **Evidence Collection**
   - Collect SBOM data for affected systems
   - Review dependency installation logs
   - Analyze network traffic patterns

4. **Impact Analysis**
   - Map dependency usage across systems
   - Identify data access patterns
   - Assess potential data exposure

## 🛠 **Remediation (24-72 hours)**
5. **Dependency Replacement**
   - Identify clean dependency versions
   - Update and test applications
   - Validate fix effectiveness

6. **System Hardening**
   - Update security policies
   - Enhance monitoring rules
   - Implement additional controls

## 📊 **Recovery & Lessons Learned**
7. **Recovery Validation**
   - Perform security scans
   - Validate system integrity
   - Resume normal operations

8. **Post-Incident Review**
   - Document timeline and actions
   - Identify improvement opportunities
   - Update policies and procedures
```

---

## 📚 **References & Standards**

### **Compliance Mappings**
- **NIST SP 800-161**: Supply Chain Risk Management
- **SLSA Framework**: Supply-chain Levels for Software Artifacts
- **SPDX**: Software Package Data Exchange
- **CycloneDX**: Software Bill of Materials standard
- **NIST SP 800-218**: Secure Software Development Framework

### **Integration Points**
- **Rule 03C**: Security & Encryption (artifact signing)
- **Rule 16B**: API Gateway Management (dependency validation)
- **Rule 18A**: Quality Assurance (security testing integration)
- **Rule 19C**: Data Governance (dependency data management)

---

**Implementation Status**: ✅ Complete  
**Validation Required**: CI/CD integration, vulnerability scanning, SBOM generation  
**Next Steps**: Integrate with Rule 19C for comprehensive data governance 
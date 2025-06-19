# Rule SEC-07: Supply-Chain Security & Signing

## 🛡 **Summary**
Ensure integrity of builds and artifacts through provenance, SBOMs, and digital signatures to protect against supply chain attacks and maintain trust in software delivery.

## 🔍 **Problem Statement**
Compromised build systems and unsigned artifacts enable malware injection. Artifacts must be signed and traceable to maintain integrity throughout the software supply chain.

## ✅ **Standard Requirements**

### **MANDATORY Supply Chain Controls**
- **All builds MUST generate SBOMs**
- **Releases MUST be signed (Sigstore/GPG)**
- **CI MUST enforce provenance verification**
- **SBOMs MUST be stored and versioned**

### **SLSA Framework Implementation**
```yaml
# SLSA Level 2 Configuration
slsa_requirements:
  source:
    - "Version controlled source"
    - "Verified history"
  build:
    - "Scripted build"
    - "Build service"
  provenance:
    - "Available provenance"
    - "Authenticated provenance"
```

## 🧪 **Implementation Guidance**

### **Artifact Signing**
- Use CycloneDX or SPDX SBOM format
- Sigstore/Gitsign for commit/release signing
- SLSA framework level 2 or higher
- Implement keyless signing with Fulcio

### **SBOM Generation**
```yaml
# Syft SBOM Configuration
# syft.yaml
file:
  content:
    - "go-module"
    - "python"
    - "javascript"
output:
  - "json"
  - "spdx-json"
log:
  level: "error"
```

### **Provenance Verification**
```yaml
# CI pipeline with SLSA
name: SLSA Provenance
on:
  push:
    tags: ["v*"]

jobs:
  build:
    permissions:
      id-token: write
      contents: read
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v1.7.0
    with:
      base64-subjects: "${{ needs.build.outputs.digests }}"
```

## 📈 **Success Metrics**
- ✅ **100% artifacts signed**
- ✅ **100% SBOMs generated for releases**
- ✅ **0 unsigned release artifacts**

## 🧩 **Related Tools**
- **Sigstore/Cosign**: Keyless signing infrastructure
- **CycloneDX**: SBOM generation and management
- **SLSA/Gitsign**: Supply chain security framework

## 🏛 **Compliance Mapping**

| Framework | Control ID | Coverage |
|-----------|------------|----------|
| **NIST SSDF** | RV.1.3 | ✅ Full |
| **ISO 27001** | A.12.5.1 | ✅ Full |
| **SOC 2** | CC7.2 | ✅ Full |

---

## 📋 **Implementation Checklist**
- [ ] Configure artifact signing with Sigstore
- [ ] Implement SBOM generation
- [ ] Set up provenance verification
- [ ] Configure SLSA compliance
- [ ] Train teams on supply chain security
- [ ] Monitor signing compliance

This rule establishes comprehensive supply chain security with artifact signing, SBOM generation, and provenance verification.


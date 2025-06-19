# Rule SEC-03: Runtime Hardening

## 🛡 **Summary**
Secure services at runtime using sandboxing, least privilege, and container policies to minimize attack surface and reduce impact of potential security breaches.

## 🔍 **Problem Statement**
Even well-written applications can be exploited at runtime. Enforcing minimal permissions and kernel hardening reduces impact of attacks and provides defense-in-depth security.

## ✅ **Standard Requirements**

### **MANDATORY Container Security**
- **Containers MUST use read-only root filesystem**
- **Capabilities MUST be dropped (no CAP_SYS_ADMIN)**
- **Seccomp, AppArmor, or SELinux profiles MUST be applied**
- **Network access MUST be scoped via CNI policies**

### **Kubernetes Security Standards**
```yaml
# Pod Security Standards
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 65534
    fsGroup: 65534
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

## 🧪 **Implementation Guidance**

### **Container Hardening**
- Use PodSecurity or OPA/Gatekeeper in Kubernetes
- Apply `seccompProfile: RuntimeDefault`
- Audit with Trivy or kube-bench
- Implement network policies for micro-segmentation

### **Runtime Policies**
```yaml
# NetworkPolicy example
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

## 📈 **Success Metrics**
- ✅ **100% pods with seccomp profiles**
- ✅ **0 privileged containers**
- ✅ **No hostPath mounts**

## 🧩 **Related Tools**
- **Trivy**: Container security scanning
- **Kyverno/OPA**: Policy enforcement
- **PodSecurity Standards**: Kubernetes-native policies

## 🏛 **Compliance Mapping**

| Framework | Control ID | Coverage |
|-----------|------------|----------|
| **NIST SSDF** | PS.3.1 | ✅ Full |
| **ISO 27001** | A.13.1.1 | ✅ Full |
| **SOC 2** | CC6.7 | ✅ Full |

---

## 📋 **Implementation Checklist**
- [ ] Configure read-only root filesystems
- [ ] Drop all unnecessary capabilities
- [ ] Apply seccomp profiles
- [ ] Implement network policies
- [ ] Set up runtime monitoring
- [ ] Audit container configurations

This rule establishes comprehensive runtime security hardening for containerized applications.


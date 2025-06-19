---
description: "Universal network topology and ingress: load balancing, service discovery, TLS termination, network policies. Cloud-native networking standards."
globs: ["**/*"]
alwaysApply: true
---

# 🌐 Universal Network Topology & Ingress

## 1. Load Balancing & Ingress

### Ingress Controller Requirements
- **MUST** use standard ingress controllers (nginx, traefik, istio-gateway, ALB)
- **REQUIRE:** TLS termination at ingress layer with valid certificates
- **IMPLEMENT:** HTTP to HTTPS redirects for all public endpoints
- **CONFIGURE:** Request timeout, body size limits, and rate limiting at ingress

### Ingress Configuration Template
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: service-ingress
  annotations:
    # TLS and Security
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    
    # Rate Limiting
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    
    # Request Size Limits
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/client-max-body-size: "10m"
    
    # Timeouts
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "30"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "30"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "30"
    
    # CORS (if needed)
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://app.example.com"
    
    # Security Headers
    nginx.ingress.kubernetes.io/configuration-snippet: |
      add_header X-Frame-Options DENY;
      add_header X-Content-Type-Options nosniff;
      add_header X-XSS-Protection "1; mode=block";
      add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
      
spec:
  tls:
    - hosts:
        - api.example.com
      secretName: api-tls-cert
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /api/v1
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 8080
```

### Load Balancer Configuration
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service
  annotations:
    # AWS Load Balancer Controller
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-path: "/healthz"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-interval: "30"
    
    # GCP Load Balancer
    cloud.google.com/neg: '{"ingress": true}'
    cloud.google.com/backend-config: '{"default": "api-backend-config"}'
    
    # Session Affinity (if needed)
    service.beta.kubernetes.io/aws-load-balancer-target-group-attributes: |
      stickiness.enabled=true,stickiness.lb_cookie.duration_seconds=86400
      
spec:
  type: LoadBalancer
  ports:
    - name: http
      port: 80
      targetPort: 8080
      protocol: TCP
    - name: https
      port: 443
      targetPort: 8080
      protocol: TCP
    - name: metrics
      port: 9090
      targetPort: 9090
      protocol: TCP
  selector:
    app: api-service
  sessionAffinity: None  # Use None unless specifically needed
```

### Health Check Configuration
- **REQUIRE:** Load balancer health checks on `/healthz` endpoint
- **SET:** Health check interval 30s, timeout 5s, healthy threshold 2, unhealthy threshold 3
- **IMPLEMENT:** Graceful degradation on health check failures
- **MONITOR:** Health check success rates and response times

## 2. Service Discovery & DNS

### Service Discovery Standards
- **USE:** Kubernetes native service discovery (DNS, environment variables)
- **IMPLEMENT:** Service mesh for complex routing (Istio, Linkerd, Consul Connect)
- **CONFIGURE:** DNS-based service discovery with consistent naming
- **MAINTAIN:** Service registry with health status and metadata

### Service Naming Convention
```yaml
# Service naming follows: <service-name>.<namespace>.svc.cluster.local
# Examples:
# - user-service.api.svc.cluster.local
# - order-processor.workers.svc.cluster.local
# - redis-cache.data.svc.cluster.local

# Service definition
apiVersion: v1
kind: Service
metadata:
  name: user-service  # MUST match metadata.yaml service.name
  namespace: api      # Environment-based namespace
  labels:
    app: user-service
    version: v1.2.3
    tier: "1"
    team: "platform"
spec:
  ports:
    - name: http
      port: 8080
      targetPort: 8080
    - name: metrics
      port: 9090
      targetPort: 9090
  selector:
    app: user-service
```

### DNS Configuration
- **CONFIGURE:** Internal DNS resolution for service-to-service communication
- **USE:** Fully qualified domain names (FQDN) for cross-namespace communication
- **IMPLEMENT:** DNS caching and TTL optimization for performance
- **MONITOR:** DNS resolution latency and failure rates

### Service Mesh Configuration (Optional)
```yaml
# Istio VirtualService example
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: user-service
spec:
  hosts:
    - user-service
  http:
    - match:
        - headers:
            version:
              exact: v2
      route:
        - destination:
            host: user-service
            subset: v2
    - route:
        - destination:
            host: user-service
            subset: v1
          weight: 100
```

## 3. TLS & Certificate Management

### TLS Requirements
- **REQUIRE:** TLS 1.2+ for all external communication
- **IMPLEMENT:** Automated certificate management (cert-manager, ACM)
- **USE:** Valid certificates from trusted CA (Let's Encrypt, commercial CA)
- **CONFIGURE:** Certificate rotation and renewal automation

### Certificate Management
```yaml
# cert-manager ClusterIssuer
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: cert-admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
      - dns01:
          route53:
            region: us-west-2
            accessKeyID: AKIAIOSFODNN7EXAMPLE
            secretAccessKeySecretRef:
              name: prod-route53-credentials-secret
              key: secret-access-key

---
# Certificate resource
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: api-example-com
spec:
  secretName: api-tls-cert
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - api.example.com
    - www.api.example.com
```

### TLS Configuration Best Practices
- **DISABLE:** SSLv3, TLS 1.0, TLS 1.1 (security vulnerabilities)
- **ENABLE:** HTTP Strict Transport Security (HSTS) headers
- **CONFIGURE:** Strong cipher suites and perfect forward secrecy
- **IMPLEMENT:** Certificate transparency monitoring

## 4. Network Policies & Security

### Network Policy Requirements
- **IMPLEMENT:** Default deny-all network policies
- **ALLOW:** Explicit ingress/egress rules for required communication
- **ISOLATE:** Namespaces and services with minimal required connectivity
- **MONITOR:** Network policy violations and blocked traffic

### Network Policy Template
```yaml
# Default deny-all policy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: api
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress

---
# Allow specific service communication
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: user-service-policy
  namespace: api
spec:
  podSelector:
    matchLabels:
      app: user-service
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # Allow ingress from nginx ingress controller
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8080
    # Allow metrics scraping from monitoring
    - from:
        - namespaceSelector:
            matchLabels:
              name: monitoring
      ports:
        - protocol: TCP
          port: 9090
  egress:
    # Allow DNS resolution
    - to: []
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
    # Allow database connection
    - to:
        - namespaceSelector:
            matchLabels:
              name: data
      ports:
        - protocol: TCP
          port: 5432
    # Allow external HTTPS
    - to: []
      ports:
        - protocol: TCP
          port: 443
```

### Security Groups & Firewall Rules
- **IMPLEMENT:** Principle of least privilege for network access
- **CONFIGURE:** Application-specific security groups/firewall rules
- **MONITOR:** Network traffic patterns and anomalies
- **AUDIT:** Regular review of network access permissions

## 5. Performance & Monitoring

### Network Performance Requirements
- **TARGET:** < 5ms latency for intra-cluster communication
- **TARGET:** < 100ms latency for cross-region communication
- **MONITOR:** Network throughput, packet loss, and latency
- **IMPLEMENT:** Network performance testing and optimization

### Load Balancer Monitoring
```yaml
# Prometheus monitoring for ingress
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: nginx-ingress
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: ingress-nginx
  endpoints:
    - port: metrics
      interval: 30s
      path: /metrics
```

### Network Metrics
- **TRACK:** Request rate, error rate, and latency (RED metrics)
- **MONITOR:** Connection pool utilization and timeouts
- **ALERT:** High latency, error rates, or connection failures
- **ANALYZE:** Traffic patterns and capacity planning

## 6. CDN & Edge Configuration

### CDN Requirements
- **IMPLEMENT:** CDN for static assets and API responses where appropriate
- **CONFIGURE:** Cache headers and TTL policies
- **USE:** Edge locations for global content delivery
- **MONITOR:** CDN hit rates and performance metrics

### Edge Configuration Template
```yaml
# CloudFront distribution example
apiVersion: cloudfront.aws.crossplane.io/v1alpha1
kind: Distribution
metadata:
  name: api-cdn
spec:
  forProvider:
    aliases:
      - api.example.com
    defaultCacheBehavior:
      targetOriginId: api-origin
      viewerProtocolPolicy: redirect-to-https
      cachePolicyId: 4135ea2d-6df8-44a3-9df3-4b5a84be39ad  # CachingOptimized
      originRequestPolicyId: 88a5eaf4-2fd4-4709-b370-b4c650ea3fcf  # CORS-S3Origin
    origins:
      - id: api-origin
        domainName: api-alb.us-west-2.elb.amazonaws.com
        customOriginConfig:
          httpPort: 80
          httpsPort: 443
          originProtocolPolicy: https-only
    enabled: true
    priceClass: PriceClass_100
    viewerCertificate:
      acmCertificateArn: arn:aws:acm:us-east-1:123456789:certificate/12345
      sslSupportMethod: sni-only
```

---

## 🛠️ Enforcement & Tooling

### Required CI Checks
- [ ] Ingress configuration validation (TLS, security headers, rate limits)
- [ ] Network policy presence and correctness
- [ ] Load balancer health check configuration
- [ ] Certificate expiration monitoring setup
- [ ] DNS configuration validation

### Repository Requirements
- [ ] `ingress.yaml` with TLS and security configurations
- [ ] `network-policies.yaml` with least-privilege access
- [ ] `service.yaml` with proper port and selector configuration
- [ ] Certificate management automation setup
- [ ] Load balancer configuration with health checks

### Recommended Tools
- **Ingress:** nginx-ingress, traefik, istio-gateway, AWS ALB Controller
- **Certificates:** cert-manager, external-dns, Let's Encrypt, AWS ACM
- **Service Mesh:** Istio, Linkerd, Consul Connect
- **Monitoring:** Prometheus, Grafana, Jaeger, Datadog

### Network Metrics
- **Latency:** P95 network latency < 5ms intra-cluster, < 100ms cross-region
- **Throughput:** Network bandwidth utilization and capacity
- **Availability:** Ingress and load balancer uptime > 99.9%
- **Security:** Network policy violations and blocked connections

---

*This rule focuses on network architecture and ingress management. See also: MI-02-service-container-design.md for container requirements and MI-03-service-metadata-roles.md for service lifecycle management.* 
# Kubernetes Services - Production Ready

A **Service** exposes an application running on a set of Pods as a network service with stable DNS and IP.

---

## Service Types Overview

| Type | Scope | Use Case |
|------|-------|----------|
| **ClusterIP** | Internal only | Internal microservices |
| **NodePort** | Node IP + Port | Development, on-prem |
| **LoadBalancer** | External LB | Cloud production |
| **ExternalName** | DNS alias | External services |
| **Headless** | Direct pod access | StatefulSets, databases |

---

## 1. ClusterIP Service (Production)

Internal cluster access only - default and most secure.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
  namespace: production
  labels:
    app.kubernetes.io/name: myapp
    app.kubernetes.io/instance: myapp-prod
    app.kubernetes.io/component: backend
    environment: production
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
    prometheus.io/path: "/metrics"
    # For service mesh
    # service.beta.kubernetes.io/aws-load-balancer-internal: "true"
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: myapp
    app.kubernetes.io/instance: myapp-prod
  ports:
    - name: http
      port: 80
      targetPort: 8080
      protocol: TCP
    - name: https
      port: 443
      targetPort: 8443
      protocol: TCP
    - name: metrics
      port: 9090
      targetPort: 9090
      protocol: TCP
    - name: grpc
      port: 50051
      targetPort: 50051
      protocol: TCP
  # Session Affinity (sticky sessions)
  sessionAffinity: None  # or ClientIP
  # sessionAffinityConfig:
  #   clientIP:
  #     timeoutSeconds: 10800  # 3 hours
  
  # IP Family (dual-stack support)
  ipFamilyPolicy: SingleStack  # SingleStack, PreferDualStack, RequireDualStack
  ipFamilies:
    - IPv4
  
  # Internal Traffic Policy
  internalTrafficPolicy: Cluster  # Cluster or Local
  
  # Publishing Not Ready Addresses
  publishNotReadyAddresses: false
```

---

## 2. NodePort Service

Exposes on each node's IP at a static port (30000-32767).

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-nodeport
  namespace: production
  labels:
    app.kubernetes.io/name: myapp
  annotations:
    # Allocate from specific port range
    # service.kubernetes.io/nodeport: "true"
spec:
  type: NodePort
  selector:
    app.kubernetes.io/name: myapp
    app.kubernetes.io/instance: myapp-prod
  ports:
    - name: http
      port: 80
      targetPort: 8080
      nodePort: 30080  # Optional: let K8s assign if omitted
      protocol: TCP
    - name: https
      port: 443
      targetPort: 8443
      nodePort: 30443
      protocol: TCP
  
  # External Traffic Policy
  externalTrafficPolicy: Local  # Local preserves client IP, Cluster distributes evenly
  
  # Health Check Node Port (when externalTrafficPolicy: Local)
  # healthCheckNodePort: 30000
```

---

## 3. LoadBalancer Service (Cloud Production)

### Azure AKS LoadBalancer

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-lb
  namespace: production
  labels:
    app.kubernetes.io/name: myapp
  annotations:
    # Azure Internal Load Balancer
    service.beta.kubernetes.io/azure-load-balancer-internal: "true"
    
    # Azure Resource Group for LB
    service.beta.kubernetes.io/azure-load-balancer-resource-group: "my-rg"
    
    # Azure Subnet (internal LB)
    service.beta.kubernetes.io/azure-load-balancer-internal-subnet: "internal-subnet"
    
    # Azure Health Probe
    service.beta.kubernetes.io/azure-load-balancer-health-probe-request-path: "/healthz"
    service.beta.kubernetes.io/azure-load-balancer-health-probe-protocol: "http"
    service.beta.kubernetes.io/azure-load-balancer-health-probe-interval: "5"
    service.beta.kubernetes.io/azure-load-balancer-health-probe-num-of-probe: "2"
    
    # Azure Standard LB
    service.beta.kubernetes.io/azure-load-balancer-sku: "Standard"
    
    # Azure PIP (Public IP)
    # service.beta.kubernetes.io/azure-pip-name: "myapp-pip"
    # service.beta.kubernetes.io/azure-dns-label-name: "myapp"
    
    # Azure Disable Floating IP
    service.beta.kubernetes.io/azure-load-balancer-disable-tcp-reset: "false"
    
    # Idle Timeout
    service.beta.kubernetes.io/azure-load-balancer-tcp-idle-timeout: "30"
spec:
  type: LoadBalancer
  selector:
    app.kubernetes.io/name: myapp
    app.kubernetes.io/instance: myapp-prod
  ports:
    - name: http
      port: 80
      targetPort: 8080
      protocol: TCP
    - name: https
      port: 443
      targetPort: 8443
      protocol: TCP
  
  # External Traffic Policy
  externalTrafficPolicy: Local  # Preserves client IP
  
  # Load Balancer Source Ranges (IP allowlist)
  loadBalancerSourceRanges:
    - 10.0.0.0/8
    - 172.16.0.0/12
    - 192.168.0.0/16
    - 203.0.113.0/24  # Specific external range
  
  # Allocate Load Balancer Node Ports
  allocateLoadBalancerNodePorts: true
  
  # Load Balancer Class (for multi-LB setups)
  # loadBalancerClass: service.k8s.azure/internal
  
  # Static IP (must pre-create)
  # loadBalancerIP: 10.0.1.100
```

### AWS EKS LoadBalancer

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-lb-aws
  namespace: production
  annotations:
    # AWS NLB (Network Load Balancer)
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    
    # AWS Internal LB
    service.beta.kubernetes.io/aws-load-balancer-internal: "true"
    
    # AWS Cross-Zone Load Balancing
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
    
    # AWS Target Group Attributes
    service.beta.kubernetes.io/aws-load-balancer-target-group-attributes: "deregistration_delay.timeout_seconds=30"
    
    # AWS SSL Certificate (ALB/NLB)
    # service.beta.kubernetes.io/aws-load-balancer-ssl-cert: "arn:aws:acm:..."
    # service.beta.kubernetes.io/aws-load-balancer-ssl-ports: "443"
    
    # AWS Backend Protocol
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: "tcp"
    
    # AWS Health Check
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-path: "/healthz"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-interval: "10"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-timeout: "5"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-healthy-threshold: "2"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-unhealthy-threshold: "2"
spec:
  type: LoadBalancer
  selector:
    app.kubernetes.io/name: myapp
  ports:
    - name: http
      port: 80
      targetPort: 8080
  externalTrafficPolicy: Local
```

### GCP GKE LoadBalancer

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-lb-gcp
  namespace: production
  annotations:
    # GCP Internal Load Balancer
    networking.gke.io/load-balancer-type: "Internal"
    
    # GCP Backend Config
    cloud.google.com/backend-config: '{"default": "myapp-backend-config"}'
    
    # GCP NEG (Network Endpoint Groups)
    cloud.google.com/neg: '{"ingress": true}'
spec:
  type: LoadBalancer
  selector:
    app.kubernetes.io/name: myapp
  ports:
    - name: http
      port: 80
      targetPort: 8080
  externalTrafficPolicy: Local
```

---

## 4. ExternalName Service

Maps service to external DNS name (CNAME).

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-database
  namespace: production
  labels:
    app.kubernetes.io/name: external-database
    app.kubernetes.io/component: database
spec:
  type: ExternalName
  externalName: mydb.database.azure.com
  # No selector needed
  # No ports needed (DNS-level redirect)
```

**Usage:**
```bash
# From within cluster
nslookup external-database.production.svc.cluster.local
# Returns: mydb.database.azure.com
```

---

## 5. Headless Service

Direct pod-to-pod DNS (no load balancing). Used for StatefulSets.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-headless
  namespace: production
  labels:
    app.kubernetes.io/name: myapp
    app.kubernetes.io/component: database
spec:
  type: ClusterIP
  clusterIP: None  # Makes it headless
  selector:
    app.kubernetes.io/name: myapp
  ports:
    - name: tcp
      port: 5432
      targetPort: 5432
      protocol: TCP
  
  # IMPORTANT for StatefulSets
  publishNotReadyAddresses: true  # Include not-ready pods in DNS
```

**DNS Resolution:**
```bash
# Returns all pod IPs
nslookup myapp-headless.production.svc.cluster.local

# Individual pod DNS (with StatefulSet)
nslookup myapp-0.myapp-headless.production.svc.cluster.local
nslookup myapp-1.myapp-headless.production.svc.cluster.local
```

---

## 6. Multi-Port Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-multiport
  namespace: production
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: myapp
  ports:
    - name: http
      port: 80
      targetPort: 8080
      protocol: TCP
    - name: https
      port: 443
      targetPort: 8443
      protocol: TCP
    - name: grpc
      port: 9000
      targetPort: 9000
      protocol: TCP
    - name: metrics
      port: 9090
      targetPort: metrics  # Can use named port
      protocol: TCP
    - name: admin
      port: 8081
      targetPort: admin
      protocol: TCP
```

---

## Service with External IPs

Route traffic from specific external IPs.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-external-ip
  namespace: production
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: myapp
  ports:
    - port: 80
      targetPort: 8080
  externalIPs:
    - 203.0.113.10
    - 203.0.113.11
```

---

## Endpoints (Manual Service)

Create service without selector, manage endpoints manually.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-api
  namespace: production
spec:
  type: ClusterIP
  ports:
    - port: 443
      targetPort: 443
---
apiVersion: v1
kind: Endpoints
metadata:
  name: external-api  # Must match service name
  namespace: production
subsets:
  - addresses:
      - ip: 203.0.113.50
      - ip: 203.0.113.51
    ports:
      - port: 443
```

---

## EndpointSlices (K8s 1.21+)

Modern replacement for Endpoints, better scalability.

```yaml
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: myapp-service-abc123
  namespace: production
  labels:
    kubernetes.io/service-name: myapp-service
addressType: IPv4
ports:
  - name: http
    port: 8080
    protocol: TCP
endpoints:
  - addresses:
      - "10.244.1.10"
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: node-1
    zone: us-east-1a
  - addresses:
      - "10.244.2.20"
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: node-2
    zone: us-east-1b
```

---

## Service Discovery

### DNS-Based Discovery

```bash
# Full DNS name
<service>.<namespace>.svc.<cluster-domain>
myapp-service.production.svc.cluster.local

# Short forms (within same namespace)
myapp-service
myapp-service.production

# SRV records (for port discovery)
_http._tcp.myapp-service.production.svc.cluster.local
```

### Environment Variables

```bash
# Auto-injected env vars (if service exists before pod)
MYAPP_SERVICE_SERVICE_HOST=10.96.100.50
MYAPP_SERVICE_SERVICE_PORT=80
MYAPP_SERVICE_SERVICE_PORT_HTTP=80
MYAPP_SERVICE_SERVICE_PORT_HTTPS=443
```

### DNS Config in Pod

```yaml
spec:
  dnsPolicy: ClusterFirst
  dnsConfig:
    nameservers:
      - 10.96.0.10
    searches:
      - production.svc.cluster.local
      - svc.cluster.local
      - cluster.local
    options:
      - name: ndots
        value: "2"
      - name: single-request-reopen
```

---

## Traffic Policies

### External Traffic Policy

| Policy | Client IP | Traffic Distribution | Health |
|--------|-----------|---------------------|--------|
| **Cluster** | SNAT (lost) | All nodes | Standard |
| **Local** | Preserved | Local pods only | Node-level health check |

```yaml
spec:
  externalTrafficPolicy: Local  # or Cluster
```

### Internal Traffic Policy (K8s 1.22+)

```yaml
spec:
  internalTrafficPolicy: Local  # Route to local pods first
```

---

## Session Affinity

### Client IP Based

```yaml
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800  # 3 hours
```

---

## Production Checklist

### Configuration
- [ ] Meaningful service name matching app
- [ ] Correct namespace
- [ ] Proper labels (app.kubernetes.io/*)
- [ ] Named ports (http, https, grpc, metrics)
- [ ] Correct selector matching pod labels

### Security
- [ ] Use ClusterIP for internal services
- [ ] LoadBalancer with `loadBalancerSourceRanges` for IP allowlist
- [ ] Internal LB annotation for cloud providers
- [ ] NetworkPolicy restricting service access

### Reliability
- [ ] Multiple replicas behind service
- [ ] Health check annotations (for LB)
- [ ] Appropriate `externalTrafficPolicy`
- [ ] Consider `publishNotReadyAddresses` for StatefulSets

### Observability
- [ ] Prometheus scrape annotations
- [ ] Metrics port exposed
- [ ] Service monitor for Prometheus Operator

---

## Common Commands

```bash
# List services
kubectl get services -n production
kubectl get svc -n production -o wide

# Describe service
kubectl describe service myapp-service -n production

# Get endpoints
kubectl get endpoints myapp-service -n production
kubectl get endpointslices -l kubernetes.io/service-name=myapp-service -n production

# Test service (from another pod)
kubectl run test --rm -it --image=busybox -- wget -qO- http://myapp-service
kubectl run test --rm -it --image=curlimages/curl -- curl -s http://myapp-service/healthz

# DNS lookup
kubectl run dns-test --rm -it --image=busybox -- nslookup myapp-service.production.svc.cluster.local

# Port forward (for local testing)
kubectl port-forward svc/myapp-service 8080:80 -n production

# Get service YAML
kubectl get svc myapp-service -n production -o yaml

# Delete service
kubectl delete svc myapp-service -n production

# Check external IP (LoadBalancer)
kubectl get svc myapp-lb -n production -w
```

---

## Debugging Services

### Service Not Reachable

```bash
# 1. Check service exists
kubectl get svc myapp-service -n production

# 2. Check endpoints are populated
kubectl get endpoints myapp-service -n production
# Empty endpoints = selector doesn't match pods

# 3. Check selector matches pod labels
kubectl get pods -l app.kubernetes.io/name=myapp -n production

# 4. Check pods are Ready
kubectl get pods -n production | grep myapp

# 5. Check pod readiness probes
kubectl describe pod myapp-xxx -n production | grep -A 10 "Readiness"

# 6. Test from within cluster
kubectl run debug --rm -it --image=busybox -n production -- sh
> wget -qO- http://myapp-service
> nslookup myapp-service

# 7. Check NetworkPolicies
kubectl get networkpolicy -n production
```

### LoadBalancer Stuck Pending

```bash
# Check events
kubectl describe svc myapp-lb -n production | grep -A 20 "Events"

# Check cloud provider logs
# Azure: Check AKS activity log
# AWS: Check cloud-controller-manager logs
kubectl logs -n kube-system -l component=cloud-controller-manager

# Verify annotations are correct for your cloud
```

### DNS Resolution Issues

```bash
# Check CoreDNS is running
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Check CoreDNS logs
kubectl logs -n kube-system -l k8s-app=kube-dns

# Test DNS from pod
kubectl run dns-debug --rm -it --image=busybox -- sh
> cat /etc/resolv.conf
> nslookup kubernetes.default
> nslookup myapp-service.production.svc.cluster.local
```

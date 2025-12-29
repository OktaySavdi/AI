# Deploy Ollama on Kubernetes (Production-Ready)

## Prerequisites

- Kubernetes cluster (1.24+) with GPU nodes
- `kubectl` CLI configured
- Helm 3.x installed
- GPU quota available (NVIDIA H100, A100, or V100)
- Storage provisioner (Azure Disk, AWS EBS, or similar)
- Ingress controller (nginx, traefik, or similar)

## Architecture Overview

- **Deployment**: Ollama with GPU support
- **Storage**: PersistentVolumeClaim for model storage (500GB+)
- **Service**: ClusterIP for internal access, LoadBalancer/Ingress for external
- **Security**: Non-root containers, network policies, resource limits
- **Monitoring**: Prometheus metrics, health checks
- **High Availability**: Optional multiple replicas with shared storage

## 1. Prepare GPU-Enabled Kubernetes Cluster

### For Azure Kubernetes Service (AKS)

```bash
# Create resource group
az group create --name AZ-RG-PROD-01 --location eastus2

# Create AKS cluster with system node pool
az aks create \
  --resource-group AZ-RG-PROD-01 \
  --name azeus2-aks-llm-prod-01 \
  --node-count 2 \
  --node-vm-size Standard_D4s_v3 \
  --enable-managed-identity \
  --network-plugin azure \
  --generate-ssh-keys

# Add GPU node pool with H100 VMs
az aks nodepool add \
  --resource-group AZ-RG-PROD-01 \
  --cluster-name azeus2-aks-llm-prod-01 \
  --name gpunp \
  --node-count 1 \
  --node-vm-size Standard_NC80adis_H100_v5 \
  --node-taints nvidia.com/gpu=present:NoSchedule \
  --labels workload=gpu-inference \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 3

# Get credentials
az aks get-credentials \
  --resource-group AZ-RG-PROD-01 \
  --name azeus2-aks-llm-prod-01
```

### For Other Kubernetes Clusters

Ensure GPU nodes are labeled:
```bash
kubectl label nodes <gpu-node-name> nvidia.com/gpu=true
kubectl label nodes <gpu-node-name> workload=gpu-inference
```

## 2. Install NVIDIA GPU Operator

The GPU Operator manages NVIDIA drivers and container runtime on Kubernetes.

```bash
# Add NVIDIA Helm repository
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

# Create namespace
kubectl create namespace gpu-operator

# Install GPU Operator
helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator \
  --set driver.enabled=true \
  --set toolkit.enabled=true \
  --set operator.defaultRuntime=containerd \
  --wait

# Verify installation (wait 5-10 minutes)
kubectl get pods -n gpu-operator
kubectl get nodes -o json | jq '.items[].status.allocatable | select(."nvidia.com/gpu" != null)'
```

**Verify GPU is available:**
```bash
kubectl run gpu-test \
  --image=nvidia/cuda:12.0.0-base-ubuntu22.04 \
  --restart=Never \
  --limits=nvidia.com/gpu=1 \
  -- nvidia-smi

kubectl logs gpu-test
kubectl delete pod gpu-test
```

## 3. Create Namespace and Resources

```bash
kubectl create namespace ollama
```

### Create PersistentVolumeClaim (PVC)

**`ollama-pvc.yaml`**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ollama-models
  namespace: ollama
  labels:
    app: ollama
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: managed-premium  # Azure: managed-premium, AWS: gp3, GCP: pd-ssd
  resources:
    requests:
      storage: 500Gi  # Adjust based on model sizes (Qwen 2.5 32B ~20GB)
```

```bash
kubectl apply -f ollama-pvc.yaml
kubectl get pvc -n ollama
```

## 4. Deploy Ollama with Production Configuration

### Option A: Using Helm (Recommended)

**`ollama-values.yaml`**
```yaml
replicaCount: 1

image:
  repository: ollama/ollama
  tag: latest
  pullPolicy: IfNotPresent

gpu:
  enabled: true
  count: 1  # Number of GPUs per pod
  type: nvidia.com/gpu

resources:
  requests:
    cpu: "8000m"
    memory: "32Gi"
    nvidia.com/gpu: "1"
  limits:
    cpu: "16000m"
    memory: "64Gi"
    nvidia.com/gpu: "1"

persistence:
  enabled: true
  existingClaim: ollama-models
  mountPath: /root/.ollama

service:
  type: LoadBalancer  # Change to ClusterIP for internal-only access
  port: 11434
  annotations:
    service.beta.kubernetes.io/azure-load-balancer-internal: "false"  # Set to "true" for internal LB

ingress:
  enabled: false  # Enable if using Ingress instead of LoadBalancer
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-body-size: "0"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
  hosts:
    - host: ollama.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: ollama-tls
      hosts:
        - ollama.yourdomain.com

livenessProbe:
  httpGet:
    path: /
    port: 11434
  initialDelaySeconds: 30
  periodSeconds: 20
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /
    port: 11434
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

securityContext:
  runAsNonRoot: false  # Ollama requires root for GPU access
  runAsUser: 0
  fsGroup: 0
  capabilities:
    drop:
      - ALL
    add:
      - CHOWN
      - SETGID
      - SETUID

podSecurityContext:
  fsGroup: 0

nodeSelector:
  workload: gpu-inference
  nvidia.com/gpu: "true"

tolerations:
  - key: nvidia.com/gpu
    operator: Exists
    effect: NoSchedule

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
              - key: app
                operator: In
                values:
                  - ollama
          topologyKey: kubernetes.io/hostname

env:
  - name: OLLAMA_HOST
    value: "0.0.0.0:11434"
  - name: OLLAMA_ORIGINS
    value: "*"
  - name: OLLAMA_NUM_PARALLEL
    value: "4"
  - name: OLLAMA_MAX_LOADED_MODELS
    value: "2"

# Horizontal Pod Autoscaler (Optional - not recommended for GPU workloads)
autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 3
  targetCPUUtilizationPercentage: 80
```

**Install with Helm:**
```bash
# If official Helm chart exists (check https://github.com/ollama/ollama)
helm repo add ollama https://ollama.github.io/charts
helm repo update

helm install ollama ollama/ollama \
  --namespace ollama \
  --values ollama-values.yaml \
  --wait
```

### Option B: Using Kubernetes Manifests

**`ollama-deployment.yaml`**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ollama-config
  namespace: ollama
data:
  OLLAMA_HOST: "0.0.0.0:11434"
  OLLAMA_ORIGINS: "*"
  OLLAMA_NUM_PARALLEL: "4"
  OLLAMA_MAX_LOADED_MODELS: "2"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: ollama
  labels:
    app: ollama
    version: v1
spec:
  replicas: 1
  strategy:
    type: Recreate  # Use Recreate for single replica with RWO volume
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "11434"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: ollama
      securityContext:
        fsGroup: 0
      nodeSelector:
        workload: gpu-inference
        nvidia.com/gpu: "true"
      tolerations:
        - key: nvidia.com/gpu
          operator: Exists
          effect: NoSchedule
      containers:
        - name: ollama
          image: ollama/ollama:latest
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 11434
              protocol: TCP
          envFrom:
            - configMapRef:
                name: ollama-config
          resources:
            requests:
              cpu: "8000m"
              memory: "32Gi"
              nvidia.com/gpu: "1"
            limits:
              cpu: "16000m"
              memory: "64Gi"
              nvidia.com/gpu: "1"
          volumeMounts:
            - name: models
              mountPath: /root/.ollama
          livenessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 30
            periodSeconds: 20
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          securityContext:
            runAsNonRoot: false
            runAsUser: 0
            capabilities:
              drop:
                - ALL
              add:
                - CHOWN
                - SETGID
                - SETUID
      volumes:
        - name: models
          persistentVolumeClaim:
            claimName: ollama-models
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ollama
  namespace: ollama
  labels:
    app: ollama
---
apiVersion: v1
kind: Service
metadata:
  name: ollama
  namespace: ollama
  labels:
    app: ollama
  annotations:
    service.beta.kubernetes.io/azure-load-balancer-internal: "false"  # "true" for internal
spec:
  type: LoadBalancer  # Change to ClusterIP for internal-only
  ports:
    - port: 11434
      targetPort: http
      protocol: TCP
      name: http
  selector:
    app: ollama
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ollama
  namespace: ollama
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-body-size: "0"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - ollama.yourdomain.com
      secretName: ollama-tls
  rules:
    - host: ollama.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: ollama
                port:
                  number: 11434
```

**Apply manifests:**
```bash
kubectl apply -f ollama-deployment.yaml
```

## 5. Verify Deployment

```bash
# Check pod status
kubectl get pods -n ollama -o wide
kubectl describe pod -n ollama -l app=ollama

# Check GPU allocation
kubectl get pod -n ollama -o json | jq '.items[].spec.containers[].resources'

# Check logs
kubectl logs -n ollama -l app=ollama -f

# Get service endpoint
kubectl get svc -n ollama ollama

# For LoadBalancer, get external IP
EXTERNAL_IP=$(kubectl get svc -n ollama ollama -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Ollama endpoint: http://$EXTERNAL_IP:11434"

# Test connectivity
curl http://$EXTERNAL_IP:11434/api/tags
```

## 6. Pull Qwen 2.5 Model

### Method 1: Using kubectl exec

```bash
# Get pod name
POD_NAME=$(kubectl get pod -n ollama -l app=ollama -o jsonpath='{.items[0].metadata.name}')

# Pull model
kubectl exec -n ollama $POD_NAME -- ollama pull qwen2.5-coder:32b

# Monitor progress
kubectl logs -n ollama $POD_NAME -f
```

### Method 2: Using API (from local machine)

```bash
EXTERNAL_IP=$(kubectl get svc -n ollama ollama -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

curl http://$EXTERNAL_IP:11434/api/pull -d '{
  "name": "qwen2.5-coder:32b"
}'
```

### Method 3: Using Init Container (Pre-load at deployment)

Add to deployment spec:
```yaml
initContainers:
  - name: model-downloader
    image: ollama/ollama:latest
    command:
      - /bin/sh
      - -c
      - |
        ollama serve &
        sleep 10
        ollama pull qwen2.5-coder:32b
        ollama pull llama3.1:8b  # Add more models as needed
        pkill ollama
    volumeMounts:
      - name: models
        mountPath: /root/.ollama
    resources:
      requests:
        cpu: "2000m"
        memory: "8Gi"
      limits:
        cpu: "4000m"
        memory: "16Gi"
```

## 7. Configure RBAC (Least Privilege)

**`ollama-rbac.yaml`**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ollama-role
  namespace: ollama
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list"]
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ollama-rolebinding
  namespace: ollama
subjects:
  - kind: ServiceAccount
    name: ollama
    namespace: ollama
roleRef:
  kind: Role
  name: ollama-role
  apiGroup: rbac.authorization.k8s.io
```

```bash
kubectl apply -f ollama-rbac.yaml
```

## 8. Deploy Open WebUI (Optional)

**`openwebui-deployment.yaml`**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: open-webui
  namespace: ollama
  labels:
    app: open-webui
spec:
  replicas: 2
  selector:
    matchLabels:
      app: open-webui
  template:
    metadata:
      labels:
        app: open-webui
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: open-webui
          image: ghcr.io/open-webui/open-webui:main
          imagePullPolicy: Always
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
          env:
            - name: OLLAMA_BASE_URL
              value: "http://ollama.ollama.svc.cluster.local:11434"
            - name: WEBUI_AUTH
              value: "true"
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "2000m"
              memory: "2Gi"
          volumeMounts:
            - name: data
              mountPath: /app/backend/data
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 20
          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: false  # WebUI needs write access
            capabilities:
              drop:
                - ALL
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: openwebui-data
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: openwebui-data
  namespace: ollama
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: managed-premium
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: open-webui
  namespace: ollama
  labels:
    app: open-webui
spec:
  type: ClusterIP
  ports:
    - port: 8080
      targetPort: http
      protocol: TCP
      name: http
  selector:
    app: open-webui
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: open-webui
  namespace: ollama
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - webui.yourdomain.com
      secretName: openwebui-tls
  rules:
    - host: webui.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: open-webui
                port:
                  number: 8080
```

```bash
kubectl apply -f openwebui-deployment.yaml
```

## 9. Monitoring and Observability

### Configure Prometheus ServiceMonitor

**`ollama-servicemonitor.yaml`**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: ollama
  namespace: ollama
  labels:
    app: ollama
spec:
  selector:
    matchLabels:
      app: ollama
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

```bash
kubectl apply -f ollama-servicemonitor.yaml
```

### Create Grafana Dashboard

Import dashboard JSON for Ollama metrics (if available) or create custom panels:
- Request rate (requests/sec)
- Model inference time (p50, p95, p99)
- GPU utilization (%)
- Memory usage (GB)
- Active connections

### Set Up Alerts

**`ollama-prometheusrule.yaml`**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: ollama-alerts
  namespace: ollama
  labels:
    app: ollama
spec:
  groups:
    - name: ollama
      interval: 30s
      rules:
        - alert: OllamaPodDown
          expr: up{job="ollama"} == 0
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Ollama pod is down"
            description: "Ollama pod in namespace {{ $labels.namespace }} has been down for more than 5 minutes."
        
        - alert: OllamaHighMemoryUsage
          expr: container_memory_usage_bytes{pod=~"ollama-.*"} / container_spec_memory_limit_bytes{pod=~"ollama-.*"} > 0.9
          for: 10m
          labels:
            severity: warning
          annotations:
            summary: "Ollama high memory usage"
            description: "Ollama pod {{ $labels.pod }} is using more than 90% of its memory limit."
        
        - alert: OllamaHighCPUUsage
          expr: rate(container_cpu_usage_seconds_total{pod=~"ollama-.*"}[5m]) / container_spec_cpu_quota{pod=~"ollama-.*"} * 100000 > 90
          for: 10m
          labels:
            severity: warning
          annotations:
            summary: "Ollama high CPU usage"
            description: "Ollama pod {{ $labels.pod }} is using more than 90% of its CPU limit."
        
        - alert: OllamaPodRestartingTooOften
          expr: rate(kube_pod_container_status_restarts_total{pod=~"ollama-.*"}[15m]) > 0
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Ollama pod restarting too often"
            description: "Ollama pod {{ $labels.pod }} has restarted {{ $value }} times in the last 15 minutes."
```

```bash
kubectl apply -f ollama-prometheusrule.yaml
```

## 10. Backup and Disaster Recovery

### Backup Model Storage

**Using Velero (Recommended):**
```bash
# Install Velero
velero install \
  --provider azure \
  --plugins velero/velero-plugin-for-microsoft-azure:v1.9.0 \
  --bucket ollama-backups \
  --backup-location-config resourceGroup=AZ-RG-PROD-01,storageAccount=ollamabackups \
  --use-volume-snapshots=true \
  --snapshot-location-config resourceGroup=AZ-RG-PROD-01

# Create backup schedule
velero schedule create ollama-daily \
  --schedule="0 2 * * *" \
  --include-namespaces ollama \
  --include-resources persistentvolumeclaims,persistentvolumes
```

### Manual Backup

```bash
# Create snapshot of PVC (Azure example)
POD_NAME=$(kubectl get pod -n ollama -l app=ollama -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n ollama $POD_NAME -- tar -czf /tmp/ollama-models-backup.tar.gz -C /root/.ollama .
kubectl cp ollama/$POD_NAME:/tmp/ollama-models-backup.tar.gz ./ollama-models-backup.tar.gz
```

### Use Spot/Preemptible Instances

```bash
# For AKS, create spot node pool
az aks nodepool add \
  --resource-group AZ-RG-PROD-01 \
  --cluster-name azeus2-aks-llm-prod-01 \
  --name gpuspot \
  --node-count 1 \
  --node-vm-size Standard_NC80adis_H100_v5 \
  --priority Spot \
  --eviction-policy Delete \
  --spot-max-price -1 \
  --node-taints kubernetes.azure.com/scalesetpriority=spot:NoSchedule \
  --labels workload=gpu-inference priority=spot
```

Update deployment tolerations:
```yaml
tolerations:
  - key: kubernetes.azure.com/scalesetpriority
    operator: Equal
    value: spot
    effect: NoSchedule
```

## 14. Testing and Validation

### Basic Functionality Test

```bash
# Get service endpoint
EXTERNAL_IP=$(kubectl get svc -n ollama ollama -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test API
curl http://$EXTERNAL_IP:11434/api/tags

# Test inference
curl http://$EXTERNAL_IP:11434/api/generate -d '{
  "model": "qwen2.5-coder:32b",
  "prompt": "Explain Kubernetes in one sentence",
  "stream": false
}'
```

### Load Test

```bash
# Install hey (HTTP load testing tool)
# brew install hey  # macOS
# apt install hey   # Ubuntu

# Run load test (100 requests, 10 concurrent)
hey -n 100 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5-coder:32b","prompt":"Hello","stream":false}' \
  http://$EXTERNAL_IP:11434/api/generate
```

## 15. Troubleshooting

### Pod Not Starting (Pending State)

```bash
# Check events
kubectl describe pod -n ollama -l app=ollama

# Common issues:
# - Insufficient GPU resources: Check node GPU allocation
# - PVC not bound: Check storage provisioner
# - Node selector mismatch: Verify GPU node labels
```

### GPU Not Available in Pod

```bash
# Check GPU operator
kubectl get pods -n gpu-operator

# Check node GPU resources
kubectl get nodes -o json | jq '.items[].status.allocatable | select(."nvidia.com/gpu" != null)'

# Verify GPU inside pod
POD_NAME=$(kubectl get pod -n ollama -l app=ollama -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n ollama $POD_NAME -- nvidia-smi
```

### Model Download Failures

```bash
# Check logs
kubectl logs -n ollama -l app=ollama -f

# Check network connectivity
kubectl run -n ollama curl-test --image=curlimages/curl:latest --rm -it -- /bin/sh
# Inside pod: curl -I https://ollama.ai

# Check DNS resolution
kubectl run -n ollama dns-test --image=busybox:latest --rm -it -- nslookup ollama.ai
```

### High Memory Usage / OOMKilled

```bash
# Check resource limits
kubectl get pod -n ollama -o json | jq '.items[].spec.containers[].resources'

# Increase memory limits in deployment
# Ollama with Qwen 2.5 32B requires ~40-60GB RAM
```

### Service Not Accessible

```bash
# Check service
kubectl get svc -n ollama

# Check endpoints
kubectl get endpoints -n ollama

# For LoadBalancer, check external IP assignment
kubectl describe svc -n ollama ollama

# Test from within cluster
kubectl run -n ollama curl-test --image=curlimages/curl:latest --rm -it -- curl http://ollama.ollama.svc.cluster.local:11434/api/tags
```

## 16. Security Hardening Checklist

- [x] Use non-root containers where possible (Ollama requires root for GPU)
- [x] Define resource limits for all containers
- [x] Implement network policies (restrict ingress/egress)
- [x] Use RBAC with least privilege
- [x] Enable Pod Security Standards (baseline/restricted)
- [x] Scan container images for vulnerabilities
- [x] Use private container registry
- [x] Encrypt secrets at rest (enable encryption in etcd)
- [x] Use TLS for Ingress (cert-manager with Let's Encrypt)
- [x] Implement audit logging
- [x] Regularly update Kubernetes and node OS
- [x] Use dedicated node pools for GPU workloads
- [x] Enable Azure Defender / AWS GuardDuty / GCP Security Command Center

## 17. Cleanup

```bash
# Delete namespace (removes all resources)
kubectl delete namespace ollama

# Delete GPU operator
helm uninstall gpu-operator -n gpu-operator
kubectl delete namespace gpu-operator

# Delete AKS cluster (Azure)
az aks delete \
  --resource-group AZ-RG-PROD-01 \
  --name azeus2-aks-llm-prod-01 \
  --yes --no-wait

# Delete resource group
az group delete --name AZ-RG-PROD-01 --yes --no-wait
```

## Cost Estimate (Azure AKS with H100)

| Component | Specification | Monthly Cost (USD) |
|-----------|--------------|-------------------|
| System Node Pool | 2x Standard_D4s_v3 | ~$280 |
| GPU Node Pool | 1x Standard_NC80adis_H100_v5 | ~$13,104 |
| Storage (PVC) | 500GB Premium SSD | ~$90 |
| Load Balancer | Standard SKU | ~$25 |
| Egress Traffic | 1TB | ~$90 |
| **Total** | | **~$13,589/month** |

**Cost Optimization:**
- Use spot instances: Save up to 80% ($2,620/month instead of $13,104)
- Scale to zero during off-hours: Save ~50% ($6,550/month)
- Use smaller GPU: V100 or A10 (~$3,000-5,000/month)

## References

- [Ollama GitHub](https://github.com/ollama/ollama)
- [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/)
- [Kubernetes GPU Support](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)
- [AKS GPU Node Pools](https://learn.microsoft.com/en-us/azure/aks/gpu-cluster)
- [Qwen 2.5 Model](https://huggingface.co/Qwen/Qwen2.5-Coder)

---

**Last Updated:** December 29, 2025

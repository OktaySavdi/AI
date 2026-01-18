# Kubernetes Pods - Production Ready

A **Pod** is the smallest deployable unit in Kubernetes. It represents a single instance of a running process in your cluster.

> ⚠️ **Important**: In production, avoid deploying Pods directly. Use Deployments, StatefulSets, or DaemonSets instead for reliability and scaling.

---

## Pod Lifecycle

| Phase | Description |
|-------|-------------|
| **Pending** | Pod accepted but containers not yet created |
| **Running** | Pod bound to a node, all containers created |
| **Succeeded** | All containers terminated successfully |
| **Failed** | All containers terminated, at least one with failure |
| **Unknown** | Pod state cannot be determined |

---

## Production-Ready Pod (Complete Example)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
  namespace: production
  labels:
    app.kubernetes.io/name: myapp
    app.kubernetes.io/instance: myapp-prod
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: backend
    app.kubernetes.io/part-of: myapp-suite
    app.kubernetes.io/managed-by: kubectl
    environment: production
    team: platform
  annotations:
    kubernetes.io/description: "Production pod for myapp"
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
spec:
  # Service Account
  serviceAccountName: myapp-sa
  automountServiceAccountToken: false
  
  # Restart Policy
  restartPolicy: Always  # Always, OnFailure, Never
  
  # Termination
  terminationGracePeriodSeconds: 60
  
  # DNS Configuration
  dnsPolicy: ClusterFirst
  dnsConfig:
    options:
      - name: ndots
        value: "2"
      - name: single-request-reopen
  
  # Host Settings (usually keep false for security)
  hostNetwork: false
  hostPID: false
  hostIPC: false
  
  # Pod Security Context
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    fsGroupChangePolicy: OnRootMismatch
    seccompProfile:
      type: RuntimeDefault
    supplementalGroups:
      - 1000
  
  # Scheduling - Node Selection
  nodeSelector:
    kubernetes.io/os: linux
    node-type: application
  
  # Scheduling - Tolerations
  tolerations:
    - key: "dedicated"
      operator: "Equal"
      value: "application"
      effect: "NoSchedule"
    - key: "node.kubernetes.io/not-ready"
      operator: "Exists"
      effect: "NoExecute"
      tolerationSeconds: 300
    - key: "node.kubernetes.io/unreachable"
      operator: "Exists"
      effect: "NoExecute"
      tolerationSeconds: 300
  
  # Scheduling - Affinity
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: kubernetes.io/os
                operator: In
                values:
                  - linux
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          preference:
            matchExpressions:
              - key: node-type
                operator: In
                values:
                  - application
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          podAffinityTerm:
            labelSelector:
              matchLabels:
                app.kubernetes.io/name: myapp
            topologyKey: kubernetes.io/hostname
  
  # Priority
  priorityClassName: high-priority
  
  # Init Containers
  initContainers:
    - name: init-permissions
      image: busybox:1.36
      command:
        - sh
        - -c
        - |
          echo "Setting up permissions..."
          chmod -R 755 /data
          echo "Init complete"
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
      resources:
        requests:
          cpu: "10m"
          memory: "16Mi"
        limits:
          cpu: "50m"
          memory: "32Mi"
      volumeMounts:
        - name: data-volume
          mountPath: /data
    
    - name: init-wait-for-db
      image: busybox:1.36
      command:
        - sh
        - -c
        - |
          echo "Waiting for database..."
          until nc -z postgres-service 5432; do
            echo "Database not ready, sleeping..."
            sleep 2
          done
          echo "Database is ready!"
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
      resources:
        requests:
          cpu: "10m"
          memory: "16Mi"
        limits:
          cpu: "50m"
          memory: "32Mi"
  
  # Main Containers
  containers:
    - name: myapp
      image: myregistry.azurecr.io/myapp:1.0.0
      imagePullPolicy: IfNotPresent
      
      # Command Override (optional)
      # command: ["/app/start.sh"]
      # args: ["--config", "/app/config/app.yaml"]
      
      # Ports
      ports:
        - name: http
          containerPort: 8080
          protocol: TCP
        - name: metrics
          containerPort: 9090
          protocol: TCP
        - name: health
          containerPort: 8081
          protocol: TCP
      
      # Environment Variables
      env:
        # Downward API - Pod Info
        - name: POD_NAME
          valueFrom:
            fieldRef:
              apiVersion: v1
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              apiVersion: v1
              fieldPath: metadata.namespace
        - name: POD_IP
          valueFrom:
            fieldRef:
              apiVersion: v1
              fieldPath: status.podIP
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              apiVersion: v1
              fieldPath: spec.nodeName
        - name: POD_SERVICE_ACCOUNT
          valueFrom:
            fieldRef:
              apiVersion: v1
              fieldPath: spec.serviceAccountName
        
        # Downward API - Resource Limits
        - name: MEMORY_LIMIT
          valueFrom:
            resourceFieldRef:
              containerName: myapp
              resource: limits.memory
        - name: CPU_LIMIT
          valueFrom:
            resourceFieldRef:
              containerName: myapp
              resource: limits.cpu
        
        # Static Values
        - name: APP_ENV
          value: "production"
        - name: LOG_FORMAT
          value: "json"
        
        # From ConfigMap
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: myapp-config
              key: log_level
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: myapp-config
              key: db_host
        
        # From Secret
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: myapp-secrets
              key: db_password
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: myapp-secrets
              key: api_key
      
      # Environment from ConfigMap/Secret
      envFrom:
        - configMapRef:
            name: myapp-env-config
            optional: true
        - secretRef:
            name: myapp-env-secrets
            optional: true
        - prefix: FEATURE_
          configMapRef:
            name: myapp-feature-flags
            optional: true
      
      # Resources (REQUIRED)
      resources:
        requests:
          cpu: "250m"
          memory: "256Mi"
          ephemeral-storage: "100Mi"
        limits:
          cpu: "1000m"
          memory: "1Gi"
          ephemeral-storage: "500Mi"
      
      # Container Security Context
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        privileged: false
        capabilities:
          drop:
            - ALL
          # Only add if absolutely required:
          # add:
          #   - NET_BIND_SERVICE
      
      # Startup Probe (for slow-starting containers)
      startupProbe:
        httpGet:
          path: /healthz
          port: health
          scheme: HTTP
        initialDelaySeconds: 10
        periodSeconds: 10
        timeoutSeconds: 5
        successThreshold: 1
        failureThreshold: 30  # 30 * 10s = 300s max startup
      
      # Liveness Probe (is the container alive?)
      livenessProbe:
        httpGet:
          path: /healthz
          port: health
          scheme: HTTP
          httpHeaders:
            - name: X-Health-Check
              value: liveness
        initialDelaySeconds: 0
        periodSeconds: 15
        timeoutSeconds: 5
        successThreshold: 1
        failureThreshold: 3
      
      # Readiness Probe (is the container ready for traffic?)
      readinessProbe:
        httpGet:
          path: /ready
          port: health
          scheme: HTTP
          httpHeaders:
            - name: X-Health-Check
              value: readiness
        initialDelaySeconds: 5
        periodSeconds: 10
        timeoutSeconds: 5
        successThreshold: 1
        failureThreshold: 3
      
      # Volume Mounts
      volumeMounts:
        - name: config-volume
          mountPath: /app/config
          readOnly: true
        - name: secrets-volume
          mountPath: /app/secrets
          readOnly: true
        - name: tls-certs
          mountPath: /app/certs
          readOnly: true
        - name: tmp-volume
          mountPath: /tmp
        - name: cache-volume
          mountPath: /app/cache
        - name: data-volume
          mountPath: /app/data
      
      # Lifecycle Hooks
      lifecycle:
        postStart:
          exec:
            command:
              - /bin/sh
              - -c
              - |
                echo "Container started at $(date)" >> /tmp/lifecycle.log
                # Additional initialization
        preStop:
          exec:
            command:
              - /bin/sh
              - -c
              - |
                echo "Container stopping at $(date)" >> /tmp/lifecycle.log
                # Graceful shutdown - wait for in-flight requests
                sleep 15
                # Send SIGTERM to application
                kill -SIGTERM 1
      
      # Stdin/TTY (usually false)
      stdin: false
      tty: false
    
    # Sidecar Container (optional - for logging, proxy, etc.)
    - name: log-shipper
      image: fluent/fluent-bit:2.1
      imagePullPolicy: IfNotPresent
      resources:
        requests:
          cpu: "50m"
          memory: "64Mi"
        limits:
          cpu: "100m"
          memory: "128Mi"
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
      volumeMounts:
        - name: app-logs
          mountPath: /var/log/app
          readOnly: true
        - name: fluent-config
          mountPath: /fluent-bit/etc
          readOnly: true
  
  # Volumes
  volumes:
    # ConfigMap Volume
    - name: config-volume
      configMap:
        name: myapp-config
        defaultMode: 0440
        items:
          - key: app.yaml
            path: app.yaml
          - key: logging.yaml
            path: logging.yaml
    
    # Secret Volume
    - name: secrets-volume
      secret:
        secretName: myapp-secrets
        defaultMode: 0400
        items:
          - key: db_password
            path: db_password
          - key: api_key
            path: api_key
    
    # TLS Certificates
    - name: tls-certs
      secret:
        secretName: myapp-tls
        defaultMode: 0400
    
    # Temporary Storage (emptyDir)
    - name: tmp-volume
      emptyDir:
        sizeLimit: 100Mi
    
    # Cache Storage
    - name: cache-volume
      emptyDir:
        sizeLimit: 500Mi
        medium: ""  # Or "Memory" for tmpfs
    
    # Data Storage (emptyDir or PVC)
    - name: data-volume
      emptyDir:
        sizeLimit: 1Gi
    
    # For sidecar
    - name: app-logs
      emptyDir:
        sizeLimit: 200Mi
    
    - name: fluent-config
      configMap:
        name: fluent-bit-config
        defaultMode: 0440
    
    # Persistent Volume Claim (if needed)
    # - name: persistent-data
    #   persistentVolumeClaim:
    #     claimName: myapp-pvc
    
    # Projected Volume (multiple sources)
    # - name: all-secrets
    #   projected:
    #     defaultMode: 0400
    #     sources:
    #       - secret:
    #           name: myapp-secrets
    #       - secret:
    #           name: myapp-tls
    #       - configMap:
    #           name: myapp-config
  
  # Image Pull Secrets
  imagePullSecrets:
    - name: acr-pull-secret
```

---

## Probe Types

### HTTP Probe

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
    scheme: HTTP
    httpHeaders:
      - name: X-Custom-Header
        value: probe
  initialDelaySeconds: 10
  periodSeconds: 15
  timeoutSeconds: 5
  successThreshold: 1
  failureThreshold: 3
```

### TCP Probe

```yaml
livenessProbe:
  tcpSocket:
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 15
  timeoutSeconds: 5
  failureThreshold: 3
```

### Exec Probe

```yaml
livenessProbe:
  exec:
    command:
      - /bin/sh
      - -c
      - /app/health-check.sh
  initialDelaySeconds: 10
  periodSeconds: 15
  timeoutSeconds: 5
  failureThreshold: 3
```

### gRPC Probe (K8s 1.24+)

```yaml
livenessProbe:
  grpc:
    port: 50051
    service: myapp.health.v1.Health
  initialDelaySeconds: 10
  periodSeconds: 15
  failureThreshold: 3
```

---

## Resource Quality of Service (QoS)

| QoS Class | Condition | Eviction Priority |
|-----------|-----------|-------------------|
| **Guaranteed** | requests = limits (both CPU & memory) | Last to evict |
| **Burstable** | requests < limits | Middle |
| **BestEffort** | No requests or limits | First to evict |

### Guaranteed QoS Example

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "512Mi"
  limits:
    cpu: "500m"      # Same as request
    memory: "512Mi"  # Same as request
```

---

## Security Context Options

### Pod Level

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  fsGroupChangePolicy: OnRootMismatch
  seccompProfile:
    type: RuntimeDefault
  sysctls:
    - name: net.core.somaxconn
      value: "1024"
```

### Container Level

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  privileged: false
  capabilities:
    drop:
      - ALL
    add: []  # Only if required: NET_BIND_SERVICE, SYS_TIME
  seLinuxOptions:
    level: "s0:c123,c456"
```

---

## Production Checklist

### Security
- [ ] `runAsNonRoot: true`
- [ ] `runAsUser: <non-root-uid>` (e.g., 1000)
- [ ] `readOnlyRootFilesystem: true`
- [ ] `allowPrivilegeEscalation: false`
- [ ] `privileged: false`
- [ ] `capabilities.drop: [ALL]`
- [ ] `seccompProfile: RuntimeDefault`
- [ ] `automountServiceAccountToken: false`
- [ ] `hostNetwork: false`, `hostPID: false`, `hostIPC: false`

### Resources
- [ ] CPU requests defined
- [ ] CPU limits defined
- [ ] Memory requests defined
- [ ] Memory limits defined
- [ ] Ephemeral storage limits defined

### Health Checks
- [ ] Startup probe (for slow apps)
- [ ] Liveness probe configured
- [ ] Readiness probe configured
- [ ] Appropriate timeouts and thresholds

### Configuration
- [ ] ConfigMaps for non-sensitive data
- [ ] Secrets for sensitive data
- [ ] Environment variables properly sourced
- [ ] Volume mounts are read-only where possible

### Reliability
- [ ] `terminationGracePeriodSeconds` set appropriately
- [ ] PreStop lifecycle hook for graceful shutdown
- [ ] Init containers for dependencies
- [ ] Appropriate restart policy

---

## Common Commands

```bash
# Create pod
kubectl apply -f pod.yaml

# List all pods
kubectl get pods -A
kubectl get pods -n production -o wide

# Get pod with labels
kubectl get pods -l app.kubernetes.io/name=myapp

# Watch pods
kubectl get pods -w

# Describe pod (detailed info + events)
kubectl describe pod myapp-pod -n production

# View pod logs
kubectl logs myapp-pod -n production
kubectl logs myapp-pod -c myapp -n production  # specific container
kubectl logs myapp-pod --all-containers -n production
kubectl logs myapp-pod -f --tail=100 -n production  # follow + last 100

# Previous container logs (after restart)
kubectl logs myapp-pod --previous -n production

# Execute command in pod
kubectl exec -it myapp-pod -n production -- /bin/sh
kubectl exec myapp-pod -c myapp -n production -- cat /app/config/app.yaml

# Copy files to/from pod
kubectl cp myapp-pod:/app/logs/app.log ./app.log -n production
kubectl cp ./config.yaml myapp-pod:/tmp/config.yaml -n production

# Port forward
kubectl port-forward pod/myapp-pod 8080:8080 -n production

# Get pod YAML
kubectl get pod myapp-pod -n production -o yaml

# Delete pod
kubectl delete pod myapp-pod -n production
kubectl delete pod myapp-pod --grace-period=0 --force -n production  # force delete

# Get resource usage
kubectl top pod myapp-pod -n production

# Debug with ephemeral container (K8s 1.25+)
kubectl debug -it myapp-pod -n production --image=busybox --target=myapp
```

---

## Debugging Pods

### Pod Not Starting

```bash
# Check events
kubectl describe pod myapp-pod -n production | grep -A 20 "Events:"

# Check node resources
kubectl describe node <node-name> | grep -A 10 "Allocated resources"

# Check image pull
kubectl get events -n production --field-selector reason=Failed

# Check init containers
kubectl logs myapp-pod -c init-wait-for-db -n production
```

### Pod CrashLoopBackOff

```bash
# Check logs
kubectl logs myapp-pod -n production --previous

# Check exit code
kubectl describe pod myapp-pod -n production | grep -A 5 "Last State"

# Check resource limits (OOMKilled)
kubectl describe pod myapp-pod -n production | grep -i oom
```

### Pod Not Ready

```bash
# Check readiness probe
kubectl describe pod myapp-pod -n production | grep -A 10 "Readiness"

# Check endpoints
kubectl get endpoints myapp-service -n production

# Test probe manually
kubectl exec myapp-pod -n production -- curl -s localhost:8081/ready
```

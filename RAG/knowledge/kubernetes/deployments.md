0# Kubernetes Deployments - Production Ready

A **Deployment** manages a set of identical Pods and ensures they are running. It handles rolling updates and rollbacks.

## Production-Ready Deployment (Complete Example)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
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
    kubernetes.io/change-cause: "Initial deployment v1.0.0"
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
spec:
  replicas: 3
  revisionHistoryLimit: 10
  progressDeadlineSeconds: 600
  selector:
    matchLabels:
      app.kubernetes.io/name: myapp
      app.kubernetes.io/instance: myapp-prod
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app.kubernetes.io/name: myapp
        app.kubernetes.io/instance: myapp-prod
        app.kubernetes.io/version: "1.0.0"
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
    spec:
      # Service Account
      serviceAccountName: myapp-sa
      automountServiceAccountToken: false
      
      # Security Context (Pod Level)
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault
      
      # Scheduling
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchLabels:
                  app.kubernetes.io/name: myapp
              topologyKey: kubernetes.io/hostname
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app.kubernetes.io/name: myapp
                topologyKey: topology.kubernetes.io/zone
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 1
              preference:
                matchExpressions:
                  - key: node-type
                    operator: In
                    values:
                      - application
      
      # Spread across zones
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: myapp
        - maxSkew: 1
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: myapp
      
      # Priority
      priorityClassName: high-priority
      
      # Termination
      terminationGracePeriodSeconds: 60
      
      # DNS Config
      dnsPolicy: ClusterFirst
      dnsConfig:
        options:
          - name: ndots
            value: "2"
      
      # Init Containers (optional)
      initContainers:
        - name: init-check-db
          image: busybox:1.36
          command: ['sh', '-c', 'until nc -z postgres-service 5432; do echo waiting for db; sleep 2; done']
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
              cpu: 10m
              memory: 16Mi
            limits:
              cpu: 50m
              memory: 32Mi
      
      containers:
        - name: myapp
          image: myregistry.azurecr.io/myapp:1.0.0
          imagePullPolicy: IfNotPresent
          
          # Ports
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
            - name: metrics
              containerPort: 9090
              protocol: TCP
          
          # Environment Variables
          env:
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            - name: POD_IP
              valueFrom:
                fieldRef:
                  fieldPath: status.podIP
            - name: NODE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
            - name: APP_ENV
              value: "production"
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
          
          # Resources (REQUIRED for production)
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
              ephemeral-storage: "100Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
              ephemeral-storage: "500Mi"
          
          # Security Context (Container Level)
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            runAsGroup: 1000
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          
          # Startup Probe (for slow-starting apps)
          startupProbe:
            httpGet:
              path: /healthz
              port: http
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 5
            successThreshold: 1
            failureThreshold: 30  # 30 * 10 = 300s max startup time
          
          # Liveness Probe
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
              scheme: HTTP
              httpHeaders:
                - name: X-Health-Check
                  value: liveness
            initialDelaySeconds: 0
            periodSeconds: 15
            timeoutSeconds: 5
            successThreshold: 1
            failureThreshold: 3
          
          # Readiness Probe
          readinessProbe:
            httpGet:
              path: /ready
              port: http
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
            - name: tmp-volume
              mountPath: /tmp
            - name: cache-volume
              mountPath: /app/cache
            - name: tls-certs
              mountPath: /app/certs
              readOnly: true
          
          # Lifecycle Hooks
          lifecycle:
            postStart:
              exec:
                command:
                  - /bin/sh
                  - -c
                  - echo "Pod started at $(date)" >> /tmp/lifecycle.log
            preStop:
              exec:
                command:
                  - /bin/sh
                  - -c
                  - sleep 15 && kill -SIGTERM 1
      
      # Volumes
      volumes:
        - name: config-volume
          configMap:
            name: myapp-config
            defaultMode: 0440
        - name: secrets-volume
          secret:
            secretName: myapp-secrets
            defaultMode: 0400
        - name: tmp-volume
          emptyDir:
            sizeLimit: 100Mi
        - name: cache-volume
          emptyDir:
            sizeLimit: 500Mi
        - name: tls-certs
          secret:
            secretName: myapp-tls
            defaultMode: 0400
      
      # Image Pull Secrets
      imagePullSecrets:
        - name: acr-pull-secret
```

---

## Supporting Resources

### 1. Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    name: production
    environment: production
    istio-injection: enabled
  annotations:
    scheduler.alpha.kubernetes.io/defaultTolerations: '[{"key":"dedicated","operator":"Equal","value":"app","effect":"NoSchedule"}]'
```

### 2. Service Account

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
  namespace: production
  labels:
    app.kubernetes.io/name: myapp
  annotations:
    azure.workload.identity/client-id: "<CLIENT_ID>"  # For Azure Workload Identity
automountServiceAccountToken: false
```

### 3. ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
  namespace: production
  labels:
    app.kubernetes.io/name: myapp
data:
  log_level: "info"
  db_host: "postgres-service.production.svc.cluster.local"
  db_port: "5432"
  db_name: "myapp"
  cache_ttl: "3600"
  app.properties: |
    server.port=8080
    server.shutdown=graceful
    management.endpoints.web.exposure.include=health,info,metrics
    management.endpoint.health.probes.enabled=true
```

### 4. Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
  namespace: production
  labels:
    app.kubernetes.io/name: myapp
type: Opaque
stringData:
  db_password: "your-secure-password"
  api_key: "your-api-key"
  jwt_secret: "your-jwt-secret"
```

### 5. Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
  namespace: production
  labels:
    app.kubernetes.io/name: myapp
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: myapp
    app.kubernetes.io/instance: myapp-prod
  ports:
    - name: http
      port: 80
      targetPort: http
      protocol: TCP
    - name: metrics
      port: 9090
      targetPort: metrics
      protocol: TCP
  sessionAffinity: None
```

### 6. Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
  namespace: production
  labels:
    app.kubernetes.io/name: myapp
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 3
  maxReplicas: 20
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
        - type: Pods
          value: 2
          periodSeconds: 60
      selectPolicy: Min
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"
```

### 7. Pod Disruption Budget (PDB)

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
  namespace: production
  labels:
    app.kubernetes.io/name: myapp
spec:
  minAvailable: 2  # OR use maxUnavailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: myapp
      app.kubernetes.io/instance: myapp-prod
```

### 8. Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: myapp-network-policy
  namespace: production
  labels:
    app.kubernetes.io/name: myapp
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: myapp
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # Allow traffic from ingress controller
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
          podSelector:
            matchLabels:
              app.kubernetes.io/name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8080
    # Allow traffic from same namespace
    - from:
        - podSelector: {}
      ports:
        - protocol: TCP
          port: 8080
    # Allow Prometheus scraping
    - from:
        - namespaceSelector:
            matchLabels:
              name: monitoring
          podSelector:
            matchLabels:
              app: prometheus
      ports:
        - protocol: TCP
          port: 9090
  egress:
    # Allow DNS
    - to:
        - namespaceSelector: {}
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
    # Allow database access
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    # Allow external HTTPS (APIs)
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
            except:
              - 10.0.0.0/8
              - 172.16.0.0/12
              - 192.168.0.0/16
      ports:
        - protocol: TCP
          port: 443
```

### 9. Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  namespace: production
  labels:
    app.kubernetes.io/name: myapp
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "30"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    nginx.ingress.kubernetes.io/limit-rps: "100"
    nginx.ingress.kubernetes.io/limit-connections: "50"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - myapp.example.com
      secretName: myapp-tls
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: myapp-service
                port:
                  number: 80
```

### 10. Priority Class

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000
globalDefault: false
description: "High priority for production workloads"
preemptionPolicy: PreemptLowerPriority
```

### 11. Resource Quota (Namespace Level)

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "50"
    requests.memory: "100Gi"
    limits.cpu: "100"
    limits.memory: "200Gi"
    persistentvolumeclaims: "20"
    pods: "100"
    services: "20"
    secrets: "50"
    configmaps: "50"
```

### 12. Limit Range (Default Resources)

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: production-limits
  namespace: production
spec:
  limits:
    - type: Container
      default:
        cpu: "500m"
        memory: "512Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      min:
        cpu: "50m"
        memory: "64Mi"
      max:
        cpu: "4"
        memory: "8Gi"
    - type: PersistentVolumeClaim
      min:
        storage: "1Gi"
      max:
        storage: "100Gi"
```

---

## Production Checklist

### Security
- [ ] `runAsNonRoot: true`
- [ ] `readOnlyRootFilesystem: true`
- [ ] `allowPrivilegeEscalation: false`
- [ ] `capabilities.drop: [ALL]`
- [ ] `seccompProfile: RuntimeDefault`
- [ ] ServiceAccount with minimal RBAC
- [ ] Network Policies defined
- [ ] Secrets managed externally (Azure Key Vault, HashiCorp Vault)
- [ ] Image from trusted registry with vulnerability scanning
- [ ] No `:latest` tag - use specific versions

### Reliability
- [ ] `replicas >= 3` for HA
- [ ] Pod Anti-Affinity (spread across nodes)
- [ ] Topology Spread Constraints (spread across zones)
- [ ] Pod Disruption Budget defined
- [ ] Liveness, Readiness, Startup probes configured
- [ ] `terminationGracePeriodSeconds` set appropriately
- [ ] PreStop hook for graceful shutdown

### Resources
- [ ] CPU/Memory requests defined
- [ ] CPU/Memory limits defined
- [ ] Ephemeral storage limits defined
- [ ] HPA configured for auto-scaling
- [ ] Resource Quotas at namespace level

### Observability
- [ ] Prometheus annotations for scraping
- [ ] Structured logging (JSON)
- [ ] Log level configurable via ConfigMap
- [ ] Metrics endpoint exposed
- [ ] Tracing headers propagated

### Configuration
- [ ] ConfigMaps for non-sensitive config
- [ ] Secrets for sensitive data
- [ ] Environment-specific configurations
- [ ] Image pull secrets configured

---

## Rolling Updates

```bash
# Update image
kubectl set image deployment/myapp myapp=myregistry.azurecr.io/myapp:1.1.0 -n production

# Check rollout status
kubectl rollout status deployment/myapp -n production

# View rollout history
kubectl rollout history deployment/myapp -n production

# Rollback to previous version
kubectl rollout undo deployment/myapp -n production

# Rollback to specific revision
kubectl rollout undo deployment/myapp --to-revision=2 -n production

# Pause rollout
kubectl rollout pause deployment/myapp -n production

# Resume rollout
kubectl rollout resume deployment/myapp -n production
```

---

## Common Commands

```bash
# List deployments
kubectl get deployments -n production

# Describe deployment
kubectl describe deployment myapp -n production

# Get pods with labels
kubectl get pods -l app.kubernetes.io/name=myapp -n production -o wide

# Watch pods during rollout
kubectl get pods -n production -w

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'

# Scale deployment
kubectl scale deployment myapp --replicas=5 -n production

# Delete deployment
kubectl delete deployment myapp -n production

# Restart deployment (rolling restart)
kubectl rollout restart deployment/myapp -n production
```

---

## Scaling

### Manual Scaling

```bash
kubectl scale deployment myapp --replicas=5 -n production
```

### Vertical Pod Autoscaler (VPA)

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: myapp-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  updatePolicy:
    updateMode: "Auto"  # Or "Off" for recommendations only
  resourcePolicy:
    containerPolicies:
      - containerName: myapp
        minAllowed:
          cpu: "100m"
          memory: "128Mi"
        maxAllowed:
          cpu: "4"
          memory: "8Gi"
        controlledResources: ["cpu", "memory"]
```

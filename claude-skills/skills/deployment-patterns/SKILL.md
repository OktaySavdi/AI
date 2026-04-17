---
name: "deployment-patterns"
description: >
  CI/CD, Docker, and Kubernetes deployment patterns covering health checks, rollbacks,
  blue/green, canary, and zero-downtime deployments. Activate when designing deployment
  pipelines or reviewing deployment configurations.
license: MIT
metadata:
  version: 1.0.0
  author: ECC
  category: devops
---

# Deployment Patterns Skill

## Zero-Downtime Deployment Checklist

- [ ] `readinessProbe` configured — traffic only after app is ready
- [ ] `preStop` hook with sleep to drain in-flight requests
- [ ] `minReadySeconds` set (default 0 is too fast)
- [ ] `maxUnavailable: 0` in rolling update strategy
- [ ] Backward-compatible DB migrations (expand/contract pattern)

## Rolling Update (Kubernetes)

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  minReadySeconds: 10
  template:
    spec:
      containers:
        - name: app
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 10"]
          readinessProbe:
            httpGet:
              path: /healthz/ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
```

## Blue/Green Deployment

```yaml
# Two deployments, one service
# Switch service selector to change traffic
apiVersion: v1
kind: Service
spec:
  selector:
    app: myapp
    slot: green  # ← switch to 'blue' to roll back
```

## Canary Deployment

```yaml
# 10% to canary, 90% to stable
# Use Ingress weight annotation or service mesh
nginx.ingress.kubernetes.io/canary: "true"
nginx.ingress.kubernetes.io/canary-weight: "10"
```

## Health Checks

```yaml
livenessProbe:
  httpGet:
    path: /healthz/live
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 20
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /healthz/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
```

## Rollback

```bash
# Kubernetes
kubectl rollout undo deployment/myapp -n production

# Check rollout history
kubectl rollout history deployment/myapp -n production

# Rollback to specific revision
kubectl rollout undo deployment/myapp --to-revision=3 -n production
```

## Expand/Contract DB Migration Pattern

Never change schema in a way that breaks the old code before the new code is deployed.

1. **Expand**: Add new column (nullable), deploy new code that writes to both
2. **Migrate**: Backfill data in the new column
3. **Contract**: Remove old column in next release

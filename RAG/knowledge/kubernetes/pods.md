# Kubernetes Pods

A **Pod** is the smallest deployable unit in Kubernetes. It represents a single instance of a running process in your cluster.

## Key Concepts

### Pod Lifecycle
- **Pending**: Pod accepted but containers not yet created
- **Running**: Pod bound to a node, all containers created
- **Succeeded**: All containers terminated successfully
- **Failed**: All containers terminated, at least one with failure
- **Unknown**: Pod state cannot be determined

### Creating a Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "500m"
```

### Apply the Pod:

```bash
kubectl apply -f pod.yaml
kubectl get pods
kubectl describe pod nginx-pod
kubectl logs nginx-pod
kubectl delete pod nginx-pod
```

## Pod Best Practices

1. **Always set resource requests and limits**
2. **Use liveness and readiness probes**
3. **Don't run as root** - use `securityContext`
4. **Use labels** for organization and selection
5. **Avoid running single pods** - use Deployments instead

## Common Commands

```bash
# List all pods
kubectl get pods -A

# Get pod details
kubectl describe pod <pod-name>

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/bash

# View pod logs
kubectl logs <pod-name> -f

# Delete pod
kubectl delete pod <pod-name>
```

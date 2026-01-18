# Kubernetes Services

A **Service** exposes an application running on a set of Pods as a network service.

## Service Types

### 1. ClusterIP (Default)
Internal cluster access only.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

### 2. NodePort
Exposes on each node's IP at a static port.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-nodeport
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080  # 30000-32767
```

### 3. LoadBalancer
Cloud provider load balancer.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-lb
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

### 4. ExternalName
Maps to external DNS name.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-db
spec:
  type: ExternalName
  externalName: db.example.com
```

## Headless Service

For StatefulSets and direct pod DNS:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-headless
spec:
  clusterIP: None  # Makes it headless
  selector:
    app: nginx
  ports:
  - port: 80
```

## Service Discovery

### DNS-based:
```bash
# Within cluster
curl nginx-service.default.svc.cluster.local

# Short form (same namespace)
curl nginx-service
```

### Environment Variables:
```bash
# Automatic env vars
echo $NGINX_SERVICE_SERVICE_HOST
echo $NGINX_SERVICE_SERVICE_PORT
```

## Common Commands

```bash
# List services
kubectl get services

# Describe service
kubectl describe service nginx-service

# Get endpoints
kubectl get endpoints nginx-service

# Test service (from another pod)
kubectl run test --rm -it --image=busybox -- wget -qO- nginx-service

# Delete service
kubectl delete service nginx-service
```

## Debugging Services

```bash
# Check endpoints are populated
kubectl get endpoints nginx-service

# Check pods have correct labels
kubectl get pods --show-labels

# Test DNS resolution
kubectl run dns-test --rm -it --image=busybox -- nslookup nginx-service

# Check service selector matches pod labels
kubectl get pods -l app=nginx
```

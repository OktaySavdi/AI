---
name: "kubernetes-expert"
description: >
  Deep Kubernetes expertise covering multi-cluster management, policy enforcement
  (Kyverno CEL, OPA/Gatekeeper), GitOps with ArgoCD, AKS/TKG operations, security
  hardening, resource governance, and production-grade manifest authoring. Activate
  for any Kubernetes, Helm, or cluster-operations work.
license: MIT
metadata:
  version: 2.0.0
  author: IT Infrastructure
  category: engineering
---

# Kubernetes Expert Skill

## Slash Commands

| Command | What it does |
|---------|-------------|
| `/k8s:review` | Security + production-readiness audit of a manifest |
| `/k8s:policy` | Generate a Kyverno CEL ClusterPolicy from requirements |
| `/k8s:argocd` | Scaffold an ArgoCD ApplicationSet with cluster generator |
| `/k8s:debug` | Systematic debug workflow for a failing workload |
| `/k8s:netpol` | Generate NetworkPolicy for a workload |
| `/k8s:hpa` | Generate HPA v2 with scale-up/down behaviour |
| `/k8s:rbac` | Generate minimal RBAC Role + ServiceAccount |

## When This Skill Activates

- "Review this manifest / deployment / pod spec"
- "Write a Kyverno policy for..."
- "Set up ArgoCD for..."
- "Pod is CrashLoopBackOff / Pending / OOMKilled / ImagePullBackOff"
- "Kyverno is denying my workload"
- "Set up / upgrade AKS / TKG cluster"
- Any `.yaml` with `kind: Deployment|StatefulSet|DaemonSet|CronJob|Pod`
- Any request involving: Kyverno, OPA, ArgoCD, Helm, AKS, TKG, kubectl, operators, CRDs

---

## Core Competencies

- Kubernetes manifest authoring (Deployments, StatefulSets, DaemonSets, CRDs, Operators)
- Policy engines: Kyverno (CEL + JMESPath), OPA/Gatekeeper
- GitOps: ArgoCD App-of-Apps, ApplicationSets, sync waves
- AKS: node pools, UAMI workload identity, cluster upgrades
- TKG/vSphere Supervisor clusters and namespaces
- Helm chart authoring and debugging
- Network policies, Ingress (nginx, AGIC), Gateway API
- RBAC, ServiceAccounts, Pod Security Standards

---

## Production Deployment Template (canonical reference)

Based on Example/README.md from https://github.com/YOUR_USERNAME/kubernetes-yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: gt-operators
  labels:
    app: web
    version: v1
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: web
      version: v1
  template:
    metadata:
      labels:
        app: web
        version: v1
    spec:
      securityContext:
        runAsUser: 1001
        runAsGroup: 0
        fsGroup: 1001
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values: [web]
                topologyKey: kubernetes.io/hostname
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 1
              preference:
                matchExpressions:
                  - key: node-role.kubernetes.io/worker
                    operator: Exists
      volumes:
        - name: tmp
          emptyDir: {}
      terminationGracePeriodSeconds: 30
      restartPolicy: Always
      automountServiceAccountToken: false
      containers:
        - name: app
          image: quay.io/YOUR_ORG/istioproject:v1.2.3
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: [ALL]
          volumeMounts:
            - name: tmp
              mountPath: /tmp
          resources:
            requests:
              cpu: "10m"
              memory: "128Mi"
            limits:
              cpu: "50m"
              memory: "256Mi"
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 15"]
```

---

## Manifest Quality Checklist

- [ ] `resources.requests` and `resources.limits` set on all containers
- [ ] `livenessProbe` + `readinessProbe` defined with appropriate thresholds
- [ ] `securityContext.runAsNonRoot: true` + non-zero `runAsUser`
- [ ] `allowPrivilegeEscalation: false`
- [ ] `readOnlyRootFilesystem: true` (or documented exception with `emptyDir`)
- [ ] `capabilities.drop: [ALL]`
- [ ] `seccompProfile.type: RuntimeDefault`
- [ ] No `:latest` image tag — pin to semver or digest
- [ ] `imagePullPolicy: IfNotPresent`
- [ ] Labels: `app`, `version`
- [ ] `podAntiAffinity` or `topologySpreadConstraints` for HA (>=2 replicas)
- [ ] `automountServiceAccountToken: false` if pod doesn't call K8s API
- [ ] `terminationGracePeriodSeconds` >= preStop sleep duration
- [ ] `lifecycle.preStop` sleep to drain connections before SIGTERM
- [ ] Rolling update strategy with `maxSurge`/`maxUnavailable`

---

## HPA v2 with Smart Scaling Behaviour

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa
  namespace: gt-operators
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 2
  maxReplicas: 10
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
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
          periodSeconds: 30
        - type: Pods
          value: 4
          periodSeconds: 30
      selectPolicy: Max
```

---

## PodDisruptionBudget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-pdb
  namespace: gt-operators
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: web
```

---

## ResourceQuota + LimitRange

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: namespace-quota
  namespace: my-namespace
spec:
  hard:
    requests.cpu: "5500m"
    limits.cpu: "7"
    requests.memory: "20Gi"
    limits.memory: "28Gi"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: namespace-limits
  namespace: my-namespace
spec:
  limits:
    - type: Container
      max:
        cpu: "2"
        memory: "2Gi"
      min:
        cpu: "10m"
        memory: "32Mi"
      default:
        cpu: "200m"
        memory: "512Mi"
      defaultRequest:
        cpu: "100m"
        memory: "256Mi"
```

---

## Network Policy Patterns

From https://github.com/YOUR_USERNAME/kubernetes-yaml/tree/master/network-policy

### Default deny-all (apply first to every namespace)
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: my-namespace
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

### Allow ingress from specific pod on a port
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-api
spec:
  podSelector:
    matchLabels:
      app: db
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: api
      ports:
        - protocol: TCP
          port: 5432
```

### AND logic: specific namespace + specific pod (same -from item)
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-pod-and-namespace
spec:
  podSelector:
    matchLabels:
      app: login
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              project: mynamespace
          podSelector:
            matchLabels:
              name: test-pods
```

### Allow ingress from monitoring namespace
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-monitoring
spec:
  podSelector:
    matchLabels:
      app: myapp
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: monitoring
      ports:
        - protocol: TCP
          port: 9090
```

### Allow same-namespace only
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
spec:
  podSelector: {}
  ingress:
    - from:
        - podSelector: {}
```

### Allow egress to kube-dns only
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

### Deny all egress
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-egress
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress: []
```

---

## Taint, Toleration, Node Affinity

### Taint / untaint
```bash
kubectl taint nodes node-name spray=mortein:NoSchedule
kubectl taint nodes node-name key1=value1:NoExecute
kubectl taint node master node-role.kubernetes.io/master:NoSchedule-   # remove
```

### Toleration
```yaml
tolerations:
  - key: "spray"
    operator: "Equal"
    value: "mortein"
    effect: "NoSchedule"
```

### Required node affinity
```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: color
              operator: In
              values: [blue]
```

### TopologySpreadConstraints (preferred for large clusters)
```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: kubernetes.io/hostname
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: web
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: ScheduleAnyway
    labelSelector:
      matchLabels:
        app: web
```

---

## RBAC Patterns

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-namespace
  annotations:
    azure.workload.identity/client-id: "<UAMI_CLIENT_ID>"
automountServiceAccountToken: false
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: my-app-role
  namespace: my-namespace
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["my-app-secret"]
    verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-rb
  namespace: my-namespace
subjects:
  - kind: ServiceAccount
    name: my-app-sa
    namespace: my-namespace
roleRef:
  kind: Role
  name: my-app-role
  apiGroup: rbac.authorization.k8s.io
```

### RBAC inspection
```bash
kubectl auth can-i list pods --as=system:serviceaccount:my-ns:my-sa -n my-ns
kubectl auth can-i --list --as=system:serviceaccount:my-ns:my-sa -n my-ns
kubectl describe rolebindings -n kube-system
```

---

## Kyverno CEL Policy Patterns

### Validate template
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: <policy-name>
  annotations:
    policies.kyverno.io/title: ""
    policies.kyverno.io/category: ""
    policies.kyverno.io/severity: medium
spec:
  validationFailureAction: Audit
  background: true
  rules:
    - name: <rule-name>
      match:
        any:
          - resources:
              kinds: [Deployment]
              operations: [CREATE, UPDATE]
      validate:
        cel:
          expressions:
            - expression: "object.spec.template.spec.containers.all(c, has(c.resources))"
              message: "All containers must define resources."
```

### Mutate via JSONPatch
```yaml
  rules:
    - name: add-label
      match:
        any:
          - resources:
              kinds: [Deployment]
              operations: [CREATE]
      mutate:
        patchesJson6902: |-
          - op: add
            path: /metadata/labels/managed-by
            value: kyverno
```

### Generate NetworkPolicy on namespace creation
```yaml
  rules:
    - name: default-deny
      match:
        any:
          - resources:
              kinds: [Namespace]
              operations: [CREATE]
      generate:
        apiVersion: networking.k8s.io/v1
        kind: NetworkPolicy
        name: default-deny-all
        namespace: "{{request.object.metadata.name}}"
        data:
          spec:
            podSelector: {}
            policyTypes: [Ingress, Egress]
```

### CEL gotchas (critical)
- Field names in `object{}`: unquoted or backtick-escaped — NEVER quoted strings
- Label keys with dots: `` object.metadata.labels[`app.kubernetes.io/name`] ``
- No `enumerate()` — use: `[0,1,2].filter(i, i < size(list) && cond(list[i]))`
- Map key check: `"key" in object.metadata.labels` (not `has()`)
- `capabilities.drop` is atomic list — mutate via JSONPatch only
- Cluster-scoped resources: always guard with `has(request.namespace)`
- PolicyException "not processed" warning is cosmetic when `enablePolicyException=true`
- Background controller evaluates pod-targeted mutations against Deployment/RS → type mismatch warnings are cosmetic

---

## ArgoCD Patterns

### ApplicationSet (cluster generator)
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: platform-apps
  namespace: argocd
spec:
  generators:
    - clusters:
        selector:
          matchLabels:
            environment: production
  template:
    metadata:
      name: "{{name}}-platform"
    spec:
      project: platform
      source:
        repoURL: https://github.com/org/gitops
        targetRevision: main
        path: "clusters/{{name}}/platform"
      destination:
        server: "{{server}}"
        namespace: platform
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
          - ServerSideApply=true
```

### Sync waves
```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"   # lower = earlier; negative allowed
```

---

## ETCD Operations

```bash
# Cert alias
alias etcdctl='etcdctl \
  --cert /etc/kubernetes/pki/etcd/peer.crt \
  --key /etc/kubernetes/pki/etcd/peer.key \
  --cacert /etc/kubernetes/pki/etcd/ca.crt'

# Health & membership
ETCDCTL_API=3 etcdctl endpoint status --cluster --write-out=table
ETCDCTL_API=3 etcdctl endpoint health --cluster
ETCDCTL_API=3 etcdctl member list --write-out table

# Backup
ETCDCTL_API=3 etcdctl snapshot save /tmp/snapshot-$(date +%F).db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Restore
ETCDCTL_API=3 etcdctl snapshot restore /tmp/snapshot.db \
  --data-dir /var/lib/etcd-from-backup \
  --initial-cluster=master=https://127.0.0.1:2380 \
  --initial-cluster-token etcd-cluster-1 \
  --initial-advertise-peer-urls=https://127.0.0.1:2380

# Read key directly
KEY="/registry/deployments/kube-system/coredns"
kubectl exec -it etcd-controlplane -- sh -c "ETCDCTL_API=3 etcdctl \
  --endpoints https://127.0.0.1:2379 \
  --cacert /etc/kubernetes/pki/etcd/ca.crt \
  --key /etc/kubernetes/pki/etcd/server.key \
  --cert /etc/kubernetes/pki/etcd/server.crt \
  get \"$KEY\" -w json" | jq '.kvs[0].value' | cut -d'"' -f2 | base64 --decode
```

---

## Node Maintenance

```bash
kubectl drain node01 --ignore-daemonsets --force --delete-emptydir-data
kubectl uncordon node01
kubectl cordon node01          # stop scheduling without eviction
kubeadm alpha certs check-expiration
```

---

## Certificate Management

```bash
kubectl get csr
kubectl certificate approve <cert-name>
kubectl certificate deny <cert-name>

# Export kubeconfig certs
kubectl config view --raw -o jsonpath="{.users[?(@.name=='clusterAdmin_<RG>_<CLUSTER>').user.client-certificate-data}" | base64 -d
kubectl config view --raw -o jsonpath="{.users[?(@.name=='clusterAdmin_<RG>_<CLUSTER>').user.client-key-data}" | base64 -d

# Decode TLS secret
kubectl get secret wildcard-cert -n acme -o go-template='{{range $k,$v := .data}}{{printf "%s: " $k}}{{if not $v}}{{$v}}{{else}}{{$v | base64decode}}{{end}}{{"\n"}}{{end}}'

# Inspect Harbor TLS secret
kubectl -n harbor get secret harbor-jobservice-crt -o jsonpath="{.data.tls\.crt}" | base64 -d | openssl x509 -noout -text
```

---

## Essential kubectl Commands

### Filtering and output
```bash
# Custom columns
kubectl get pod -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName,NAMESPACE:.metadata.namespace -A

# All images in cluster
kubectl get pods -A -o jsonpath="{..image}" | tr -s '[[:space:]]' '\n' | sort -u

# All image pull policies
kubectl get deploy --no-headers -A -o jsonpath='{range .items[*]}NS:{.metadata.namespace}{"\t"}APP:{.metadata.name}{"\t"}image:{.spec.template.spec.containers[*].image}{"\t"}Policy:{.spec.template.spec.containers[*].imagePullPolicy}{"\n"}'

# Node internal IPs
kubectl get nodes -o json | jq -r '.items[].status.addresses[]? | select(.type=="InternalIP") | .address'

# All services and nodePorts
kubectl get svc -A -o json | jq -r '.items[] | [.metadata.name, ([.spec.ports[].nodePort | tostring] | join("|"))] | @tsv'

# Pods sorted by restart count
kubectl get pods --sort-by='.status.containerStatuses[0].restartCount' -A

# PVs sorted by capacity
kubectl get pv --sort-by=.spec.capacity.storage -o=custom-columns=NAME:.metadata.name,CAPACITY:.spec.capacity.storage

# Running pods only
kubectl get pods --field-selector=status.phase=Running -A

# Worker nodes only
kubectl get node --selector='!node-role.kubernetes.io/master'

# Pod subnets
kubectl get nodes -o jsonpath='{.items[*].spec.podCIDR}' | tr ' ' '\n'
```

### Patching
```bash
# Update container image
kubectl set image deployment/my-app app=my-repo/my-app:v2.0.0

# JSONPatch — remove livenessProbe
kubectl patch deployment my-app --type=json \
  -p='[{"op":"remove","path":"/spec/template/spec/containers/0/livenessProbe"}]'

# Cordon a node via patch
kubectl patch node k8s-node-1 -p '{"spec":{"unschedulable":true}}'
```

### Rollout
```bash
kubectl rollout status deployment my-app --timeout 90s
kubectl rollout history deployment my-app
kubectl rollout history deployment my-app --revision=2
kubectl rollout undo deployment my-app
kubectl rollout undo deployment my-app --to-revision=3
```

### Logs
```bash
kubectl logs -f deployment/myapp -c myapp --tail=100
kubectl logs -l app=myapp --tail=100 -A
kubectl logs my-pod --previous       # crashed container
kubectl logs my-pod --all-containers
```

### Secrets and ConfigMaps
```bash
kubectl create configmap myconfig --from-file=app.properties
kubectl create configmap myconfig --from-literal=key=value

kubectl create secret generic db-secret \
  --from-literal=DB_HOST=sql01 \
  --from-literal=DB_User=root \
  --from-literal=DB_Password=password123

kubectl create secret docker-registry my-reg \
  --docker-username=user \
  --docker-password=pass \
  --docker-server=registry.example.com

kubectl get secret my-secret -o jsonpath="{.data.password}" | base64 -d
```

### kubeconfig
```bash
KUBECONFIG=~/.kube/config:~/.kube/other kubectl config view --merge --flatten
kubectl config get-contexts
kubectl config use-context my-cluster
kubectl config set-context --current --namespace=my-ns
kubectl config view -o jsonpath='{.users[?(@.name=="admin")].user.password}'
```

### API exploration
```bash
kubectl api-resources
kubectl explain deployment.spec.strategy
kubectl get --raw='/readyz?verbose'
kubectl get pods --v=8    # debug API calls
```

### Cleanup orphaned ReplicaSets
```bash
kubectl get replicasets -A -ojson \
  | jq -r '.items[] | select(.status.replicas == 0) | "\(.metadata.namespace) \(.metadata.name)"' \
  | while read ns rs; do kubectl delete replicaset "$rs" -n "$ns"; done
```

### Delete evicted/failed pods
```bash
kubectl get pods -A | grep Evicted | awk '{print $1" "$2}' | while read ns pod; do kubectl delete pod "$pod" -n "$ns"; done
kubectl delete $(kubectl get pods --field-selector=status.phase=Failed -o name -A) -A
```

---

## Debugging Workflow (`/k8s:debug`)

1. `kubectl describe pod <pod> -n <ns>` → read **Events** section first
2. `kubectl logs <pod> -n <ns> --previous` → if CrashLoopBackOff
3. `kubectl get events --sort-by=.lastTimestamp -n <ns>` → timeline
4. For Kyverno denials: `kubectl get admissionreports -A -o json | jq '.items[] | select(.spec.summary.fail > 0)'`
5. For ArgoCD sync: check sync waves, resource hooks, `ignoreDifferences`
6. For image pull: verify imagePullSecret, ACR role, image tag exists
7. For OOMKilled: `kubectl top pod -n <ns>` → increase `memory.limits`
8. For Pending: `kubectl describe node` → resource pressure or taint
9. For network: `kubectl run debug --image=nicolaka/netshoot -it --rm`
10. For API calls: `kubectl proxy --port=8001` then `curl http://localhost:8001/api/v1/pods`

---

## Proactive Triggers

Flag these without being asked:
- **`:latest` image tag** → Pin to digest or semver
- **No resource limits** → Unbounded pods cause node pressure
- **No probes** → Add `livenessProbe` + `readinessProbe`
- **`runAsRoot` or missing `runAsNonRoot`** → Critical security violation
- **Single replica** → Add `podAntiAffinity` or `topologySpreadConstraints`
- **`automountServiceAccountToken: true`** on pods not calling K8s API → set `false`
- **No NetworkPolicy in namespace** → Generate default-deny + explicit allows
- **No PodDisruptionBudget on HA workload** → Add PDB with `maxUnavailable: 1`
- **Kyverno policy without `background: true`** → Existing violations won't be caught
- **PolicyException without expiry annotation** → Add `kyverno.io/expires` label
- **Wildcard RBAC** (`verbs: ["*"]` or `resources: ["*"]`) → Scope to minimum
- **`seccompProfile` missing** → Add `type: RuntimeDefault`
- **No `lifecycle.preStop`** on long-running services → Add sleep to drain connections gracefully

---

## Repository Reference

Personal Kubernetes YAML examples: https://github.com/YOUR_USERNAME/kubernetes-yaml

| Folder | Contents |
|--------|---------|
| `Example/` | Production Deployment + HPA v2 + PDB + ResourceQuota + LimitRange |
| `network-policy/` | NetworkPolicy patterns (allow/deny, multi-selector, egress) |
| `Kyverno/` (workspace) | `01-security` to `06-exceptions` ClusterPolicy set |
| `ArgoCD/` (workspace) | App-of-Apps bootstrap, ApplicationSets |
| `Operator/` (workspace) | CronJob operators: cert-expiry, pod-cleanup, etcd-backup, cost-opt |
| `Monitoring/` | PrometheusRule, ServiceMonitor YAMLs |
| `KEDA/` | KEDA ScaledObject examples |
| `Vault/` | Vault Agent injector + CSI provider patterns |
| `Cert Manager/` | Certificate + ClusterIssuer manifests |
| `Login_MultiClusters/` | Multi-cluster kubeconfig patterns |
| `Troubleshooting/` | Common issue debugging guides |
| `strategies/` | Deployment strategies (blue/green, canary, recreate) |
| `persistent-volume/` | PV + PVC + StorageClass examples |
| `ingress/` | Ingress controller + TLS termination patterns |

---

## Python: Kubernetes API Client Patterns

Use the official `kubernetes` Python client for automation scripts:

```python
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

# Load kubeconfig (in-cluster: config.load_incluster_config())
config.load_kube_config()

v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()

# List pods in a namespace
def list_pods(namespace: str) -> list[str]:
    pods = v1.list_namespaced_pod(namespace=namespace)
    return [pod.metadata.name for pod in pods.items]

# Get deployment status
def get_deployment_ready(namespace: str, name: str) -> bool:
    try:
        dep = apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
        return dep.status.ready_replicas == dep.spec.replicas
    except ApiException as exc:
        if exc.status == 404:
            return False
        raise
```

```python
# Force restart a deployment (equivalent to kubectl rollout restart)
from datetime import datetime, timezone
import json

def rollout_restart(namespace: str, name: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    patch = {
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {
                        "kubectl.kubernetes.io/restartedAt": now
                    }
                }
            }
        }
    }
    apps_v1.patch_namespaced_deployment(
        name=name, namespace=namespace, body=patch
    )
```

```python
# Apply a manifest from a dict (like kubectl apply)
from kubernetes.utils import create_from_dict

def apply_manifest(manifest: dict) -> None:
    k8s_client = client.ApiClient()
    create_from_dict(k8s_client, manifest, verbose=True)
```

```python
# Watch pod logs (streaming)
from kubernetes import watch

def stream_pod_logs(namespace: str, pod_name: str, container: str) -> None:
    w = watch.Watch()
    for line in w.stream(
        v1.read_namespaced_pod_log,
        name=pod_name,
        namespace=namespace,
        container=container,
        follow=True,
        _preload_content=False,
    ):
        print(line.decode("utf-8"), end="")
```

## Related Skills

- `terraform-azure` — provision the AKS cluster this skill operates on
- `infrastructure-security` — policy-as-code deep dive, Wiz, OPA
- `devops-cicd` — Azure DevOps pipelines to deploy to these clusters
- `helm-chart-builder` — package manifests as Helm charts
- `observability-designer` — Prometheus/Grafana/Loki for the cluster

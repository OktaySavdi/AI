# Patterns Rules

## Design Principles

### Single Responsibility
Every module, class, and function does exactly one thing.
If you need "and" to describe what it does, split it.

### Dependency Inversion
High-level modules do not depend on low-level modules.
Both depend on abstractions (interfaces).
Inject dependencies — don't instantiate them inside functions.

### Explicit over Implicit
Prefer explicit configuration over convention-based magic.
If the behaviour isn't obvious from reading the code, make it explicit.

### Fail Fast
Validate inputs at system boundaries immediately.
Don't propagate invalid data through the system.
Return/raise errors as soon as they're detected.

## Common Patterns for This Codebase

### Configuration Pattern (Bash)
```bash
#!/usr/bin/env bash
set -euo pipefail

# Constants (immutable, UPPER_SNAKE)
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"

# Configurable via environment (provide defaults)
readonly TARGET_NAMESPACE="${TARGET_NAMESPACE:-production}"
readonly RETRY_COUNT="${RETRY_COUNT:-3}"

main() {
  parse_args "$@"
  validate_prerequisites
  do_work
}

main "$@"
```

### Retry Pattern (Bash)
```bash
retry() {
  local max_attempts="$1"
  local delay="$2"
  shift 2
  local cmd=("$@")
  local attempt=1

  while (( attempt <= max_attempts )); do
    if "${cmd[@]}"; then
      return 0
    fi
    echo "[WARN] Attempt $attempt/$max_attempts failed. Retrying in ${delay}s..." >&2
    sleep "$delay"
    (( attempt++ ))
  done
  echo "[ERROR] All $max_attempts attempts failed." >&2
  return 1
}
```

### Repository Pattern (Python)
Separate data access from business logic:
```python
from abc import ABC, abstractmethod

class ClusterRepository(ABC):
    @abstractmethod
    def get_by_name(self, name: str) -> Cluster: ...
    @abstractmethod
    def list_all(self) -> list[Cluster]: ...

class KubernetesClusterRepository(ClusterRepository):
    def __init__(self, k8s_client: CoreV1Api) -> None:
        self._client = k8s_client
    # ...
```

### Kubernetes Resource Pattern
Always use full resource spec:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    app.kubernetes.io/name: my-app
    app.kubernetes.io/managed-by: argocd
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: my-app
  template:
    metadata:
      labels:
        app.kubernetes.io/name: my-app
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
        - name: my-app
          image: registry/my-app:1.0.0  # Never :latest
          resources:
            requests: {cpu: 100m, memory: 128Mi}
            limits: {cpu: 500m, memory: 512Mi}
          livenessProbe:
            httpGet: {path: /healthz, port: 8080}
          readinessProbe:
            httpGet: {path: /readyz, port: 8080}
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: [ALL]
```

### ArgoCD App-of-Apps Pattern
```yaml
# Bootstrap application points to a directory of applications
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: bootstrap
  namespace: argocd
spec:
  source:
    path: ArgoCD/bootstrap
    targetRevision: main
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Terraform Module Pattern
```hcl
# Always use modules from TfModules/, not raw resources
module "aks" {
  source = "../../TfModules/AKS"
  # Match variable names exactly from module's variables.tf
  cluster_name     = local.cluster_name
  resource_group   = azurerm_resource_group.main.name
  node_count       = var.node_count
  tags             = local.common_tags
}
```

## Anti-Patterns to Avoid
- **God functions**: functions that do everything
- **Primitive obsession**: using raw strings for domain concepts (use types)
- **Feature envy**: a class that uses another class's data more than its own
- **Magic configuration**: behaviour that changes based on undocumented env vars
- **Manual resource management**: always use `defer`/`with`/`trap` for cleanup

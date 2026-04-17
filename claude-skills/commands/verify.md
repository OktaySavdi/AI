# Verify

Run validation suite for the current workspace context.

## Usage

```
/verify
```

## Validation Steps by Context

### Kubernetes
```bash
kubectl apply --dry-run=server -f <manifest>
kubeval <manifest>
```

### Kyverno
```bash
kubectl apply --dry-run=server -f Kyverno/
kyverno test .
```

### Terraform
```bash
terraform fmt -check
terraform validate
tflint
```

### Helm
```bash
helm lint <chart>
helm template <chart> | kubeval
```

### Python
```bash
ruff check .
mypy .
pytest --tb=short
```

### Bash
```bash
shellcheck Shell/*.sh
```

Run all applicable validators for changed files and report results.

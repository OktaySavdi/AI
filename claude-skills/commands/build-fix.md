# Build Fix

Invoke the `build-error-resolver` agent to diagnose and fix build, test, or lint errors.

## Usage

```
/build-fix
```

Paste the error output after invoking.

## Supported Environments

- Python (pytest, mypy, ruff, bandit)
- Bash (shellcheck, set -e failures)
- Go (go build, go test, golint)
- Terraform (terraform validate, tflint)
- Kubernetes manifests (kubectl dry-run, kubeval)
- Helm (helm lint, helm template)
- Kyverno (policy apply --dry-run)

## Process

1. Parse error message and identify root cause
2. Locate affected file and line
3. Propose minimal fix
4. Verify fix resolves the error without side effects

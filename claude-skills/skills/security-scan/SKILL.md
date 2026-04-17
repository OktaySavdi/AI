---
name: "security-scan"
description: >
  AgentShield security auditor integration. Automated security scanning patterns
  for code, infrastructure, and dependencies. Activate for automated security scans.
metadata:
  version: 1.0.0
  category: security
---

# Security Scan Skill

## Scan Pipeline

Run in sequence — stop on CRITICAL findings:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Secret Scanning ==="
gitleaks detect --source . --no-git

echo "=== Dependency Audit ==="
# Python
pip-audit --requirement requirements.txt

# Node.js
npm audit --audit-level=high

# Go
govulncheck ./...

echo "=== Container Image Scan ==="
trivy image --exit-code 1 --severity CRITICAL,HIGH myapp:latest

echo "=== SAST ==="
# Python
bandit -r src/ -ll

# Terraform
tfsec .

# Kubernetes manifests
kubesec scan manifests/*.yaml
```

## Findings Severity

| Level | Response |
|---|---|
| CRITICAL | Block deploy, immediate fix required |
| HIGH | Block deploy unless documented exception |
| MEDIUM | Fix in next sprint, create ticket |
| LOW | Fix when touching that code |
| INFO | Log for awareness |

## Kubernetes-Specific Scans

```bash
# Polaris (best practices)
polaris audit --audit-path manifests/

# kubesec (security risk analysis)
kubesec scan deployment.yaml

# Kyverno policy audit
kubectl apply --dry-run=server -f Kyverno/
```

## CI Integration

```yaml
# Azure DevOps
- task: Bash@3
  displayName: Security Scan
  inputs:
    script: |
      gitleaks detect --source . --no-git --exit-code 1
      trivy image --exit-code 1 --severity CRITICAL $(IMAGE_TAG)
      bandit -r src/ -ll
```

## OWASP Top 10 Quick Check

| Risk | Tool | Check |
|---|---|---|
| A01 Broken Access Control | Manual + RBAC audit | No wildcard roles |
| A02 Cryptographic Failures | trivy, pip-audit | No weak cipher deps |
| A03 Injection | bandit, eslint-security | Parameterized queries |
| A04 Insecure Design | Code review | Defense in depth |
| A05 Security Misconfiguration | tfsec, polaris | Secure defaults |
| A06 Vulnerable Components | pip-audit, npm audit | No known CVEs |
| A07 Auth Failures | Manual | Token expiry, revocation |
| A08 Software Integrity | cosign, sbom | Signed images |
| A09 Logging Failures | Manual | Audit logs enabled |
| A10 SSRF | Manual | Validate outbound URLs |

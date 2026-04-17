# Security Rules

These rules are mandatory. Flag violations immediately — do not wait until the
end of a review.

## Secrets and Credentials
- **NEVER** hardcode secrets, passwords, API keys, or tokens in code
- **NEVER** commit `.env` files containing real credentials
- Secrets belong in: Azure Key Vault, Kubernetes Secrets (sealed), or
  Azure DevOps Variable Groups (secret type)
- If a secret is found in code: flag it as CRITICAL before anything else

## Input Validation
- Validate at every system boundary (API endpoints, CLI args, file reads)
- Reject input that doesn't match expected format/range — never try to sanitise
  untrusted SQL or shell input
- Use parameterised queries for all database operations (no string concatenation)
- Never pass user input to `shell=True`, `eval()`, or `exec()`

## Authentication & Authorisation
- Use Managed Identity / UAMI for Azure resource access (never service principal
  client secrets in code)
- RBAC: Principle of least privilege — request only the permissions actually needed
- No wildcard RBAC: `verbs: ["*"]` or `resources: ["*"]` is always CRITICAL
- `automountServiceAccountToken: false` unless the pod explicitly calls the K8s API

## Network Security
- All services default to ClusterIP (internal only) — justify any NodePort or LoadBalancer
- NetworkPolicy: default-deny all, then explicitly allow required traffic
- No direct internet access from workload pods without justification and review
- TLS termination at ingress — no plaintext HTTP between public internet and app

## Container Security
- `runAsNonRoot: true` and a non-zero `runAsUser`
- `allowPrivilegeEscalation: false`
- `readOnlyRootFilesystem: true` (use emptyDir for writable paths)
- `capabilities.drop: [ALL]` — add back only what is specifically required
- No `privileged: true` containers
- No `:latest` image tags — pin to digest or semver

## Pipeline Security
- Secret variables are marked secret in Azure DevOps — never echo them
- `failOnStandardError: true` on all AzureCLI steps
- Approval gates required before any production change
- Image vulnerability scanning in CI before deployment

## Audit Trail
- Structural changes to infrastructure require a Jira ticket
- Kyverno PolicyExceptions require documented Jira reference in annotations
- All production changes are traceable to a pipeline run and commit

## Dependency Security
- No dependencies with known critical CVEs
- Container base images: prefer distroless or alpine; scan with Trivy in CI
- Terraform providers pinned to minor version (`~> 4.0`) — not unpinned

## Incident Response Trigger
If any of the following are found, raise immediately as CRITICAL:
1. Secret committed to source control
2. Wildcard RBAC role
3. Container running as root (UID 0) in production
4. Unencrypted secrets in ConfigMap
5. Public-facing port without NetworkPolicy restriction

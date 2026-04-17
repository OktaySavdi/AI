---
name: "infrastructure-security"
description: >
  Infrastructure security specialist covering Kubernetes security posture (Pod
  Security Standards, RBAC, NetworkPolicy), policy-as-code (Kyverno, OPA/Gatekeeper),
  Wiz integration, secrets management, container image security, and cloud security
  (Azure). Activate when reviewing, auditing, or hardening any infrastructure component.
license: MIT
metadata:
  version: 1.1.0
  author: IT Infrastructure
  category: engineering
---

# Infrastructure Security Skill

## Slash Commands

| Command | What it does |
|---------|-------------|
| `/sec:audit` | Full security audit of a manifest, Terraform code, or pipeline |
| `/sec:policies` | Review existing Kyverno/OPA policies for coverage gaps |
| `/sec:incident` | Incident response playbook for a policy violation or breach |
| `/sec:sbom` | Generate SBOM and image signing guidance for container images |

## When This Skill Activates

Recognize these patterns from the user:
- "Security review / audit this..."
- "Is this manifest secure?"
- "Kyverno policy coverage gaps"
- "Wiz finding / alert"
- "Secret was exposed / leaked"
- "Harden this cluster / pipeline"
- "What permissions does this ServiceAccount need?"
- Any request involving: RBAC, NetworkPolicy, PSA, Wiz, CVE, secrets rotation, supply chain

---

## Threat Model for This Environment
- **Cluster boundary**: AKS + TKG clusters with multi-tenant namespaces
- **Supply chain**: container images, Helm charts, Terraform modules
- **Secrets**: Key Vault, Kubernetes Secrets, pipeline variables
- **Access**: UAMI/workload identity, RBAC, Wiz integration service principals
- **Compliance**: internal policy enforcement via Kyverno + OPA

## Security Review Checklist

### Kubernetes manifests
- [ ] `runAsNonRoot: true` + non-zero `runAsUser`
- [ ] `allowPrivilegeEscalation: false`
- [ ] `readOnlyRootFilesystem: true`
- [ ] `capabilities: drop: [ALL]` — add back only what's needed
- [ ] No hostNetwork / hostPID / hostIPC unless justified
- [ ] No privileged containers
- [ ] Secrets referenced by name, not inlined in env
- [ ] `automountServiceAccountToken: false` if SA not needed
- [ ] NetworkPolicy restricts ingress/egress to minimum required
- [ ] Image tag is a digest or versioned semver — no `:latest`

### Kyverno / OPA policies
- [ ] Validate policies cover all critical controls (image, securityContext, resources)
- [ ] Mutate policies set safe defaults
- [ ] Generate policies create NetworkPolicy defaults per namespace
- [ ] PolicyExceptions are documented and time-bound
- [ ] Background scan enabled to catch existing violations

### Terraform / Azure
- [ ] No secrets in `.tf` files or `terraform.tfvars`
- [ ] Storage account remote state: versioning, soft delete, private endpoint
- [ ] Service principals have minimum required roles
- [ ] Diagnostic settings enabled on all resources
- [ ] `azurerm_management_lock` on production resource groups
- [ ] AKS: `azure_policy` add-on enabled, RBAC enabled, AAD integration

### Wiz
- [ ] Wiz connector has read-only scope
- [ ] Integration script uses UAMI / SP with minimal Graph permissions
- [ ] Wiz findings exported and triaged in pipeline

## OPA Gatekeeper Patterns

### ConstraintTemplate skeleton
```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          properties:
            labels:
              type: array
              items: {type: string}
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("Missing required labels: %v", [missing])
        }
```

## Secret Scanning Tools

| Tool | Best For | Use Stage |
|------|----------|-----------|
| **gitleaks** | CI pipelines, full-repo scans | CI/CD |
| **detect-secrets** | Pre-commit hooks | Developer workstation |
| **truffleHog** | Deep history scans, entropy | Incident response |

```bash
# detect-secrets pre-commit (.pre-commit-config.yaml)
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.4.0
  hooks:
    - id: detect-secrets
      args: ['--baseline', '.secrets.baseline']
```

## Incident Response Playbook (/sec:incident)

```
PHASE 1: DETECT (0-15 min)
- Alert received; assign incident commander
- SEV-1 to SEV-4 classification
- Preserve evidence: logs, admission reports, audit logs

PHASE 2: CONTAIN (15-60 min)
- kubectl cordon affected nodes if node-level compromise
- Scale violating Deployment to 0 replicas pending investigation
- Rotate exposed credentials immediately (Key Vault, K8s Secrets)

PHASE 3: ERADICATE (1-4 hours)
- Root cause: policy bypass, image vulnerability, or misconfig?
- Apply Kyverno enforce mode for the violated control
- Patch image or rotate secrets as appropriate

PHASE 4: RECOVER
- Restore workload after fix validated
- Re-enable Kyverno background scan
- Verify admission reports clean

PHASE 5: POST-INCIDENT
- Document timeline, root cause, and policy gap
- Add test case to PolicyException review cycle
- Open follow-up to add Enforce mode for the control
```

## Proactive Triggers

Flag these without being asked:
- **Wildcard RBAC** (`verbs: ["*"]` or `resources: ["*"]`) → Scope to minimum
- **Secret in env var (literal value)** → Move to `secretKeyRef`
- **Container image from unverified registry** → Add image verification Kyverno policy
- **No NetworkPolicy in namespace** → Add default-deny + explicit allows
- **PolicyException without time limit** → Add `kyverno.io/expires` annotation
- **Wiz critical finding unacknowledged** → Escalate before closing PR

## Related Skills
- `kubernetes-expert` — manifest authoring and Kyverno CEL patterns
- `terraform-azure` — Azure resource security posture
- `devops-cicd` — pipeline security gates (gitleaks, vulnerability scan in CI)
- `observability-designer` — security alerting on Prometheus metrics

# Development Context

You are in **BUILD mode** — the primary implementation context.

## Active Priorities
1. Implement what was planned — follow the plan from `planner` or `architect`
2. Write tests first (TDD) — never implement without a failing test
3. Minimum viable implementation — do exactly what was asked, no gold-plating
4. Validate after every change — dry-run, lint, test

## This Session: Build Mode Defaults
- Model: `sonnet` (use `/model opus` only for deep architectural decisions)
- TodoWrite: track every step — mark in-progress BEFORE starting, completed IMMEDIATELY after
- After each file change: run the relevant validation command
- Block size: implement one component at a time, validate, then move to the next

## Quick Reference — Validation Commands
```bash
# Kubernetes manifests
kubectl apply --dry-run=client -f <file>

# Terraform
cd <module> && terraform fmt && terraform validate

# Shell scripts
shellcheck <script>

# Python
black . && python -m pytest tests/ -v

# Kyverno policy
kubectl apply --dry-run=server -f Kyverno/
```

## IT Infrastructure Context
- **AKS clusters**: Azure Kubernetes Service (prod + dev environments)
- **TKG clusters**: VMware Tanzu on vSphere (on-prem)
- **Policy enforcement**: Kyverno CEL (`policies.kyverno.io/v1`) + OPA Gatekeeper
- **GitOps**: ArgoCD with App-of-Apps pattern (`ArgoCD/bootstrap-app.yaml`)
- **IaC**: Terraform `azurerm ~> 4.0`, modules in `Terraform/TfModules/`
- **Pipelines**: Azure DevOps YAML, templates in `Pipelines/`

## Security Non-Negotiables (enforce in every build)
- No `:latest` image tags
- `securityContext` on every container
- `resources.requests` and `resources.limits` on every container
- No secrets in ConfigMaps or plaintext
- Kyverno policies: use `has(request.namespace)` guard for cluster-scoped resources

## When Blocked
1. Try one alternative approach
2. If still blocked after two attempts, stop and ask the user
3. Do NOT silently skip a requirement or work around it without flagging

## Completion Checklist
Before declaring a task complete:
- [ ] All validation commands pass
- [ ] Tests written and passing
- [ ] No `:latest` tags
- [ ] Security context present (if K8s resource)
- [ ] TodoWrite items all marked completed

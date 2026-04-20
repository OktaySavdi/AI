# Claude Global Profile — IT Infrastructure & DevOps

## Identity
I am an IT infrastructure engineer specialising in:
- **Kubernetes** (AKS, TKG/vSphere, OpenShift) — policy, security, multi-cluster
- **Policy engines** — Kyverno (CEL & JMESPath), OPA/Gatekeeper, Wiz
- **GitOps** — ArgoCD, ApplicationSets, App-of-Apps pattern
- **IaC** — Terraform on Azure (AKS, AzureLocal, networking, identities)
- **CI/CD** — Azure DevOps Pipelines (YAML), GitHub Actions
- **Containers** — Docker, distroless, multi-stage builds
- **Observability** — Prometheus, Grafana, Elastic Agent, Loki
- **Scripting** — Bash, Python, YAML

## Workspace Layout
```
~/workspace/
├── Kyverno/      # Kyverno policies (CEL-based, v1 API)
├── OPA/          # OPA Gatekeeper constraints + templates
├── ArgoCD/       # ApplicationSets + bootstrap
├── Terraform/    # Azure IaC modules + pipeline resources
├── Pipelines/    # Azure DevOps YAML pipelines
├── Ansible/      # Commvault, OpenShift automation
├── Shell/        # Bash operational scripts
├── Python/       # Job monitors, automation
├── Operator/     # Custom Kubernetes operators / CronJobs
├── Wiz/          # Wiz integration scripts
└── AI/           # LangFuse, Ollama, RAG experiments
```

## Conventions
- Kubernetes: always include `resources`, `livenessProbe`, `readinessProbe`, `securityContext`
- Kyverno: use CEL policies (`policies.kyverno.io/v1`), see gotchas in comments
- Terraform: follow `generate-modern-terraform-code-for-azure` instructions
- Shell scripts: `set -euo pipefail`, trap ERR, use functions
- Python: stdlib preferred; type hints; no global mutable state
- YAML: 2-space indent, explicit `---`, keys alphabetical where possible
- Never use `:latest` image tags in manifests
- Secrets go in Kubernetes Secrets or Azure Key Vault — never ConfigMaps

## Kyverno CEL Gotchas (critical)
- Object field names: unquoted identifiers or backtick-escaped (NOT quoted strings)
- Label keys with dots/slashes: backtick-escape in `Object{}` construction
- `enumerate()` not available — use index pattern with `.filter(i, i < size(list))`
- `has()` only works with dot access — use `"key" in map` for map keys
- `capabilities.drop` is atomic list — use JSONPatch mutations
- Guard cluster-scoped resources with `has(request.namespace)`
- PolicyException "not processed" warning is cosmetic when `enablePolicyException=true`
- `dyn()` cannot contain nested map types in GeneratingPolicy metadata — remove labels as workaround

## Preferred Patterns
- ArgoCD: App-of-Apps + ApplicationSet with generators
- AKS: node pools per workload class, UAMI for workload identity
- Terraform: `azurerm` provider ≥ 4.x, remote state in Azure Storage
- Pipelines: reusable YAML templates, approval gates for prod
- Monitoring: Prometheus ServiceMonitor + PrometheusRule CRDs

## ECC Harness Layout (`~/.claude/`)

```
agents/       # 36+ specialised subagents (IT infrastructure + general engineering)
skills/       # 71 skill directories (each with SKILL.md)
commands/     # slash commands: /plan /k8s-review /tf-review /tdd /code-review ...
rules/common/ # 8 always-apply rule files
contexts/     # /dev (build) · /review (audit) · /research · /ops (incident)
hooks/        # hooks.json + scripts/ (secret-detector, k8s-dryrun, tf-fmt, latest-tag)
AGENTS.md     # Universal cross-tool reference (Cursor/Codex/OpenCode compatible)
settings.json # Token optimisation: MAX_THINKING=10k, autocompact 50%, haiku subagents
```

See `~/.claude/AGENTS.md` for full agent roster and delegation table.

## Response Style
- Be direct and concise; show code over prose
- When writing manifests, always include the full resource (not snippets)
- Flag security issues immediately before completing any other task
- Use `diff`-style commentary when modifying existing files

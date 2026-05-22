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

---

## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately — don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for the relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes — don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

---

## Task Management

1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

---

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

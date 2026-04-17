# AGENTS.md — Universal Agent Reference

> This file is read by Claude Code, Cursor, Codex, and OpenCode.
> It documents the full ECC harness at `~/.claude/` for the IT Infrastructure environment.

---

## Quick Reference

| Context | Command | Agent Invoked |
|---|---|---|
| Plan a feature | `/plan "description"` | `planner` |
| Deep architecture | `/plan` with complexity flag | `architect` |
| K8s manifest review | `/k8s-review` | `k8s-reviewer` |
| Security audit | `/security-audit` | `security-reviewer` |
| Kyverno policy | `/kyverno-policy` | `policy-engineer` |
| Terraform IaC | `/tf-review` | `terraform-engineer` |
| ADO pipeline | `/pipeline-generate` | `pipeline-builder` |
| Helm chart | `/helm-create` | `helm-packager` |
| Incident response | Describe issue | `incident-responder` |
| ArgoCD GitOps | Describe app | `argocd-operator` |
| Observability | Describe metric/alert | `observability-designer` |
| TDD workflow | `/tdd` | `tdd-guide` |
| Code review | `/code-review` | `code-reviewer` |
| Build/test fix | `/build-fix` | `build-error-resolver` |
| Refactor safely | `/refactor-clean` | `refactor-cleaner` |
| Docs sync | Describe docs | `doc-updater` |
| Python review | Describe py file | `python-reviewer` |
| Go review | Describe go file | `go-reviewer` |
| DB schema review | Describe schema | `database-reviewer` |
| Status/comm | Describe context | `chief-of-staff` |

---

## Agent Roster

### IT Infrastructure Agents

**`k8s-reviewer`** — Production readiness check for Kubernetes manifests.
Checks: securityContext, resources, probes, RBAC, NetworkPolicy, image tags, Kyverno policy alignment.

**`security-reviewer`** — Infrastructure security audit.
Covers: OWASP Top 10, CIS K8s Benchmark, Terraform misconfiguration, exposed secrets, RBAC escalation, pipeline injection.

**`policy-engineer`** — Kyverno CEL (`policies.kyverno.io/v1`) and OPA/Gatekeeper policy author.
Knows all CEL gotchas; writes validate, mutate, generate, and PolicyException resources.

**`terraform-engineer`** — Azure Terraform IaC using all 28 TfModules.
Provider: `azurerm ~> 4.0`, `azuread ~> 3.0`. Remote state in Azure Storage. Follows module conventions.

**`pipeline-builder`** — Azure DevOps YAML CI/CD pipelines.
Templates in `Pipelines/`, approval gates, variable groups, AKS/TKG deployment strategies.

**`incident-responder`** — Kubernetes and Azure incident triage.
Structured runbook: classify → collect → diagnose → mitigate → restore → post-mortem.
TKG SSH: staging `ssh root@<TKG_STAGING_IP>`, prod via jump `ssh <JUMP_USER>@<JUMP_HOST_IP>`.

**`argocd-operator`** — ArgoCD App-of-Apps + ApplicationSet configuration.
Bootstrap patterns, sync policies, wave ordering, health checks.

**`helm-packager`** — Helm chart authoring for Kubernetes applications.
Chart structure, values schema, named templates, hooks, tests, AKS-specific patterns.

**`observability-designer`** — Prometheus/Grafana/Loki/Elastic observability stack.
ServiceMonitor, PrometheusRule, Grafana dashboards, SLO/SLA alerting, OpenTelemetry.

### General Engineering Agents

**`planner`** — Feature implementation blueprints.
Produces: scope, acceptance criteria, sub-tasks, risk flags, agent delegation plan.

**`architect`** — System design and ADRs. Uses `opus` model for deep reasoning.
Produces: C4 diagrams (Mermaid), ADR documents, trade-off matrices, NFR frameworks.

**`tdd-guide`** — Test-driven development RED-GREEN-REFACTOR workflow.
Writes failing tests first, then minimal implementation, then refactors.

**`code-reviewer`** — General code quality, correctness, security review.
Structured report: blocker → major → minor → nit. No behaviour-change suggestions.

**`build-error-resolver`** — Build, test, and lint error diagnosis.
Covers: Python, Bash, Go, Terraform, K8s manifests, Helm, Kyverno.

**`refactor-cleaner`** — Dead code removal and cleanup without behaviour change.
Validates: all tests pass before and after, no new features added.

**`doc-updater`** — Documentation synchronisation with code changes.
Updates: README, CHANGELOG, inline comments, API docs.

**`python-reviewer`** — Python-specific code review.
Checks: type hints, idioms, security (bandit), pytest patterns, stdlib vs third-party.

**`go-reviewer`** — Go-specific code review.
Checks: error handling, goroutine safety, idiomatic Go, interface design.

**`database-reviewer`** — SQL/schema/migration review (PostgreSQL focus).
Checks: index strategy, N+1 risks, migration safety, constraint correctness.

**`chief-of-staff`** — Communication, Jira tickets, incident summaries, status updates.
Jira: PROJECT_ID 10008, ISSUETYPE_ID 10002, AREA_ID 17610.

**`senior-cloud-architect`** — Azure/K8s architecture with Mermaid diagrams and ADRs.

**`loop-operator`** — Autonomous loop execution for sequential multi-step tasks.

---

## Skills Directory

Skills are loaded on-demand (read SKILL.md before generating output):

| Skill | Domain |
|---|---|
| `kubernetes-expert` | Multi-cluster K8s, policy, GitOps, AKS/TKG ops |
| `terraform-azure` | All 28 TfModules, azurerm 4.x, remote state |
| `devops-cicd` | Azure DevOps Pipelines, GitHub Actions, Ansible |
| `shell-scripting` | Bash automation, error handling, SSH patterns |
| `infrastructure-security` | Pod Security Standards, RBAC, NetworkPolicy, Wiz |
| `helm-chart-builder` | Helm chart authoring, values schema, hooks |
| `azure-cloud-architect` | AKS design, AzureLocal, hub-spoke, UAMI |
| `observability-designer` | Prometheus, Grafana, Loki, Elastic, OTel |

---

## Active Rules (always-apply)

Loaded from `~/.claude/rules/common/`:

- **coding-style** — File organisation, naming, YAML 2-space indent, explicit `---`
- **security** — No secrets in ConfigMaps, no `:latest` tags, runAsNonRoot always
- **git-workflow** — Conventional Commits, no force-push, PR required for main
- **testing** — AAA pattern, 80% coverage floor, no-tests = no-merge
- **performance** — Model routing guide, compact strategy, K8s resource efficiency
- **patterns** — Bash config/retry, K8s resource, Terraform module patterns
- **agents** — Full delegation table, how to write effective agent prompts
- **hooks** — Hook events, ECC_HOOK_PROFILE, TodoWrite integration

---

## Contexts (load as needed)

```
/dev      → BUILD mode: TDD, validation commands, security non-negotiables
/review   → REVIEW mode: structured audit report, K8s/TF/Kyverno checklists
/research → RESEARCH mode: 4-step protocol, evidence-based output
```

---

## Workspace Layout

```
~/workspace/
├── Kyverno/      # policies 01-06: security, HA, reliability, governance, mutate, exceptions
├── OPA/          # Gatekeeper ConstraintTemplates + constraints + mutations
├── ArgoCD/       # App-of-Apps bootstrap + ApplicationSets
├── Terraform/    # TfModules/ (28 modules) + Pipelines/
├── Pipelines/    # Azure DevOps YAML pipelines
├── Ansible/      # Commvault, OpenShift automation
├── Operator/     # Custom K8s operators / CronJobs
├── Shell/        # Bash operational scripts
├── Python/       # Job monitors, automation
├── Wiz/          # Wiz integration configs
└── AI/           # LangFuse, Ollama, RAG experiments
```

---

## Critical Kyverno CEL Gotchas

```
# Object field names: unquoted or backtick-escaped
WRONG: object{"nodeAffinity": ...}
RIGHT: object{nodeAffinity: ...}

# Label keys with dots/slashes
WRONG: labels{"app.kubernetes.io/name": "x"}
RIGHT: labels{`app.kubernetes.io/name`: "x"}

# No enumerate() — use index filter pattern
[0,1,2,3,4].filter(i, i < size(list) && condition(list[i]))

# has() only for dot access
WRONG: has(object.metadata.labels["key"])
RIGHT: "key" in object.metadata.labels

# capabilities.drop is atomic — JSONPatch only
# Cluster-scoped resources — always guard with has(request.namespace)
```

---

## Token Optimisation

| Task | Model |
|---|---|
| Simple edits, lookups | haiku (subagent default) |
| Standard coding, manifests | sonnet (session default) |
| Architecture, complex reasoning | opus (`/model opus`) |

Settings: `MAX_THINKING_TOKENS=10000`, autocompact at 50%.

---

## Hooks Active

| Event | Trigger | Action |
|---|---|---|
| `PreToolUse/Bash` | any bash command | Block if credential pattern detected |
| `PostToolUse/Write` | `*.yaml` / `*.yml` | Warn if K8s manifest, remind dry-run |
| `PostToolUse/Write` | `*.tf` | Remind `terraform fmt && validate` |
| `PostToolUse/Write` | `*.yaml` / `*.yml` | Block if `:latest` image tag found |
| `SessionStart` | session open | Display context banner |

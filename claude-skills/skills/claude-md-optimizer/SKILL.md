---
name: claude-md-optimizer
description: >
  Best practices for writing optimal CLAUDE.md project memory files. Covers structure,
  what to include and exclude, the stateless LLM principle, length constraints, and
  patterns for different project types (infra, backend, frontend). Activate when creating
  or reviewing CLAUDE.md files, or when asked about Claude Code project memory setup.
---

# CLAUDE.md Optimizer

## The Core Principle

**LLMs are stateless.** CLAUDE.md is the only file automatically included in every conversation. It is the single source of persistent project context.

This means:
- If it's not in CLAUDE.md, Claude starts every session without that knowledge
- Every byte you put in CLAUDE.md costs tokens on every single request
- The goal is maximum signal, minimum noise

---

## The Golden Rules

1. **Less is more** — target under 300 lines, hard limit 500
2. **Universal applicability** — only include information relevant to EVERY session
3. **No linting via Claude** — use deterministic tools (pre-commit, CI) for style enforcement
4. **Never auto-generate** — craft it manually with care; generated CLAUDE.md files are always bloated
5. **Update regularly** — stale context is worse than no context

---

## Essential Sections (in priority order)

```markdown
# Project Name
One-line description of what this project does.

## Tech Stack
- Language: Python 3.11
- Framework: FastAPI
- Database: PostgreSQL 15
- Infra: AKS, Terraform (azurerm 4.x)

## Development Commands
\`\`\`bash
make install    # Install dependencies
make test       # Run test suite
make lint       # Run linters
make build      # Build artifact
\`\`\`

## Critical Conventions
- Kubernetes: always set resources, probes, securityContext
- Never use :latest image tags
- Secrets in Azure Key Vault — never ConfigMaps
- Kyverno policies use CEL (policies.kyverno.io/v1)

## Known Gotchas
- `has()` only works with dot access in CEL — use `"key" in map` for map keys
- Terraform state is in Azure Storage — always `terraform init` before plan
- AKS node pool changes require node pool recreation (not in-place)

## Architecture Notes
Brief description of non-obvious design decisions only.
```

---

## What to Include

✅ Build/test/run commands that differ from standard conventions
✅ Non-obvious architectural decisions (explain WHY not WHAT)
✅ Common gotchas that would trip up a developer unfamiliar with the codebase
✅ Technology versions that matter (Python 3.11 vs 3.9 behavior differences)
✅ Key environment variables and where they come from
✅ Security constraints ("secrets go in Key Vault, never env vars in manifests")
✅ Naming conventions that are project-specific and not obvious
✅ Which branch strategy / PR flow to follow

---

## What NOT to Include

❌ Coding style rules (use a linter/formatter config file instead)
❌ Generic best practices (use your ECC rules files instead)
❌ Information that changes frequently (use a separate docs file)
❌ Large code examples (link to the file instead)
❌ Things that apply to only one type of task (put in a skill instead)
❌ Obvious conventions for the tech stack (Claude already knows React patterns)
❌ The entire README (link to it instead)

---

## Template: Infrastructure Project

```markdown
# Project: [Cluster Name] AKS Platform

## Stack
- AKS: Kubernetes 1.31, Azure CNI Overlay
- IaC: Terraform azurerm ~> 4.x, state in Azure Storage
- GitOps: ArgoCD 2.x, App-of-Apps pattern
- Policy: Kyverno CEL (policies.kyverno.io/v1)
- CI/CD: Azure DevOps YAML pipelines

## Key Commands
\`\`\`bash
cd Terraform/ && terraform init && terraform plan
kubectl apply --dry-run=server -f Kyverno/
bash ArgoCD/bootstrap.sh
\`\`\`

## Critical Rules
- Never use :latest image tags — Kyverno enforces this
- Kyverno: use CEL policies, NOT JMESPath (legacy)
- Secrets: Azure Key Vault or Sealed Secrets — never ConfigMaps
- All manifests: must pass kubectl --dry-run=client before commit
- Terraform: remote state in Azure Storage, never local

## Kyverno CEL Gotchas
- `has()` only works with dot access, not map keys
- `capabilities.drop` is atomic list — use JSONPatch mutations
- Guard cluster-scoped resources with `has(request.namespace)`
- Label keys with dots/slashes: backtick-escape in Object{} construction

## Architecture
- AKS: hub-spoke networking, private cluster
- UAMI for workload identity (no service principal secrets in code)
- Kyverno backgroundScan: enabled; failureAction: Audit (dev) / Enforce (prod)
```

---

## Template: Backend Service

```markdown
# Project: [Service Name]

## Stack
- Go 1.22, Gin framework
- PostgreSQL 15, sqlx
- Redis 7 (caching)
- Deployed on AKS via Helm

## Commands
\`\`\`bash
make run        # Run locally with hot-reload
make test       # go test -race ./...
make migrate    # Run DB migrations (golang-migrate)
make docker     # Build Docker image
\`\`\`

## Conventions
- Errors: wrap with fmt.Errorf("action: %w", err) — never bare return err
- DB: always use parameterized queries — no string concatenation
- Config: all from environment via envconfig struct, never process.env inline
- Tests: table-driven, -race flag required in CI

## Key Gotchas
- Redis connection pool size: set REDIS_POOL_SIZE=20 locally
- Migration files: numbered sequentially, never edit after merge
- Integration tests need POSTGRES_DSN env var — see .env.test.example
```

---

## Template: Python Automation/Scripting

```markdown
# Project: [Name]

## Stack
- Python 3.11+, uv for package management
- Dependencies in pyproject.toml

## Commands
\`\`\`bash
uv sync                  # Install dependencies
uv run pytest            # Run tests
uv run ruff check .      # Lint
uv run mypy src/         # Type check
\`\`\`

## Conventions
- Type hints required on all public functions
- No bare except: — always catch specific exceptions
- No global mutable state — pass config as function args
- Scripts: set -euo pipefail equivalent via explicit error handling

## Environment
- ANTHROPIC_API_KEY: from Azure Key Vault via infra team
- See .env.example for all required variables
```

---

## Skill vs CLAUDE.md Decision

| Context | Put in CLAUDE.md | Put in a Skill |
|---|---|---|
| Applies to every session in this project | ✅ | ❌ |
| Applies to a specific type of task | ❌ | ✅ |
| Needed by the whole team | ✅ | ✅ (project skill) |
| Personal workflow preference | ❌ | ✅ (user skill) |
| Non-obvious project gotcha | ✅ | ❌ |
| Reusable across multiple projects | ❌ | ✅ |

---

## Reviewing an Existing CLAUDE.md

When reviewing, ask for each line:
1. Is this relevant to **every** session, or only specific tasks?
2. Would Claude already know this without being told?
3. Does this change frequently? (If yes, link to a file instead)
4. Is this better enforced by a linter/formatter than by LLM instruction?
5. Is this a security constraint? (If yes, keep it — critical context)

Remove anything that fails test 1 or passes tests 2/4.

---

## Length Guidelines

| Project Size | Target | Max |
|---|---|---|
| Single service / script | 50–100 lines | 200 lines |
| Medium project | 100–200 lines | 300 lines |
| Large platform / monorepo | 200–300 lines | 500 lines |

If you're over the max: move tech-stack details to README, move task-specific instructions to skills, move conventions to linter configs.

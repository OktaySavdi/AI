# Claude Code ECC Harness — Setup & Reference

> **Everything Claude Code (ECC)** is an agent harness performance system for Claude Code.
> This is a fully configured, IT infrastructure–specialized implementation combining the
> ECC v1.10.0 framework with a bespoke DevOps/Kubernetes/Azure stack.

---

## What Is This?

By default, Claude Code is a capable AI assistant. With the ECC harness, it becomes a
**structured multi-agent system** with:

- **45+ specialised subagents & slash commands** — fast entry points for every workflow
- **71 skills** — domain knowledge loaded on demand (languages, frameworks, cloud, security, content)
- **Hooks** — automated guardrails that fire on tool events (block secrets, warn on `:latest` tags)
- **Rules** — always-apply guidelines covering 5 languages (Python, Go, TypeScript, Swift, PHP)
- **Contexts** — mode-switching that changes Claude's behaviour for build, review, or incident work
- **Scripts** — Node.js session/hook lifecycle scripts for state management
- **Examples** — ready-made CLAUDE.md templates for common project types
- **Dashboard** — `ecc_dashboard.py` Tkinter GUI for harness status at a glance
- **Token optimisation** — settings that reduce cost by ~70% without sacrificing quality

---

## Directory Structure

```
~/.claude/
├── AGENTS.md              ← Universal cross-tool reference (Cursor/Codex/OpenCode)
├── CLAUDE.md              ← Your IT infrastructure profile (loaded at every session)
├── settings.json          ← Token optimisation + model settings
│
├── agents/                ← 40+ specialised subagents
│   ├── planner.md         ← Feature implementation blueprints
│   ├── architect.md       ← System design + ADRs (opus model)
│   ├── k8s-reviewer.md    ← Kubernetes manifest review
│   ├── policy-engineer.md ← Kyverno CEL + OPA policies
│   ├── terraform-engineer.md ← Azure IaC (28 TfModules)
│   ├── security-reviewer.md  ← Infrastructure security audit
│   ├── incident-responder.md ← Live incident triage
│   └── ... (33+ more)
│
├── commands/              ← 45 slash command entry points
│   ├── plan.md            ← /plan
│   ├── tdd.md             ← /tdd
│   ├── k8s-review.md      ← /k8s-review
│   ├── learn-eval.md      ← /learn-eval  (pattern extraction)
│   ├── instinct-status.md ← /instinct-status
│   ├── multi-plan.md      ← /multi-plan  (multi-agent decomposition)
│   └── ... (39 more)
│
├── skills/                ← 71 domain knowledge modules (loaded on demand)
│   ├── kubernetes-expert/ ← Multi-cluster K8s, Kyverno CEL, ArgoCD
│   ├── terraform-azure/   ← All 28 TfModules, azurerm 4.x
│   ├── devops-cicd/       ← Azure DevOps Pipelines, Ansible
│   ├── shell-scripting/   ← Bash patterns, SSH, error handling
│   ├── infrastructure-security/ ← Pod Security, Wiz, secrets
│   ├── golang-patterns/   ← Go idioms, goroutines, error handling
│   ├── python-patterns/   ← Dataclasses, type hints, generators
│   ├── django-patterns/   ← DRF, service layer, ORM
│   ├── springboot-patterns/ ← Spring Boot 3.x, JPA, security
│   ├── laravel-patterns/  ← Eloquent, policies, Pest tests
│   ├── swift-concurrency-6-2/ ← Swift 6.2 async/await, actors
│   ├── liquid-glass-design/   ← iOS 26 glassmorphism
│   ├── security-scan/     ← OWASP scanning pipeline
│   ├── videodb/           ← Video/audio ingest and search
│   └── ... (57 more)
│
├── rules/                 ← Always-apply guidelines
│   ├── README.md
│   ├── common/            ← 8 universal rules files
│   │   ├── coding-style.md
│   │   ├── security.md
│   │   ├── git-workflow.md
│   │   ├── testing.md
│   │   ├── performance.md
│   │   ├── patterns.md
│   │   ├── agents.md
│   │   └── hooks.md
│   ├── python/            ← Python-specific rules
│   ├── golang/            ← Go-specific rules
│   ├── typescript/        ← TypeScript-specific rules
│   ├── swift/             ← Swift 5.10+ / Swift 6 rules
│   └── php/               ← PHP 8.2+ / PSR-12 rules
│
├── contexts/              ← Mode-switching system prompts
│   ├── dev.md             ← BUILD mode: TDD, validation commands
│   ├── review.md          ← REVIEW mode: audit checklists
│   ├── research.md        ← RESEARCH mode: evidence-based output
│   └── ops.md             ← OPS mode: incident response runbook
│
├── hooks/
│   ├── hooks.json          ← Hook configuration (8 hooks: PreToolUse, PostToolUse, Stop, PreCompact)
│   ├── README.md           ← Hook authoring guide
│   ├── memory-persistence/ ← Session lifecycle hooks (longform guide + install.sh)
│   ├── strategic-compact/  ← Compaction suggestion hooks (longform guide + install.sh)
│   └── scripts/
│       ├── secret-detector.sh      ← Blocks bash commands with credentials
│       ├── k8s-dryrun-reminder.sh  ← Reminds kubectl dry-run after YAML edits
│       ├── latest-tag-check.sh     ← Blocks :latest image tags in YAML
│       ├── terraform-fmt-reminder.sh ← Reminds terraform fmt after .tf edits
│       └── session-start.sh        ← Displays context banner on session open
│
├── scripts/               ← Node.js lifecycle scripts
│   ├── lib/
│   │   ├── utils.js        ← Cross-platform utilities
│   │   └── package-manager.js ← Package manager detection
│   ├── hooks/
│   │   ├── session-start.js   ← Load context on session start
│   │   ├── session-end.js     ← Save state on session end
│   │   ├── pre-compact.js     ← Pre-compaction state saving
│   │   ├── suggest-compact.js ← Strategic compaction suggestions
│   │   └── evaluate-session.js ← Pattern extraction trigger
│   └── setup-package-manager.js
│
├── examples/              ← Ready-made CLAUDE.md templates
│   ├── CLAUDE.md                   ← Generic project template
│   ├── user-CLAUDE.md              ← User-level profile template
│   ├── saas-nextjs-CLAUDE.md       ← Next.js + Supabase + Stripe
│   ├── go-microservice-CLAUDE.md   ← Go microservice
│   ├── django-api-CLAUDE.md        ← Django REST API
│   ├── laravel-api-CLAUDE.md       ← Laravel API
│   └── rust-api-CLAUDE.md          ← Rust / Axum API
│
├── mcp-configs/
│   └── mcp-servers.json   ← GitHub, Supabase, Vercel, Railway MCP config
│
├── .claude-plugin/
│   ├── plugin.json        ← Plugin metadata
│   └── marketplace.json   ← Marketplace catalog entry
│
├── tests/
│   └── run-all.js         ← Structure verification test suite
│
└── ecc_dashboard.py       ← Tkinter desktop GUI (skills/commands/instincts)
```

---

## Setup

### Prerequisites

- Claude Code CLI v2.1.0 or later
- macOS or Linux
- The `~/.claude/` directory structure already populated (if reading this, it is)

### Verify Installation

```bash
# Check all directories exist
ls ~/.claude/agents/ | wc -l      # 40+
ls ~/.claude/commands/ | wc -l    # 45
ls ~/.claude/skills/ | wc -l      # 71
ls ~/.claude/rules/               # common/ python/ golang/ typescript/ swift/ php/ README.md

# Verify hooks are executable
ls -la ~/.claude/hooks/scripts/

# Make scripts executable (run once if needed)
chmod +x ~/.claude/hooks/scripts/*.sh
```

### Verify settings.json

```bash
cat ~/.claude/settings.json
```

Should contain:
```json
{
  "model": "sonnet",
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  }
}
```

---

## How It Works

### 1. Skills — Primary Workflow Surface

Skills are domain knowledge modules. When a skill is relevant to your task,
Claude reads `~/.claude/skills/<name>/SKILL.md` before responding, giving it
accurate, tested patterns for that domain.

**Example:** Working on a Kyverno policy → `kubernetes-expert` skill is loaded
→ Claude gets the full CEL gotchas, valid API patterns, and policy structure
before writing a single line.

Skills cover: infrastructure (K8s, Terraform, ArgoCD, shell), languages (Go, Python,
TypeScript, Swift, PHP, Rust, Java, Kotlin, C++, Perl), frameworks (Django, Spring Boot,
Laravel, Next.js), databases (PostgreSQL, ClickHouse), cloud (Azure), mobile (SwiftUI,
Liquid Glass, Foundation Models), business (market research, investor materials,
content engine), and AI/ML (VideoDB, cost-aware LLM pipelines, eval harnesses).

Skills activate automatically based on context, or you can load them explicitly:
> "Load the kubernetes-expert skill and review this policy..."

### 2. Agents — Specialised Delegation

Agents are subagents with a focused scope. They get fresh context when invoked,
preventing the main session's history from polluting their judgement.

**When to use agents:**
- Complex tasks that benefit from specialist focus
- Reviews (reviewers should be objective, not attached to the code)
- Parallel tasks that can run independently

**Example delegation:**
```
User: "Review this Terraform module for security issues"
Claude: invokes security-reviewer agent with the file path and context
Agent: returns structured CRITICAL/HIGH/MEDIUM/LOW security report
```

See the full delegation table in [AGENTS.md](./AGENTS.md).

### 3. Commands — Slash Entry Points

Commands are quick-start workflows. Type `/` followed by a command name in Claude Code.

```
/plan "Add OAuth login"         → invokes planner agent
/k8s-review                     → invokes k8s-reviewer agent
/security-audit                 → invokes security-reviewer agent
/tdd "validate namespace names" → starts RED-GREEN-REFACTOR cycle
/build-fix                      → invokes build-error-resolver agent
```

### 4. Hooks — Automated Guardrails

Hooks fire automatically on tool events — no user action required. No plugin installation needed;
Claude Code reads `hooks.json` natively.

| Hook | Event | Action |
|---|---|---|
| `secret-detector` | PreToolUse (Bash) | Blocks if credential patterns found |
| `latest-tag-check` | PostToolUse (Write YAML) | Blocks if `:latest` image tag found |
| `k8s-dryrun-reminder` | PostToolUse (Write YAML) | Reminds to run kubectl dry-run |
| `terraform-fmt-reminder` | PostToolUse (Write .tf) | Reminds to run terraform fmt |
| `suggest-compact` | PostToolUse | Suggests `/compact` when context ≥ 50% |
| `session-start` | SessionStart | Displays context banner + pending instinct count |
| `session-end` | Stop | Persists session record to history |
| `pre-compact` | PreCompact | Snapshots state before compaction |

### Hook Guide Directories

| Directory | Purpose |
|---|---|
| `hooks/memory-persistence/` | Session lifecycle guide — how state is saved across sessions |
| `hooks/strategic-compact/` | Compaction timing guide — optimal `/compact` decision points |

Run the install scripts to verify wiring:

```bash
bash ~/.claude/hooks/memory-persistence/install.sh
bash ~/.claude/hooks/strategic-compact/install.sh
```

### 5. Rules — Always-Apply Guidelines

Rules in `~/.claude/rules/common/` are loaded at every session. They define:
- Coding style (naming, file organisation, YAML formatting)
- Security requirements (no secrets in ConfigMap, no `:latest`, always securityContext)
- Git workflow (Conventional Commits, branch strategy, PR process)
- Testing standards (80% coverage, AAA pattern, no-tests = no-merge)

### 6. Contexts — Mode Switching

Contexts change Claude's entire posture for a session type.

```
/dev      → BUILD mode: TDD defaults, validation commands, security non-negotiables
/review   → REVIEW mode: structured audit report, full K8s/TF/Kyverno checklists
/research → RESEARCH mode: 4-step protocol, evidence-based output
/ops      → OPS mode: incident triage runbook, P1-P4 classification
```

---

## Common Workflows

### Starting a New Feature

```
/plan "Add Kyverno policy to block privileged containers"
↓ planner creates implementation blueprint with tasks
/tdd "validate container securityContext in CEL"
↓ tdd-guide writes failing test first
... implement ...
/k8s-review
↓ k8s-reviewer validates the final manifest
/security-audit
↓ security-reviewer checks for gaps
```

### Reviewing Infrastructure

```
/review
↓ activates REVIEW mode with full K8s/Terraform/Kyverno checklists
/k8s-review
↓ structured manifest review: BLOCKER / MAJOR / MINOR / NIT
/tf-review
↓ Terraform review using azurerm 4.x patterns + TfModules conventions
```

### Incident Response

```
/ops
↓ activates OPS mode with live-system debugging posture
"pods are crashlooping in production namespace"
↓ incident-responder guides systematic triage
```

### Building Terraform

```
/tf-review
↓ terraform-engineer reviews existing code against TfModules conventions
"Create an AKS cluster using the AKS AzModule"
↓ terraform-engineer uses all 28 TfModules conventions
```

### Kyverno Policy Work

```
/kyverno-policy "block containers without resource limits"
↓ policy-engineer creates valid CEL policy with all gotchas handled
↓ includes validate + mutate + PolicyException structure
```

---

## Agent Quick Reference

### IT Infrastructure Agents

| Agent | Trigger | What It Does |
|---|---|---|
| `k8s-reviewer` | Kubernetes manifest review | Production readiness check |
| `security-reviewer` | Security audit | OWASP Top 10 + CIS K8s Benchmark |
| `policy-engineer` | Kyverno / OPA work | CEL policies, mutations, exceptions |
| `terraform-engineer` | Azure IaC | All 28 TfModules, azurerm 4.x |
| `pipeline-builder` | ADO pipelines | YAML pipelines, approval gates |
| `incident-responder` | Something is broken | P1-P4 triage runbook |
| `argocd-operator` | GitOps / ArgoCD | App-of-Apps, ApplicationSets |
| `helm-packager` | Helm charts | Chart authoring, values schema |
| `observability-designer` | Monitoring / alerts | Prometheus, Grafana, Loki |

### General Engineering Agents

| Agent | Trigger | What It Does |
|---|---|---|
| `planner` | New non-trivial work | Implementation blueprint |
| `architect` | Architecture decision | ADRs, C4 diagrams, trade-offs |
| `tdd-guide` | Write tests first | RED-GREEN-REFACTOR |
| `code-reviewer` | Code quality check | Structured review report |
| `build-error-resolver` | Build/test failing | Error diagnosis and fix |
| `refactor-cleaner` | Dead code removal | Safe cleanup, no behaviour change |
| `doc-updater` | Docs out of date | Sync documentation with code |
| `python-reviewer` | Python code review | Type hints, idioms, security |
| `go-reviewer` | Go code review | Error handling, goroutines |
| `typescript-reviewer` | TS/JS code review | Type safety, React patterns |
| `java-reviewer` | Java code review | Spring Boot, JPA, security |
| `kotlin-reviewer` | Kotlin code review | Coroutines, Android, KMP |
| `rust-reviewer` | Rust code review | Ownership, lifetimes, async |
| `cpp-reviewer` | C++ code review | Modern C++17/20, memory safety |
| `database-reviewer` | DB/SQL review | Schema, indexes, migrations |
| `chief-of-staff` | Communication / Jira | Status updates, tickets |
| `senior-cloud-architect` | Cloud architecture | Azure/K8s NFR frameworks |
| `loop-operator` | Iterative tasks | Autonomous loop execution |
| `harness-optimizer` | ECC config issues | Audit harness configuration |
| `e2e-runner` | E2E tests | Playwright Page Object Model |
| `docs-lookup` | Unknown API/library | Documentation verification |

---

## Token Optimisation

The settings in `~/.claude/settings.json` reduce costs by ~70%:

| Setting | Default | Configured | Impact |
|---|---|---|---|
| `model` | opus | sonnet | ~60% cost reduction |
| `MAX_THINKING_TOKENS` | 31,999 | 10,000 | ~70% thinking cost reduction |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 95% | 50% | Better quality in long sessions |
| `CLAUDE_CODE_SUBAGENT_MODEL` | sonnet | haiku | Cheap fast subagents |

### When to Switch Models

```
/model opus    → deep architecture, complex debugging, strategic decisions
/model sonnet  → default for coding, manifests, scripts
/model haiku   → simple lookups, formatting, quick edits
```

### Context Management

```
/cost          → check current token spending
/clear         → free instant reset between unrelated tasks
/compact       → summarise context at logical breakpoints
```

**When to compact:**
- After research, before implementation
- After completing a milestone
- After debugging, before new feature work

**Never compact:**
- Mid-implementation (you'll lose variable names and partial state)

---

## Key Technical Context

### Kyverno CEL Gotchas

Critical patterns that must be followed for Kyverno CEL policies:

```
# Object field names: unquoted or backtick-escaped
WRONG: object{"nodeAffinity": ...}
RIGHT: object{nodeAffinity: ...}

# Label keys with dots/slashes
WRONG: labels{"app.kubernetes.io/name": "x"}
RIGHT: labels{`app.kubernetes.io/name`: "x"}

# No enumerate() — use index filter
[0,1,2,3,4].filter(i, i < size(list) && condition(list[i]))

# has() only for dot access
WRONG: has(object.metadata.labels["key"])
RIGHT: "key" in object.metadata.labels

# capabilities.drop is atomic — JSONPatch only
# Cluster-scoped resources — guard with has(request.namespace)
```

### Workspace Layout

```
~/workspace/
├── Kyverno/      # policies 01-security → 06-exceptions
├── OPA/          # Gatekeeper ConstraintTemplates + constraints
├── ArgoCD/       # App-of-Apps bootstrap + ApplicationSets
├── Terraform/    # TfModules/ (28) + Pipelines/
├── Pipelines/    # Azure DevOps YAML pipelines
├── Ansible/      # Commvault, OpenShift automation
├── Operator/     # Custom K8s operators / CronJobs
├── Shell/        # Bash operational scripts
├── Python/       # Job monitors, automation
└── Wiz/          # Wiz integration configs
```

### TKG Cluster SSH

## Dashboard

Launch the Tkinter desktop GUI to see harness status at a glance:

```bash
python3 ~/.claude/ecc_dashboard.py
```

Shows: skill count, command count, rule file count, and any pending instincts from `/learn-eval`.

---

## MCP Server Configuration

Copy `~/.claude/mcp-configs/mcp-servers.json` entries into your Claude Code MCP config
and set the corresponding environment variables:

| Server | Env Var |
|---|---|
| GitHub | `GITHUB_TOKEN` |
| Supabase | `SUPABASE_ACCESS_TOKEN` |
| Vercel | `VERCEL_TOKEN` |
| Railway | `RAILWAY_TOKEN` |

---

## TKG Cluster SSH

```bash
# Staging (direct)
ssh root@<TKG_STAGING_IP>

# Production (via jump host)
ssh <JUMP_USER>@<JUMP_HOST_IP>
# then:
ssh root@<TKG_PROD_IP>
```

---

## Hook Configuration

Hooks fire automatically. To tune behaviour:

```bash
# Hook strictness profiles
export ECC_HOOK_PROFILE=minimal   # fewer checks, faster
export ECC_HOOK_PROFILE=standard  # default
export ECC_HOOK_PROFILE=strict    # all checks enabled

# Disable specific hooks
export ECC_DISABLED_HOOKS="post:write:k8s-dryrun"
```

---

## Troubleshooting

### Hooks not firing

```bash
# Check scripts are executable
ls -la ~/.claude/hooks/scripts/

# Fix permissions
chmod +x ~/.claude/hooks/scripts/*.sh

# Validate hooks.json is valid JSON
python3 -m json.tool ~/.claude/hooks/hooks.json
```

### Agents not available

```bash
# Check agents directory
ls ~/.claude/agents/

# Verify frontmatter in an agent file
head -10 ~/.claude/agents/k8s-reviewer.md
# Should show:
# ---
# name: k8s-reviewer
# description: ...
# tools: [...]
# model: sonnet
# ---
```

### Skills not loading

Skills are loaded by reading `SKILL.md` before responding. If a skill seems inactive:

1. Verify the SKILL.md exists: `ls ~/.claude/skills/<name>/SKILL.md`
2. Explicitly reference it: "Load the kubernetes-expert skill and then..."

### Context not switching

Contexts are not automatically loaded — they must be activated with the `/` command
(e.g., `/dev`, `/review`). They inject additional system prompt content for that session.

### Run Harness Audit

```
/harness-audit
```

Checks all agents, skills, commands, hooks, rules, and settings for completeness.

---

## Benefits Summary

| Without ECC | With ECC |
|---|---|
| Generic responses | Domain-expert responses tuned to IT infrastructure |
| No guardrails | Automated hooks block secrets, `:latest` tags, missing dry-runs |
| High token costs | ~70% cost reduction via model routing and compact strategy |
| Manual context loading | Skills auto-loaded based on task context |
| Single Claude instance | 36 specialist agents, each with focused scope |
| Reactive coding | Structured TDD, review, and incident workflows |
| Forgotten patterns | Rules always applied, Kyverno CEL gotchas always remembered |

---

## Cross-Tool Compatibility

The `AGENTS.md` at `~/.claude/AGENTS.md` is read natively by:

- **Claude Code** — primary tool
- **Cursor** — AGENTS.md at root is auto-detected
- **Codex** — AGENTS.md loaded automatically
- **OpenCode** — compatible via AGENTS.md

All agents, skills, and command structures work across these tools.

---

## Maintenance

### Adding a New Agent

Create `~/.claude/agents/<name>.md` with YAML frontmatter:

```markdown
---
name: my-agent
description: One-sentence description for delegation matching.
tools: ["Read", "Write", "Bash", "Grep"]
model: sonnet
---

# My Agent

Agent instructions here...
```

### Adding a New Skill

Create `~/.claude/skills/<name>/SKILL.md`:

```markdown
---
name: "my-skill"
description: >
  When this skill activates and what it provides.
metadata:
  version: 1.0.0
---

# My Skill

## When This Skill Activates
...

## Patterns
...
```

### Adding a New Command

Create `~/.claude/commands/<name>.md` with usage documentation.

### Updating Rules

Edit the relevant file in `~/.claude/rules/common/` or the language-specific directory.
Rules take effect immediately in the next session.

---

*Built on [Everything Claude Code](https://github.com/affaan-m/everything-claude-code) v1.10.0 — customised for IT Infrastructure / DevOps / Azure.*

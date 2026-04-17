# Agent Delegation Rules

## When to Delegate to a Subagent

Delegate when the task:
1. Requires deep specialised knowledge (Kyverno CEL, Terraform modules, etc.)
2. Is a complete, self-contained unit of work
3. Needs a fresh context without the current session's history
4. Is a review task (reviewers should be objective, not attached to the code)

## Agent Roster and Triggers

| Trigger | Agent to Invoke |
|---------|----------------|
| "plan this feature" / new non-trivial work | `planner` |
| "design this system" / architecture question | `architect` or `senior-cloud-architect` |
| "review this code" / PR review | `code-reviewer` |
| "write tests" / TDD workflow | `tdd-guide` |
| Build / test / lint is failing | `build-error-resolver` |
| "remove dead code" / cleanup | `refactor-cleaner` |
| "update the docs" | `doc-updater` |
| Python code review | `python-reviewer` |
| Go code review | `go-reviewer` |
| Database query review | `database-reviewer` |
| Kubernetes manifest review | `k8s-reviewer` |
| Security audit of anything | `security-reviewer` |
| Kyverno / OPA policy | `policy-engineer` |
| Terraform / Azure IaC | `terraform-engineer` |
| Azure DevOps pipeline | `pipeline-builder` |
| ArgoCD / GitOps | `argocd-operator` |
| Helm chart | `helm-packager` |
| Monitoring / alerting | `observability-designer` |
| Incident / something is broken | `incident-responder` |
| Email / Jira / status update | `chief-of-staff` |
| Loop / repeated iteration task | `loop-operator` |

## How to Delegate Effectively

### Give Context
When invoking a subagent, provide:
1. **What** needs to be done (specific, not vague)
2. **Where** — file paths, namespaces, cluster names
3. **Constraints** — must not break X, must use pattern Y
4. **Success criteria** — how will we know it's done?

### Bad Delegation
> "Review this and fix it"

### Good Delegation
> "Review `Kyverno/01-security.yaml` for CEL syntax errors. The policy should
> enforce `runAsNonRoot: true` for all pods in namespaces not starting with
> `kube-`. It must use `has(request.namespace)` guard for cluster-scoped resources."

## Parallel Delegation
Independent tasks can be delegated simultaneously:
- Review manifests AND update docs → delegate both at once
- Security review AND test generation → parallel

Sequential tasks (where output of one feeds the other) must be done in order:
- Plan → then implement → then review

## Context Problem
Subagents get a fresh context. They cannot see the current conversation.
Provide all relevant context inline when delegating — don't assume they know
what you've been discussing.

## Result Handling
After a subagent returns:
1. Read the result fully before acting
2. If the result has blocking issues, fix them before proceeding
3. Incorporate the agent's output into your plan
4. Report the combined result back to the user

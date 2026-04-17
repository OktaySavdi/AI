# /multi-workflow — General Multi-Service Orchestration

General-purpose multi-agent workflow for tasks spanning multiple services, repos,
or domains that don't fit the backend or frontend-specific orchestrators.

## Usage

```
/multi-workflow "Implement OAuth login across API, frontend, and mobile"
/multi-workflow "Deploy new AKS cluster with all policies and observability"
```

## What It Does

1. Analyses the task to identify involved services/domains
2. Maps each component to the best available agent
3. Determines parallelism opportunities
4. Executes with progress reporting

## Related Commands

- `/multi-plan` — see the plan before executing
- `/multi-backend` — backend-focused variant
- `/multi-frontend` — frontend-focused variant
- `/orchestrate` — simpler single-step orchestration

# /multi-plan — Multi-Agent Task Decomposition

Decomposes a complex task into parallel and sequential sub-tasks, assigning each
to the best-fit agent. Produces an execution plan before any work begins.

## Usage

```
/multi-plan "Build a REST API with tests and documentation"
/multi-plan "Migrate AKS cluster to new node pool configuration"
```

## Output Format

```
Task: Build REST API with tests and documentation
Decomposed into 4 sub-tasks:

[SEQUENTIAL]
1. planner → "Design API endpoint structure and data models"
2. architect → "Review design and produce ADR for tech decisions"

[PARALLEL after step 2]
3a. tdd-guide → "Write tests for all endpoints (RED phase)"
3b. doc-updater → "Draft OpenAPI spec from design"

[SEQUENTIAL]
4. code-reviewer → "Review implementation after GREEN phase"

Estimated token cost: ~45k tokens
Run /multi-execute to proceed.
```

## Related Commands

- `/multi-execute` — execute the generated plan
- `/orchestrate` — simpler single-orchestrator coordination

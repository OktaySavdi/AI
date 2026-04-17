# /multi-execute — Orchestrated Multi-Agent Workflow Execution

Executes a plan produced by `/multi-plan`, running agents in parallel or sequentially
as specified. Provides a progress dashboard and result aggregation.

## Usage

```
/multi-execute          ← executes last /multi-plan output
/multi-execute plan.md  ← executes a saved plan file
```

## Execution Behaviour

- Parallel tasks are launched simultaneously as subagents
- Sequential tasks wait for all parallel predecessors to complete
- Each agent gets full context from preceding agents' outputs
- Failures in any agent pause execution and report the blocking error
- Results are aggregated and presented as a unified report

## Related Commands

- `/multi-plan` — decompose a task before executing
- `/loop-start` — iterative loop-based execution
- `/orchestrate` — simpler coordination for smaller tasks

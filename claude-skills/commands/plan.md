# Plan

Invoke the `planner` agent to create a feature implementation blueprint.

## Usage

```
/plan "description of feature or task"
```

## What it does

The planner agent produces:
1. **Scope** — what is in/out of scope
2. **Acceptance criteria** — testable conditions for done
3. **Sub-tasks** — ordered implementation steps
4. **Risk flags** — blockers, unknowns, security concerns
5. **Agent delegation** — which specialised agent handles each sub-task

## Example

```
/plan "Add Kyverno policy to block privileged containers in production namespaces"
```

---
name: "autonomous-loops"
description: >
  Autonomous loop patterns for multi-step agentic workflows: sequential pipelines,
  PR review loops, and DAG-style orchestration with quality gates. Activate for any
  task requiring repeated iteration until a quality criterion is met.
license: MIT
metadata:
  version: 1.0.0
  author: ECC
  category: workflow
---

# Autonomous Loops Skill

## Core Concepts

An autonomous loop runs a task repeatedly until a **quality gate** passes or a
**max iteration** limit is reached.

## Pattern 1: Sequential Pipeline

Each step must pass before the next runs.

```
implement → test → lint → security → done
     ↑_____________|  (loop back on failure)
```

Implementation:
```
1. Implement the change
2. Run tests → if FAIL, fix and go to 1
3. Run lint → if FAIL, fix and go to 2
4. Run security scan → if FAIL, fix and go to 3
5. Gate PASSED → commit
```

## Pattern 2: PR Review Loop

```
address comment → verify no regressions → check all comments resolved
      ↑_____________________________________________|
```

```
1. Read all PR review comments
2. Address one comment
3. Run tests to confirm no regression
4. Mark comment as resolved
5. Repeat until all comments resolved
6. Final review pass
```

## Pattern 3: Fix-Until-Clean

```
run checks → collect failures → fix one → run checks again
     ↑___________________________|
```

Best for:
- Zero lint errors
- All tests green
- Security findings remediated

## Safety Controls

Always set:
- `max_iterations: 10` — prevents infinite loops
- `stop_on_blocker: true` — stop if issue cannot be fixed programmatically
- Log each iteration result

## Quality Gate Definition

A good gate is:
- **Objective** — pass/fail, not subjective
- **Automated** — runs without human input
- **Fast** — < 60 seconds

Examples:
```
✅ "all pytest tests pass"
✅ "zero ruff errors"
✅ "kubectl dry-run succeeds"
❌ "code looks good" (subjective)
❌ "stakeholder approves" (human in loop)
```

## Commands

- `/loop-start "task" --gate "criteria"` — start loop
- `/loop-status` — check progress
- `/quality-gate` — manual gate check

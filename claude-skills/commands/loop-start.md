# Loop Start

Start a controlled agentic loop for iterative tasks with quality gates.

## Usage

```
/loop-start "task description" --iterations N --gate "quality criteria"
```

## Loop Types

### Sequential Pipeline
Each step depends on the previous:
```
/loop-start "implement and verify feature X"
→ implement → test → review → fix → test → ...
```

### Validation Loop
Iterate until quality gate passes:
```
/loop-start "fix all lint errors" --gate "zero lint errors"
→ fix errors → run lint → check gate → repeat if needed
```

### PR Review Loop
```
/loop-start "address all PR review comments" --gate "all comments resolved"
```

## Safety Controls

- Maximum iterations: 10 (default), configurable
- Stops on: gate passed, max iterations reached, or blocker found
- Check status: `/loop-status`

## Related

- `/loop-status` — inspect active loop progress
- `/quality-gate` — run quality gate checks without a loop

# Loop Status

Inspect the status of an active agentic loop.

## Usage

```
/loop-status
```

## Output Format

```
## Loop Status

Task: <description>
Iteration: N / max_N
Gate: <quality criteria>

### Completed Steps
- [x] Step 1: description — PASSED
- [x] Step 2: description — PASSED

### Current Step
- [ ] Step 3: description — IN PROGRESS

### Gate Check
Status: PENDING / PASSED / FAILED
Reason: <explanation if failed>

### Next Action
<what the loop will do next>
```

## Related

- `/loop-start` — start a new loop
- `/quality-gate` — run gate check manually
- `/checkpoint` — save state at current iteration

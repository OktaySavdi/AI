# Model Route

Route the current task to the optimal model based on complexity and cost.

## Usage

```
/model-route
```

Or describe the task type:
```
/model-route "deep architecture decision with many trade-offs"
/model-route "fix a typo in a string"
```

## Routing Table

| Task Type | Model | Reason |
|---|---|---|
| Simple edits, lookups, formatting | `haiku` | Fast, cheap, sufficient |
| Standard coding, YAML, scripts | `sonnet` | Best cost/quality balance |
| Deep architecture, complex debugging | `opus` | Maximum reasoning depth |
| Subagent delegation (most tasks) | `haiku` | `CLAUDE_CODE_SUBAGENT_MODEL=haiku` |

## Switch Model

```
/model haiku     # for simple tasks
/model sonnet    # default
/model opus      # for hard problems
```

## Cost Reference

- haiku ≈ 1x
- sonnet ≈ 5x
- opus ≈ 15x

Switch back to sonnet after completing opus-level work.

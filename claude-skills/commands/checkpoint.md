# Checkpoint

Save current verification state and progress to session memory.

## Usage

```
/checkpoint
```

## What it saves

- Current task and sub-task status
- Files modified in this session
- Tests passing / failing
- Blockers and open questions
- Next action

## Format

```markdown
## Checkpoint — <timestamp>

### Task
<description>

### Status
- [x] Completed sub-tasks
- [ ] Pending sub-tasks

### Files Modified
- path/to/file.yaml

### Tests
- passing: N
- failing: N (list failures)

### Blockers
- <any blockers>

### Next Action
<what to do next>
```

Use `/verify` to run validations before checkpointing.

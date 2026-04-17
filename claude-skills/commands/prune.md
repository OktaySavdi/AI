# /prune — Delete Expired Pending Instincts

Removes pending instincts that have not been promoted or confirmed within their
expiry window (default: 14 days). Prevents accumulation of low-quality patterns.

## Usage

```
/prune
/prune --dry-run
/prune --older-than 7d
/prune --all-pending
```

## Behaviour

- Shows list of instincts to be pruned before deleting
- `--dry-run` shows what would be pruned without deleting
- Saved (promoted) instincts are never pruned
- Only pending/unconfirmed instincts are eligible

## Related Commands

- `/instinct-status` — view pending instincts before pruning
- `/evolve` — promote instincts into skills before pruning

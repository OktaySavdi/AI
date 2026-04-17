# /instinct-status — View Learned Instincts

Displays all saved instincts from `~/.claude/skills/continuous-learning-v2/instincts/`.
Shows confidence scores, categories, and pending review queue.

## Usage

```
/instinct-status
/instinct-status --category kyverno
/instinct-status --pending
```

## Output Format

```
=== SAVED INSTINCTS (12) ===
[kyverno] (95) Backtick-escape CEL label keys with dots/slashes
[kyverno] (88) Guard cluster-scoped resources with has(request.namespace)
[terraform] (82) Pin azurerm provider to minor version ~> 4.x
[bash] (79) Always use set -euo pipefail + trap ERR
...

=== PENDING REVIEW (3) ===
[k8s] (62) Prefer emptyDir for writable paths with readOnlyRootFilesystem
[python] (55) Use dataclass(frozen=True) for value objects
[general] (44) Break functions > 80 lines
```

## Related Commands

- `/learn-eval` — extract and save new instincts
- `/instinct-export` — export instincts to a file
- `/instinct-import` — import instincts from a file
- `/evolve` — cluster instincts into reusable skills
- `/prune` — delete expired pending instincts

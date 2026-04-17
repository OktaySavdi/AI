# /instinct-import — Import Learned Instincts

Imports instincts from a JSON file previously exported with `/instinct-export`.
Merges with existing instincts, resolving conflicts by keeping the higher-confidence version.

## Usage

```
/instinct-import ~/instincts-backup.json
/instinct-import kyverno-instincts.json --merge
/instinct-import team-instincts.json --overwrite
```

## Conflict Resolution

- `--merge` (default): keep higher-confidence version of duplicates
- `--overwrite`: imported file wins all conflicts
- `--skip`: existing instincts always win conflicts

## Related Commands

- `/instinct-export` — export instincts to a file
- `/instinct-status` — view merged instincts

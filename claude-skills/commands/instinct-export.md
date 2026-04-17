# /instinct-export — Export Learned Instincts

Exports all saved instincts to a portable JSON file. Useful for sharing patterns
across machines or backing up learned knowledge.

## Usage

```
/instinct-export
/instinct-export --output ~/instincts-backup.json
/instinct-export --category kyverno --output kyverno-instincts.json
```

## Output File Format

```json
{
  "version": "2.0",
  "exported": "2026-04-17T10:00:00Z",
  "instincts": [
    {
      "id": "kyverno-001",
      "category": "kyverno",
      "text": "Backtick-escape CEL label keys with dots/slashes",
      "confidence": 95,
      "created": "2026-04-10T09:00:00Z"
    }
  ]
}
```

## Related Commands

- `/instinct-import` — import from exported file
- `/instinct-status` — view current instincts
- `/evolve` — evolve instincts into skills

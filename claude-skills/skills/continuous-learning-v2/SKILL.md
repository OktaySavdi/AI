---
name: "continuous-learning-v2"
description: >
  Instinct-based learning with confidence scoring. Extracts, scores, saves, and
  evolves patterns from sessions into reusable skills. Activate for /learn-eval.
metadata:
  version: 2.0.0
  category: meta
---

# Continuous Learning v2 Skill

## Confidence Score (0-100)

| Range | Action | Meaning |
|---|---|---|
| 70-100 | SAVE immediately | High confidence, clearly generalizable |
| 40-69 | PENDING review | Potentially useful, needs confirmation |
| 0-39 | DISCARD | Too specific, too vague, or uncertain |

## Instinct Schema

```json
{
  "id": "kyverno-001",
  "category": "kyverno",
  "text": "Backtick-escape CEL label keys with dots or slashes",
  "example": "labels{`app.kubernetes.io/name`: \"x\"} not labels{\"app.kubernetes.io/name\": \"x\"}",
  "confidence": 95,
  "source": "session-2026-04-10",
  "status": "saved",
  "created": "2026-04-10T09:00:00Z"
}
```

## Storage Layout

```
~/.claude/skills/continuous-learning-v2/
  instincts/
    saved/
      kyverno-001.json
      terraform-001.json
    pending/
      general-005.json
  sessions/
    2026-04-17.md
```

## Scoring Criteria

A high-confidence instinct is:
- **Specific** — has a clear example or counter-example
- **Generalizable** — applies beyond this one session
- **Actionable** — tells Claude what to DO differently
- **Verified** — was confirmed correct by the user

A low-confidence instinct is:
- Only happened once with no clear pattern
- Too obvious (already in rules)
- User-preference only (no general value)
- Contradicts existing high-confidence instinct

## Evolving into Skills

When ≥3 instincts share a theme, run `/evolve` to generate a new SKILL.md.

## Commands

- `/learn-eval` — run full extraction + scoring session
- `/instinct-status` — view all saved and pending
- `/evolve` — cluster into skills
- `/prune` — delete expired pending instincts

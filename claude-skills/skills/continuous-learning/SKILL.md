---
name: "continuous-learning"
description: >
  Legacy v1 Stop-hook pattern extraction. Extracts patterns from completed sessions
  and saves them as reusable rules. Activate when extracting session learnings.
metadata:
  version: 1.0.0
  category: meta
---

# Continuous Learning Skill (v1)

## Pattern Extraction (Stop Hook)

At the end of each session, scan for:
1. **Corrections** — places Claude was wrong and got corrected
2. **Discoveries** — new facts about the codebase or system
3. **Preferences** — user choices that should persist
4. **Patterns** — code patterns that worked or failed

## Extraction Template

```
Session: [date]
Task: [brief description]

CORRECTIONS:
- [what was wrong] → [what is correct]

DISCOVERIES:
- [new fact about the system]

PREFERENCES:
- [user prefers X over Y]

PATTERNS:
- [code pattern that worked]
- [pattern to avoid and why]
```

## Storage

Save to `~/.claude/skills/continuous-learning/instincts/YYYY-MM-DD.md`

## Activation

This skill activates automatically via the Stop hook in `hooks.json`.
Manual activation: `/learn`

## Upgrade Path

For confidence-scored instincts with pending/saved states, use
`continuous-learning-v2` skill instead.

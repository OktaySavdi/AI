# /learn-eval — Extract, Evaluate, and Save Patterns

Extracts patterns from the current session, evaluates them for quality with confidence
scoring, and saves them as instincts to `~/.claude/skills/continuous-learning-v2/`.

## Usage

```
/learn-eval
/learn-eval "focus on error handling patterns"
```

## What It Does

1. Scans the current session for repeated patterns, corrections, and insights
2. Evaluates each pattern against confidence criteria (specificity, generality, impact)
3. Assigns confidence score 0-100
4. Saves high-confidence patterns (>70) as instincts immediately
5. Queues borderline patterns (40-70) as pending instincts for review
6. Discards low-confidence patterns (<40)

## Output Format

```
Extracted 5 patterns:
✅ SAVED (85): "Always use backtick-escape for CEL label keys with dots"
✅ SAVED (78): "Guard cluster-scoped resources with has(request.namespace)"
⏳ PENDING (62): "Prefer JSONPatch over ApplyConfiguration for atomic lists"
⏳ PENDING (55): "Use filter+index instead of enumerate in CEL"
❌ SKIPPED (32): "Use single quotes in bash"
```

## Related Commands

- `/learn` — lighter extraction without evaluation
- `/instinct-status` — view all saved instincts
- `/evolve` — cluster instincts into skills
- `/prune` — delete expired pending instincts

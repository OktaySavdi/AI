# Strategic Compact — Longform Guide

The strategic compact system suggests the **optimal moment to run `/compact`**
during long sessions, preserving response quality without losing in-progress state.

## Why This Matters

Claude Code has a 200k-token context window. As it fills:
- Response quality degrades after ~80% usage
- Auto-compact at 95% loses variable names and partial state
- Running `/compact` at 50% preserves maximum usable context

## How It Works

```
Every tool call  →  suggest-compact.js checks CLAUDE_CONTEXT_USAGE_PCT
                    If >= threshold (default 50%), prints a suggestion to stderr
```

The hook is **advisory only** — it never blocks or auto-compacts.

## Setup

The `suggest-compact.js` hook is registered in `hooks.json` under `PostToolUse`.

Check it's registered:

```bash
grep -A5 "suggest-compact" ~/.claude/hooks/hooks.json
```

If missing, add this block to the `hooks` array in `hooks.json`:

```json
{
  "description": "Suggest /compact when context approaches threshold",
  "event": "PostToolUse",
  "hooks": [
    {
      "type": "command",
      "command": "node ~/.claude/scripts/hooks/suggest-compact.js"
    }
  ]
}
```

## Configuration

Set the threshold via environment variable (default: 50%):

```bash
# In ~/.claude/settings.json env block:
{
  "env": {
    "COMPACT_SUGGEST_THRESHOLD": "50"
  }
}
```

| Threshold | When to Use |
|---|---|
| `40` | Conservative — suggest early, maximum quality |
| `50` | Default — balanced |
| `70` | Aggressive — only suggest when nearly full |

## Optimal Compact Points

✅ **Good times to `/compact`:**
- After research phase, before writing code
- After completing a milestone feature
- After a debugging session, before new work
- When the suggestion appears in the terminal

❌ **Never compact:**
- Mid-implementation (loses variable names and partial state)
- When reviewing multiple related files (loses cross-file context)

## Manual Check

```bash
# See current context usage
/cost

# Run compact
/compact

# Run clear (instant, full reset — use between unrelated tasks)
/clear
```

## Related

- `~/.claude/scripts/hooks/suggest-compact.js` — the hook script
- `~/.claude/skills/strategic-compact/SKILL.md` — full skill with decision framework
- `~/.claude/settings.json` — `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE: 50`

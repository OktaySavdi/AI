---
name: "strategic-compact"
description: >
  Context management for long Claude Code sessions. Suggests optimal /compact points to
  preserve quality and avoid context window exhaustion. Activate when working on long
  multi-step tasks.
license: MIT
metadata:
  version: 1.0.0
  author: ECC
  category: performance
---

# Strategic Compact Skill

## The Problem

Claude Code has a 200k token context window. At ~95% full, it auto-compacts — but this
often happens mid-implementation, causing loss of variable names, file paths, and
partial state.

## When to Compact (`/compact`)

✅ **Compact here:**
- After research/exploration, before implementation
- After completing a milestone (feature merged, task done)
- After a debugging session, before new feature work
- After a failed approach, before trying a new one

❌ **Do NOT compact:**
- Mid-implementation (you'll lose partial state)
- Mid-refactor (you'll lose the before/after context)
- When holding multiple file diffs in mind

## When to Clear (`/clear`)

Use `/clear` (free, instant) between unrelated tasks:
- After helping with a one-off question
- Before starting a completely different project
- When context from previous task is noise

## `/cost` Monitoring

Run `/cost` periodically in long sessions:
- If > 50k tokens: consider `/compact` at next milestone
- If > 150k tokens: compact now, don't wait

## Session Quality Signals

Signs you need to compact:
- Claude starting to confuse variable names between files
- Repeated context recap in responses
- Responses feel "foggy" or miss earlier context

## Settings

Token optimization already configured in `~/.claude/settings.json`:
```json
"CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50"
```
This auto-compacts at 50% instead of 95%, preserving quality in long sessions.

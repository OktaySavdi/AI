# Memory Persistence Hooks — Longform Guide

These hooks maintain memory across Claude Code sessions by saving and loading
state automatically at session boundaries.

## How It Works

```
Session Start  →  session-start.sh reads ~/.claude/session/current.json
                  and prints context (pending instincts, active project)

Session End    →  session-end.js appends session record to history.json

Pre-Compact    →  pre-compact.js snapshots in-progress state before
                  the context is summarised
```

No plugin installation needed. Hooks fire via `hooks.json` automatically.

## Setup (already done if hooks.json is in place)

Verify the session-lifecycle hooks are registered:

```bash
grep -A5 '"SessionStart"' ~/.claude/hooks/hooks.json
grep -A5 '"Stop"' ~/.claude/hooks/hooks.json
```

## Session State Files

| File | Purpose |
|---|---|
| `~/.claude/session/current.json` | Active session metadata (start time, cwd) |
| `~/.claude/session/history.json` | Last 50 completed sessions |
| `~/.claude/session/compact-log.json` | Compaction events log |
| `~/.claude/instincts/pending.json` | Patterns awaiting review |

## Customising Session Start Banner

Edit `~/.claude/hooks/scripts/session-start.sh` to add your own context.
For example, display active Jira ticket or current git branch:

```bash
# Add to session-start.sh
BRANCH=$(git -C "$PWD" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "none")
echo "[ECC] Branch: $BRANCH"
```

## Memory Files Layout

```
~/.claude/
├── session/
│   ├── current.json    ← written at SessionStart
│   ├── history.json    ← appended at Stop
│   └── compact-log.json
└── instincts/
    └── pending.json    ← patterns from /learn-eval
```

## Triggering Manually

```bash
# Simulate session start (test the hook)
bash ~/.claude/hooks/scripts/session-start.sh

# Simulate session end (Node.js hook)
node ~/.claude/scripts/hooks/session-end.js

# Check pending instincts count
node -e "const d=require(os.homedir()+'/.claude/instincts/pending.json'); console.log(d.pending?.length || 0)"
```

## Troubleshooting

**Hook not firing?**
- Check `hooks.json` has the correct event name (`SessionStart`, `Stop`)
- Ensure script is executable: `chmod +x ~/.claude/hooks/scripts/session-start.sh`
- Claude Code 2.1+ is required for hook support

**History not growing?**
- The Stop hook requires `~/.claude/session/` directory to exist
- Run: `mkdir -p ~/.claude/session`

#!/usr/bin/env bash
# Lessons capture reminder
# Fires at Stop. Nudges Claude to persist corrections into tasks/lessons.md
# per the "Self-Improvement Loop" rule in CLAUDE.md. Non-blocking (exit 0 always) —
# this is a reminder, not a gate, since Stop hooks cannot see conversation content.

set -uo pipefail

if [[ ! -d "tasks" ]]; then
  # No tasks/ directory in this project yet — nothing to remind about.
  exit 0
fi

if [[ ! -f "tasks/lessons.md" ]]; then
  cat >&2 <<'EOF'

[Lessons Hook] tasks/lessons.md does not exist yet in this project.
If the user corrected an approach this session, capture it now:
  1. Create tasks/lessons.md (template: ~/.claude/templates/lessons.md)
  2. Add a dated entry: what was wrong, the fix, the rule going forward
EOF
fi

echo "" >&2
echo "[Lessons Hook] Reminder: if the user corrected you this turn, log it in tasks/lessons.md before ending." >&2

exit 0

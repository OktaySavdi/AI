#!/usr/bin/env bash
# memory-persistence/install.sh
# Ensures session state directories exist and hooks are wired up.
set -euo pipefail

CLAUDE_DIR="$HOME/.claude"
SESSION_DIR="$CLAUDE_DIR/session"
INSTINCTS_DIR="$CLAUDE_DIR/instincts"

echo "[memory-persistence] Creating state directories..."
mkdir -p "$SESSION_DIR"
mkdir -p "$INSTINCTS_DIR"

# Seed pending instincts file if missing
if [ ! -f "$INSTINCTS_DIR/pending.json" ]; then
  echo '{"pending":[]}' > "$INSTINCTS_DIR/pending.json"
  echo "[memory-persistence] Created instincts/pending.json"
fi

# Verify session-start hook is in hooks.json
if grep -q "session-start.sh" "$CLAUDE_DIR/hooks/hooks.json" 2>/dev/null; then
  echo "[memory-persistence] ✅ session-start hook registered"
else
  echo "[memory-persistence] ⚠️  session-start hook not found in hooks.json"
  echo "    Add the SessionStart hook block — see README.md"
fi

echo "[memory-persistence] Done."

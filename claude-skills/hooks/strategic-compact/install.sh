#!/usr/bin/env bash
# strategic-compact/install.sh
# Verifies suggest-compact hook is wired and threshold is configured.
set -euo pipefail

CLAUDE_DIR="$HOME/.claude"

echo "[strategic-compact] Checking configuration..."

# Check hooks.json
if grep -q "suggest-compact" "$CLAUDE_DIR/hooks/hooks.json" 2>/dev/null; then
  echo "[strategic-compact] ✅ suggest-compact hook registered in hooks.json"
else
  echo "[strategic-compact] ⚠️  suggest-compact hook missing from hooks.json"
  echo "    See README.md for the JSON block to add."
fi

# Check settings.json for threshold
if grep -q "COMPACT_SUGGEST_THRESHOLD\|CLAUDE_AUTOCOMPACT_PCT_OVERRIDE" "$CLAUDE_DIR/settings.json" 2>/dev/null; then
  echo "[strategic-compact] ✅ Compact threshold configured in settings.json"
else
  echo "[strategic-compact] ℹ️  No custom threshold set — using default 50%"
fi

# Check script exists
if [ -f "$CLAUDE_DIR/scripts/hooks/suggest-compact.js" ]; then
  echo "[strategic-compact] ✅ suggest-compact.js found"
else
  echo "[strategic-compact] ❌ Missing: ~/.claude/scripts/hooks/suggest-compact.js"
fi

echo "[strategic-compact] Done."

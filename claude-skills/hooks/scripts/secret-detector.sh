#!/usr/bin/env bash
# Secret pattern detector
# Scans bash commands for credential patterns before execution
# Exit 2 to block; exit 0 to allow

set -uo pipefail

TOOL_INPUT="${CLAUDE_TOOL_INPUT:-}"
COMMAND="${CLAUDE_BASH_COMMAND:-$TOOL_INPUT}"

# Patterns that indicate secrets in commands
SECRET_PATTERNS=(
  'sk-[a-zA-Z0-9]{20,}'          # OpenAI / Anthropic API keys
  'ghp_[a-zA-Z0-9]{36}'          # GitHub Personal Access Token
  'AKIA[0-9A-Z]{16}'             # AWS Access Key ID
  'eyJ[a-zA-Z0-9+/=]{50,}'      # JWT tokens
  'Bearer [a-zA-Z0-9._-]{20,}'  # Bearer auth tokens
  'password\s*=\s*["\x27][^"\x27]{4,}' # password = "value"
  'secret\s*=\s*["\x27][^"\x27]{4,}'   # secret = "value"
  'token\s*=\s*["\x27][^"\x27]{4,}'    # token = "value"
)

for pattern in "${SECRET_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qE "$pattern" 2>/dev/null; then
    echo "[SECURITY] Potential secret pattern detected in command." >&2
    echo "[SECURITY] Pattern matched: $pattern" >&2
    echo "[SECURITY] If this is a false positive, review the command carefully before proceeding." >&2
    echo "[SECURITY] Secrets should be in Azure Key Vault, K8s Secrets, or ADO Variable Groups." >&2
    exit 2
  fi
done

exit 0

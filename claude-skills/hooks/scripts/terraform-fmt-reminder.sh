#!/usr/bin/env bash
# Terraform format reminder
# After editing a .tf file, remind to run terraform fmt

set -uo pipefail

FILE_PATH="${CLAUDE_TOOL_INPUT_FILE_PATH:-${1:-}}"

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

echo "" >&2
echo "[Terraform Hook] .tf file edited: $FILE_PATH" >&2
echo "[Terraform Hook] Run before committing:" >&2
echo "  terraform fmt" >&2
echo "  terraform validate" >&2

exit 0

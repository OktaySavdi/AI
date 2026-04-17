#!/usr/bin/env bash
# Latest tag checker
# Scans edited YAML files for :latest image tags

set -uo pipefail

FILE_PATH="${CLAUDE_TOOL_INPUT_FILE_PATH:-${1:-}}"

if [[ -z "$FILE_PATH" ]] || [[ ! -f "$FILE_PATH" ]]; then
  exit 0
fi

# Only check YAML files
if ! [[ "$FILE_PATH" =~ \.(yaml|yml)$ ]]; then
  exit 0
fi

# Look for :latest image tags
if grep -qE 'image:\s+\S+:latest' "$FILE_PATH" 2>/dev/null; then
  echo "" >&2
  echo "[Policy Hook] :latest image tag detected in $FILE_PATH" >&2
  echo "[Policy Hook] Pin to a specific version or digest to comply with policy:" >&2
  grep -nE 'image:\s+\S+:latest' "$FILE_PATH" >&2
  echo "[Policy Hook] Kyverno policy will block :latest tags in production namespaces." >&2
  exit 2
fi

exit 0

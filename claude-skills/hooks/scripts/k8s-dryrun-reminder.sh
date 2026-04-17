#!/usr/bin/env bash
# K8s dry-run reminder
# After editing a YAML file, remind to validate with kubectl dry-run

set -uo pipefail

FILE_PATH="${CLAUDE_TOOL_INPUT_FILE_PATH:-${1:-}}"

# Only remind for files that look like Kubernetes manifests
if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Check if file contains Kubernetes resource markers
if [[ -f "$FILE_PATH" ]] && grep -qE '^(apiVersion|kind):\s+' "$FILE_PATH" 2>/dev/null; then
  echo "" >&2
  echo "[K8s Hook] Kubernetes manifest edited: $FILE_PATH" >&2
  echo "[K8s Hook] Remember to validate before applying:" >&2
  echo "  kubectl apply --dry-run=client -f $FILE_PATH" >&2
  echo "  kubectl apply --dry-run=server -f $FILE_PATH  # (when cluster is available)" >&2
fi

exit 0

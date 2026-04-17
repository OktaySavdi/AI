---
name: "plankton-code-quality"
description: >
  Write-time code quality enforcement with Plankton hooks. Runs quality checks
  automatically after every file write. Activate for automated quality gates.
metadata:
  version: 1.0.0
  category: meta
---

# Plankton Code Quality Skill

## What Is Plankton?

Plankton is a Claude Code hook pattern that automatically runs code quality
checks immediately after Claude writes a file — before moving to the next task.
This enforces quality at write-time rather than at commit-time.

## Hook Configuration

```json
{
  "hooks": [
    {
      "event": "PostToolUse",
      "matcher": "Write",
      "script": "~/.claude/hooks/scripts/plankton-check.sh"
    }
  ]
}
```

## plankton-check.sh

```bash
#!/usr/bin/env bash
# Run appropriate linter based on file extension
TOOL_INPUT="$1"
FILE=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('path',''))")

case "${FILE##*.}" in
  py)   ruff check "$FILE" && mypy "$FILE" ;;
  ts|tsx) npx eslint "$FILE" ;;
  go)   go vet "$FILE" ;;
  sh)   shellcheck "$FILE" ;;
  yaml|yml)
    if grep -q ":latest" "$FILE"; then
      echo "WARNING: :latest tag found in $FILE" >&2
    fi
    ;;
esac
```

## Benefits

- Errors caught immediately while context is fresh
- No need to run linter separately before committing
- Feedback loop is seconds, not minutes
- Claude can fix issues in the same turn

## Quality Checks by Language

| Language | Checks Run |
|---|---|
| Python | ruff (lint + format), mypy (types) |
| TypeScript | eslint, tsc --noEmit |
| Go | go vet, golangci-lint |
| Bash | shellcheck |
| YAML/K8s | :latest check, kubectl dry-run prompt |
| Terraform | terraform validate, tflint |

## Exit Codes

- `0` — checks passed, proceed
- `1` — warning, shown to user but not blocking
- `2` — blocking error, Claude should fix before proceeding

## Integration with verification-loop

Plankton runs per-file checks. The `verification-loop` skill runs full suite checks.
Use both: Plankton for immediate per-file feedback, verification-loop for full pipeline gates.

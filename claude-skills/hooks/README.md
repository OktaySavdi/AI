# Hooks

Shell scripts and configuration that run automatically around Claude Code tool events.

## hooks.json

The `hooks.json` file registers all hooks. Hooks fire on `PreToolUse` or `PostToolUse` events.

## Scripts

| Script | Event | Purpose |
|---|---|---|
| `secret-detector.sh` | PreToolUse (Bash) | Block commands containing secrets |
| `k8s-dryrun-reminder.sh` | PostToolUse (Write) | Remind to dry-run K8s manifests |
| `tf-fmt-reminder.sh` | PostToolUse (Write) | Remind to run `terraform fmt` |
| `latest-tag-check.sh` | PostToolUse (Write) | Warn when `:latest` tag used |

## Hook Exit Codes

| Code | Meaning |
|---|---|
| `0` | Proceed normally |
| `2` | Block the tool and show stderr message |
| Other non-zero | Show warning but proceed |

## Adding a New Hook

1. Create script in `hooks/scripts/`
2. Make executable: `chmod +x hooks/scripts/my-hook.sh`
3. Register in `hooks/hooks.json`:

```json
{
  "hooks": [
    {
      "event": "PostToolUse",
      "tool": "write_file",
      "script": "hooks/scripts/my-hook.sh"
    }
  ]
}
```

## Disabling Hooks

```bash
export ECC_DISABLED_HOOKS="post:write:k8s-dryrun-reminder"
```

Or set `ECC_HOOK_PROFILE=minimal` to reduce to essential-only hooks.

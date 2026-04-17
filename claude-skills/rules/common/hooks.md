# Hooks Rules

## What Hooks Do
Hooks are automated checks that run before or after Claude Code tool events.
They enforce quality gates without requiring explicit user instruction.

## Available Hook Events
| Event | When It Fires | Use For |
|-------|---------------|---------|
| `PreToolUse` | Before any tool runs | Block unsafe operations, warn |
| `PostToolUse` | After any tool completes | Validate, format, check |
| `Stop` | When Claude finishes a response | Session summaries, cleanup |
| `SessionStart` | At the start of each session | Load context, greet |

## Hook Behaviour
- Hooks that exit with code `0` → proceed normally
- Hooks that exit with code `2` → block the tool and show the message
- Hooks that exit with non-zero (not 2) → show warning but proceed
- Hook output to stderr is shown to the user

## Active Hooks (configured in `~/.claude/hooks/hooks.json`)
1. **Secret detector** (PreToolUse): Scans bash commands for patterns like
   `sk-`, `ghp_`, `AKIA`, connection strings before execution
2. **Dry-run reminder** (PostToolUse Write): Reminds to run
   `kubectl apply --dry-run` after editing Kubernetes manifests
3. **Terraform format** (PostToolUse Write): Reminds to run `terraform fmt`
   after editing `.tf` files

## TodoWrite Integration
Use TodoWrite to track multi-step tasks:
- Mark todo `in_progress` before starting each step
- Mark todo `completed` immediately after finishing
- Never have more than one todo `in_progress` at a time

This gives the user visibility into what Claude is doing during long tasks.

## Hook Safety Rules
- Hooks must be fast (< 2 seconds) — slow hooks block tool execution
- Hooks must not modify files without the user knowing
- Hooks must not make network calls
- Destructive hooks (exit 2 blocking) must have a clear error message explaining
  what was blocked and why

## ECC Hook Profile
The hook strictness can be tuned via environment variable:
```bash
export ECC_HOOK_PROFILE=standard   # default
export ECC_HOOK_PROFILE=minimal    # fewer checks, faster
export ECC_HOOK_PROFILE=strict     # all checks enabled
```

Disable specific hooks without editing the config:
```bash
export ECC_DISABLED_HOOKS="post:write:dry-run-reminder"
```

## Writing Custom Hooks
If adding a new hook, follow these rules:
1. Script goes in `~/.claude/hooks/scripts/`
2. Register in `~/.claude/hooks/hooks.json`
3. Test with a dry run before enabling
4. Document in this file what the hook does and when it fires

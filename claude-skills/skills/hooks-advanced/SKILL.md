---
name: hooks-advanced
description: >
  Advanced Claude Code hook patterns covering all 5 hook types (command, http, prompt,
  mcp_tool, agent), all 28 hook events, component-scoped hooks, context tracking, and
  security hardening. Activate when designing, reviewing, or debugging Claude Code hooks,
  or when asked about automating Claude Code workflows with event-driven logic.
---

# Advanced Hook Patterns

## Hook Types (v2.1.119)

| Type | When to Use |
|---|---|
| `command` | Shell script / Python — default. Fastest, most flexible |
| `http` | POST JSON to a remote webhook endpoint |
| `prompt` | LLM evaluates a prompt — only useful on `Stop`/`SubagentStop` |
| `mcp_tool` | Call a configured MCP tool directly (v2.1.118+) |
| `agent` | Spawn a subagent for multi-step verification (can use tools) |

### Agent Hook (most powerful)
```json
{
  "type": "agent",
  "prompt": "Verify the code changes follow architecture guidelines. Check design docs and compare.",
  "timeout": 120
}
```
Unlike `prompt` hooks (single-turn), agent hooks can use `Read`, `Grep`, `Bash` to perform multi-step verification.

### MCP Tool Hook (v2.1.118+)
```json
{
  "matcher": "Edit",
  "hooks": [{ "type": "mcp_tool", "server": "my-mcp-server", "tool": "validate_edit" }]
}
```

### Prompt Hook (Stop/SubagentStop only)
```json
{
  "type": "prompt",
  "prompt": "Evaluate if Claude completed all requested tasks. Check: 1) Were all files created? 2) Any unresolved errors?",
  "timeout": 30
}
```

---

## All 28 Hook Events

| Event | Blockable | Primary Use |
|---|---|---|
| `SessionStart` | No | Setup env vars, load context |
| `InstructionsLoaded` | No | Modify/filter CLAUDE.md |
| `UserPromptSubmit` | Yes | Validate/transform prompts |
| `UserPromptExpansion` | Yes | Inspect expanded @ mentions |
| `PreToolUse` | Yes | Validate/modify tool inputs |
| `PermissionRequest` | Yes | Auto-approve/deny |
| `PermissionDenied` | No | Logging |
| `PostToolUse` | No | Add context, trigger checks |
| `PostToolUseFailure` | No | Error handling |
| `PostToolBatch` | No | Aggregate reporting |
| `Notification` | No | Custom notifications |
| `SubagentStart` | No | Per-subagent setup |
| `SubagentStop` | Yes | Validate subagent output |
| `Stop` | Yes | Task completion check |
| `StopFailure` | No | Error recovery |
| `TeammateIdle` | Yes | Team coordination |
| `TaskCompleted` | Yes | Post-task validation |
| `TaskCreated` | No | Task tracking |
| `ConfigChange` | Yes | React to config updates |
| `CwdChanged` | No | Directory-specific setup |
| `FileChanged` | No | File monitoring, rebuild |
| `PreCompact` | No | Pre-compaction actions |
| `PostCompact` | No | Post-compaction actions |
| `WorktreeCreate` | Yes | Worktree initialization |
| `WorktreeRemove` | No | Worktree cleanup |
| `Elicitation` | Yes | MCP user input validation |
| `ElicitationResult` | Yes | Response processing |
| `SessionEnd` | No | Cleanup, final logging |

`SessionStart` matchers: `startup` / `resume` / `clear` / `compact`

---

## Configuration Scopes

```
~/.claude/settings.json          ← User (all projects)
.claude/settings.json            ← Project (committed)
.claude/settings.local.json      ← Project local (not committed)
Managed policy                   ← Org-wide (cannot override)
<plugin>/hooks/hooks.json        ← Plugin-scoped
SKILL.md / agent.md frontmatter  ← Component-scoped
```

---

## Component-Scoped Hooks (in SKILL.md / agent.md frontmatter)

```yaml
---
name: secure-operations
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/check.sh"
          once: true   # only fires once per session
  Stop:
    - hooks:
        - type: prompt
          prompt: "Verify all operations completed safely."
---
```

When a `Stop` hook is in a **subagent's** frontmatter, it auto-converts to `SubagentStop` scoped to that agent only.

---

## Key Patterns

### Pattern 1 — Bash Command Validator (PreToolUse)
```python
#!/usr/bin/env python3
import json, sys, re

BLOCKED = [
    (r"\brm\s+-rf\s+/", "Blocking dangerous rm -rf /"),
    (r"\bsudo\s+rm", "Blocking sudo rm"),
]

data = json.load(sys.stdin)
if data.get("tool_name") != "Bash":
    sys.exit(0)

cmd = data.get("tool_input", {}).get("command", "")
for pattern, msg in BLOCKED:
    if re.search(pattern, cmd):
        print(msg, file=sys.stderr)
        sys.exit(2)   # exit 2 = blocking error
sys.exit(0)
```

### Pattern 2 — Secret Scanner (PostToolUse)
```python
#!/usr/bin/env python3
import json, sys, re

SECRETS = [
    (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password"),
    (r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]", "Hardcoded API key"),
]

data = json.load(sys.stdin)
if data.get("tool_name") not in ["Write", "Edit"]:
    sys.exit(0)

ti = data.get("tool_input", {})
content = ti.get("content", "") or ti.get("new_string", "")
warnings = [msg for pat, msg in SECRETS if re.search(pat, content, re.IGNORECASE)]

if warnings:
    out = {"hookSpecificOutput": {"hookEventName": "PostToolUse",
           "additionalContext": "; ".join(warnings)}}
    print(json.dumps(out))
sys.exit(0)
```

### Pattern 3 — Context Usage Tracker (UserPromptSubmit + Stop pair)
```python
#!/usr/bin/env python3
"""Track token consumption per request using hook pairs."""
import json, os, sys, tempfile

CONTEXT_LIMIT = 128000

def state_file(session_id):
    return os.path.join(tempfile.gettempdir(), f"claude-ctx-{session_id}.json")

def count_tokens(text):
    return len(text) // 4   # ~4 chars per token estimate

def read_transcript(path):
    content = []
    if not path or not os.path.exists(path): return ""
    with open(path) as f:
        for line in f:
            try:
                entry = json.loads(line)
                msg = entry.get("message", {})
                c = msg.get("content", "")
                if isinstance(c, str): content.append(c)
                elif isinstance(c, list):
                    for b in c:
                        if isinstance(b, dict) and b.get("type") == "text":
                            content.append(b.get("text", ""))
            except json.JSONDecodeError:
                continue
    return "\n".join(content)

data = json.load(sys.stdin)
event = data.get("hook_event_name", "")
session_id = data.get("session_id", "unknown")
sf = state_file(session_id)

if event == "UserPromptSubmit":
    tokens = count_tokens(read_transcript(data.get("transcript_path", "")))
    with open(sf, "w") as f: json.dump({"pre": tokens}, f)

elif event == "Stop":
    tokens = count_tokens(read_transcript(data.get("transcript_path", "")))
    pre = 0
    if os.path.exists(sf):
        with open(sf) as f: pre = json.load(f).get("pre", 0)
    pct = tokens / CONTEXT_LIMIT * 100
    print(f"Context: ~{tokens:,} tokens ({pct:.1f}% used, ~{CONTEXT_LIMIT-tokens:,} remaining)", file=sys.stderr)
    if tokens - pre > 0:
        print(f"This request: ~{tokens-pre:,} tokens", file=sys.stderr)
sys.exit(0)
```
Hook configuration for the context tracker:
```json
{
  "hooks": {
    "UserPromptSubmit": [{"hooks": [{"type": "command",
      "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/context-tracker.py\""}]}],
    "Stop": [{"hooks": [{"type": "command",
      "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/context-tracker.py\""}]}]
  }
}
```

### Pattern 4 — Auto-Format on Write (PostToolUse)
```bash
#!/usr/bin/env bash
set -euo pipefail
INPUT=$(cat)
TOOL=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))")
FILE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))")
[[ "$TOOL" != "Write" && "$TOOL" != "Edit" ]] && exit 0
case "$FILE" in
  *.py) command -v black &>/dev/null && black "$FILE" 2>/dev/null ;;
  *.go) command -v gofmt &>/dev/null && gofmt -w "$FILE" 2>/dev/null ;;
  *.js|*.ts|*.tsx) command -v prettier &>/dev/null && prettier --write "$FILE" 2>/dev/null ;;
  *.tf) command -v terraform &>/dev/null && terraform fmt "$FILE" 2>/dev/null ;;
  *.yaml|*.yml) command -v yamllint &>/dev/null && yamllint "$FILE" 2>/dev/null ;;
esac
exit 0
```

### Pattern 5 — SessionEnd Logger
```bash
#!/usr/bin/env bash
# SessionEnd fires ONCE on exit — not after every response like Stop
PROGRESS_FILE="$HOME/.claude-sessions.json"
[ ! -f "$PROGRESS_FILE" ] && echo '{"sessions":[]}' > "$PROGRESS_FILE"

DATE=$(date +"%Y-%m-%d")
TIME=$(date +"%H:%M")
printf "Session summary (optional, Enter to skip): "
read -r NOTES </dev/tty
[ -z "$NOTES" ] && exit 0

python3 - "$PROGRESS_FILE" "$DATE" "$TIME" "$NOTES" <<'EOF'
import sys, json
path, date, time_str, notes = sys.argv[1:]
with open(path) as f: data = json.load(f)
data.setdefault("sessions", []).append({"date": date, "time": time_str, "notes": notes})
with open(path, "w") as f: json.dump(data, f, indent=2)
EOF
```

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Allow / proceed, optionally parse JSON stdout |
| `2` | **Block** — stderr shown as error message |
| Other | Non-blocking warning, shown in verbose mode only |

---

## JSON Output Fields

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Optional warning shown to user",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "Explanation",
    "updatedInput": { "file_path": "/modified/path" },
    "additionalContext": "Text appended to Claude's context"
  }
}
```

---

## Environment Variables

| Variable | Available In | Purpose |
|---|---|---|
| `CLAUDE_PROJECT_DIR` | All hooks | Absolute path to project root |
| `CLAUDE_ENV_FILE` | SessionStart, CwdChanged, FileChanged | Persist env vars across restarts |
| `CLAUDE_CODE_REMOTE` | All hooks | "true" in remote environments |
| `${CLAUDE_PLUGIN_ROOT}` | Plugin hooks | Plugin directory path |
| `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` | SessionEnd | Override default timeout |

Persist env vars from SessionStart:
```bash
if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export KUBECONFIG=/etc/kubernetes/admin.conf' >> "$CLAUDE_ENV_FILE"
fi
```

---

## Security Rules

- Always quote shell variables: `"$VAR"` not `$VAR`
- Use `$CLAUDE_PROJECT_DIR` — never hardcode paths
- Skip `.env`, `.git/`, `*.key`, `*.pem` files in file-scanning hooks
- HTTP hooks require explicit `allowedEnvVars` — never expose all env to webhooks
- Test hooks independently before enabling: `echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | python3 hook.py`
- Use `claude --debug` to see hook execution logs
- `disableAllHooks: true` in managed policy disables all hooks org-wide

---

## Debugging

```bash
# Test hook with sample input
echo '{"tool_name": "Write", "tool_input": {"file_path": "/tmp/test.py", "content": "x=1"}}' \
  | python3 .claude/hooks/security-scan.py

# Enable full debug output
claude --debug

# Enable verbose mode in interactive session: Ctrl+O
```

---
name: subagent-advanced
description: >
  Advanced Claude Code subagent patterns including worktree isolation, forked subagents
  (context: fork), background agents, resumable agents, persistent memory, restrict
  spawnable subagents, and experimental Agent Teams. Activate when designing complex
  multi-agent workflows, delegating long-running tasks, or using Claude Code v2.1.117+
  subagent features.
---

# Advanced Subagent Patterns

## Complete Frontmatter Reference

```yaml
---
name: my-agent                          # lowercase, hyphens only
description: "What it does. Use PROACTIVELY when..."  # triggers auto-invocation
tools: Read, Grep, Glob, Bash           # omit = inherit all
disallowedTools: Write, Edit            # explicit deny list
model: haiku                            # sonnet | opus | haiku | inherit
permissionMode: acceptEdits             # default | acceptEdits | dontAsk | bypassPermissions | plan
maxTurns: 20                            # cap agentic turns
skills: code-review, security-review    # preload skill content into context
mcpServers: github                      # MCP servers available to agent
memory: user                            # user | project | local
background: false                       # true = always run as background task
effort: high                            # low | medium | high | max
isolation: worktree                     # git worktree isolation
context: fork                           # fork = inherit parent conversation
initialPrompt: "Start by reading..."    # auto-submitted first turn
hooks:                                  # component-scoped hooks
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

---

## Pattern 1 — Worktree Isolation

Gives the subagent its own git branch. Changes don't affect the main working tree.

```yaml
---
name: feature-builder
isolation: worktree
description: Implements features in an isolated git worktree. Use when implementing
  features that should not affect the main branch until reviewed.
tools: Read, Write, Edit, Bash, Grep, Glob
---

You are a feature implementation agent working in an isolated git worktree.
Implement the requested feature, run tests, and report back your branch name.
The main agent will review and merge if appropriate.
```

**Behavior:**
- Subagent operates on a separate branch
- If no changes made → worktree auto-cleaned up
- If changes exist → returns worktree path + branch name to main agent for review
- Safe for experimental work that may be discarded

---

## Pattern 2 — Forked Subagent (context: fork)

Inherits the **full parent conversation** at fork time. Use to explore alternatives without losing context.

```yaml
---
name: alternative-explorer
description: Explore an alternative implementation path while preserving parent context.
  Use when comparing two approaches without losing current work.
context: fork
tools: Read, Edit, Bash, Grep, Glob
---

You are a forked subagent. You inherit the parent's full conversation.
Explore the alternative approach requested. Return findings — the parent
decides whether to adopt them.
```

**Enable on non-first-party builds:**
```bash
export CLAUDE_CODE_FORK_SUBAGENT=1
```

**Fork vs Clean context decision:**
| Scenario | Use Fork | Use Clean |
|---|---|---|
| Explore alternative implementations | ✅ | ❌ |
| Long research with existing context | ✅ | ❌ |
| Independent specialized task | ❌ | ✅ |
| Avoiding context pollution | ❌ | ✅ |

---

## Pattern 3 — Background Subagents

```yaml
---
name: long-analyzer
background: true
description: Performs long-running analysis that should not block the main conversation.
tools: Read, Grep, Glob, Bash
---

Run the analysis requested. Output a structured report when complete.
```

**Keyboard shortcuts:**
- `Ctrl+B` — Background a currently running subagent task
- `Ctrl+F` — Kill all background agents (press twice to confirm)

**Disable background tasks entirely:**
```bash
export CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1
```

---

## Pattern 4 — Resumable Agents

```bash
# Initial invocation — returns agentId
> Use the code-analyzer agent to start reviewing the authentication module
# Returns: agentId: "abc123"

# Resume later with full context preserved
> Resume agent abc123 and now analyze the authorization logic as well
```

Use cases:
- Long-running research across multiple sessions
- Iterative refinement without losing context
- Multi-step workflows maintaining state

---

## Pattern 5 — Persistent Memory

The `memory` field gives a subagent a persistent directory that survives across conversations.

```yaml
---
name: k8s-researcher
memory: user
description: Research Kubernetes topics and accumulate findings across sessions.
tools: Read, Grep, Glob, Bash, WebSearch
---

You are a Kubernetes research agent with persistent memory.
At session start, read ~/.claude/agent-memory/k8s-researcher/MEMORY.md to recall
previous findings. Update it with new discoveries before finishing.
```

**Memory scopes:**
| Scope | Path | Shared |
|---|---|---|
| `user` | `~/.claude/agent-memory/<name>/` | All projects, personal |
| `project` | `.claude/agent-memory/<name>/` | Team (via git) |
| `local` | `.claude/agent-memory-local/<name>/` | Local only, not committed |

First 200 lines of `MEMORY.md` are auto-loaded into the agent's system prompt.

---

## Pattern 6 — Restrict Spawnable Subagents

Control which subagents a coordinator can spawn:

```yaml
---
name: coordinator
description: Coordinates work between specialized agents.
tools: Agent(worker, researcher), Read, Bash
---

You are a coordinator. You may ONLY spawn the 'worker' and 'researcher' subagents.
Break work into clear tasks and delegate appropriately.
```

> Note: `Task(...)` is an alias for `Agent(...)` — both work.

---

## Pattern 7 — Agent Teams (Experimental)

Unlike subagents (delegated subtasks), teammates work **independently** in parallel with their own context windows and can message each other.

**Enable:**
```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
# or in settings.json:
# { "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```

**Invoke:**
```
Build the authentication module. Use a team — one teammate for the API endpoints,
one for the database schema, and one for the test suite.
```

**Display modes:**
```bash
claude --teammate-mode in-process   # inline output (default)
claude --teammate-mode tmux         # separate tmux panes
claude --teammate-mode auto         # auto-detect
```

**Best practices for teams:**
- 3-5 teammates for optimal coordination
- Tasks of 5-15 minutes each
- Assign different files/directories to prevent merge conflicts
- Start with `in-process` mode first

**Team hooks:**
| Event | Use |
|---|---|
| `TeammateIdle` | Trigger notifications, assign follow-up tasks |
| `TaskCompleted` | Run validation, chain dependent work |

**Limitations:**
- No session resumption for in-process teammates
- One team per session
- Requires tmux/iTerm2 for split-pane mode (not in VS Code terminal)

---

## Subagent vs Slash Command vs Skill vs Memory

| Feature | User-Invoked | Auto-Invoked | Isolated Context | Persistent | External Data |
|---|---|---|---|---|---|
| Slash Commands | ✅ | ❌ | ❌ | ❌ | ❌ |
| Subagents | ✅ | ✅ | ✅ | ❌ | ✅ |
| Memory (CLAUDE.md) | Auto | Auto | ❌ | ✅ | ❌ |
| Skills | ✅ | ✅ | Optional | ❌ | ❌ |
| MCP | Auto | ✅ | ❌ | ❌ | ✅ |
| Hooks | Event-driven | Event-driven | ❌ | ❌ | ❌ |

---

## Auto-Invocation Best Practices

Include "use PROACTIVELY" or "MUST BE USED" in description to encourage automatic delegation:

```yaml
description: Expert code review specialist. Use PROACTIVELY after writing or modifying
  any code files. Must be used for security-sensitive changes.
```

**Explicit invocation options:**
```
# Natural language
> Use the security-reviewer subagent to audit the auth module

# @-mention (bypasses auto-delegation heuristics)
> @"security-reviewer (agent)" review src/auth/
```

---

## Tool Access Strategy

1. **Start restrictive** — begin with Read/Grep/Glob only
2. **Add Bash conditionally** — `Bash(git *), Bash(kubectl get *)` for scoped access
3. **Never give Write/Edit to read-only analysis agents** — prevents accidental changes
4. **Use `disallowedTools`** for explicit deny when inheriting all tools

```yaml
# Good — scoped bash access
tools: Read, Grep, Glob, Bash(kubectl get *), Bash(kubectl describe *)

# Risky — full bash to a research agent
tools: Read, Grep, Glob, Bash
```

---

## Context Management

- Each subagent gets a **fresh context window** — main conversation history is NOT passed
- Only task-relevant context is provided
- Results are distilled back to the main agent
- Subagent transcripts: `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl`
- Auto-compaction at ~95% capacity (override: `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`)

---

## CLI Commands

```bash
# List all configured agents
claude agents

# Run session with a specific agent as main
claude --agent security-reviewer

# Define agent for single session (JSON)
claude --agents '{"infra-reviewer": {"description": "Infra review", "prompt": "You are a Kubernetes expert.", "tools": ["Read","Grep","Glob"]}}'
```

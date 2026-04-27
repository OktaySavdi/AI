# Claude-Mem — Installation & Benefits Guide

> Persistent memory compression system for Claude Code. Automatically captures tool usage, generates semantic summaries, and injects relevant context into future sessions. **68k+ stars**, actively maintained (v12.4.7).

---

## What Problem Does It Solve?

Claude Code is stateless — every session starts with zero memory of previous work. Claude-Mem fixes this by:

- Capturing everything Claude does during sessions (tool calls, observations, decisions)
- Compressing it into searchable summaries with AI
- Automatically injecting relevant past context at the start of new sessions

**Result:** Claude "remembers" your project architecture, past bugs, decisions, and conventions across sessions.

---

## System Requirements

| Requirement | Version |
|---|---|
| Node.js | 18.0.0 or higher |
| Claude Code | Latest (plugin support required) |
| Bun | Auto-installed if missing |
| uv (Python) | Auto-installed if missing (for vector search) |
| SQLite 3 | Bundled |

---

## Installation

### Option A — Plugin Marketplace (recommended)

Run these two commands inside Claude Code:

```bash
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

Then restart Claude Code. Done.

### Option B — npx (command line)

```bash
npx claude-mem install
```

Restart Claude Code after install.

### Option C — Gemini CLI

```bash
npx claude-mem install --ide gemini-cli
```

### Option D — OpenCode

```bash
npx claude-mem install --ide opencode
```

> **Important:** `npm install -g claude-mem` installs the SDK/library only — it does NOT register hooks or start the worker service. Always use `npx claude-mem install` or the `/plugin` commands above.

---

## How It Works

Claude-Mem runs invisibly in the background via 5 lifecycle hooks:

| Hook | What It Does |
|---|---|
| `SessionStart` | Injects relevant past context into new sessions |
| `UserPromptSubmit` | Captures the incoming request |
| `PostToolUse` | Records observations after each tool call |
| `Stop` | Triggers summary compression when Claude finishes |
| `SessionEnd` | Finalises and stores the session record |

### Storage Architecture

- **SQLite database** — sessions, observations, summaries with full-text search (FTS5)
- **Chroma vector database** — semantic (embedding-based) search
- **Worker service** — HTTP API on `http://localhost:37777` with web viewer UI

---

## Key Features

| Feature | Description |
|---|---|
| Persistent Memory | Context survives session restarts and reconnects |
| Progressive Disclosure | Layered retrieval — only injects tokens you actually need |
| MCP Search Tools | Query your project history with natural language |
| Web Viewer UI | Live memory stream at `http://localhost:37777` |
| Privacy Tags | Wrap content in `<private>` to exclude from storage |
| Automatic Operation | Zero manual intervention required |
| Citations | Reference past observations by ID |

---

## Searching Your Memory

Claude-Mem exposes 4 MCP tools following a **3-layer token-efficient workflow**:

```
1. search()       → Get compact index with IDs (~50–100 tokens/result)
2. timeline()     → Get chronological context around interesting results
3. get_observations() → Fetch full details for specific IDs (~500–1,000 tokens/result)
```

**10x token savings** by filtering before fetching full details.

### Example

```javascript
// Step 1: Find relevant entries
search(query="authentication bug", type="bugfix", limit=10)

// Step 2: Review the index, identify IDs (e.g., #123, #456)

// Step 3: Fetch only what you need
get_observations(ids=[123, 456])
```

You can also search directly from the web viewer at `http://localhost:37777`.

---

## Configuration

Settings file: `~/.claude-mem/settings.json` (auto-created on first run)

### Language / Mode

```json
{
  "CLAUDE_MEM_MODE": "code"
}
```

| Mode | Description |
|---|---|
| `code` | Default English mode |
| `code--zh` | Simplified Chinese |
| `code--ja` | Japanese |
| `code--es` | Spanish (and other ISO 639-1 codes) |

Restart Claude Code after changing mode.

---

## Benefits for Infrastructure / DevOps Work

Given a Kubernetes + Terraform + Azure workflow, claude-mem is particularly valuable for:

- **Remembering Kyverno CEL gotchas** you've encountered across sessions
- **Retaining Terraform module decisions** — why a specific azurerm pattern was chosen
- **Tracking pipeline failures** — past errors and their resolutions are searchable
- **Preserving cluster context** — AKS node pool configs, ArgoCD application state discovered in previous sessions
- **Cross-session debugging** — "what did we find last time this CrashLoopBackOff appeared?"

---

## Troubleshooting

If something is broken, tell Claude about the issue — the built-in `troubleshoot` skill will diagnose automatically.

Or run the bug report generator:

```bash
cd ~/.claude/plugins/marketplaces/thedotmack
npm run bug-report
```

Full troubleshooting guide: https://docs.claude-mem.ai/troubleshooting

---

## Resources

| Resource | Link |
|---|---|
| Official Docs | https://docs.claude-mem.ai |
| GitHub | https://github.com/thedotmack/claude-mem |
| Discord | https://discord.com/invite/J4wttp9vDu |
| Web Viewer (after install) | http://localhost:37777 |
| Installation Guide | https://docs.claude-mem.ai/installation |
| Architecture Overview | https://docs.claude-mem.ai/architecture/overview |

---

## License

AGPL-3.0 — free to use, modify, and distribute. If you modify and deploy on a network server, you must make your source code available.

# Performance Rules

## Model Selection (Claude Code)
Use the right model for each task to minimise cost without sacrificing quality:

| Task | Model | Why |
|------|-------|-----|
| Most coding tasks | `sonnet` | Default — handles 80%+ of work |
| Deep architecture / debugging | `opus` | Only when needed |
| Simple subagent tasks | `haiku` | Cost-efficient for delegation |

Switch with `/model opus` for complex reasoning, return to sonnet after.

## Token Management
- Run `/cost` periodically during long sessions to monitor token spend
- Run `/clear` between unrelated tasks — free and instant context reset
- Run `/compact` at logical breakpoints (research done, milestone complete)
- **Never compact mid-implementation** — you'll lose variable names and partial state

### When to Compact
✅ After research/exploration, before implementation  
✅ After completing a milestone, before starting the next  
✅ After a debugging session, before new feature work  
✅ After a failed approach, before trying a new direction  

### MCP Server Limits
Keep under 10 MCPs enabled per project. Each MCP tool description consumes tokens
from the 200k context window, potentially reducing usable context to ~70k.
Use `disabledMcpServers` in project-level settings to disable unused ones.

## Context Management
```json
// ~/.claude/settings.json — already configured
{
  "model": "sonnet",
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  }
}
```
- `MAX_THINKING_TOKENS: 10000` → 70% reduction in hidden thinking cost
- `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE: 50` → compacts earlier for better quality in long sessions

## Code Performance
- Profile before optimising — never optimise what you haven't measured
- Avoid N+1 queries: use bulk operations, prefetch, or joins
- Pre-allocate slices/lists when length is known
- Cache results that are expensive to compute and unlikely to change
- Use connection pooling for database connections

## Kubernetes Resource Efficiency
- Set accurate `resources.requests` based on actual usage (use VPA recommendations)
- Don't over-provision `resources.limits` — it wastes cluster capacity
- Use `HorizontalPodAutoscaler` for variable workloads instead of static replicas
- `PreferredDuringScheduling` pod anti-affinity over hard `RequiredDuringScheduling`
  unless HA is critical (reduces scheduling pressure)

## Shell Script Performance
- Avoid spawning subshells in loops: `$(command)` in a loop is expensive
- Use `mapfile` / `readarray` to read files into arrays (not `while read` loops)
- Prefer `awk` / `grep` over multiple piped `sed` calls
- Cache external tool outputs when called multiple times with the same args

## Pipeline Performance
- Parallelise independent stages
- Cache dependencies (pip, terraform providers) between pipeline runs
- Use `--changes-only` / incremental modes where available (Terraform, ArgoCD sync)

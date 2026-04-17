# Harness Audit

Audit the ECC harness configuration for completeness and correctness.

## Usage

```
/harness-audit
```

## Checks

### Agents (`~/.claude/agents/`)
- All `.md` files have valid YAML frontmatter
- `name`, `description`, `tools`, `model` fields present
- No agents reference non-existent skills

### Skills (`~/.claude/skills/`)
- Each skill directory has a `SKILL.md`
- Version header present

### Rules (`~/.claude/rules/common/`)
- Expected files present: coding-style, security, git-workflow, testing, performance, patterns, agents, hooks

### Contexts (`~/.claude/contexts/`)
- Expected files: dev, review, research, ops

### Hooks (`~/.claude/hooks/`)
- `hooks.json` is valid JSON
- All referenced scripts exist and are executable

### Settings (`~/.claude/settings.json`)
- Valid JSON
- Token optimisation settings present

### AGENTS.md
- File exists at `~/.claude/AGENTS.md`
- Agent roster matches actual agents/ directory

Report: ✅ OK, ⚠️ WARNING, ❌ MISSING for each item.

# Skill Create

Generate a Claude Code skill from the current repository's patterns.

## Usage

```
/skill-create
/skill-create --name "my-patterns"
```

## What it does

1. Analyses git history for repeated patterns
2. Identifies domain-specific conventions in the codebase
3. Generates a `SKILL.md` with frontmatter in `~/.claude/skills/`

## Output

A new skill directory at `~/.claude/skills/<name>/SKILL.md` containing:
- Identified patterns and conventions
- Common workflows for this codebase
- Anti-patterns to avoid
- Example code snippets

## When to Use

- After setting up a new project (capture its conventions)
- After establishing a recurring pattern (save it for reuse)
- Before onboarding another developer using Claude Code

## Related

- `/learn` — extract patterns from current session (lighter weight)
- `/evolve` — cluster multiple instincts into a formal skill

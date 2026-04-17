# Learn

Extract reusable patterns from the current session and save them to memory.

## Usage

```
/learn
```

## What it does

Analyzes the current session for:
1. Patterns that worked and should be repeated
2. Anti-patterns discovered and avoided
3. Domain knowledge gained
4. Configuration/setup that should persist

## Output

Saves to `~/.claude/skills/` or `~/.claude/rules/common/` depending on the type:
- **Workflow patterns** → new or updated skill
- **Universal rules** → update relevant rules file
- **Session-specific** → session memory file

## When to Use

- After solving a tricky bug
- After establishing a new coding pattern for the project
- After a successful architecture decision
- At the end of a productive session before `/clear`

## Related

Use `/checkpoint` to save task state instead of learned patterns.
Use `/evolve` to cluster multiple learned instincts into a skill.

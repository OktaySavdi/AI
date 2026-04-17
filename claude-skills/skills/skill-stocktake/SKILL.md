---
name: "skill-stocktake"
description: >
  Audit all skills, commands, and agents for quality, completeness, and accuracy.
  Activate when reviewing or improving the ECC harness configuration.
metadata:
  version: 1.0.0
  category: meta
---

# Skill Stocktake Skill

## What It Does

Audits `~/.claude/` for:
1. Skills missing SKILL.md or with empty/stub content
2. Commands with no actionable instructions
3. Agents with missing required frontmatter fields
4. Duplicate or overlapping skills that should be merged
5. Rules that conflict with each other

## Audit Procedure

```bash
# Check all skills have SKILL.md
for dir in ~/.claude/skills/*/; do
    if [[ ! -f "$dir/SKILL.md" ]]; then
        echo "MISSING SKILL.md: $dir"
    fi
done

# Check all agents have required frontmatter
for f in ~/.claude/agents/*.md; do
    if ! grep -q "^name:" "$f"; then
        echo "MISSING name: $f"
    fi
    if ! grep -q "^description:" "$f"; then
        echo "MISSING description: $f"
    fi
done

# Check all commands are non-empty
for f in ~/.claude/commands/*.md; do
    if [[ $(wc -l < "$f") -lt 5 ]]; then
        echo "STUB COMMAND: $f"
    fi
done
```

## Quality Rubric for Skills

A quality SKILL.md includes:
- [ ] YAML frontmatter with `name`, `description`, `metadata.version`
- [ ] "When This Skill Activates" or "Activation Triggers" section
- [ ] Concrete code examples (not just prose)
- [ ] Anti-patterns or common pitfalls section
- [ ] Related skills cross-references

## Slash Command

```
/harness-audit
```

Invokes the `harness-optimizer` agent for a full structured audit.

## Output Format

```
=== SKILL AUDIT (20 skills) ===
✅ kubernetes-expert — complete (8 sections, 42 code examples)
✅ terraform-azure — complete (6 sections, 31 code examples)
⚠️ configure-ecc — stub (< 10 lines)
❌ videodb — SKILL.md missing

=== COMMAND AUDIT (31 commands) ===
✅ 29 complete
⚠️ 2 stub (< 5 lines)

=== AGENT AUDIT (36 agents) ===
✅ All 36 agents have valid frontmatter
```

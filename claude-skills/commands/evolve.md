# /evolve — Cluster Instincts into Skills

Analyzes saved instincts and clusters related ones into a reusable skill.
Invokes the `continuous-learning-v2` skill to detect patterns and generate a SKILL.md.

## Usage

```
/evolve
/evolve --category kyverno
/evolve --min-confidence 70
/evolve --output ~/.claude/skills/my-new-skill/
```

## What It Does

1. Reads all instincts from `continuous-learning-v2/instincts/`
2. Clusters semantically related instincts using similarity analysis
3. For each cluster with ≥3 instincts, proposes a new skill name and description
4. Generates a `SKILL.md` with the clustered patterns
5. Prompts for confirmation before writing the skill

## Example Output

```
Found 3 clusters suitable for evolution:

Cluster 1 (8 instincts): "kyverno-cel-patterns"
  → Create ~/.claude/skills/kyverno-cel-patterns/SKILL.md? [y/n]

Cluster 2 (5 instincts): "terraform-azure-naming"
  → Create ~/.claude/skills/terraform-azure-naming/SKILL.md? [y/n]
```

## Related Commands

- `/instinct-status` — view instincts before evolving
- `/learn-eval` — add more instincts before evolving
- `/prune` — clean expired instincts before evolving

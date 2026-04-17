# Coding Style Rules

These rules apply universally across all code in this repository.
Follow them without exception.

## File Organization
- One concept per file. Split when a file exceeds 400 lines (with rare exceptions for generated code).
- Group related files in directories. Directory names are lowercase with hyphens.
- Index/entrypoint files export from their directory — they don't contain logic.
- Test files live alongside the code they test (not in a separate `tests/` tree), except
  for integration/E2E tests which go in a dedicated directory.

## Naming Conventions
| Language | Functions | Variables | Constants | Types/Classes |
|----------|-----------|-----------|-----------|---------------|
| Python | `snake_case` | `snake_case` | `UPPER_SNAKE` | `PascalCase` |
| Go | `camelCase` | `camelCase` | `PascalCase` / `camelCase` | `PascalCase` |
| Bash | `snake_case` | `UPPER_SNAKE` (globals) / `lower_snake` (locals) | `UPPER_SNAKE` | N/A |
| YAML keys | `camelCase` (K8s) or `snake_case` (config) | — | — | — |

Names must be self-documenting. If you need a comment to explain what a name means,
the name is wrong.

## Immutability Preference
- Prefer immutable data structures. Mutate only when necessary.
- Avoid global mutable state. Pass state explicitly through function arguments.
- In Python: use `dataclass(frozen=True)` or `NamedTuple` for value objects.
- In Bash: use `readonly` for constants.

## Magic Numbers / Strings
Replace magic numbers and strings with named constants:
```bash
# WRONG
sleep 30

# CORRECT
readonly RETRY_DELAY_SECONDS=30
sleep "$RETRY_DELAY_SECONDS"
```

## Function Length
- Target: ≤ 30 lines per function
- Hard limit: 80 lines (split if exceeded)
- Exception: generated code, parsing tables

## Error Handling
- Handle errors explicitly. Never ignore them.
- Python: catch specific exceptions, not bare `except:`
- Go: wrap errors with context using `fmt.Errorf("action: %w", err)`
- Bash: use `set -euo pipefail` + trap ERR at the top of every script
- Log errors before re-raising/returning them

## Comments
- Comment the *why*, not the *what*
- Remove commented-out code — use git history
- `TODO: <ticket>` format for deferred work; never unlinked TODOs
- Keep comments current — wrong comments are worse than no comments

## Dependencies
- Pin exact versions in lockfiles
- No new runtime dependency without team discussion
- Prefer stdlib over third-party for simple tasks
- Never import a package just for one function you could write in 5 lines

## YAML Specifically
- 2-space indent
- Explicit `---` document separator
- Keys in alphabetical order within a block (where order is not semantically significant)
- Multiline strings use `|` (literal) or `>` (folded) — never escaped `\n`
- No trailing whitespace

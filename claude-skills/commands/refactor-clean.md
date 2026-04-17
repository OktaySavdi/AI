# Refactor Clean

Invoke the `refactor-cleaner` agent for safe dead-code removal and cleanup.

## Usage

```
/refactor-clean
```

Provide the file or code to clean.

## Constraints

- **No behaviour changes** — all tests must pass before and after
- **No new features** — scope is cleanup only
- Dead code removal, unused imports, extract duplicated logic
- Naming improvements if clearly better

## Process

1. Run existing tests to establish baseline (all green)
2. Apply refactoring changes
3. Run tests again to confirm no regression
4. Report what was changed and why

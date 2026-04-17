# Update Docs

Invoke the `doc-updater` agent to synchronise documentation with code changes.

## Usage

```
/update-docs
```

Optionally specify scope:
```
/update-docs README
/update-docs "API reference for UserService"
```

## What gets updated

- README.md — setup steps, feature list, architecture overview
- CHANGELOG.md — entry for current changes
- Inline comments — for changed functions
- API documentation — for changed endpoints/methods
- Architecture docs — if structural changes were made

## Rules

- Never invent content — only document what exists in the code
- Keep examples runnable and tested
- Flag outdated docs even if not in scope of current change

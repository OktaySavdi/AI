---
name: "coding-standards"
description: >
  Universal coding standards applicable across all languages. Covers naming, file
  organisation, function length, error handling, and code review checklist. Activate
  for any code writing or review task.
license: MIT
metadata:
  version: 1.0.0
  author: ECC
  category: engineering
---

# Coding Standards Skill

## Universal Rules

### Naming
- Names must be self-documenting — no comments needed to explain
- Functions: verb + noun (`validateEmail`, `fetchUser`, `processOrder`)
- Variables: noun or noun phrase (`userId`, `orderItems`, `isActive`)
- Constants: UPPER_SNAKE or PascalCase depending on language
- Avoid abbreviations unless universally known (`url`, `id`, `http`)

### File Organisation
- One concept per file
- Split files exceeding 400 lines (exceptions: generated code, parser tables)
- Related files grouped in directories
- Index/entrypoint files export — they don't contain logic

### Function Design
- Target: ≤ 30 lines per function
- Hard limit: 80 lines — split above this
- Single responsibility: if "and" describes what it does, split it
- No more than 4 parameters — use a config object/struct for more

### Error Handling
- Handle errors explicitly — never ignore them
- Return/raise at detection point, not layers later
- Log at the boundary where you handle it, not inside domain code
- Specific exception types — no bare `except` / `catch (Exception e)`

### Magic Numbers and Strings

```python
# WRONG
time.sleep(30)
if status == 3:

# CORRECT
RETRY_DELAY_SECONDS = 30
time.sleep(RETRY_DELAY_SECONDS)

class OrderStatus:
    PENDING = 3
if status == OrderStatus.PENDING:
```

### Comments
- Comment WHY, not WHAT (the code shows what)
- Never leave commented-out code — use git history
- `TODO: <ticket-id>` format — never unlinked TODOs
- Keep comments current — wrong comments are worse than none

### Immutability
- Prefer immutable data structures
- Avoid global mutable state — pass state as arguments
- Use frozen/readonly types for value objects

## Code Review Checklist

- [ ] Does the code do what it says?
- [ ] Are edge cases handled?
- [ ] Are tests present and meaningful?
- [ ] Is error handling appropriate?
- [ ] No hardcoded secrets or magic values
- [ ] No `:latest` image tags (infrastructure)
- [ ] Logging is present at key decision points
- [ ] Performance: no obvious N+1 queries or unnecessary allocations

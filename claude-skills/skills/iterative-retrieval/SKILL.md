---
name: "iterative-retrieval"
description: >
  Progressive context refinement for subagent delegation. Prevents subagents from
  operating on insufficient context. Teaches the pattern of building context incrementally
  before acting. Activate when delegating complex research or multi-file tasks to subagents.
license: MIT
metadata:
  version: 1.0.0
  author: ECC
  category: workflow
---

# Iterative Retrieval Skill

## The Context Problem

Subagents get a **fresh context** — they cannot see the current conversation.
If you give them insufficient context, they will:
- Miss dependencies and side effects
- Duplicate work already done
- Make assumptions that contradict established patterns

## The Pattern: Build Context Before Acting

### Phase 1: Broad Search (what exists?)

```python
# Agent prompt example
"""
Search the codebase for:
1. All files related to user authentication
2. Existing test patterns for this module
3. Any TODOs or FIXMEs near this code

Return: file list + key patterns found
"""
```

### Phase 2: Deep Read (understand the specifics)

```python
"""
Read these specific files:
- src/auth/login.py (the implementation to modify)
- tests/auth/test_login.py (existing test patterns)
- src/auth/models.py (data models used)

Return: current implementation summary + test conventions
"""
```

### Phase 3: Act (with full context)

Now the subagent has enough context to act correctly.

## When to Apply

- Delegating to `code-reviewer` on unfamiliar code
- Asking `tdd-guide` to write tests for a module
- Having `refactor-cleaner` clean up a complex file
- Any task where the agent needs to understand existing patterns first

## Anti-Pattern

```
# BAD: no context
"Write tests for the user service"

# GOOD: context-rich delegation
"Write tests for src/user/service.py. 
Existing test patterns are in tests/user/. 
The service uses the Repository pattern (see src/user/repository.py).
Follow the AAA pattern used in tests/auth/test_login.py."
```

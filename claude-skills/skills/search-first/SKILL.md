---
name: "search-first"
description: >
  Research-before-coding workflow. Prevents hallucinated APIs and outdated patterns by
  searching documentation, codebase, and recent examples before writing code. Activate
  when working with unfamiliar libraries, APIs, or recently-updated frameworks.
license: MIT
metadata:
  version: 1.0.0
  author: ECC
  category: workflow
---

# Search First Skill

## Core Principle

**Never write code for an unfamiliar API without first verifying it exists.**

## Workflow

### Step 1: Search the codebase

```bash
# Find existing usages
grep -r "LibraryName" --include="*.py" .
grep -r "functionName" --include="*.ts" src/
```

Look for:
- Existing patterns to follow
- Import conventions
- Configuration examples

### Step 2: Check documentation

Use `docs-lookup` agent or WebFetch to verify:
- Exact function signatures
- Required vs optional parameters
- Return types
- Breaking changes in recent versions

### Step 3: Check recent issues/PRs

Search GitHub for:
- Known bugs in the version being used
- Deprecation notices
- Migration guides

### Step 4: Write a minimal test first

Before full implementation, write a minimal usage to confirm the API works as expected.

## Triggers

Activate this skill when you see:
- "using library X"
- "calling API Y"
- "integrating with service Z"
- Version mentions (e.g., "Next.js 16", "Python 3.12")

## Anti-Patterns

- Guessing parameter order from memory
- Using APIs that "sound right" without verification
- Mixing API versions (SDK v3 and v4 patterns)
- Copy-pasting Stack Overflow without checking the year

## Related

- `docs-lookup` agent — structured documentation verification
- `iterative-retrieval` skill — progressive context refinement for subagents

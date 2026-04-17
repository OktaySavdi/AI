# Orchestrate

Coordinate a multi-agent workflow for complex tasks that span multiple domains.

## Usage

```
/orchestrate "describe the complex task"
```

## When to Use

Use `/orchestrate` when a task requires:
- Multiple specialist agents (e.g., plan → implement → test → review)
- Parallel workstreams that can be delegated simultaneously
- Sequential dependencies across different domains

## Workflow Template

```
Step 1: planner → creates blueprint
Step 2: [specialist agents] → implement each component
Step 3: code-reviewer → validates all changes
Step 4: security-reviewer → security check
Step 5: doc-updater → sync documentation
```

## Example

```
/orchestrate "Add OAuth2 login with Google, tests, and docs"

→ planner: break into subtasks
→ typescript-reviewer: review OAuth flow implementation  
→ tdd-guide: write auth tests
→ security-reviewer: audit token handling
→ doc-updater: update auth docs
```

## Parallel vs Sequential

- **Parallel**: review + security audit (both read-only)
- **Sequential**: plan → implement → test (each depends on previous)

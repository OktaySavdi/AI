# /multi-frontend — Frontend Multi-Service Orchestration

Orchestrates multi-agent workflows for frontend development: components, styling,
state management, accessibility, E2E tests, and Storybook stories.

## Usage

```
/multi-frontend "Add dark mode toggle to the navigation"
/multi-frontend "Build a data table component with sorting and pagination"
```

## Agent Routing

| Component | Agent |
|---|---|
| Component architecture | `architect` |
| Implementation | `typescript-reviewer` |
| Accessibility | `security-reviewer` (WCAG audit) |
| E2E tests | `e2e-runner` |
| Documentation | `doc-updater` |
| Code review | `code-reviewer` |

## Related Commands

- `/multi-backend` — backend-specific orchestration
- `/multi-workflow` — general multi-service orchestration

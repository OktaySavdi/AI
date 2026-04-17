# /multi-backend — Backend Multi-Service Orchestration

Orchestrates multi-agent workflows specifically for backend service development:
API layer, database, authentication, background jobs, and tests.

## Usage

```
/multi-backend "Add rate limiting to the API"
/multi-backend "Migrate users table and update all affected services"
```

## Agent Routing

| Component | Agent |
|---|---|
| API endpoints | `architect` + `tdd-guide` |
| Database migrations | `database-reviewer` |
| Security | `security-reviewer` |
| Tests | `tdd-guide` |
| Documentation | `doc-updater` |
| Code review | `code-reviewer` |

## Related Commands

- `/multi-frontend` — frontend-specific orchestration
- `/multi-workflow` — general multi-service orchestration
- `/multi-plan` — custom task decomposition

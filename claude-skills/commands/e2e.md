# E2E Tests

Invoke the `e2e-runner` agent to generate and run Playwright end-to-end tests.

## Usage

```
/e2e "describe the user flow to test"
```

## What it creates

- Test file in `tests/e2e/` or `e2e/`
- Page Object Model class in `tests/e2e/pages/`
- Test fixtures if needed

## Example

```
/e2e "user signup, login, and checkout flow"
```

## Critical Flows to Cover

1. Authentication (signup, login, logout)
2. Primary business workflow
3. Error states (invalid input, network failure)
4. Auth boundaries (protected routes reject unauthenticated users)

# TDD

Invoke the `tdd-guide` agent to drive test-first development.

## Usage

```
/tdd "description of what to implement"
```

## Workflow

RED → GREEN → REFACTOR

1. **RED** — Write a failing test that defines the desired behaviour
2. **GREEN** — Write the minimal code to make the test pass
3. **REFACTOR** — Clean up while keeping all tests green

## Output

- Failing test file (step 1)
- Minimal implementation (step 2)
- Refactored version with explanation (step 3)

## Example

```
/tdd "Python function that validates Kubernetes namespace names"
```

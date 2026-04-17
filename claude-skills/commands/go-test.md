# Go TDD

Invoke the `tdd-guide` agent with Go-specific patterns.

## Usage

```
/go-test "describe what to implement"
```

## Go TDD Workflow

1. **RED** — Write failing table-driven test
2. **GREEN** — Implement minimal code to pass
3. **REFACTOR** — Clean up, extract interfaces

## Example

```
/go-test "HTTP handler that validates and stores user profile"
```

## Go Test Conventions

```bash
go test ./...                    # run all tests
go test -race ./...              # with race detector
go test -cover ./...             # with coverage
go test -run TestFoo ./pkg/...   # run specific test
```

## Target Coverage

- 80% minimum line coverage
- 100% on business logic and error paths
- Table-driven tests for all public functions

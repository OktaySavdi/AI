# Test Coverage

Analyse test coverage for the current codebase and report gaps.

## Usage

```
/test-coverage
```

## What it does

1. Runs the test suite with coverage enabled
2. Identifies files/functions below 80% coverage threshold
3. Prioritises gaps by risk (business logic > utilities > generated code)
4. Suggests specific test cases to close the gaps

## Coverage Commands by Language

```bash
# Python
pytest --cov=. --cov-report=term-missing

# Go
go test -cover ./...
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# JavaScript/TypeScript
npx jest --coverage
npx vitest --coverage

# Java
./gradlew test jacocoTestReport
```

## Minimum Thresholds

| Scope | Threshold |
|---|---|
| Business logic | 100% |
| API handlers | 90% |
| Utilities | 80% |
| Generated code | Excluded |

Report shows: file path, current %, gap %, and recommended test cases.

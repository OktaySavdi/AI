---
name: "tdd-workflow"
description: >
  Test-driven development methodology. RED-GREEN-REFACTOR cycle with language-specific
  patterns. Covers pytest, go test, Jest/Vitest, and JUnit. Activate for any TDD work.
license: MIT
metadata:
  version: 1.0.0
  author: ECC
  category: engineering
---

# TDD Workflow Skill

## Slash Commands

| Command | What it does |
|---------|-------------|
| `/tdd` | Start RED-GREEN-REFACTOR cycle |
| `/test-coverage` | Analyse coverage gaps |

## The Cycle

### RED — Write a failing test first

```python
# Python
def test_should_validate_email_format():
    # Arrange
    validator = EmailValidator()
    # Act
    result = validator.validate("not-an-email")
    # Assert
    assert not result.is_valid
    assert "invalid format" in result.error
```

Run: confirm test FAILS before implementing.

### GREEN — Minimal implementation

Write the simplest code that makes the test pass. No more.

### REFACTOR — Clean up

- Extract duplication
- Improve names
- Add edge case tests
- All tests still green

## Coverage Targets

| Layer | Target |
|---|---|
| Business logic | 100% |
| API/handlers | 90% |
| Utilities | 80% |
| Generated code | Excluded |

## Language Commands

```bash
# Python
pytest --tb=short -q
pytest --cov=. --cov-report=term-missing

# Go
go test -race ./...
go test -cover -coverprofile=coverage.out ./...

# JavaScript
npx vitest --reporter=verbose
npx jest --coverage

# Java
./gradlew test
./gradlew jacocoTestReport
```

## Anti-Patterns to Avoid

- Writing implementation before tests
- Tests that test implementation details (not behaviour)
- Mocking own code (mock external boundaries only)
- Tests that pass without an assert

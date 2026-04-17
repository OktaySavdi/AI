# Testing Rules

## Minimum Coverage
- **80% line coverage** on all new code
- 100% coverage on business logic / policy enforcement code
- Coverage is measured on CI — PRs that drop coverage are rejected

## Test Structure: AAA Pattern
Every test follows Arrange → Act → Assert:
```python
def test_should_return_error_when_input_is_empty():
    # Arrange
    processor = DataProcessor(config=default_config)
    empty_input = ""

    # Act
    result = processor.process(empty_input)

    # Assert
    assert result.is_error()
    assert "empty input" in result.error_message
```

## Test Naming
Name tests after **behaviour**, not implementation:
```
# GOOD
test_should_reject_request_when_namespace_is_system
test_returns_empty_list_when_no_results_found
test_retries_three_times_before_failing

# BAD
test_process_input
test_function_v2
test_thing
```

## Test Types and Ratios
```
Unit Tests (70%)
  - No external dependencies (no DB, no network, no filesystem)
  - Run in < 1ms each
  - Test one behaviour per test

Integration Tests (20%)
  - Test interaction with real (or testcontainer) dependencies
  - OK to be slower (< 10s)
  - Use test-specific DB schemas / namespaces

E2E Tests (10%)
  - Critical user flows only
  - Run against a real environment (staging)
  - Isolate test data with unique identifiers
```

## What to Test
Always write tests for:
- Happy path (valid input, expected output)
- Boundary conditions (empty, nil, zero, max values)
- Error paths (invalid input, dependency unavailable)
- Security-relevant paths (auth failures, input validation)

## Test Independence
- Tests must not depend on execution order
- No shared mutable state between tests
- Each test sets up its own data and tears it down
- Parallel-safe: tests can run concurrently without conflicts

## Mocking
- Mock at the boundary — mock the interface, not the implementation
- Never mock what you own (mock the HTTP client, not your own service)
- Prefer dependency injection over global state so mocking is possible

## Infrastructure / Policy Testing
```bash
# Kubernetes manifest dry-run (always before commit)
kubectl apply --dry-run=client -f manifest.yaml
kubectl apply --dry-run=server -f manifest.yaml  # for admission webhook testing

# Kyverno policy testing
kyverno test Kyverno/  # if kyverno CLI is installed

# Terraform
terraform validate
terraform plan -out=plan.tfplan
```

## No Tests = No Merge
If new code has no tests and tests cannot be written (generated code, external adapter),
document explicitly why in the PR description. This is an exception requiring approval,
not a default.

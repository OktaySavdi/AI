# Quality Gate

Run quality gate checks for the current workspace or specified path.

## Usage

```
/quality-gate
/quality-gate src/
/quality-gate --full
```

## Checks Performed

| Check | Tool | Pass Criteria |
|---|---|---|
| Tests | pytest / go test / jest | All pass |
| Coverage | coverage.py / go cover | ≥ 80% |
| Linting | ruff / golangci-lint / eslint | Zero errors |
| Type check | mypy / tsc | Zero errors |
| Security | bandit / gosec | No HIGH findings |
| K8s manifests | kubectl dry-run | No validation errors |
| Terraform | terraform validate | Valid |
| Shell scripts | shellcheck | No errors |

## Output

```
## Quality Gate Report

✅ Tests: 142 passed, 0 failed
✅ Coverage: 84%
❌ Linting: 3 errors (src/foo.py:42)
⚠️ Security: 1 MEDIUM finding

GATE: FAILED — fix linting errors before proceeding
```

## Related

- `/verify` — same checks, less structured output
- `/loop-start` — automated loop that runs gate repeatedly until pass

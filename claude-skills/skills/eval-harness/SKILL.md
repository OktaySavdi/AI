---
name: "eval-harness"
description: >
  Evaluation harness for verifying AI output quality: criteria definition,
  scoring rubrics, and automated verification loops. Activate for eval work.
metadata:
  version: 1.0.0
  category: meta
---

# Eval Harness Skill

## What Is an Eval Harness?

A structured framework for verifying that Claude's output meets defined quality
criteria before it's accepted. Used to:
- Validate generated code against a rubric
- Score responses on multiple dimensions
- Run verification loops until criteria are met

## Evaluation Dimensions

| Dimension | Weight | Criteria |
|---|---|---|
| Correctness | 40% | Code runs, tests pass, no logic errors |
| Security | 25% | No OWASP issues, no secrets, safe patterns |
| Style | 15% | Follows project conventions, readable |
| Completeness | 10% | All requested features implemented |
| Tests | 10% | Coverage ≥ 80%, edge cases covered |

## Evaluation Template

```markdown
## Eval: [task name]
Date: [date]
Model: claude-sonnet-4-5

### Criteria
- [ ] All tests pass
- [ ] Coverage ≥ 80%
- [ ] No OWASP Top 10 vulnerabilities
- [ ] Follows coding-style.md conventions
- [ ] Error handling for all failure paths

### Results
| Criterion | Score | Notes |
|---|---|---|
| Tests pass | PASS | 23/23 |
| Coverage | PASS | 84% |
| Security | PASS | No issues |
| Style | WARN | 2 functions > 30 lines |
| Errors | PASS | All paths handled |

Overall: PASS (4/5 criteria fully met)
```

## Automated Verification

```bash
#!/usr/bin/env bash
# run-eval.sh
set -e

PASS=0
FAIL=0

check() {
    local name="$1"; shift
    if "$@" > /dev/null 2>&1; then
        echo "✅ PASS: $name"
        ((PASS++))
    else
        echo "❌ FAIL: $name"
        ((FAIL++))
    fi
}

check "Tests"    pytest --tb=no -q
check "Coverage" pytest --cov=. --cov-fail-under=80 -q
check "Lint"     ruff check . --quiet
check "Types"    mypy --strict . --no-error-summary
check "Security" bandit -r . -ll -q

echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]] || exit 1
```

## Slash Command

```
/eval "Does this service correctly handle rate limiting?"
```

Claude scores the current implementation against the rubric and reports results.

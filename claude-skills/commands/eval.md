# Eval

Evaluate output against specified criteria using structured scoring.

## Usage

```
/eval "criteria to evaluate against"
```

Or provide a file with criteria.

## Output Format

```
## Evaluation Report

### Criteria
1. <criterion 1>
2. <criterion 2>

### Scores
| Criterion | Score | Notes |
|---|---|---|
| Criterion 1 | PASS/FAIL/PARTIAL | explanation |

### Summary
Overall: PASS / FAIL
Issues: <list any blockers>
```

## Use Cases

- Evaluate code against architecture decision records
- Check implementation against acceptance criteria from `/plan`
- Verify security controls from a compliance checklist
- Score output from `/verify` against quality gates

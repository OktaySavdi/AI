# Code Review

Invoke the `code-reviewer` agent for a structured code quality review.

## Usage

```
/code-review
```

Then provide the code or file path to review.

## Report Format

```
## BLOCKER
- Issues that must be fixed before merge

## MAJOR
- Significant problems (correctness, security, performance)

## MINOR
- Style, clarity, maintainability

## NIT
- Cosmetic / optional suggestions
```

## Agent Scope

- Correctness and logic errors
- Security vulnerabilities (OWASP Top 10)
- Performance anti-patterns
- Code style and readability
- Test coverage gaps

For language-specific reviews, use `python-reviewer`, `go-reviewer`, or `database-reviewer`.

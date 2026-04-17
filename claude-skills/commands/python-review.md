# Python Review

Invoke the `python-reviewer` agent for a Python-specific code review.

## Usage

```
/python-review
```

Then provide the file path or paste the Python code to review.

## Covers

- Type hints (`mypy --strict` compliance)
- PEP 8 and Ruff lint rules
- Security (bandit findings: SQL injection, subprocess, eval)
- Idiomatic patterns (dataclasses, context managers, generators)
- pytest test quality

## Quick Reference

```python
# Type hints
def process(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# Dataclass for value objects
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    host: str
    port: int = 8080

# Context manager for resources
with open(path, encoding="utf-8") as f:
    data = f.read()
```

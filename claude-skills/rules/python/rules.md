# Python Rules

Language-specific rules for Python development. Extends `common/` rules.

## Formatting and Style

- **Formatter**: `ruff format` (or `black`)
- **Linter**: `ruff check` with rules `E,W,F,I,N,S,B,ANN`
- **Type checker**: `mypy --strict`
- Line length: 88 characters
- Python version: 3.11+ minimum for new projects

## Type Annotations

Always annotate public functions and class attributes:

```python
# All public functions annotated
def fetch_user(user_id: str) -> User | None:
    ...

# Dataclasses for value objects
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    host: str
    port: int = 8080
    timeout: float = 30.0
```

Never use `Any` without a comment explaining why it's unavoidable.

## Error Handling

```python
# Specific exceptions only — no bare except
try:
    result = fetch_data(url)
except requests.ConnectionError as exc:
    logger.error("Connection failed: %s", exc)
    raise ServiceUnavailableError("upstream") from exc

# Custom exception hierarchy
class AppError(Exception): ...
class ValidationError(AppError): ...
class NotFoundError(AppError): ...
```

## Testing

- Framework: `pytest`
- Coverage: `pytest-cov` — minimum 80%
- Fixtures for shared setup
- `parametrize` for multiple inputs

```python
import pytest

@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("not-an-email", False),
    ("", False),
])
def test_validate_email(email: str, valid: bool) -> None:
    assert validate_email(email) == valid
```

## Import Organisation

```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
import requests
from pydantic import BaseModel

# Local
from myapp.models import User
from myapp.services import UserService
```

Use `isort` or `ruff --select I` to enforce order.

## Security

- Never use `subprocess` with `shell=True` and user input
- Never use `eval()` or `exec()` with untrusted data
- Parameterise SQL — never format strings into queries
- `bandit -r src/` in CI

## Tools

```bash
ruff check .                  # lint
ruff format --check .         # format check
mypy --strict .               # type check
pytest --cov=. --tb=short     # test with coverage
bandit -r src/ -ll            # security scan
```

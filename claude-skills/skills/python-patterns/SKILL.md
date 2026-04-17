---
name: "python-patterns"
description: >
  Python idioms and best practices: dataclasses, type hints, generators, context
  managers, functional patterns, and clean architecture. Activate for Python code.
metadata:
  version: 1.0.0
  category: engineering
---

# Python Patterns Skill

## Dataclasses for Value Objects

```python
from dataclasses import dataclass, field
from typing import ClassVar

@dataclass(frozen=True)
class Money:
    amount: int   # in cents
    currency: str = "EUR"
    _VALID_CURRENCIES: ClassVar[set] = {"EUR", "USD", "GBP"}

    def __post_init__(self) -> None:
        if self.currency not in self._VALID_CURRENCIES:
            raise ValueError(f"Unknown currency: {self.currency}")
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
```

## Type Hints

```python
from typing import TypeVar, Generic, Protocol

T = TypeVar("T")

class Repository(Protocol[T]):
    def find_by_id(self, id: str) -> T | None: ...
    def save(self, entity: T) -> T: ...

# Union types (Python 3.10+)
def process(value: int | str | None) -> str: ...
```

## Generators for Large Data

```python
def read_large_file(path: str) -> Generator[str, None, None]:
    with open(path) as f:
        for line in f:
            yield line.rstrip()

# Memory-efficient processing
def process_csv(path: str) -> int:
    return sum(1 for _ in read_large_file(path))
```

## Context Managers

```python
from contextlib import contextmanager

@contextmanager
def managed_connection(url: str) -> Generator[Connection, None, None]:
    conn = connect(url)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

## Functional Patterns

```python
from functools import reduce, partial
from itertools import chain, groupby

# Compose functions
def compose(*fns):
    return reduce(lambda f, g: lambda x: f(g(x)), fns)

# Partial application
validate_email = partial(validate, pattern=EMAIL_REGEX)

# Group and aggregate
by_category = {
    k: list(v)
    for k, v in groupby(sorted(items, key=attrgetter("category")), key=attrgetter("category"))
}
```

## Dependency Injection

```python
class UserService:
    def __init__(
        self,
        repo: UserRepository,
        mailer: EmailService,
        logger: logging.Logger | None = None,
    ) -> None:
        self._repo = repo
        self._mailer = mailer
        self._logger = logger or logging.getLogger(__name__)
```

## Exception Hierarchy

```python
class AppError(Exception):
    """Base for all application errors."""

class ValidationError(AppError):
    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"{field}: {message}")
        self.field = field

class NotFoundError(AppError):
    pass
```

## Anti-Patterns

- Bare `except:` — catch specific exception types
- Global mutable state — use dependency injection
- `type: ignore` comments without explanation
- `Any` without a comment explaining why
- Mutable default arguments: `def f(items=[]):`

## Tools

```bash
ruff check . && ruff format --check .
mypy --strict .
pytest --cov=. --tb=short
bandit -r src/ -ll
```

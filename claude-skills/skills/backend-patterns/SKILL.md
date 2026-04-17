---
name: "backend-patterns"
description: >
  Backend architecture patterns covering repository pattern, service layer, dependency injection,
  caching, database access, and async patterns. Language-agnostic. Activate when designing
  or reviewing backend service code.
license: MIT
metadata:
  version: 1.0.0
  author: ECC
  category: engineering
---

# Backend Patterns Skill

## Repository Pattern

Separate data access from business logic.

```python
# Python
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: str) -> User | None: ...

    @abstractmethod
    def save(self, user: User) -> User: ...

class PostgresUserRepository(UserRepository):
    def __init__(self, db: Database) -> None:
        self._db = db

    def find_by_id(self, user_id: str) -> User | None:
        row = self._db.query("SELECT * FROM users WHERE id = $1", user_id)
        return User.from_row(row) if row else None
```

## Service Layer

Business logic lives here, not in controllers/handlers.

```python
class UserService:
    def __init__(self, repo: UserRepository, mailer: Mailer) -> None:
        self._repo = repo
        self._mailer = mailer

    def register(self, email: str, password: str) -> User:
        if self._repo.find_by_email(email):
            raise DuplicateEmailError(email)
        user = User(email=email, password_hash=hash_password(password))
        saved = self._repo.save(user)
        self._mailer.send_welcome(saved)
        return saved
```

## Caching Patterns

```python
# Cache-aside (lazy loading)
def get_user(user_id: str) -> User:
    cached = cache.get(f"user:{user_id}")
    if cached:
        return User.from_dict(cached)
    user = repo.find_by_id(user_id)
    cache.set(f"user:{user_id}", user.to_dict(), ttl=300)
    return user

# Write-through
def update_user(user: User) -> User:
    saved = repo.save(user)
    cache.set(f"user:{user.id}", saved.to_dict(), ttl=300)
    return saved
```

## Database Access

```python
# Always use connection pooling
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)

# Transactions explicit
with engine.begin() as conn:
    conn.execute(update_stmt)
    conn.execute(log_stmt)
    # auto-commits or rolls back
```

## Async Patterns

```python
# Don't block the event loop
async def get_user_data(user_id: str) -> dict:
    # Good: async I/O
    user = await repo.find_by_id(user_id)
    # Bad: blocking call inside async function
    # user = requests.get(...)  ← blocks event loop
    return user.to_dict()
```

## Error Handling

```python
# Domain errors (4xx)
class DuplicateEmailError(ValueError):
    def __init__(self, email: str) -> None:
        super().__init__(f"Email already registered: {email}")

# Infrastructure errors (5xx) — let them propagate
# Log at the boundary, not inside domain code
```

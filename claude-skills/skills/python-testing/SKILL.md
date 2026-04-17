---
name: "python-testing"
description: >
  Python testing with pytest: fixtures, parametrize, mocking, coverage, TDD,
  and integration tests. Activate when writing or reviewing Python tests.
metadata:
  version: 1.0.0
  category: engineering
---

# Python Testing Skill

## Test Structure (AAA)

```python
def test_should_return_none_when_user_not_found(
    user_service: UserService,
    mock_repo: MagicMock,
) -> None:
    # Arrange
    mock_repo.find_by_id.return_value = None

    # Act
    result = user_service.get_user("nonexistent")

    # Assert
    assert result is None
    mock_repo.find_by_id.assert_called_once_with("nonexistent")
```

## Fixtures

```python
import pytest
from unittest.mock import MagicMock, create_autospec

@pytest.fixture
def mock_repo() -> MagicMock:
    return create_autospec(UserRepository)

@pytest.fixture
def user_service(mock_repo: MagicMock) -> UserService:
    return UserService(repo=mock_repo)

# Scoped fixture (one DB per test session)
@pytest.fixture(scope="session")
def db_engine() -> Engine:
    engine = create_engine("postgresql://localhost/test")
    yield engine
    engine.dispose()
```

## Parametrize

```python
@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("", False),
    ("no-at-sign", False),
    ("a@b.c", True),
])
def test_validate_email(email: str, valid: bool) -> None:
    assert validate_email(email) == valid
```

## Mocking

```python
from unittest.mock import patch, MagicMock

# Patch as decorator
@patch("myapp.services.send_email")
def test_sends_welcome_email(mock_send: MagicMock) -> None:
    register_user("test@example.com")
    mock_send.assert_called_once_with(
        to="test@example.com",
        subject="Welcome!"
    )

# Patch as context manager
def test_handles_email_failure() -> None:
    with patch("myapp.services.send_email", side_effect=SMTPError):
        with pytest.raises(EmailDeliveryError):
            register_user("test@example.com")
```

## Testing Exceptions

```python
def test_raises_validation_error_for_empty_name() -> None:
    with pytest.raises(ValidationError, match="name: cannot be empty"):
        create_user(name="", email="a@b.com")
```

## Integration Tests

```python
import pytest

@pytest.mark.integration
def test_save_and_retrieve_user(db_session: Session) -> None:
    repo = UserRepository(db_session)
    user = User(id="1", name="Alice", email="alice@example.com")
    repo.save(user)

    retrieved = repo.find_by_id("1")
    assert retrieved == user
```

Run only unit tests: `pytest -m "not integration"`
Run all: `pytest`

## Coverage

```ini
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=80"
```

## conftest.py Pattern

```python
# tests/conftest.py
import pytest
from myapp.config import Config

@pytest.fixture(autouse=True)
def reset_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset environment to defaults for each test."""
    monkeypatch.setenv("ENV", "test")
```

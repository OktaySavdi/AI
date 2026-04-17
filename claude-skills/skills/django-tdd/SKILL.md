---
name: "django-tdd"
description: >
  Django TDD workflow with pytest-django: test structure, fixtures, factory_boy,
  API testing, and RED-GREEN-REFACTOR. Activate for Django TDD work.
metadata:
  version: 1.0.0
  category: engineering
---

# Django TDD Skill

## Setup

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
addopts = --reuse-db --cov=. --cov-report=term-missing --cov-fail-under=80
```

## Model Factories (factory_boy)

```python
import factory
from factory.django import DjangoModelFactory

class UserFactory(DjangoModelFactory):
    class Meta:
        model = "users.User"

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = factory.Faker("name")
    is_active = True

# Usage
user = UserFactory()
users = UserFactory.create_batch(5)
```

## Test Classes

```python
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestUserAPI:
    def test_creates_user(self, api_client: APIClient) -> None:
        response = api_client.post("/api/users/", {
            "email": "new@example.com",
            "name": "New User",
        })
        assert response.status_code == 201
        assert response.data["email"] == "new@example.com"

    def test_rejects_duplicate_email(self, api_client: APIClient, user: User) -> None:
        response = api_client.post("/api/users/", {"email": user.email, "name": "Copy"})
        assert response.status_code == 400
        assert "email" in response.data
```

## Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client() -> APIClient:
    return APIClient()

@pytest.fixture
def user(db) -> User:
    return UserFactory()

@pytest.fixture
def auth_client(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client
```

## Testing Celery Tasks

```python
@pytest.mark.django_db
def test_sends_welcome_email(mailoutbox, user):
    from myapp.tasks import send_welcome_email
    send_welcome_email(user.id)
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [user.email]
```

## TDD RED-GREEN-REFACTOR

```
RED:   Write a failing test first
       pytest tests/test_users.py::TestUserAPI::test_creates_user

GREEN: Write minimum code to make it pass
       Add the endpoint, serializer, view

REFACTOR: Improve without breaking tests
          Extract service layer, add validation

REPEAT
```

## Commands

```bash
pytest tests/                          # all tests
pytest -k "TestUserAPI"                # filter by name
pytest --lf                            # last failed only
pytest -x                              # stop on first failure
pytest --cov=myapp --cov-report=html   # coverage report
```

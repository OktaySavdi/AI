---
name: "django-verification"
description: >
  Django verification loop: run tests, linting, type checking, and security
  checks in sequence. Activate when verifying a Django implementation.
metadata:
  version: 1.0.0
  category: engineering
---

# Django Verification Loop Skill

## Verification Sequence

Run in this exact order. Stop on first failure:

```bash
# 1. Lint
ruff check .

# 2. Format check
ruff format --check .

# 3. Type check
mypy --strict .

# 4. Security
bandit -r . -ll
safety check

# 5. Tests with coverage
pytest --cov=. --cov-fail-under=80 -x

# 6. Django system checks
python manage.py check --deploy
```

## Django System Check (production settings)

```bash
DJANGO_SETTINGS_MODULE=config.settings.production \
  python manage.py check --deploy
```

Expected output — all should pass:
- `SECURITY.W004` — HSTS settings
- `SECURITY.W008` — SSL redirect
- `SECURITY.W012` — CSRF cookie secure
- `SECURITY.W016` — Session cookie secure

## Migration Check

```bash
python manage.py makemigrations --check  # fails if model changes without migration
python manage.py migrate --check          # fails if pending migrations exist
```

## Full CI Verification Script

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Lint ===" && ruff check .
echo "=== Format ===" && ruff format --check .
echo "=== Types ===" && mypy --strict .
echo "=== Security ===" && bandit -r . -ll
echo "=== Migrations ===" && python manage.py makemigrations --check
echo "=== Tests ===" && pytest --cov=. --cov-fail-under=80
echo "=== Deploy Check ===" && python manage.py check --deploy
echo "All checks passed."
```

---
name: "laravel-verification"
description: >
  Laravel verification loop: lint, static analysis, security, and test suite.
  Activate when verifying a Laravel implementation.
metadata:
  version: 1.0.0
  category: engineering
---

# Laravel Verification Loop Skill

## Verification Sequence

```bash
# 1. PHP syntax check
find . -name "*.php" -not -path "*/vendor/*" | xargs php -l

# 2. Code style (Laravel Pint)
./vendor/bin/pint --test

# 3. Static analysis (PHPStan level 8)
./vendor/bin/phpstan analyse --level=8

# 4. Security audit
composer audit

# 5. Tests with coverage
php artisan test --coverage --min=80

# 6. Migration check
php artisan migrate --pretend
```

## Full CI Script

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Syntax ===" && find . -name "*.php" ! -path "*/vendor/*" | xargs php -l
echo "=== Style ===" && ./vendor/bin/pint --test
echo "=== Static Analysis ===" && ./vendor/bin/phpstan analyse --level=8
echo "=== Security ===" && composer audit
echo "=== Tests ===" && php artisan test --parallel --coverage --min=80
echo "All checks passed."
```

## phpstan.neon

```neon
parameters:
  level: 8
  paths:
    - app
    - tests
  ignoreErrors:
    - '#Call to an undefined method Illuminate\\.*#'
```

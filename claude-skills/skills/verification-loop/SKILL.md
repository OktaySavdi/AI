---
name: "verification-loop"
description: >
  Continuous verification workflow. Runs build, test, lint, typecheck, and security checks
  in sequence. Stops on first failure and explains the fix. Activate when implementing
  a feature to verify at each step.
license: MIT
metadata:
  version: 1.0.0
  author: ECC
  category: workflow
---

# Verification Loop Skill

## Core Pattern

After every meaningful code change, run the full verification stack before moving on.

## Verification Stack (run in order)

### 1. Build / Compile
```bash
# Python
python -m py_compile src/**/*.py

# Go
go build ./...

# TypeScript
npx tsc --noEmit

# Java
./gradlew compileJava
```

### 2. Unit Tests
```bash
# Python
pytest --tb=short -q

# Go
go test -race ./...

# JS/TS
npx vitest run

# Java
./gradlew test
```

### 3. Linting
```bash
# Python
ruff check .

# Go
golangci-lint run

# TypeScript
npx eslint src/

# Shell
shellcheck Shell/*.sh
```

### 4. Type Check
```bash
# Python
mypy --strict .

# TypeScript
npx tsc --noEmit

# Go (built-in — go build already checks)
```

### 5. Security
```bash
# Python
bandit -r src/

# Go
gosec ./...

# Dependencies
pip-audit  # or: npm audit
```

### 6. Infrastructure (if changed)
```bash
kubectl apply --dry-run=server -f manifest.yaml
terraform validate
helm lint chart/
```

## Stop on First Failure

When a step fails:
1. Fix it completely before running the next step
2. Re-run all previous steps after the fix
3. Only proceed when the step is green

## Integration

Use with `/verify` command or as part of `/loop-start` quality gate.

# /setup-pm — Configure Package Manager

Interactively detects and configures the package manager for the current project.
Supports npm, yarn, pnpm, bun (Node.js) and pip, uv, poetry, conda (Python).

## Usage

```
/setup-pm
/setup-pm --force bun
```

## What It Does

1. Scans the project for lockfiles to auto-detect the package manager
2. If ambiguous, prompts for selection
3. Writes the selection to project settings so all subsequent commands use it
4. Installs dependencies using the chosen package manager

## Detection Priority

| Lockfile | Package Manager |
|---|---|
| `bun.lockb` | bun |
| `pnpm-lock.yaml` | pnpm |
| `yarn.lock` | yarn |
| `package-lock.json` | npm |
| `uv.lock` | uv |
| `poetry.lock` | poetry |
| `Pipfile.lock` | pipenv |
| `requirements.txt` | pip |

## Related Commands

- `/pm2` — PM2 service lifecycle management

# /update-codemaps — Update Codemaps

Regenerates or updates the codebase structure map used by agents for orientation.
Produces a concise directory tree with module summaries written to `CODEBASE.md`
or `.claude/codemap.md` at the project root.

## Usage

```
/update-codemaps
/update-codemaps --depth 3
/update-codemaps --output .claude/codemap.md
```

## What It Generates

```markdown
# Codebase Map — updated 2026-04-17

## Structure
src/
  api/          REST endpoints (Express, OpenAPI 3.1)
  services/     Business logic, no framework dependency
  models/       Prisma schema + generated types
  jobs/         BullMQ background job handlers
tests/
  unit/         Vitest unit tests (80% coverage)
  e2e/          Playwright E2E tests

## Key Entry Points
- src/index.ts     → server bootstrap
- src/api/router.ts → all route registrations
- prisma/schema.prisma → database schema
```

## Related Commands

- `/update-docs` — update human-facing documentation
- `/plan` — uses codemap for accurate implementation blueprints

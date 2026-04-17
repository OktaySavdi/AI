# TypeScript Rules

Language-specific rules for TypeScript and JavaScript development. Extends `common/` rules.

## Configuration

```json
// tsconfig.json — strict mode always
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true
  }
}
```

## Type Safety

```typescript
// No 'any' — use 'unknown' for unsafe input
function parseInput(raw: unknown): ParsedInput {
  if (!isValidInput(raw)) throw new ValidationError("invalid input");
  return raw as ParsedInput;
}

// Discriminated unions over optional fields
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: string };

// Branded types for domain values
type UserId = string & { readonly _brand: "UserId" };
const userId = (id: string): UserId => id as UserId;
```

## Immutability

```typescript
// Prefer readonly
interface Config {
  readonly host: string;
  readonly port: number;
}

// const assertions
const ROLES = ["admin", "user", "guest"] as const;
type Role = typeof ROLES[number];
```

## Async

```typescript
// Always async/await over .then()
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new ApiError(`Failed to fetch user: ${response.status}`);
  }
  return response.json() as Promise<User>;
}

// Handle errors explicitly
try {
  const user = await fetchUser(id);
} catch (error) {
  if (error instanceof ApiError) {
    // handle known error
  }
  throw error; // re-throw unknown
}
```

## Modules

```typescript
// Named exports preferred over default exports
export function validateEmail(email: string): boolean { ... }
export type { ValidationResult };

// Barrel files only for public API (not internal modules)
```

## Testing

- Framework: Vitest or Jest
- Coverage: `--coverage` with 80% threshold
- Mock external dependencies, not own code

## Security

- Never `eval()` or `new Function()`
- Never `dangerouslySetInnerHTML` without `DOMPurify`
- `zod` or `valibot` for runtime input validation at boundaries
- Environment variables via typed config object — never `process.env.X` inline

## Tools

```bash
npx tsc --noEmit          # type check
npx eslint src/           # lint
npx vitest run --coverage # test with coverage
npx audit                 # dependency security
```

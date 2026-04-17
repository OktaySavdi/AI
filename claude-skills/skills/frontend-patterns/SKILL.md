---
name: "frontend-patterns"
description: >
  React and Next.js patterns: component design, hooks, state management, data
  fetching, performance optimization, and accessibility. Activate for frontend work.
metadata:
  version: 1.0.0
  category: engineering
---

# Frontend Patterns Skill

## Component Design Principles

- **Single responsibility**: one component, one concern
- **Composition over configuration**: prefer small composable components
- **Controlled inputs**: always control form state through React
- **Accessibility first**: semantic HTML, ARIA where necessary

## Custom Hooks

```typescript
// Extract logic into hooks — components stay thin
function useUser(id: string) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchUser(id)
      .then((u) => { if (!cancelled) setUser(u); })
      .catch((e) => { if (!cancelled) setError(e); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [id]);

  return { user, loading, error };
}
```

## Next.js Server Components (App Router)

```typescript
// Server Component — no "use client", fetches data directly
export default async function UserPage({ params }: { params: { id: string } }) {
  const user = await getUser(params.id);  // runs on server
  if (!user) notFound();
  return <UserProfile user={user} />;
}

// Client Component — only for interactivity
"use client";
export function LikeButton({ postId }: { postId: string }) {
  const [liked, setLiked] = useState(false);
  return <button onClick={() => setLiked(!liked)}>{liked ? "♥" : "♡"}</button>;
}
```

## Data Fetching (SWR / React Query)

```typescript
import useSWR from "swr";

function UserCard({ id }: { id: string }) {
  const { data, error, isLoading } = useSWR(`/api/users/${id}`, fetcher);

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage error={error} />;
  return <div>{data.name}</div>;
}
```

## Form Handling (React Hook Form + Zod)

```typescript
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
});

type FormData = z.infer<typeof schema>;

function SignupForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register("email")} aria-invalid={!!errors.email} />
      {errors.email && <span role="alert">{errors.email.message}</span>}
    </form>
  );
}
```

## Performance

```typescript
// Memoize expensive computations
const sorted = useMemo(() => [...items].sort(compareFn), [items]);

// Stable callbacks for child components
const handleClick = useCallback((id: string) => {
  dispatch({ type: "SELECT", id });
}, [dispatch]);

// Lazy-load heavy components
const HeavyChart = lazy(() => import("./HeavyChart"));
```

## Accessibility Checklist

- [ ] All images have `alt` text (or `alt=""` for decorative)
- [ ] Form inputs have associated `<label>` via `htmlFor`
- [ ] Error messages use `role="alert"`
- [ ] Interactive elements are keyboard-navigable
- [ ] Color contrast ratio ≥ 4.5:1 for normal text
- [ ] Focus visible on all interactive elements

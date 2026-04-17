---
name: "database-migrations"
description: >
  Database migration patterns for Prisma, Drizzle, Django, Go (golang-migrate).
  Covers safe migration strategies, rollbacks, and zero-downtime deployments.
metadata:
  version: 1.0.0
  category: engineering
---

# Database Migrations Skill

## Migration Principles

1. **Always reversible** — write `down` migrations
2. **Additive first** — add columns before removing old ones
3. **Non-blocking** — avoid full-table locks in production
4. **Tested** — run against a copy of production data before deploy
5. **Atomic** — each migration does one logical change

## Zero-Downtime Patterns

### Adding a Column

```sql
-- SAFE: Add nullable column first, then backfill, then add constraint
ALTER TABLE users ADD COLUMN phone VARCHAR(20);           -- instant
UPDATE users SET phone = '' WHERE phone IS NULL;          -- backfill
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;        -- after backfill
```

### Renaming a Column

```sql
-- 3-step deploy: add new → dual-write in app → remove old
ALTER TABLE users ADD COLUMN full_name VARCHAR(255);
-- Deploy code that writes to both name and full_name
UPDATE users SET full_name = name WHERE full_name IS NULL;
-- Deploy code that reads from full_name only
ALTER TABLE users DROP COLUMN name;
```

### Dropping a Column

```sql
-- Always: remove from application code first, then drop
ALTER TABLE users DROP COLUMN legacy_field;
```

## Prisma

```bash
# Create migration
npx prisma migrate dev --name add_phone_to_users

# Apply in production
npx prisma migrate deploy

# Reset dev DB
npx prisma migrate reset
```

```prisma
model User {
  id    String @id @default(cuid())
  email String @unique
  phone String?  // nullable for backward compatibility
}
```

## Drizzle

```typescript
import { pgTable, text, varchar } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: text("id").primaryKey(),
  email: varchar("email", { length: 255 }).notNull().unique(),
  phone: varchar("phone", { length: 20 }),
});
```

```bash
npx drizzle-kit generate
npx drizzle-kit migrate
```

## Django

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --fake  # mark as applied without running
```

```python
# Custom migration operation
class Migration(migrations.Migration):
    dependencies = [("users", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="user",
            name="phone",
            field=models.CharField(max_length=20, blank=True),
        ),
    ]
```

## golang-migrate

```bash
migrate create -ext sql -dir db/migrations -seq add_phone_to_users
migrate -database "${DATABASE_URL}" -path db/migrations up
migrate -database "${DATABASE_URL}" -path db/migrations down 1
```

```sql
-- 000002_add_phone_to_users.up.sql
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- 000002_add_phone_to_users.down.sql
ALTER TABLE users DROP COLUMN phone;
```

## CI/CD Integration

```yaml
# Run migrations in pipeline before deploying app
- script: |
    npx prisma migrate deploy
  displayName: "Run database migrations"
  env:
    DATABASE_URL: $(DATABASE_URL)
```

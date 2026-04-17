---
name: "postgres-patterns"
description: >
  PostgreSQL optimization patterns: indexes, query plans, partitioning, CTEs,
  window functions, JSONB, and connection pooling. Activate for PostgreSQL work.
metadata:
  version: 1.0.0
  category: engineering
---

# PostgreSQL Patterns Skill

## Index Strategy

```sql
-- B-tree (default) — equality and range queries
CREATE INDEX idx_users_email ON users(email);

-- Partial index — only index subset of rows
CREATE INDEX idx_active_users ON users(email) WHERE active = true;

-- Covering index — avoid heap fetch
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at DESC)
INCLUDE (total_amount, status);

-- GIN index for JSONB
CREATE INDEX idx_metadata ON events USING GIN(metadata);

-- Always CONCURRENTLY in production (no lock)
CREATE INDEX CONCURRENTLY idx_new ON large_table(column);
```

## EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.*, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.active = true
GROUP BY u.id;
```

Red flags: `Seq Scan` on large tables, `Hash Join` with large batches, high `rows` estimate mismatch.

## CTEs

```sql
-- Materialized CTE (PostgreSQL 12+: non-materialized by default)
WITH RECURSIVE org_tree AS (
    SELECT id, name, parent_id, 0 AS depth
    FROM departments WHERE parent_id IS NULL
    UNION ALL
    SELECT d.id, d.name, d.parent_id, t.depth + 1
    FROM departments d
    JOIN org_tree t ON d.parent_id = t.id
)
SELECT * FROM org_tree ORDER BY depth, name;
```

## Window Functions

```sql
SELECT
    user_id,
    order_date,
    total_amount,
    SUM(total_amount) OVER (PARTITION BY user_id ORDER BY order_date) AS running_total,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date DESC) AS recency_rank
FROM orders;
```

## JSONB

```sql
-- Query JSONB
SELECT data->>'name', data->'address'->>'city'
FROM profiles
WHERE data @> '{"verified": true}'::jsonb;

-- Update nested key
UPDATE profiles
SET data = jsonb_set(data, '{address, city}', '"Berlin"')
WHERE id = 1;
```

## Partitioning

```sql
-- Range partitioning by date
CREATE TABLE events (
    id BIGSERIAL,
    created_at TIMESTAMPTZ NOT NULL,
    payload JSONB
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2026_q1 PARTITION OF events
    FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
```

## Connection Pooling

Use PgBouncer in transaction mode for most workloads:
```ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

## Maintenance

```sql
-- Table bloat check
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;

-- Missing indexes
SELECT * FROM pg_stat_user_tables WHERE seq_scan > idx_scan AND n_live_tup > 10000;
```

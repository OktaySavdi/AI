---
name: "clickhouse-io"
description: >
  ClickHouse analytics: table design (MergeTree family), aggregations, materialized
  views, data ingestion patterns, and query optimization. Activate for ClickHouse work.
metadata:
  version: 1.0.0
  category: engineering
---

# ClickHouse I/O Skill

## Table Design — MergeTree Family

```sql
-- Main analytics table
CREATE TABLE events (
    event_date    Date,
    event_time    DateTime,
    user_id       UInt64,
    event_type    LowCardinality(String),
    properties    Map(String, String),
    session_id    String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_type, user_id, event_time)
SETTINGS index_granularity = 8192;
```

### Engine Selection

| Engine | Use Case |
|---|---|
| `MergeTree` | General analytics, append-only |
| `ReplacingMergeTree` | Deduplication by ORDER BY key |
| `SummingMergeTree` | Pre-aggregation of numeric columns |
| `AggregatingMergeTree` | Materialized views with partial states |
| `ReplicatedMergeTree` | HA with ZooKeeper/ClickHouse Keeper |

## Materialized Views

```sql
-- Aggregate at ingest time
CREATE MATERIALIZED VIEW daily_event_counts
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, event_type)
AS SELECT
    event_date,
    event_type,
    count() AS cnt,
    uniqState(user_id) AS unique_users_state
FROM events
GROUP BY event_date, event_type;

-- Query the materialized view
SELECT event_date, event_type, sum(cnt), uniqMerge(unique_users_state)
FROM daily_event_counts
GROUP BY event_date, event_type;
```

## Efficient Inserts

```sql
-- Batch inserts — never insert row by row
INSERT INTO events
SELECT * FROM generateRandom('event_date Date, user_id UInt64', 1, 10, 2)
LIMIT 1000000;

-- Buffer table to batch small inserts
CREATE TABLE events_buffer AS events
ENGINE = Buffer(default, events, 16, 10, 100, 10000, 1000000, 10000000, 100000000);
```

## Query Optimization

```sql
-- Use prewhere for conditions on sparse columns
SELECT * FROM events
PREWHERE event_type = 'purchase'  -- applied before reading full row
WHERE user_id = 12345;

-- Approximate aggregations for dashboards
SELECT
    uniq(user_id) AS approx_users,    -- faster than COUNT(DISTINCT)
    quantile(0.95)(response_ms) AS p95
FROM events
WHERE event_date >= today() - 7;

-- Use sampling for exploratory queries
SELECT count() FROM events SAMPLE 0.1;  -- 10% sample, 10x faster
```

## Data Types

```sql
-- Use LowCardinality for string columns with < 10k distinct values
event_type LowCardinality(String)

-- Use Nullable sparingly — it has overhead
-- Prefer default values instead of NULL

-- Codec compression
bytes_transferred UInt64 CODEC(Delta, ZSTD)
```

## Ingestion Patterns

```bash
# CSV via clickhouse-client
clickhouse-client --query "INSERT INTO events FORMAT CSV" < data.csv

# Via HTTP interface
curl -X POST "http://localhost:8123/?query=INSERT+INTO+events+FORMAT+JSONEachRow" \
  --data-binary @events.ndjson
```

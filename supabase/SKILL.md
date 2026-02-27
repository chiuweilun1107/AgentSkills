---
name: supabase
description: 'Supabase development and self-hosted operations. Use when user mentions supabase, database query, migration, Edge Function, RLS policy, pgvector, vector search, backup, health check, or says "資料庫", "supabase掛了", "備份", "向量搜尋", "RAG". Covers CLI ops, Docker management, schema design, and vector/RAG pipelines.'
---

# Supabase Expert (Development + Operations)

Unified skill for Supabase development and self-hosted instance management. Covers Edge Functions, schema design, RLS, migrations, pgvector/RAG, CLI operations, Docker management, and troubleshooting.

## When to Use

- Writing Edge Functions, RLS policies, migrations, DB functions
- Managing self-hosted Supabase (health check, start/stop, backup)
- Building RAG/vector search with pgvector
- Querying or modifying the database
- Troubleshooting Supabase issues

## When NOT to Use

- General PostgreSQL questions unrelated to Supabase
- Supabase cloud dashboard operations (use web UI)

## Decision Flow

```
User mentions Supabase
    │
    ├─ Writing code? (Edge Functions, RLS, schema, functions)
    │   → Read references/development.md
    │
    ├─ Operations? (health, start/stop, backup, Docker, config)
    │   → Read references/operations.md
    │
    ├─ Vector/RAG? (embedding, similarity search, pgvector)
    │   → Read references/pgvector.md
    │
    └─ Quick query or check?
        → Use commands below
```

## Quick Reference

### Self-Hosted Environment

```bash
# Project directory (REQUIRED for all CLI commands)
SUPABASE_DIR="$HOME/.openclaw/workspace/projects/project-20260202-144247/supabase"

# Health check
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep supabase

# Status
supabase status --workdir "$SUPABASE_DIR"
```

### Database Access

```bash
# Direct psql (via Docker — no local psql needed)
docker exec supabase_db_project-20260202-144247 psql -U postgres -c "SQL_HERE"

# Connection string
# postgresql://postgres:postgres@127.0.0.1:54322/postgres
```

### Key Ports

| Service | Port | URL |
|---------|------|-----|
| API (Kong) | 54321 | http://127.0.0.1:54321 |
| Database | 54322 | postgresql://postgres:postgres@127.0.0.1:54322/postgres |
| Studio | 54323 | http://127.0.0.1:54323 |
| MCP | — | http://127.0.0.1:54321/mcp |

### Migrations

```bash
# List applied
supabase migration list --workdir "$SUPABASE_DIR"

# Generate from schema diff
supabase db diff -f <name> --workdir "$SUPABASE_DIR"

# Create empty migration
supabase migration new <name> --workdir "$SUPABASE_DIR"

# Reset local DB (applies all migrations + seed)
supabase db reset --workdir "$SUPABASE_DIR"
```

### Start / Stop

```bash
supabase start --workdir "$SUPABASE_DIR"
supabase stop --workdir "$SUPABASE_DIR"
```

### Backup & Restore

```bash
# Backup
docker exec supabase_db_<project-id> pg_dump -U postgres -Fc postgres > backup.dump

# Restore
docker exec -i supabase_db_<project-id> pg_restore -U postgres -d postgres --clean < backup.dump
```

### Type Generation

```bash
supabase gen types typescript --local --workdir "$SUPABASE_DIR" > types/supabase.ts
```

## Critical Rules (Non-Obvious)

### Edge Functions
- **No bare specifiers**: `npm:@supabase/supabase-js` not `@supabase/supabase-js`
- **Version required**: `npm:express@4.18.2` not `npm:express`
- **Use `Deno.serve`** not old `import { serve } from "https://deno.land/std/..."`
- **Writes only to `/tmp`**
- **Pre-populated env vars**: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_DB_URL`
- **Multi-route**: prefix with `/function-name`, use Hono or Express

### RLS Performance
- **Always wrap auth functions**: `(select auth.uid())` not `auth.uid()` — enables initPlan caching
- **Specify roles**: `to authenticated` prevents policy running for `anon`
- **Avoid joins** in policies — rewrite as `IN (select ...)` subqueries
- **Index columns** used in policies

### Database Functions
- Default to `SECURITY INVOKER`
- Always `set search_path = ''` and use fully qualified names
- Prefer `IMMUTABLE` or `STABLE` when no side effects

### Declarative Schema
- Schema files in `supabase/schemas/`, migrations auto-generated via `supabase db diff`
- **Stop local env before diffing**: `supabase stop` → update schema → `supabase db diff -f <name>`
- Known diff limitations: DML, view ownership, materialized views, RLS alterations, column privileges, comments, partitions

## Current DB Schema

```
alice schema:     broker_chip_signals, broker_daily_signals, broker_winrate_stats,
                  broker_yearly_agg, expense_categories, expenses, habit_logs,
                  habits, portfolio_holdings, portfolio_transactions, scan_results, tasks

public schema:    alert_events, alerts, app_runs, app_settings, backtest_metrics,
                  backtest_runs, backtest_trades, candles, instruments,
                  watchlist_groups, watchlist_items
```

## Active Services (9 containers, ~900MB)

db, kong, rest, auth, studio, pg_meta, storage, realtime, edge_runtime

**Disabled**: analytics, vector (log collector), inbucket — saves ~870MB

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `supabase status` fails | Add `--workdir` pointing to dir with `config.toml` |
| Container name mismatch | Names use project ID: `supabase_db_project-20260202-144247` |
| Port already in use | `lsof -i :54322` to find conflict |
| DB connection refused | `docker inspect --format='{{.State.Health.Status}}' <container>` |
| Migrations out of sync | `supabase migration list` then `supabase db reset` |
| Edge Function deploy fail | Check `npm:` prefix, version pinning, `/tmp` writes only |
| RLS slow queries | Wrap `auth.uid()` in `(select ...)`, add indexes, minimize joins |
| No psql on host | Use `docker exec supabase_db_<id> psql -U postgres -c "SQL"` |

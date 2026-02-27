---
name: supabase-ops
description: 'Self-hosted Supabase operations and management via CLI and Docker. Use when user mentions supabase status, health check, database query, migration, backup, restore, supabase start/stop, container issues, or says "supabase掛了", "資料庫", "備份", "db query". Covers CLI commands, Docker container management, pg_dump/restore, and troubleshooting.'
---

# Supabase Operations (Self-Hosted)

Manage self-hosted Supabase instances via CLI and Docker. Covers health checks, database operations, migrations, backup/restore, and troubleshooting.

## When to Use

- Check Supabase service health or container status
- Run SQL queries against the database
- Create/apply/manage migrations
- Backup or restore the database
- Start, stop, or restart Supabase services
- Troubleshoot container or connection issues
- User says "supabase掛了", "db query", "備份資料庫"

## When NOT to Use

- Writing Edge Functions, RLS policies, or schema design → use `supabase` skill
- Supabase cloud-hosted projects (this skill is for self-hosted)

## Step 1: Identify Project Directory (CRITICAL)

Self-hosted Supabase requires `--workdir` for all CLI commands. The project directory contains `config.toml`.

```bash
# Find Supabase project directories
find ~ -name "config.toml" -path "*/supabase/*" 2>/dev/null

# Common location on Mac Mini (OpenClaw)
SUPABASE_DIR="$HOME/.openclaw/workspace/projects/project-20260202-144247/supabase"
```

**Every `supabase` CLI command needs:**
```bash
supabase <command> --workdir "$SUPABASE_DIR"
```

## Step 2: Health Check

### Quick Status
```bash
# Check all Supabase containers
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep supabase

# Supabase CLI status (needs workdir)
supabase status --workdir "$SUPABASE_DIR"
```

### API Health
```bash
# REST API health
curl -s http://localhost:54321/rest/v1/ -H "apikey: <anon-key>" | head -20

# Auth health
curl -s http://localhost:54321/auth/v1/health

# Get keys from status
supabase status --workdir "$SUPABASE_DIR" 2>/dev/null | grep -E "anon key|service_role"
```

### Container-Level Check
```bash
# Specific container health
docker inspect --format='{{.State.Health.Status}}' supabase_db_<project-id>

# Container logs (last 50 lines)
docker logs --tail 50 supabase_db_<project-id>

# Resource usage
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}' | grep supabase
```

## Step 3: Start / Stop / Restart

```bash
# Start all services
supabase start --workdir "$SUPABASE_DIR"

# Stop all services
supabase stop --workdir "$SUPABASE_DIR"

# Stop and remove volumes (DESTRUCTIVE - resets data)
supabase stop --workdir "$SUPABASE_DIR" --no-backup

# Restart a single container
docker restart supabase_db_<project-id>

# Restart all Supabase containers
docker ps --format '{{.Names}}' | grep supabase | xargs docker restart
```

## Step 4: Database Operations

### Direct SQL via CLI
```bash
# Interactive psql
supabase db execute --workdir "$SUPABASE_DIR" "SELECT 1"

# Run SQL file
supabase db execute --workdir "$SUPABASE_DIR" < query.sql

# Via psql directly (port 54322)
psql postgresql://postgres:postgres@localhost:54322/postgres -c "SELECT * FROM instruments LIMIT 5"
```

### Common Queries
```bash
# List all tables
psql postgresql://postgres:postgres@localhost:54322/postgres -c "
  SELECT schemaname, tablename
  FROM pg_tables
  WHERE schemaname = 'public'
  ORDER BY tablename;
"

# Table row counts
psql postgresql://postgres:postgres@localhost:54322/postgres -c "
  SELECT relname AS table, n_live_tup AS rows
  FROM pg_stat_user_tables
  ORDER BY n_live_tup DESC;
"

# Database size
psql postgresql://postgres:postgres@localhost:54322/postgres -c "
  SELECT pg_size_pretty(pg_database_size('postgres'));
"

# Active connections
psql postgresql://postgres:postgres@localhost:54322/postgres -c "
  SELECT count(*) as connections, state
  FROM pg_stat_activity
  GROUP BY state;
"
```

## Step 5: Migrations

```bash
# List applied migrations
supabase migration list --workdir "$SUPABASE_DIR"

# Create new migration from schema diff
supabase db diff -f <migration_name> --workdir "$SUPABASE_DIR"

# Apply pending migrations (local)
supabase db reset --workdir "$SUPABASE_DIR"

# Push migrations to remote
supabase db push --workdir "$SUPABASE_DIR"

# Create empty migration file
supabase migration new <name> --workdir "$SUPABASE_DIR"
```

## Step 6: Backup & Restore

### Backup
```bash
# Full database dump
docker exec supabase_db_<project-id> pg_dump -U postgres -Fc postgres > backup_$(date +%Y%m%d).dump

# SQL format (human-readable)
docker exec supabase_db_<project-id> pg_dump -U postgres postgres > backup_$(date +%Y%m%d).sql

# Specific tables only
docker exec supabase_db_<project-id> pg_dump -U postgres -t public.instruments -t public.watchlists postgres > tables_backup.sql

# Schema only (no data)
docker exec supabase_db_<project-id> pg_dump -U postgres --schema-only postgres > schema_backup.sql
```

### Restore
```bash
# From custom format dump
docker exec -i supabase_db_<project-id> pg_restore -U postgres -d postgres --clean < backup.dump

# From SQL file
docker exec -i supabase_db_<project-id> psql -U postgres postgres < backup.sql

# Specific table restore
docker exec -i supabase_db_<project-id> psql -U postgres postgres < tables_backup.sql
```

## Step 7: Configuration

### View Config
```bash
cat "$SUPABASE_DIR/config.toml"
```

### Key Ports (Default)
| Service | Port |
|---------|------|
| API (Kong) | 54321 |
| Database | 54322 |
| Studio | 54323 |
| Inbucket (Email) | 54324 |
| Analytics | 54327 |

### Type Generation
```bash
supabase gen types typescript --local --workdir "$SUPABASE_DIR" > types/supabase.ts
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `supabase status` fails | Add `--workdir` pointing to project dir with `config.toml` |
| Container name mismatch | Use `docker ps \| grep supabase` to find actual container names |
| "No such container" | Containers use project-specific names: `supabase_db_<project-id>` |
| Port already in use | `lsof -i :54322` to find conflicting process |
| DB connection refused | Check if db container is healthy: `docker inspect --format='{{.State.Health.Status}}' <container>` |
| Out of memory | `docker stats --no-stream \| grep supabase` — analytics container uses ~660MB |
| Migrations out of sync | `supabase migration list --workdir "$SUPABASE_DIR"` then `supabase db reset` |
| Auth not working | Check auth container logs: `docker logs supabase_auth_<project-id>` |
| Slow queries | `psql -c "SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10"` |

## Architecture Notes

Self-hosted Supabase runs 11 Docker containers:
- **db** (Postgres) — primary database
- **kong** — API gateway (port 54321)
- **auth** — GoTrue authentication
- **rest** (PostgREST) — auto-generated REST API
- **realtime** — WebSocket change subscriptions
- **storage** — file storage (S3-compatible)
- **studio** — web dashboard (port 54323)
- **pg_meta** — Postgres metadata API
- **inbucket** — local email testing
- **vector** — log collection
- **analytics** — usage analytics (~660MB RAM)

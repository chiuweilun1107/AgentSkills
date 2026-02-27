# Supabase Operations Reference (Self-Hosted)

## Environment

- **Project dir**: `~/.openclaw/workspace/projects/project-20260202-144247/supabase`
- **Container naming**: `supabase_<service>_project-20260202-144247`
- **DB access**: `docker exec supabase_db_project-20260202-144247 psql -U postgres -c "SQL"`
- **Config**: `config.toml` in project dir
- **LaunchAgent**: `com.supabase.autostart` (auto-starts after Docker ready)

## Health Checks

### Quick
```bash
# All containers
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep supabase

# CLI status
supabase status --workdir "$SUPABASE_DIR"

# API health
curl -s http://localhost:54321/auth/v1/health
```

### Detailed
```bash
# Specific container health
docker inspect --format='{{.State.Health.Status}}' supabase_db_project-20260202-144247

# Container logs
docker logs --tail 50 supabase_db_project-20260202-144247

# Resource usage
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}' | grep supabase
```

### Database Health
```bash
docker exec supabase_db_project-20260202-144247 psql -U postgres -c "
  SELECT count(*) as connections, state FROM pg_stat_activity GROUP BY state;
"

docker exec supabase_db_project-20260202-144247 psql -U postgres -c "
  SELECT pg_size_pretty(pg_database_size('postgres')) as db_size;
"

docker exec supabase_db_project-20260202-144247 psql -U postgres -c "
  SELECT relname AS table, n_live_tup AS rows
  FROM pg_stat_user_tables ORDER BY n_live_tup DESC;
"
```

## Start / Stop / Restart

```bash
# Full start/stop
supabase start --workdir "$SUPABASE_DIR"
supabase stop --workdir "$SUPABASE_DIR"

# Stop with data backup to Docker volume (default)
supabase stop --workdir "$SUPABASE_DIR"

# Stop and REMOVE volumes (DESTRUCTIVE)
supabase stop --workdir "$SUPABASE_DIR" --no-backup

# Restart single container
docker restart supabase_db_project-20260202-144247

# Restart all
docker ps --format '{{.Names}}' | grep supabase | xargs docker restart
```

## Backup & Restore

### Backup
```bash
# Custom format (recommended — supports selective restore)
docker exec supabase_db_project-20260202-144247 pg_dump -U postgres -Fc postgres > backup_$(date +%Y%m%d).dump

# SQL format (human-readable)
docker exec supabase_db_project-20260202-144247 pg_dump -U postgres postgres > backup_$(date +%Y%m%d).sql

# Specific tables
docker exec supabase_db_project-20260202-144247 pg_dump -U postgres \
  -t public.instruments -t public.candles postgres > tables_backup.sql

# Schema only
docker exec supabase_db_project-20260202-144247 pg_dump -U postgres --schema-only postgres > schema.sql

# Specific schema
docker exec supabase_db_project-20260202-144247 pg_dump -U postgres -n alice postgres > alice_backup.sql
```

### Restore
```bash
# From custom format
docker exec -i supabase_db_project-20260202-144247 pg_restore -U postgres -d postgres --clean < backup.dump

# From SQL
docker exec -i supabase_db_project-20260202-144247 psql -U postgres postgres < backup.sql
```

## Configuration

### config.toml Key Settings

```toml
[api]
schemas = ["public", "graphql_public", "alice"]  # Exposed via REST API
max_rows = 1000

[db]
port = 54322
major_version = 17

[realtime]
enabled = true

[studio]
enabled = true
port = 54323

[analytics]
enabled = false  # Disabled — saves ~725MB RAM

[inbucket]
enabled = false  # Disabled — email testing not needed
```

### Changing Config
1. Edit `config.toml`
2. `supabase stop --workdir "$SUPABASE_DIR"`
3. `supabase start --workdir "$SUPABASE_DIR"`

## Active Architecture (9 containers, ~900MB)

| Container | Purpose | RAM |
|-----------|---------|-----|
| db | PostgreSQL 17 | ~260MB |
| kong | API gateway (port 54321) | ~140MB |
| rest | PostgREST auto-REST API | ~130MB |
| auth | GoTrue authentication | ~15MB |
| studio | Web dashboard (port 54323) | ~270MB |
| pg_meta | Postgres metadata API (Studio uses) | ~150MB |
| storage | S3-compatible file storage | ~185MB |
| realtime | WebSocket change subscriptions | ~275MB |
| edge_runtime | Deno Edge Functions runtime | ~100MB |

**Disabled**: analytics (~725MB), vector/log collector (~117MB), inbucket (~27MB)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `supabase status` fails | Add `--workdir` to point at dir with `config.toml` |
| "No such container" | Container names include project ID: `supabase_db_project-20260202-144247` |
| Port conflict | `lsof -i :54322` to find conflicting process |
| DB connection refused | Check health: `docker inspect --format='{{.State.Health.Status}}' <container>` |
| Out of memory | `docker stats --no-stream \| grep supabase` — consider disabling more services |
| Migrations out of sync | `supabase migration list` then `supabase db reset` |
| Auth not working | `docker logs supabase_auth_project-20260202-144247` |
| After config change | Must `supabase stop` then `supabase start` to apply |
| Docker not starting | Check LaunchAgent: `launchctl list \| grep supabase` |
| Slow queries | Enable `pg_stat_statements`: check `total_exec_time` |

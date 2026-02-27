# Supabase Development Reference

## Edge Functions (TypeScript/Deno)

### Import Rules

```tsx
// CORRECT — npm: prefix with version
import express from "npm:express@4.18.2";
import { createClient } from "npm:@supabase/supabase-js@2";

// CORRECT — jsr: prefix
import { z } from "jsr:@zod/zod@3";

// CORRECT — Node built-in
import process from "node:process";
import { randomBytes } from "node:crypto";

// WRONG — bare specifier (will fail)
import express from "express";

// WRONG — old deno.land serve
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
```

### Function Template

```tsx
Deno.serve(async (req: Request) => {
  const { method, url } = req;
  const params = new URL(url).searchParams;

  // Pre-populated env vars (no setup needed):
  // SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_DB_URL
  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;

  return new Response(JSON.stringify({ ok: true }), {
    headers: { "Content-Type": "application/json" },
  });
});
```

### Key Rules

- **Multi-route**: use Hono or Express, prefix routes with `/function-name`
- **Shared code**: put in `supabase/functions/_shared/`, import with relative path
- **No cross-deps**: Edge Functions must not import from other Edge Functions
- **File writes**: `/tmp` directory ONLY
- **Background tasks**: `EdgeRuntime.waitUntil(promise)` — do NOT assume it's in request context
- **Secrets**: `supabase secrets set --env-file path/to/env-file`

### Supabase.ai Embedding (Built-in)

```tsx
const model = new Supabase.ai.Session('gte-small');

Deno.serve(async (req: Request) => {
  const { text } = await req.json();
  const embedding = await model.run(text, { mean_pool: true, normalize: true });
  return new Response(JSON.stringify(embedding), {
    headers: { "Content-Type": "application/json" },
  });
});
```

---

## Declarative Schema Management

### Workflow

1. **Stop local env**: `supabase stop`
2. **Update schema files** in `supabase/schemas/` (lexicographic execution order)
3. **Generate migration**: `supabase db diff -f <migration_name>`
4. **Review** generated SQL in `supabase/migrations/`
5. **Start**: `supabase start`

### Schema File Rules

- One file per entity (table, view, function)
- Append new columns at end of table definition (prevents unnecessary diffs)
- Name files for correct dependency order

### diff Tool Limitations (Use Versioned Migrations Instead)

- DML statements (insert/update/delete)
- View ownership, grants, security invoker on views
- Materialized views
- ALTER POLICY statements
- Column privileges
- Comments, partitions
- Schema privileges, domain statements

---

## Database Functions

### Template

```sql
create or replace function public.my_function(param_name bigint)
returns text
language plpgsql
security invoker
set search_path = ''
as $$
begin
  -- Always use fully qualified names: public.table_name
  return 'result';
end;
$$;
```

### Rules

- Default to `SECURITY INVOKER` (safer access control)
- Always `set search_path = ''` + fully qualified names
- Use `IMMUTABLE` or `STABLE` when no side effects
- Reference parameter by function name: `my_function.param_name`

### Trigger Template

```sql
create or replace function public.update_updated_at()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

create trigger set_updated_at
before update on public.my_table
for each row execute function public.update_updated_at();
```

---

## Row Level Security (RLS)

### Policy Rules

- **Separate policies per operation**: SELECT, INSERT, UPDATE, DELETE (never `FOR ALL`)
- **Separate per role**: `to authenticated` and `to anon` individually
- **Always enable RLS** on new tables, even for public access

### Operation Requirements

| Operation | USING | WITH CHECK |
|-----------|-------|------------|
| SELECT | Yes | No |
| INSERT | No | Yes |
| UPDATE | Yes (usually) | Yes |
| DELETE | Yes | No |

### Performance Patterns

```sql
-- GOOD: initPlan caching with (select ...)
create policy "Users own records" on public.items
for select to authenticated
using ( (select auth.uid()) = user_id );

-- BAD: function called per row
using ( auth.uid() = user_id );
```

```sql
-- GOOD: no join, filter into set
create policy "Team access" on public.items
for select to authenticated
using (
  team_id in (
    select team_id from public.team_members
    where user_id = (select auth.uid())
  )
);

-- BAD: joins source to target
using (
  (select auth.uid()) in (
    select user_id from public.team_members
    where team_members.team_id = team_id  -- join!
  )
);
```

### Auth Helpers

- `auth.uid()` — current user ID
- `auth.jwt()` — full JWT (access `raw_app_meta_data` for authorization)
- `auth.jwt()->>'aal'` — assurance level for MFA checks

### Naming

- Tables: plural snake_case (`instruments`, `watchlist_items`)
- Columns: singular snake_case (`user_id`, `created_at`)
- PK: `id bigint generated always as identity primary key`
- FK: `<singular_table>_id` (e.g., `author_id references authors(id)`)
- Always add table comment: `comment on table public.books is 'Description';`

---

## Migration Files

### Naming Format

```
YYYYMMDDHHmmss_short_description.sql
```
Example: `20260227120000_add_embeddings_table.sql`

### Rules

- Always enable RLS on new tables
- Granular policies (one per operation per role)
- Include header comment with purpose
- Add comments for destructive operations (DROP, TRUNCATE, ALTER COLUMN)

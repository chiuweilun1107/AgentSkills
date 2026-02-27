# pgvector & RAG Reference

## Enable pgvector

```sql
create extension if not exists vector with schema extensions;
```

## Table Schema

```sql
-- Parent documents
create table public.documents (
  id bigint primary key generated always as identity,
  name text not null,
  source text,
  metadata jsonb default '{}',
  created_at timestamptz not null default now()
);

-- Chunked sections with embeddings
create table public.document_sections (
  id bigint primary key generated always as identity,
  document_id bigint not null references public.documents (id) on delete cascade,
  content text not null,
  metadata jsonb default '{}',
  embedding extensions.vector(768),  -- adjust to your model's dimensions
  created_at timestamptz not null default now()
);

alter table public.documents enable row level security;
alter table public.document_sections enable row level security;
comment on table public.documents is 'RAG document store';
comment on table public.document_sections is 'Chunked document sections with vector embeddings';
```

## Embedding Model Dimensions

| Model | Provider | Dimensions | Notes |
|-------|----------|------------|-------|
| `nomic-embed-text` | Ollama (local) | 768 | Best local option, 8K context |
| `gte-small` | Supabase.ai (built-in) | 384 | Lightweight, no API key needed |
| `text-embedding-3-small` | OpenAI | 1536 | Best cloud price/performance |
| `text-embedding-3-large` | OpenAI | 3072 | Highest quality |
| `text-embedding-004` | Google | 768 | Gemini ecosystem |
| `mxbai-embed-large` | Ollama (local) | 1024 | Strong open-source |

**Rule**: Never mix models in the same embedding column.

## Index: HNSW vs IVFFlat

| | HNSW | IVFFlat |
|---|---|---|
| Search speed | Fast (log scale) | Slower |
| Build time | Slow | 32x faster |
| Index size | ~3x larger | Compact |
| Data updates | Handles well | Needs rebuild |
| **Use when** | **Production** | **Prototyping** |

### HNSW (Recommended for Production)

```sql
-- Build index (set memory high first)
set maintenance_work_mem = '512MB';

create index on public.document_sections
using hnsw (embedding extensions.vector_cosine_ops)
with (m = 16, ef_construction = 64);

-- Tune search quality per query
set local hnsw.ef_search = 100;
```

- `m` (default 16): connections per node. Higher = better recall, more RAM
- `ef_construction` (default 64, must be >= 2*m): build quality
- `ef_search` (default 40): query-time quality tuning

### IVFFlat (Quick Prototyping)

```sql
create index on public.document_sections
using ivfflat (embedding extensions.vector_cosine_ops)
with (lists = 100);  -- rule: rows / 1000

set local ivfflat.probes = 10;  -- start with sqrt(lists)
```

## Distance Operators

| Operator | Metric | Index Ops | Default |
|----------|--------|-----------|---------|
| `<=>` | Cosine distance | `vector_cosine_ops` | **Use this** |
| `<#>` | Neg. inner product | `vector_ip_ops` | Normalized embeddings |
| `<->` | L2 (Euclidean) | `vector_l2_ops` | When magnitude matters |

**Note**: `<=>` returns distance (0–2), not similarity. Similarity = `1 - distance`.

## Similarity Search Function

```sql
create or replace function public.match_documents (
  query_embedding extensions.vector(768),
  match_threshold float default 0.78,
  match_count int default 10
)
returns table (
  id bigint,
  document_id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language sql stable
set search_path = ''
as $$
  select
    ds.id,
    ds.document_id,
    ds.content,
    ds.metadata,
    1 - (ds.embedding <=> query_embedding) as similarity
  from public.document_sections ds
  where ds.embedding <=> query_embedding < 1 - match_threshold
  order by ds.embedding <=> query_embedding asc
  limit least(match_count, 200);
$$;
```

### Call via RPC (PostgREST can't use pgvector operators directly)

```bash
# Via curl
curl -X POST 'http://localhost:54321/rest/v1/rpc/match_documents' \
  -H "apikey: <anon-key>" \
  -H "Content-Type: application/json" \
  -d '{"query_embedding": [0.1, 0.2, ...], "match_threshold": 0.78, "match_count": 5}'
```

```python
# Via supabase-py
result = supabase.rpc('match_documents', {
    'query_embedding': embedding_list,
    'match_threshold': 0.78,
    'match_count': 10
}).execute()
```

## Hybrid Search (Vector + Keyword)

```sql
create or replace function public.hybrid_search (
  query_text text,
  query_embedding extensions.vector(768),
  match_count int default 10,
  keyword_weight float default 0.3,
  vector_weight float default 0.7
)
returns table (
  id bigint,
  content text,
  metadata jsonb,
  score float
)
language sql stable
set search_path = ''
as $$
  with vector_results as (
    select ds.id, ds.content, ds.metadata,
           1 - (ds.embedding <=> query_embedding) as similarity
    from public.document_sections ds
    order by ds.embedding <=> query_embedding asc
    limit match_count * 2
  ),
  keyword_results as (
    select ds.id, ds.content, ds.metadata,
           ts_rank(to_tsvector('english', ds.content),
                   plainto_tsquery('english', query_text)) as rank
    from public.document_sections ds
    where to_tsvector('english', ds.content) @@ plainto_tsquery('english', query_text)
    limit match_count * 2
  )
  select
    coalesce(v.id, k.id),
    coalesce(v.content, k.content),
    coalesce(v.metadata, k.metadata),
    (coalesce(v.similarity, 0) * vector_weight +
     coalesce(k.rank, 0) * keyword_weight) as score
  from vector_results v
  full outer join keyword_results k on v.id = k.id
  order by score desc
  limit match_count;
$$;
```

## Chunking Strategy

| Query Type | Chunk Size | Use Case |
|------------|-----------|----------|
| Factoid (names, dates) | 256–512 tokens | FAQ, knowledge bases |
| Analytical (explanations) | 1024+ tokens | Reports, documentation |
| **General (start here)** | **400–512 tokens** | Most RAG applications |

- **Overlap**: 10–20% of chunk size (50–100 tokens for 500-token chunks)
- **Metadata per chunk**: `chunk_index`, `total_chunks`, `source_file`, `heading`, `page_number`

## Performance Tips

- **GIN index on metadata** for filtered queries:
  ```sql
  create index on public.document_sections using gin (metadata);
  ```
- **Iterative scan** for filtered vector search:
  ```sql
  set local hnsw.iterative_scan = relaxed_order;
  ```
- Batch inserts (not row-by-row) for large datasets
- pgvector works well up to ~5–10M vectors
- `least(match_count, 200)` in functions to cap results

## RAG Pipeline Overview

```
Documents → Chunk (400-512 tokens) → Embed (model API) → Store in document_sections
                                                              │
User Query → Embed query → match_documents() RPC → Top-K results → LLM context
```

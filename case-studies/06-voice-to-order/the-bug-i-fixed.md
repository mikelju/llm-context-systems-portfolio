# A Real Bug I Fixed — the vector search that never used its index

## Symptom

In production (Cloud Run + Supabase cloud), **every** RPC call to `buscar_articulos` and
`buscar_historicos` started failing with Postgres error `57014`:

```
canceling statement due to statement timeout
```

Consistently, not intermittently. The frontend showed "SIN OPCIONES" for every line of every order —
the product was effectively down for its core function. Detected 2026-03, in the middle of normal
client usage.

## Root cause #1 — the SQL shape never triggered the index

pgvector only plans an index scan (IVFFlat/HNSW) when the query follows the pattern it recognizes:

```sql
ORDER BY embedding <=> query_vector LIMIT n
```

The functions instead filtered on a computed similarity and ordered by an alias:

```sql
WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
ORDER BY similarity DESC
```

That is a **full sequential scan** — a cosine distance computed against every row of the embeddings
table on every call. Under the Supabase `authenticated` role's default `statement_timeout` of **8s**,
the scan was cancelled before finishing. A red herring made it worse: we had just migrated the index
IVFFlat → HNSW, which changed nothing — because *no* index was being used. The `db_semaphore` allowing
10 concurrent searches meant 10 simultaneous sequential scans.

**The fix:** rewrite both functions around a CTE that isolates the index-friendly part —

```sql
WITH vector_matches AS (
  SELECT e.id_articulo, 1 - (e.embedding <=> query_embedding) AS similarity
  FROM embeddings e
  ORDER BY e.embedding <=> query_embedding     -- the pattern pgvector plans an index scan for
  LIMIT match_count * 3                        -- headroom for the filters below
)
SELECT c.id_articulo, c.articulo, c.fecha_ultima_compra, vm.similarity
FROM vector_matches vm JOIN catalogo c ON vm.id_articulo = c.id_articulo
WHERE c.is_active = TRUE AND vm.similarity > match_threshold
ORDER BY vm.similarity DESC LIMIT match_count;
```

(`supabase_utils/schema/functions/buscar_articulos.sql` and `buscar_historicos.sql` — the `×3`
headroom compensates for candidates dropped by `is_active`/threshold.) `EXPLAIN ANALYZE` confirmed
`Index Scan using embeddings_embedding_idx` at **220ms warm**.

## Root cause #2 — it *still* timed out, once a day

With the index provably in use, timeouts persisted — specifically on the **first order of the day**
(~06:13). Three factors compounding:

1. `statement_timeout` is **per-role** in Supabase: `authenticated` (what the API uses) = **8s**,
   while `postgres` = 2min — so the dev experience never reproduced production.
2. **Cold cache:** after hours idle, the HNSW pages aren't in `shared_buffers`. The recorded plan
   showed **347 disk reads vs 595 cache hits** on a cold run.
3. **Concurrency:** ~10 parallel first-queries all competing for that disk I/O.

**The fix:** scope a bigger timeout to exactly the two functions, nothing else:

```sql
CREATE OR REPLACE FUNCTION public.buscar_articulos(...)
LANGUAGE sql STABLE
SET statement_timeout = '30s'    -- overrides the role's 8s for this function only
```

Plus a follow-up mitigation: an HNSW **warmup query fired during `process-audio`** — the index warms
while the technician is still reviewing the transcription, so the real searches in Step 4 hit a warm
cache (plan 12.22).

## Result

Vector search stable in production since the second deploy (2026-03). Warm searches at 220ms; the
first-order-of-the-day case covered by the 30s scoped timeout + warmup. The remaining observation
(Cloud Run's own ~20s cold start with `min-instances 0`) is documented as a separate, measured-trigger
decision (~$15–20/month for `min-instances 1`).

## Why it's a good story

It is two root causes deep, and both are invisible in development: the planner silently chooses a
sequential scan (everything *works*, just 100× slower than intended), and the timeout that kills it is
per-role, so the `postgres`-role dev connection never failed. The debugging path — reproduce →
`EXPLAIN ANALYZE` → learn the planner's pattern → CTE → *still failing* → role config + cold-cache
forensics → scoped timeout + warmup — is exactly the kind of layered, evidence-driven debugging that
operating LLM systems on real infrastructure demands. And the fix is surgical: 30 seconds for two
functions, not a global timeout bump.

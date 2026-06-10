# The signature decision: productionizing the per-article pipeline

The product's hot path is **Step 4–5 of the request flow**: for each dictated line, search the learned
memory, search the catalog, fetch details, and re-rank with an LLM. A 21-line order means ~40+ DB
queries and ~21 LLM calls for a technician standing in a van. How that work is scheduled *is* the
product decision — it went through four documented stages, each driven by a production failure, and
the final shape is argued here.

## The problem

Sequential per-article processing made big orders unusable (the time grew linearly with lines).
But the naive fix — "just `asyncio.gather` everything" — failed in three different ways before the
architecture below held. The decision is not "use parallelism"; it is **where to put the limits**.

## The choice: parallel per article, with a named limit on every shared resource

From `search_service.py` (all values are the real code constants —
[`artifacts/pipeline-structure.json`](artifacts/pipeline-structure.json)):

| Mechanism | Real value | What it bounds |
|---|---|---|
| `asyncio.gather(*tasks, return_exceptions=True)` | one task per dictated line | wall-clock ≈ slowest line, not the sum; one line failing doesn't kill the order |
| `llm_semaphore = asyncio.Semaphore(10)` | 10 | concurrent Gemini re-rank calls (rate-limit safety) |
| `db_semaphore = asyncio.Semaphore(10)` | 10 | concurrent Supabase queries (socket/IO safety) |
| memory-first rule | threshold **0.75**, count 1 | the learned memory is searched before the 31,070-row catalog (threshold **0.5**, top **25**) and its hit is pinned above catalog candidates |
| deterministic fallback | sort by `(Historical_match desc, Score desc)` | if the re-rank LLM fails or returns bad JSON, ranking degrades to similarity order — never to an error |
| dedup rule | skip the catalog candidate whose description equals the memory hit | the technician never sees the same article twice |

The four stages it took to get here (each is in the project's plan 12.7, written as it happened):

1. **Sequential** — correct, unusably slow on real orders.
2. **Naive parallel** (`gather` over everything) — fast until production: Gemini rate-limit errors,
   then `httpx.ReadError` socket exhaustion; searches failed *silently* and the UI showed "SIN
   OPCIONES" for random lines.
3. **Semaphores** (LLM=10, DB=10) — bounded the damage, but errors persisted at lower frequency: the
   stack was *half* async (sync Supabase client inside `to_thread`), so OS-level socket pressure
   remained.
4. **True async end-to-end** — `create_async_client` for Supabase, every data-access function a real
   coroutine, `to_thread` removed. This refactor surfaced its own bug (one missed `await` in
   `order_delivery_service.py` returned a coroutine instead of data) — fixed, and the stack has been
   stable since.

The companion decision — **pgvector in managed Postgres rather than a dedicated vector DB or the
earlier FAISS pickles** — follows the same logic: the index lives where the data, auth and RLS already
live; one fewer system to operate; and the CTE/HNSW incident ([the-bug-i-fixed.md](the-bug-i-fixed.md))
was debuggable with plain `EXPLAIN ANALYZE` precisely because it's just Postgres.

## When I would do it differently / scale it

- **(a) Past ~50 lines per order or ~10× current request volume** — the per-request `gather` model
  starts to contend with itself (the two semaphores serialize across requests too, since Cloud Run
  packs concurrent requests per instance). The symptom to watch, *measured first*: p95 of
  `/orders/search-articles` rising while per-query DB time (the **220ms** warm index scan) stays flat —
  that gap is queueing, not search. The change it justifies: per-request semaphore budgets or a task
  queue (e.g. Cloud Tasks) with a worker pool, not bigger semaphores.
- **(b) If the rate-limit ceiling moves** — the LLM=10 limit encodes today's Gemini quota. The metric
  that justifies raising it is the re-rank fallback rate (how often ranking degraded to
  similarity-order) staying at zero while queue wait grows; raising it without that evidence just
  re-creates failure mode 2.
- **(c) If cold-cache timeouts recur** — the current mitigation is the function-level 30s timeout +
  an HNSW warmup query during `process-audio` (the user is still reviewing the transcription, so the
  warmup is free — plan 12.22). If monitoring showed first-order-of-the-day failures again, the
  measured trigger would justify `min-instances 1` (~$15–20/month) and/or a scheduled warmup, both
  documented in fix-1 — not a vector-DB migration, which none of the observed failures actually calls
  for.

The general rule this case taught me: **every scaling step here was justified by a production symptom,
and the two times I scaled without one (naive gather; the half-async refactor) produced the two worst
incidents.** Measurement-first is not a slogan in this project; it is the changelog.

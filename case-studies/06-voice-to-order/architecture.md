# Architecture

## Pattern

A classic product stack — SPA → API → managed Postgres — with the AI work concentrated in two
services and everything around it deterministic and observable:

```
React (Netlify, multi-step)  ──JWT──►  FastAPI (Cloud Run, Docker, VPC+static IP)
                                          ├─ transcription_service      whisper-1
                                          ├─ order_processing_service   gemini-2.5-flash, retry ×3
                                          ├─ search_service             asyncio.gather + 2 semaphores
                                          │     └─ Supabase RPC: buscar_historicos / buscar_articulos
                                          │        (pgvector HNSW, CTE pattern, SET timeout 30s)
                                          ├─ order_delivery_service     PDF + O365 email (workday cutoff 14h)
                                          ├─ erp_integration_service    ERP-X API
                                          └─ historical_data_service    upsert the learned memory
Supabase: catalogo (31,070) · embeddings · historico (1,001) · Auth/RLS
GitHub Actions (nightly): ERP-X ──► catalogo + embeddings sync
```

## Components (real modules)

| Layer | Real module / object | What it does |
|------|----------------------|--------------|
| API | `app/routers/order_processing_router.py`, `catalog_router.py` | `/orders/process-audio`, `/orders/search-articles`, `/orders/finalize`, `/orders/send`, `/catalog/search` — all JWT-protected |
| Transcription | `app/services/transcription_service.py` | `whisper-1` via `asyncio.to_thread` |
| Extraction | `app/services/order_processing_service.py` + `app/core/prompts.py` | dictated text → structured JSON (articles, quantities incl. decimals, observations); **retry ×3 with 2s·attempt backoff** after the truncated-JSON incident (fix-4) |
| Search | `app/services/search_service.py` + `search_utils.py` (`PgVectorSearcher`) | per-article parallel pipeline: memory-first → catalog → LLM re-rank with deterministic fallback — see [productionizing-concurrency.md](productionizing-concurrency.md) |
| Vector RPC | `supabase_utils/schema/functions/buscar_articulos.sql`, `buscar_historicos.sql` | the CTE pattern that actually triggers the HNSW index scan — see [the-bug-i-fixed.md](the-bug-i-fixed.md) |
| Model routing | `app/core/llm_wrapper.py` | one `get_llm_completion()` that routes by model-name prefix (`gpt-` / `claude-` / `gemini-`) — swapping providers is a config change, which is how fix-4's model swap shipped in hours |
| Delivery | `order_delivery_service.py`, `erp_integration_service.py`, `historical_data_service.py` | three **independent** channels (email+PDF, ERP-X, memory upsert), each with its own status light and its own chaos-injection point |
| Learning loop | `historico` table | every confirmed line upserts (dictated phrase → confirmed article, frequency++) — tomorrow's search is better than today's |
| Sync | GitHub Actions nightly job | pulls the ERP-X master catalog, diffs, re-embeds only what changed (timeouts 30s auth / 120s catalog) |
| Config/chaos | `app/core/config.py` | Pydantic settings, per-environment `.env.{ENVIRONMENT}`, `SIMULATE_FAILURE=erp,email,history` |

Structure + every constant: [`artifacts/pipeline-structure.json`](artifacts/pipeline-structure.json).

## Why the boring parts are the architecture

The model calls are 3 lines each. What made this deployable was everything around them: true-async
end-to-end (a half-async stack exhausted Windows/container sockets under `asyncio.gather`), bounded
concurrency, per-function DB timeouts, JWT + RLS, per-channel failure isolation, environment-split
configs, and a nightly sync so the search corpus can't drift from the ERP. The discarded earlier
stacks (Streamlit, Heroku, FAISS pickles — see [lessons-learned.md](lessons-learned.md)) are the
measure of how much of this was learned the hard way.

## Design principle

> Parallelism is free until it isn't: parallelize everything per-article, then put a named limit on
> every shared resource the parallelism touches — the LLM, the DB, and each delivery channel.

Diagrams: [assets/architecture-diagram.md](assets/architecture-diagram.md) ·
[assets/request-sequence.md](assets/request-sequence.md)

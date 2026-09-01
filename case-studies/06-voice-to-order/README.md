# Voice-to-Order — an Applied-AI Product, 0→1 to Production

A complete product for an industrial plumbing/HVAC supplier (client): field technicians **dictate a
purchase order by phone**, and the system turns the audio into a validated order in the client's ERP.
FastAPI backend on **Google Cloud Run** + React (Vite/TS) frontend on Netlify, Supabase
(**pgvector/HNSW** + Auth + RLS), Whisper transcription, Gemini extraction and re-ranking, a nightly
**ERP-X** catalog sync, PDF/email delivery, and a learned **historical memory** that gets better with
every confirmed order. This is the portfolio's productionization case: the interesting engineering is
not one model call — it's making ~30 concurrent model/DB calls per order fast, bounded and safe, and
surviving real-world failure modes (cold HNSW caches, statement timeouts, truncated LLM JSON, DNS
quirks).

> **Runnable replica:** this system is also published as a standalone public repository you can
> clone and run locally — Docker plus two commands, on the same anonymized data, no cloud and no
> API keys required: **[github.com/mikelju/voice-to-order](https://github.com/mikelju/voice-to-order)**.

## TL;DR (with real numbers)

- **Scale of the matching problem:** each dictated line is matched against a **31,070-row** synced ERP
  catalog plus a **1,001-row learned memory** (dictated phrase → confirmed article), via pgvector/HNSW
  with thresholds **0.75** (memory) / **0.5** (catalog), top-**25** candidates per article.
  *(`artifacts/catalog-stats.json`, `artifacts/historical-memory-sample.json`)*
- **Concurrency is the signature decision:** every article is processed end-to-end in parallel
  (`asyncio.gather`) under **two semaphores (LLM=10, DB=10)** after sequential search, naive
  parallelism (socket exhaustion) and a half-async stack all failed in production. *(`artifacts/pipeline-structure.json`)*
- **The production bug:** vector search died with statement timeouts because the SQL never triggered
  the HNSW index — rewritten as a CTE (`ORDER BY <=> LIMIT ×3`), the index scan takes **220ms warm**;
  the residual cold-cache case needed `SET statement_timeout = '30s'` over the role's **8s**.
  *(fix-1, [the-bug-i-fixed.md](the-bug-i-fixed.md))*
- **Extraction is evidenced, not claimed:** **47 hand-validated** (transcription → expected order)
  pairs, including a **21-line** dictated order with coreference ("dos espigas… *para esa manguera*").
  *(`artifacts/extraction-examples.json`)*
- **Failure is a feature:** a chaos switch (`SIMULATE_FAILURE=erp,email,history`) injects per-channel
  failures; each delivery channel (ERP, email, history) fails independently and reports its own status
  light to the UI. *(`artifacts/chaos-degradation.json`)*

## Review this case study in 5 minutes

1. [`demo/example_output.txt`](demo/example_output.txt) — the learned-memory lookup and the chaos
   degradation matrix, run offline over real data.
2. [`productionizing-concurrency.md`](productionizing-concurrency.md) — the signature decision: how the
   search went sequential → parallel → *correctly* parallel.
3. [`the-bug-i-fixed.md`](the-bug-i-fixed.md) — the HNSW statement-timeout hunt (two root causes deep).
4. [`artifacts/`](artifacts/) — real catalog stats, real learned memory, real validated extractions.

## The real problem

Field technicians phone in orders using **shop slang** ("taco fischer de 10", "tirafondo de 8",
"válvula de bola de media de latón") that has to land on **exact ERP article codes** out of 31,070 rows
whose canonical descriptions look like `VALVULA BOLA 1/2 LATON H PN30 PALANCA` — messy rows, missing
data and all. An order can have 20+ lines, the technician is standing in a van, and a wrong article
costs a return trip. The product has to transcribe, extract (quantities, decimals, observations,
coreference), match every line with ranked options, let a human confirm, and then deliver to **three
independent channels** (ERP API, PDF/email, the learning memory) — fast enough to be usable and safe
enough to be trusted.

## My role

I designed, built and operate the whole product: the FastAPI backend (routers/services/Pydantic
models), the React multi-step frontend, the Supabase schema (pgvector functions, RLS, auth flows), the
prompt engineering for extraction and re-ranking (domain abbreviations, materials, coreference), the
concurrency architecture, the nightly ERP sync (GitHub Actions), the Docker/Cloud Run deployment, and
the production debugging. **Off-the-shelf:** Whisper, Gemini, `text-embedding-3-small`, Supabase,
Cloud Run, Netlify. **What I did NOT build:** the models, the vector index implementation, or the ERP —
the ERP-X API contract was agreed with the client's ERP team. Parts of the code were AI-assisted; the
architecture, decisions and debugging are mine.

## Evidence in this case study

| File | What it is |
|------|-----------|
| [architecture.md](architecture.md) | backend/frontend/data/deploy layers with the real module names |
| [productionizing-concurrency.md](productionizing-concurrency.md) | the signature decision + its failure-driven history |
| [request-flow.md](request-flow.md) | the 7-step flow, with the recorded extraction pair vs the degraded run |
| [reliability-and-evaluation.md](reliability-and-evaluation.md) | reliability mechanisms tied to real code + eval honesty |
| [EVALUATION.md](EVALUATION.md) | case matrix incl. graceful-degradation negative cases |
| [the-bug-i-fixed.md](the-bug-i-fixed.md) | fix-1: the statement-timeout / HNSW index-scan bug |
| [artifacts/](artifacts/) | pipeline constants, learned memory, validated extractions, catalog stats, chaos modes |
| [demo/](demo/) | offline demo of the memory-first rule + the degradation matrix |

## What is real / replayed / simulated

| Element | Status | Note |
|---|---|---|
| catalog stats, learned-memory rows, extraction pairs, code constants | **Real** (sanitized) | read from the synced catalog, the live `historico` table and `fine_tuning.jsonl` |
| the memory-first lookup in the demo | **Real rule, approximated offline** | the real system matches by embedding similarity; the demo matches dictated text against the real memory rows and prints the divergence |
| the chaos degradation matrix in the demo | **Real, run live (offline)** | the actual `SIMULATE_FAILURE` semantics from the three services |
| fix-1 measurements (220ms, 347/595, 8s/30s) | **Real, replayed** | from the recorded `EXPLAIN ANALYZE` + Supabase role config |
| transcription/extraction/search/delivery in the demo | **Not run** | need live APIs; represented by the recorded pairs and constants |
| per-request latency/token traces | **Not archived** | Cloud Run logs rotated; declared, not invented — see EVALUATION.md |

## Stack

**Active:** FastAPI (async end-to-end) · React + Vite + TypeScript + Tailwind (Netlify) · Supabase
(pgvector **HNSW**, Auth/JWT, RLS) · `whisper-1` (transcription) · `gemini-2.5-flash` (extraction +
re-ranking, via a provider-agnostic `llm_wrapper` that routes `gpt-/claude-/gemini-` by prefix) ·
`text-embedding-3-small` · Google Cloud Run (Docker, VPC + static IP for the ERP) · O365 email ·
GitHub Actions (nightly ERP-X sync) · a chaos-testing switch. **Tried and discarded** (the archaeology
is in [lessons-learned.md](lessons-learned.md)): Streamlit UI, Heroku, FAISS pickled indexes, BERT
embeddings, a fine-tuned extraction model, mem0.

## Status

**Working system, deployed and in production use** with the client (Cloud Run + Netlify + Supabase
cloud, nightly sync active). Top open items: exporting per-request latency metrics before log rotation
(the measurability gap declared in [EVALUATION.md](EVALUATION.md)) and the HNSW warmup refinement
(plan 12.22).

## Contact

See the [root README](../../README.md#contact).

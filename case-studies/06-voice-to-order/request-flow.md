# The request flow

One dictated order becomes an ERP order in **7 steps**. The same numbering is used in the README, the
[sequence diagram](assets/request-sequence.md) and `demo/run_demo.py`.

## The 7 steps

**Step 1 — Record / upload (React).** The technician records in the browser (or uploads a file). The
multi-step UI owns the order state from here to submission.

**Step 2 — Transcribe.** `transcription_service.py` → `whisper-1`. Output: the dictated text
(real examples: [`artifacts/extraction-examples.json`](artifacts/extraction-examples.json)).

**Step 3 — Extract the structured order.** `order_processing_service.py` → `gemini-2.5-flash` with a
domain prompt (abbreviations DN/INOX/M/H-MH-HH, material rules, dictation patterns, **coreference** —
"dos espigas… *para esa manguera*" must inherit the hose's spec). Output: JSON of
(quantity incl. decimals, description, observations). Guarded by **retry ×3 with 2s·attempt backoff**
(fix-4: the preview model returned truncated JSON under load).

**Step 4 — Per-article parallel search.** `search_service.py` fans out one task per line
(`asyncio.gather`). Each task, under the **DB semaphore (10)**: searches the **learned memory** first
(`buscar_historicos`, threshold 0.75, count 1 → pinned candidate with the article's *live* catalog
description), then the **catalog** (`buscar_articulos`, threshold 0.5, top 25, deduped against the
memory hit). Both RPCs use the CTE/HNSW pattern with `match_count*3` candidates and a 30s function
timeout ([the-bug-i-fixed.md](the-bug-i-fixed.md)).

**Step 5 — Re-rank per article.** Under the **LLM semaphore (10)**: `gemini-2.5-flash` orders that
article's candidates (domain-aware: material, measure, DN). If the call or its JSON fails →
**deterministic fallback**: sort by `(Historical_match desc, Score desc)`. Ranking can degrade;
it cannot error.

**Step 6 — Human review (React).** The technician sees per-line ranked options, can re-search, add
manually from the catalog, delete lines, edit decimal quantities, and confirm. This HITL step is why
search precision is a UX variable, not a correctness gate.

**Step 7 — Finalize & deliver, on three independent channels.** PDF + O365 email (recipients switch at
the **14h** workday cutoff), the **ERP-X** API, and the **memory upsert** (confirmed line → phrase
mapping, frequency++). Each channel reports its own status light; one failing never aborts the others
([`artifacts/chaos-degradation.json`](artifacts/chaos-degradation.json)).

The model is touched at Steps 2, 3 and 5; Steps 4 and 7 are deterministic orchestration; Steps 1 and 6
are the human's.

## Two contrasting runs

The axis the signature decision controls is **bounded parallel fan-out + isolated failure**, so the
contrast is a clean high-volume run vs a degraded delivery:

| | Run A — recorded extraction (21 lines) | Run B — degraded delivery (chaos: `erp`) |
|---|---|---|
| input | the real dictated order "obra [order-ref], [site]…" | any confirmed order with `SIMULATE_FAILURE=erp` |
| Step 3 output | **21 expected lines** incl. coreference, recorded in `extraction-examples.json` | normal |
| Step 4–5 fan-out | 21 parallel tasks under semaphores 10/10 | normal |
| Step 7 ERP | delivered | **fails (injected)** → status light red |
| Step 7 email + PDF | delivered | **delivered anyway** |
| Step 7 memory upsert | recorded | **recorded anyway** |
| outcome | order in ERP + email + memory | order delivered by email, ERP flagged for office follow-up — no data lost, no error page |

Run A's evidence is one of the **47 hand-validated** pairs (recorded artifact). Run B's evidence is the
implemented chaos switch with its three real injection points (`file:line` in
[`artifacts/chaos-degradation.json`](artifacts/chaos-degradation.json)) — exercised during Phase-12
testing, **no archived execution log**, declared as such in [EVALUATION.md](EVALUATION.md).

**The honest metric gap:** no per-request latency/token traces were exported before Cloud Run log
rotation. The plan records the stress-test outcome qualitatively (orders of 22+ articles, more than
double the articles in less time than sequential); the hard recorded numbers in this case are the fix-1
measurements and the data volumes — see [`artifacts/README.md`](artifacts/README.md).

## Why this matters

Steps 4–5 are where an applied-AI product lives or dies: the difference between "demo" and "deployed"
was not a better model — it was bounding the fan-out (two semaphores), making degradation deterministic
(the fallback sort), isolating delivery failures (three channels, three status lights), and feeding the
result back into the system's memory so next month's search is better than this month's.

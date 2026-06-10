# Reliability and Evaluation

## Reliability mechanisms (in the real system)

| Mechanism | Where | Why |
|---|---|---|
| **Two concurrency semaphores** (LLM=10, DB=10) | `search_service.py` | bound the per-order fan-out; prevent the rate-limit and socket-exhaustion failures that naive `gather` produced |
| **Deterministic re-rank fallback** | `search_service.py` — sort `(Historical_match desc, Score desc)` | a failed/garbled LLM re-rank degrades ranking, never errors the order |
| **Extraction retry ×3, backoff 2s·attempt** | `order_processing_service.py` (`MAX_LLM_RETRIES=3`) | survives truncated/non-JSON LLM responses (the fix-4 incident); raw response fully logged on failure |
| **Scoped DB timeout + CTE/HNSW pattern** | `buscar_*.sql` — `SET statement_timeout='30s'`, `LIMIT match_count*3` | the fix-1 pair: force the index scan, and give only these two functions headroom over the role's 8s |
| **HNSW warmup during `process-audio`** | plan 12.22 | warms the cold index while the human reviews the transcription — free latency |
| **Three independent delivery channels** | `order_delivery_service` / `erp_integration_service` / `historical_data_service` | ERP, email+PDF and memory upsert each fail alone with their own status light; no failure aborts the others |
| **Chaos switch** | `SIMULATE_FAILURE=erp,email,history` (`config.py` + 3 injection points) | failure paths are testable on demand without touching infrastructure |
| **`gather(return_exceptions=True)`** | `search_service.py` | one line's search failing never kills the other 20 |
| **JWT + RLS** | Supabase Auth, `auth_utils.py` | every endpoint authenticated; rows scoped per user |
| **Nightly ERP sync** | GitHub Actions (timeouts 30s/120s) | the search corpus cannot drift from the ERP master |
| **Structured JSON logging** | `app/core/logging_config.py` | every stage logs with user/component/attempt context |
| **Per-environment config** | `.env.{ENVIRONMENT}` via Pydantic settings | dev/prod separation (incl. separate Supabase projects, plan 12.13) |

## How I evaluate

Extraction is evidenced by **47 hand-validated** (transcription → expected order) pairs
([`artifacts/extraction-examples.json`](artifacts/extraction-examples.json)); search quality is
exercised continuously by the HITL step (the technician sees and corrects the ranking — Step 6); and
failure behaviour is testable on demand via the chaos switch. The matrix, the negative cases and the
declared gaps are in **[EVALUATION.md](EVALUATION.md)**.

Honest gaps: **no automated end-to-end scorer**, and **no archived per-request latency/token traces**
(Cloud Run logs rotated before export). The stress-test result is recorded qualitatively in the project
plan, not as raw numbers.

## Known limitations

- **Measurability:** the biggest one — latency percentiles and per-request costs are not exported;
  declared throughout rather than estimated.
- **Cold start:** Cloud Run `min-instances 0` adds ~20s to the first request of the day (documented,
  with the measured-trigger upgrade path in [the-bug-i-fixed.md](the-bug-i-fixed.md)).
- **Whisper mishears domain words** ("mistos" for "mixtos", invented site names) — absorbed downstream
  by the extraction prompt and the HITL review rather than fixed at the source.
- **The learned memory needs the human loop:** a wrong confirmation would teach the memory a wrong
  mapping; frequency counting mitigates but doesn't eliminate it.

# Artifacts — real outputs (sanitized)

Real data from the deployed voice-to-order system (FastAPI + React on Cloud Run/Netlify, Supabase
pgvector). Everything below is read from the real repository: the synced ERP catalog, the live
"historical memory" table, hand-validated extraction pairs, and the real code constants.

| File | What it is | Real? | Sanitized? |
|------|-----------|:----:|:----------:|
| [`pipeline-structure.json`](pipeline-structure.json) | The 7-stage request flow with **every real constant from code**: semaphores 10/10, retry ×3 (backoff 2s·attempt), thresholds 0.75/0.5, top-25, CTE ×3, timeouts 8s→30s, the fix-1 EXPLAIN numbers | ✅ | nothing to change |
| [`historical-memory-sample.json`](historical-memory-sample.json) | 14 real rows of the system's **learned memory** (dictated phrase → confirmed catalog article + frequency), the table `buscar_historicos` searches first | ✅ | order/user ids dropped; article ids regenerated; dates → month |
| [`extraction-examples.json`](extraction-examples.json) | 3 of the **47 hand-validated** (transcription → expected order) pairs, incl. a 21-line order | ✅ | `[customer]`/`[site]`/`[order-ref]` tokens |
| [`catalog-stats.json`](catalog-stats.json) | The synced ERP catalog: **31,070 rows**, schema, real messy-data examples, 5 sample rows | ✅ | article ids regenerated; supplier column dropped |
| [`chaos-degradation.json`](chaos-degradation.json) | The `SIMULATE_FAILURE` chaos switch: 3 failure modes with their real injection points (`file:line`) and the per-channel degraded behaviour | ✅ | none needed |

Each JSON carries a `_provenance` block naming the real code path or table it came from.

## What "sanitized" changed

- **Client identity:** the client (an industrial plumbing/HVAC supplier) and its ERP product name → `ClientA` / `ERP-X` in prose. Neither appears in these artifacts.
- **Dictated proper nouns:** end-customers → `[customer]`, site names → `[site]`, internal order numbers → `[order-ref]`.
- **Identifiers:** ERP article ids regenerated as `ART-<8hex>` (deterministic over the real id, so the same article keeps the same token across artifacts). The supplier column of the catalog CSV is dropped.
- **Dates:** `last_used` coarsened to month.

## Corrections disclosed (field-level)

- `id_articulo` — **regenerated** (`ART-` + 8-hex over the real ERP id) in `historical-memory-sample.json` and `catalog-stats.json`. Identifier regeneration, not a metric change.
- No count, constant, threshold, or text beyond the tokens above was altered. Article **descriptions are kept verbatim** (generic plumbing/HVAC vocabulary — they are the evidence that the matching problem is real).

## What is NOT changed (this is the evidence)

- The **code constants** in `pipeline-structure.json` (semaphore limits, retries, thresholds, the CTE ×3 pattern, the 8s/30s timeouts, the 220ms warm index scan, 347 cold disk reads vs 595 cache hits).
- The **counts**: 31,070 catalog rows · 1,001 learned mappings · 47 validated extraction pairs · 283 archived transcriptions · 216 audio files · 321 commits.
- The **dictated text** of the transcriptions (minus the three token substitutions) and the expected order lines.

## Note on per-request metrics (the honest gap)

There is **no archived per-request latency/token trace**: the system runs on Cloud Run and request
logs were not exported before rotation. The stress-test claim recorded in the project plan
("orders of 22+ articles processed, more than twice the articles in less time than the sequential
implementation") ships **as a recorded claim without its raw numbers** — it is never presented as a
measured metric here. The hard numbers that do exist are the fix-1 measurements and the data volumes
above. See [../EVALUATION.md](../EVALUATION.md).

> Confidentiality: no credentials, API keys, JWTs, Supabase project refs or PII appear in any
> artifact. Written only after `verify_case_study.py` passes.

# Artifacts — real outputs (sanitized)

These are **real outputs from the actual system**, not mock-ups. Client/site/brand names and
locations have been replaced with generic labels; structure, counts, timings, token usage and
retrieval logic are untouched.

| File | What it is | Real? | Sanitized? |
|------|-----------|:----:|:----------:|
| [`catalog.sample.json`](catalog.sample.json) | The knowledge-base catalog (6 documents): titles, types, strategy, chapters, tags, summaries | ✅ | site/brand/city names → generic labels |
| [`query-trace.power-zones.json`](query-trace.power-zones.json) | Full query trace over a public book (*Cycling Science*): steps, references, metrics | ✅ | none needed (public source) |
| [`query-trace.safety.json`](query-trace.safety.json) | Full cross-document query trace over boiler manuals: steps, references, metrics, answer | ✅ | document titles → "Site A/B/C" |
| [`processing-log.sample.txt`](processing-log.sample.txt) | Ingestion log for a 15.4M-char spreadsheet (154 parts) | ✅ | client name removed; translated to English |

## What "sanitized" changed

- Company / client names → `an industrial plumbing/HVAC supplier (client)`, `ClientA`.
- Installation sites & city → `Site A/B/C`, `[location]`.
- Equipment brands → generic (`an industrial gas/oil boiler`, `a major boiler brand`).
- Document IDs (opaque hashes) are kept as-is — they identify nothing.

## Two corrections I made (disclosed for honesty)

1. **`query-trace.safety.json` — reconciled reference IDs.** The original system populated the
   `references[].document_id` field with a **duplicated value** (a real propagation bug: all three
   site manuals shared one id), while `steps_log` and `chapters_read` held the correct, distinct
   ids. I reconciled `references` against those authoritative fields and normalized the titles to
   match the catalog. **Metrics, funnel and answer are untouched.** (Worth noting because
   traceability is exactly what this artifact is meant to demonstrate.)
2. **`Cycling Science`** is a real, publicly published reference book. Only its **metadata and the
   generated trace** are included here — the source PDF is **not** distributed.

## What is NOT changed

Document/chapter **counts**, processing **dates**, `strategy` decisions, the retrieval **funnel**
(`steps_log`), and the **metrics** block (`elapsed_seconds`, `api_calls`, `input/output/total
tokens`). Those are the evidence — altering them would defeat the purpose.

## Reading the traces

Each query trace contains:

- `steps_log` — the retrieval funnel: documents selected → confirmed → candidate chapters → read;
- `references` / `chapters_read` — the exact sources used (document → chapter), i.e. traceability;
- `metrics` — wall-clock seconds, API calls, and input/output/total tokens for the whole query;
- `answer` — the grounded answer the system produced.

> Confidentiality: no credentials, API keys, production URLs or personally identifiable
> information appear in any artifact.

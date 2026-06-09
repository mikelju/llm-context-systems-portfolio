# Artifacts — real outputs (sanitized)

These are **real outputs from the actual system**, not mock-ups. Identifiers and client-specific
details have been sanitized; the **measured evidence** (counts, timings, token usage, funnel,
answer text) is untouched. Every change beyond token substitution is disclosed below.

| File | What it is | Real? | Sanitized? |
|------|-----------|:----:|:----------:|
| [`catalog.sample.json`](catalog.sample.json) | Knowledge-base catalog (6 documents): titles, types, strategy, chapters, tags, summaries | ✅ | site/brand/city names → generic; IDs regenerated; dates coarsened |
| [`query-trace.power-zones.json`](query-trace.power-zones.json) | Query trace over a public book (*Cycling Science*): steps, references, metrics | ✅ | IDs regenerated; references rebuilt (see below) |
| [`query-trace.safety.json`](query-trace.safety.json) | Cross-document query trace over boiler manuals: steps, references, metrics, answer | ✅ | titles → "Site A/B/C"; IDs regenerated; references reconciled |
| [`processing-log.sample.txt`](processing-log.sample.txt) | Ingestion log for a 15.4M-char spreadsheet (154 parts) | ✅ | client name + internal paths generalized; English |

Produced by the real system (`build_catalog.py`, `query_library.py`); see each file's
`_provenance` field.

## What "sanitized" changed

- **Client / company names** → `an industrial plumbing/HVAC supplier (client)`.
- **Installation sites & city** → `Site A/B/C`, `[location]`; the `winery` sector tell was removed
  (a quasi-identifier: sector + region + capacity could re-identify a client).
- **Equipment brands** → generic (`an industrial gas/oil boiler`).
- **Document IDs** → **regenerated as opaque 12-hex tokens** deterministically from the *sanitized*
  labels, and made **consistent across every artifact** (so traces still join to the catalog). The
  real content-hash IDs are not used (a content hash is a reversible fingerprint of the source).
- **Internal filesystem paths / sheet names** in the log → `[storage]/<id>/original/source.xlsx`,
  `[tmp]/<id>`, `[sheet]`.
- **Absolute dates** → coarsened to month (`2026-03-11` → `2026-03`). Durations/elapsed times are
  kept verbatim (they are metrics).

## Corrections disclosed (field-level)

Beyond token substitution, these structural fixes were applied. **No metric, funnel count, or
answer text was changed.**

1. **`query-trace.safety.json` — references reconciled.** The original system emitted
   `references[].document_id` with a **duplicated value** (all three site manuals shared one id),
   while `steps_log`/`chapters_read` held the correct distinct ids. References were rebuilt from
   the authoritative `chapters_read`, so every reference now resolves.
2. **`query-trace.power-zones.json` — references rebuilt.** The original `references[]` put the
   *chapter* title in `document_title` and left `chapter_id` empty for 2 of 5 entries. Rebuilt from
   `chapters_read` so all 5 references resolve (correct `document_title` = "Cycling Science",
   non-empty `chapter_id`).
3. **Document IDs regenerated + unified** across catalog/traces/log (see above).

> **Cross-artifact consistency (verifiable):** every `document_id` in a trace exists in the
> catalog, and every `references[]` entry resolves to a `chapters_read` entry with a non-empty
> `chapter_id`. The repo's `verify_case_study.py` checks this.

## What is NOT changed

The **metrics** block (`elapsed_seconds`, `api_calls`, `input/output/total tokens`), the **funnel
counts** in `steps_log`, the **answer** text, and the chapter/document **counts**. Those are the
evidence.

## Reading the traces

- `steps_log` — the retrieval funnel: documents selected → confirmed → candidate chapters → read;
- `references` / `chapters_read` — the exact sources used (document → chapter): traceability;
- `metrics` — wall-clock seconds, API calls, input/output/total tokens for the whole query;
- `answer` — the grounded answer the system produced.

> Confidentiality: no credentials, API keys, production URLs or personally identifiable
> information appear in any artifact. *Cycling Science* is a public book — only metadata and the
> generated trace are included; the source PDF is not distributed.

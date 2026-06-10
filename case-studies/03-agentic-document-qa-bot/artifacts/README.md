# Artifacts — real outputs (sanitized)

Real data from the deployed DocBot/FieldBot system (n8n Cloud + Gemini File API + Telegram). The
artifacts are **extracted from the real n8n workflow exports** and from the **Phase-4 validation run**;
client/site identities are anonymized.

| File | What it is | Real? | Sanitized? |
|------|-----------|:----:|:----------:|
| [`tool-structure.json`](tool-structure.json) | The 19 functional nodes of WF-DocBot-Tool, each tagged **deterministic / llm / io** — the signature decision made measurable (10 deterministic, **2 LLM judgment calls**, 7 io) | ✅ | node names translated |
| [`agent-architecture.json`](agent-architecture.json) | WF-Principal: the deterministic router (menu + Switch + Static Data), the 2 agents, memory, and DocBot's 2 tools | ✅ | node names translated |
| [`catalog-sample.json`](catalog-sample.json) | The `catalog.json` the processing pipeline emits to Drive: 15-doc library with **real page counts** + 2 rejected over-limit examples | ✅ | sites → Site A..N; ids regenerated; titles/tags generalized; summaries omitted |
| [`query-runs.json`](query-runs.json) | Two **contrasting** recorded outcomes: a tool-path answer (P1) vs an off-topic refusal (P10) | ✅ | queries translated/sanitized |
| [`validation-battery.json`](validation-battery.json) | The real Phase-4 battery: 10 questions over the real library, **9 pass / 1 fail**, 2 recorded negative cases | ✅ | questions translated; sites anonymized |
| [`security-audit-summary.md`](security-audit-summary.md) | The real Phase-2 security audit (0C/0H/2M/4L/4I) | ✅ | node names translated |

Each JSON carries a `_provenance` block naming the real code path it came from.

## What "sanitized" changed

- **Client + sites:** the client company → "a heating-systems field-service company"; the end-installation
  building names that appear in the manuals → **Site A..N**.
- **Product names:** the two bot modes → **DocBot** (documentation) and **FieldBot** (interventions).
- **Identifiers:** `document_id`s regenerated as opaque 12-hex from the sanitized site label, consistent
  across `catalog-sample.json` and the traces. n8n node names translated to English.
- **Catalog content:** titles and tags are **generalized**; the recorded Gemini-generated `summary_global`
  values were not archived, so they are omitted (not invented).

## Corrections disclosed (field-level)

- `document_id` — **regenerated** (12-hex over the sanitized site label) in `catalog-sample.json`; the
  same id is reused for the same site in the traces. This is identifier regeneration, not a metric change.
- No metric, funnel count, page count, or verdict was altered.

## What is NOT changed (this is the evidence)

- The **node counts and the deterministic/LLM split** in `tool-structure.json` and
  `agent-architecture.json` (read straight off the real workflows).
- The **page counts** and **library composition** in `catalog-sample.json` (14 manuals of 13–14 pages,
  1 one-page protocol; 2 controller manuals of 88 and 44 pages rejected by the 20-page limit).
- The **validation verdicts** (9 pass / 1 fail) and the recorded negative cases.

## Note on per-query metrics (the honest gap)

There is **no per-query token/latency trace** here. The deployed system runs on n8n Cloud, where
execution history is retained only briefly — and we deliberately **reduced** that retention for privacy
(finding SEC-208). So the cost/latency figures that exist are: the **typical latency ranges** observed
during validation (under 30 seconds with 1–3 documents, under 60 seconds with 5+), and the **per-query
cost estimate** in [../tool-vs-llm-boundary.md](../tool-vs-llm-boundary.md) (clearly labelled an
*estimate*, from the model's published pricing — not a measured trace). I won't fabricate a token trace
to fill the gap; see [../EVALUATION.md](../EVALUATION.md).

> Confidentiality: no credentials, API keys, OAuth/workflow ids, Telegram tokens or PII appear in any
> artifact. n8n references credentials by id and never exports their values. Written only after
> `verify_case_study.py` passes.

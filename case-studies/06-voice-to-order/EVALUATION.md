# Evaluation

The evaluation evidence is of three kinds: **47 hand-validated extraction pairs** (recorded), the
**implemented and exercised failure modes** (chaos switch), and the production incidents themselves
(fix-1, fix-4 — each a recorded failure with a verified fix). The declared gap: no automated scorer
and no archived per-request latency traces.

## Case matrix

| # | Scenario type | Why it matters | Status | Evidence |
|---|---------------|----------------|--------|----------|
| 1 | Simple order extraction (3 lines) | baseline | ✅ Recorded | `extraction-examples.json` ex.1 |
| 2 | High-volume order (21 lines) | the concurrency case | ✅ Recorded | `extraction-examples.json` ex.3 |
| 3 | Coreference ("…para esa manguera") | dictation is not a list — context propagates | ✅ Recorded | `extraction-examples.json` ex.3, prompt rules |
| 4 | Slang → canonical article ("taco fischer de 10") | the core matching problem | ✅ Recorded | `historical-memory-sample.json` (real learned mappings) |
| 5 | Decimal quantities (1.5 m) | real orders aren't integers | ✅ Implemented + UAT-checked | plan 12.8, UAT checklist §2 |
| 6 | **Degraded delivery: ERP fails → email still goes** | graceful degradation (the product negative case) | ✅ Implemented, exercised via chaos switch; no archived log | `chaos-degradation.json` (3 injection points, `file:line`) |
| 7 | **No-match line → "SIN OPCIONES", human resolves** | bad input must not invent an article | ✅ Behaviour implemented (empty candidate set renders as no options; manual catalog add available) | `search_service.py` empty-result path |
| 8 | LLM returns truncated/garbage JSON | the fix-4 incident | ✅ Recorded incident + fix (retry ×3 + model swap) | master plan fix-4; `pipeline-structure.json` |
| 9 | Vector search timeout (cold cache) | the fix-1 incident | ✅ Recorded incident + fix + EXPLAIN numbers | [the-bug-i-fixed.md](the-bug-i-fixed.md) |
| 10 | Two users in parallel, independent state | multi-user product | ✅ UAT-checked | UAT checklist (two-account test) |
| 11 | Latency percentiles / throughput under load | the spec metric for a product case | ⏳ **Pending — the declared gap** | see below |
| 12 | Automated extraction scorer over the 47 pairs | regression safety | ⏳ Pending | see below |

10 of 12 recorded/implemented; 2 pending — within the "at most half" rule.

## The negative cases (product-flavoured: graceful degradation)

Per the spec's per-type guidance, the product negative case is "bad/no-match input → graceful
degradation", and it is enforced structurally in two places:

1. **Delivery failure** (case 6): each channel — ERP, email+PDF, memory — has its own injection point
   and its own status light; `SIMULATE_FAILURE=erp` proves an ERP outage demotes to "delivered by
   email, flagged for follow-up", not an error page. Blocker on a *recorded* run: the chaos runs were
   done interactively in Phase-12 testing and the execution logs were not archived. Exact steps to
   record one: set `SIMULATE_FAILURE=erp` in `.env.development`, submit any order via the UI, export
   the structured JSON log of `order_delivery_service` + the response payload showing
   `erp: failed (simulated) / email: sent / history: saved`.
2. **No-match line** (case 7): an article below both thresholds (memory 0.75, catalog 0.5) yields an
   empty candidate list → the UI renders "SIN OPCIONES" for that line and the technician resolves it
   manually (manual catalog add) — the system never silently substitutes an article.

## Faithfulness — extraction pair (recorded)

From `extraction-examples.json`, example 1 (a real dictated order):

| Dictated | Expected extraction (hand-validated) |
|---|---|
| "24 tornillos allen métrica 10x25 inox" | `TORNILLO ALLEN M10*25 INOX × 24.0` |
| "24 tuercas métrica 10 inox" | `TUERCA M10 INOX DIN 934 × 24.0` |
| "24 arandelas métrica 10 inox" | `ARANDELA M10 INOX DIN125 × 24.0` |

Every output line maps to a dictated phrase; quantities are preserved; the DIN specs come from the
catalog's canonical vocabulary (the prompt's abbreviation/material rules), not invention.

## The declared gap (and what closing it takes)

**No per-request latency/token traces were exported before Cloud Run log rotation**, so latency
percentiles and throughput — the headline metrics for a product case — are missing. The stress-test
outcome exists only as the plan's qualitative record (22+ article orders, more than double the
articles in less time than sequential). What closing it takes: a log sink (BigQuery export or a
`latency_ms` column written per request), one week of production traffic, and a percentile query —
listed as the top open item in the [README](README.md#status). I will not back-fill these numbers.

## What would make this a real eval suite

1. An automated **extraction scorer** over the 47 recorded pairs (exact-match + quantity accuracy per
   line), run on every prompt/model change.
2. A **retrieval benchmark** from the learned memory: for each historical mapping, does
   `buscar_articulos` rank the confirmed article top-1/top-5? (The 1,001 mappings are a free labelled
   set.)
3. The **latency export** above, plus an alert on the re-rank fallback rate.
4. A recorded chaos-run log per failure mode, refreshed per release.

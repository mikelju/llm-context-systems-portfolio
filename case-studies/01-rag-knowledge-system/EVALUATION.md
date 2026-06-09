# Evaluation

How I think about evaluating this retrieval system, what is **recorded** today, and what is
**pending** — stated honestly, because for a RAG system the evaluation discipline matters as much
as the architecture.

## Case matrix

| # | Question type | Why it matters | Status | Evidence |
|---|---------------|----------------|--------|----------|
| 1 | **Single-document** | Baseline retrieval + faithful synthesis | ✅ Recorded | [`artifacts/query-trace.power-zones.json`](artifacts/query-trace.power-zones.json) — 1 doc, 5/6 chapters, 5 cited refs, 73.7 s, 52,786 tokens |
| 2 | **Cross-document** | Merge evidence from several sources | ✅ Recorded | [`artifacts/query-trace.safety.json`](artifacts/query-trace.safety.json) — 4 docs, 8/9 chapters, 8 cited refs, 88.5 s, 44,691 tokens |
| 3 | **No answer in the library** | The system must say *"I don't know"* instead of hallucinating | ⏳ **Pending** — not yet recorded | see below |
| 4 | **Wrong-document distractor** | Robustness when a tempting-but-irrelevant doc is present | ⏳ Pending | — |

## Dimensions I measure (or will)

- **Retrieval precision / recall** — did Steps 1–3 select the right documents and chapters?
- **Answer faithfulness** — does every claim trace to a read chapter? (the traces carry
  `references`, so this is checkable per answer).
- **Source traceability** — number and correctness of cited sources.
- **Cost / latency** — seconds, API calls, input/output tokens per query (already instrumented in
  `gemini_client.py`).
- **Robustness** on scanned / visually rich documents.

## The "no answer" case (case 3)

The most important *missing* test. The intended behavior, for a query with no support in the
library (e.g. *"What are the warranty terms for this boiler model?"*), is an explicit refusal:

> "I cannot answer this from the available documents."

**Why there is no trace file for it yet — and why I won't fake one.** Every artifact in this case
study is a real recorded run. I could hand-write a `query-trace.no-answer.json` with invented
metrics, but that would break the one rule that makes this portfolio credible: *the numbers are
real.* So this case is listed as pending rather than dressed up. Recording it (plus an automated
faithfulness check) is the top roadmap item.

## What would make this a real eval suite

1. A small **labeled set**: ~20–30 questions × expected source chapters, across the four types above.
2. An **automated scorer**: retrieval precision/recall vs. labels + a faithfulness check (does each
   answer sentence map to a cited chapter?).
3. Run it **before/after** any change (e.g. turning embeddings on — see
   [context-strategy.md](context-strategy.md)) so improvements are measured, not assumed.

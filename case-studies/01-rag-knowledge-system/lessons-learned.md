# Lessons Learned

Grounded in building and running this system on real, mixed documents — not generic RAG advice.

## 1. RAG is a context-selection problem, not an LLM-calling problem

The model call is the easy part. The engineering is in *deciding what reaches the prompt*. The
whole system exists to make that decision cheap, measurable and traceable (see the
[funnel numbers](retrieval-flow.md)).

## 2. A metadata catalog can replace a vector DB at this scale

I built the embeddings phase and then **disabled it** ([context-strategy](context-strategy.md)).
A catalog of titles/summaries/tags + LLM selection is simpler, inspectable ("why was this doc
chosen?"), and good enough for dozens of heterogeneous documents. Vector search is operational
weight I deferred until the corpus justifies it. *Knowing when **not** to add infrastructure is a
skill.*

## 3. Chunking is the wrong abstraction for technical/visual documents

Tables, diagrams and scanned pages lose meaning when chunked. Page-as-image reading + full-context
for small docs preserved fidelity that a chunk-and-embed pipeline would have destroyed.

## 4. Full-context is sometimes the *best* strategy, not a fallback

For small manuals, sending the whole document beats building a retrieval pipeline around it —
cheaper to build, more reliable, and the model sees the full picture. Hence the explicit
`FULL_CONTEXT_MAX_PAGES = 80` switch.

## 5. Distrust upstream "successes"

The [TOC bug](the-bug-i-fixed.md) taught this concretely: a component returning *plausible but
wrong* structure is more dangerous than one that fails. Validate between fallback layers.

## 6. Cost and latency must be first-class metrics

Because `gemini_client.py` tracks tokens/calls/time per query, I can compare runs and catch
regressions. A RAG system without these numbers can't be improved systematically — and can't be
*shown* to anyone with credibility.

## 7. Ingestion is where reliability is won

Resumable, thread-safe, per-chapter state turned a fragile 154-part / 15.4M-char ingestion into
something that survives crashes. The expensive work is paid once; queries stay cheap.

## What I'd do next

- Build a labeled eval set (precision/recall + the "no answer" refusal case) — the honest gap.
- Add an automated faithfulness check: does every answer sentence map to a cited chapter?
- Turn embeddings back on as a *hybrid* re-ranker once the corpus reaches hundreds of documents.

# Context Strategy

This is the heart of the system: **deciding how much context to give the model**, per document
and per query.

## The dual strategy

The processing/query path is chosen by document size, with a single explicit threshold in code:

```python
# process_batch.py
FULL_CONTEXT_MAX_PAGES = 80   # PDFs with <= 80 pages use the full_context strategy
```

### 1. Full-context (CAG-style)

For small or visually rich documents, send the **whole document** (as text and/or page images)
instead of chunking it.

Best for: short manuals, visual/scanned documents, anything where chunking would lose structure,
and cases where simplicity and visual fidelity matter more than squeezing tokens.

In the real catalog, the boiler manuals (13–14 pages) are tagged `"strategy": "full_context"`.

### 2. Hierarchical narrowing

For large, tabular or multi-chapter documents, progressively reduce context:

```text
catalog → document index → summaries/tags → selected chapters/pages → LLM synthesis
```

In the real catalog, a 59-chapter book and a 154-"chapter" spreadsheet are
`"strategy": "hierarchical"`.

## A deliberate choice: metadata-first retrieval (no vector DB *yet*)

For this corpus size (dozens of heterogeneous documents) I deliberately started with
**metadata-first retrieval** instead of reaching for embeddings by default. The pipeline *has* an
embeddings phase (`generate_embeddings.py`) — kept in place but **disabled for now**. The real
ingestion log says it plainly:

```
[Phase 5/6] Embeddings disabled (to be enabled when the model is available)
```

Retrieval is instead driven by a **catalog of titles, summaries, tags and structure**, with the
LLM doing the selection. Why this is a deliberate choice, not a shortcut:

- **Tables, diagrams and scanned pages** survive better as page-images + visual descriptions than
  as embedded text chunks.
- **A summary/tag catalog prunes the search space cheaply** before any expensive reading, and it's
  inspectable and debuggable (you can read *why* a document was selected — see the
  [query traces](artifacts/)).
- **For ~dozens of heterogeneous documents**, an LLM choosing over a compact catalog is simpler,
  more transparent and good enough — a vector store is operational complexity you don't yet need.

This is not "embeddings vs. no embeddings" dogma — it's choosing the lightest approach that fits
the corpus, while keeping the embeddings phase in the pipeline and knowing exactly when to switch
it on.

## When I would add vector search

Metadata-first is right *here*; it stops scaling. For a larger or higher-recall corpus I would add:

- **Hybrid retrieval** — metadata/tag filters **+ BM25 + embeddings**, not embeddings alone.
- **A managed vector store** — e.g. Supabase **pgvector** (already used in a sibling project), so
  candidate selection isn't a single LLM pass over the whole catalog.
- **A reranker** over the merged candidate set before reading.
- **An evaluation set first** — measure retrieval precision/recall *before and after* vectorizing,
  so the added complexity is justified by numbers, not by fashion.

Rough trigger: once the catalog passes ~**a few hundred documents** (where one LLM pass over the
catalog gets slow/expensive and tag overlap loses precision), hybrid + vector becomes worth its
operational weight. The multimodal-RAG and production-backend case studies cover that step.

## The key tradeoff

> The goal is **not** to always minimize context. It's to pick the **cheapest strategy that
> preserves answer quality.** Sometimes that's full-context; sometimes it's hierarchical narrowing.
> Making that an explicit architectural decision — rather than defaulting to "chunk + vector
> search" — is the whole point.

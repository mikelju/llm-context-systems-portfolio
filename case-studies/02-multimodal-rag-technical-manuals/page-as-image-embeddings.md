# The signature decision: page-as-image embeddings

## The problem

A boiler manual's answer is frequently a **table** (fault codes, gas pressures), a **wiring diagram**,
or an **exploded parts drawing**. Two common RAG choices both fail here:

- **Text extraction + chunking** silently drops tables/diagrams or mangles them into unusable token
  soup — and scanned/print-styled pages extract poorly.
- **Metadata-first / no vectors** (what I did in [case 01](../01-rag-knowledge-system/)) works for
  dozens of heterogeneous documents, but this corpus is **122 manuals / 6,896 pages** of near-homogeneous,
  highly visual content — exactly where you need real semantic vector search.

## The choice + why

**Embed each page as an image** with a multimodal model (`gemini-embedding-2`), and retrieve by cosine
similarity over those page vectors. The model "sees" the table/diagram, so visual structure becomes
part of the embedding. At answer time, the **page images** (not text) are sent to a vision LLM, and the
**source page image is returned to the technician** — they get the actual table to read.

Real parameters from the code:

- `MODEL = "gemini-embedding-2"`, `DIM = 1536` (configurable 768 / 1536 / 3072 — accuracy vs. size).
- `ZOOM = 2.0` when rendering (raise for small-print tables).
- `TOP_K = 5`; vectors L2-normalized so cosine = dot product.

The retrieval is a single dot-product against the page matrix — **sub-millisecond over 6,896 pages**.
The expensive part is the vision-LLM answer, not the search. (You can watch the real cosine search run
offline in the [demo](demo/).)

## When I would do it differently / scale it

This is an in-memory + pickle-cache PoC sized for one machine. The documented Phase-3 move, once the
client validates retrieval quality:

- **Trigger:** the corpus is already ~6,900 pages and will grow across clients; in-memory + a 43 MB
  pickle stops being appropriate the moment it must be multi-tenant or survive restarts cleanly.
- **Measure first:** build a small labelled query→expected-page set and compare recall **before**
  committing to a heavier backend — the open question is whether this *preview* embedding model is good
  enough, not whether the plumbing scales.
- **Then:** move vectors to **pgvector / a managed vector store** (also closes the pickle-RCE finding,
  SEC-002), put the endpoint behind **auth + rate limiting** (SEC-001), and replace the ngrok tunnel
  with a deployed service.

The point isn't "embeddings good, metadata bad" — it's matching the retrieval strategy to the corpus.
Case 01 and case 02 are the two ends of that judgement.

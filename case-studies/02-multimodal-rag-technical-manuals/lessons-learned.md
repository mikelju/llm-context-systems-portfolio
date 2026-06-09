# Lessons Learned

## 1. Match retrieval to the corpus, not to fashion
Case 01 was metadata-first with no vector DB; this one is multimodal vectors. The corpus decided it:
122 near-homogeneous, highly visual manuals (6,896 pages) need real semantic search; a few dozen
heterogeneous docs did not. The skill is choosing, not defaulting.

## 2. Embedding the page as an image earns its keep
Boiler answers live in tables and wiring diagrams. Embedding the page image (not extracted text) kept
that structure in the vector — and the recorded nearest-neighbours cluster cleanly by model/topic
(e.g. the same regulation topic across models at 0.96 cosine).

## 3. Retrieval is cheap; the model is the cost
Cosine over 6,896 vectors is sub-millisecond. The wall-clock and the bill are the embedding call and
the vision answer. So the engineering effort went where it mattered: caching, resumability, and
returning the source page instead of more tokens.

## 4. A cache is a trust boundary
The 43 MB pickle that makes the server boot instantly is also an RCE vector (`pickle.load`, CWE-502).
Convenient persistence and safe persistence are not the same; Phase 3 swaps it for pgvector + JSON.

## 5. Audit a PoC like a service, then decide consciously
A public, paid-API endpoint on an ngrok URL still deserved a real audit. The valuable output wasn't
just the SEC-003 fix — it was the **explicit, written decision** to defer the High finding while the
PoC is frozen, instead of quietly shipping something unsafe or over-claiming it's production-ready.

## 6. Know what you're blocked on
This project is intentionally stopped at "is the retrieval good enough?" — a question only the client's
labelled validation answers. Naming the blocker beats building more plumbing on an unvalidated core.

## What I'd do next
- Build the labelled query→expected-page set and measure recall@5 at DIM 768/1536/3072.
- pgvector + auth + rate limiting (closes SEC-001/002), drop the ngrok tunnel.
- Record one refusal trace to close the negative-case gap.

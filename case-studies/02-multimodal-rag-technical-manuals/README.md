# Multimodal RAG over Technical Manuals — Page-as-Image Retrieval

A proof-of-concept retrieval system that answers a field technician's question from a large library
of boiler manuals by embedding **each page as an image** (not extracted text), retrieving the most
similar pages, and returning the answer **together with the source page image**. Built as the
documentation tool ("DocBot") inside an n8n + Telegram agent for a heating-systems field-service
company (client).

> This is the **counterpart to [case study 01](../01-rag-knowledge-system/)**: there I deliberately
> went *metadata-first, no vector DB*; here the corpus is large and visual, so the right call was the
> opposite — **multimodal page-image embeddings + vector search**. Same engineer, opposite decision,
> for documented reasons.

## TL;DR (with real numbers)

- **122 boiler manuals → 6,896 pages embedded as images** (`gemini-embedding-2`, **1536-dim**).
- Retrieval = **cosine top-5** over the page vectors; the search itself is sub-millisecond even over
  ~6,900 pages (the cost is the LLM answer, not the search).
- Each answer returns the **source page image** (Telegram-ready), so the technician sees the actual
  table/diagram the answer came from — not a lossy text rendering.
- **Security-audited**: 0 Critical / 1 High / 2 Medium / 2 Low; SEC-003 fixed with 2 regression tests
  (22 tests total).

## Review this case study in 5 minutes

1. [`demo/example_output.txt`](demo/example_output.txt) — the real vector search, run offline.
2. [`page-as-image-embeddings.md`](page-as-image-embeddings.md) — the signature decision.
3. [`the-bug-i-fixed.md`](the-bug-i-fixed.md) — a security finding (DoS) and its fix.
4. [`artifacts/`](artifacts/) — the real index sample + real nearest-neighbour results.

## The real problem

Technicians need answers from ~6,900 pages of boiler manuals where the answer is often a **table, a
wiring diagram, or an exploded parts view** — not prose. Plain text extraction destroys exactly that.
The hard part is retrieving the right *page* across many manuals while preserving its visual content,
and giving the technician something they can act on (the page itself).

## My role

I designed and built the indexer, the embedding approach, the FastAPI retrieval server, the
n8n/Telegram integration, and the security-audit response. **Off-the-shelf:** Gemini embeddings +
vision model, FastAPI, PyMuPDF. **What I did NOT build:** the embedding/vision models — the
engineering is the page-as-image pipeline, the retrieval, and making it safe and serviceable.

## Evidence in this case study

| File | What it is |
|------|-----------|
| [architecture.md](architecture.md) | indexer + retrieval server + n8n/Telegram, with the real modules |
| [page-as-image-embeddings.md](page-as-image-embeddings.md) | the signature decision + when I'd scale it |
| [retrieval-flow.md](retrieval-flow.md) | the query → cosine → vision-LLM → source-page flow |
| [reliability-and-evaluation.md](reliability-and-evaluation.md) | reliability mechanisms + the security audit + eval honesty |
| [EVALUATION.md](EVALUATION.md) | case matrix incl. the built-in refusal behavior |
| [the-bug-i-fixed.md](the-bug-i-fixed.md) | SEC-003: an unbounded-query DoS, fixed + tested |
| [artifacts/](artifacts/) | real index sample, real nearest-neighbour results, audit summary |
| [demo/](demo/) | offline demo running the **real cosine search** over real embeddings |

## What is real / replayed / simulated

| Element | Status | Note |
|---|---|---|
| index sample, nearest-neighbour results, audit summary | **Real** (sanitized) | actual system data; corpus is public manuals |
| the 120-page vector sample + cosine top-K in the demo | **Real, run live (offline)** | the actual retrieval algorithm over real embeddings; no API |
| full-index nearest-neighbour results | **Real, replayed** | computed offline from the real index |
| natural-language query → answer (embed question + vision LLM) | **Not run / not archived** | needs the live API; the demo seeds from an indexed page instead |
| code constants, security findings, the bug | **Real** | from the actual codebase + audit |

## Stack

Python · `google-genai` (`gemini-embedding-2` embeddings + a Gemini vision model for answers) ·
PyMuPDF (page rendering) · NumPy (cosine) · FastAPI (the `/consultar` endpoint) · n8n Cloud +
Telegram (the agent) · ngrok (PoC tunnel). Vectors live in memory + a disk cache; **no vector DB
yet** — that's the documented Phase-3 step.

## Status

**Prototype / PoC — functional end-to-end.** Advancing to a production backend is **deliberately
blocked awaiting the client's validation** of retrieval quality with this (preview) embedding model.
The security audit's High finding (SEC-001) is consciously deferred for the same reason (the ngrok
URL is ephemeral and the PoC is frozen pending that validation) — see
[reliability-and-evaluation.md](reliability-and-evaluation.md).

## Contact

See the [root README](../../README.md#contact).

# RAG Knowledge System — Hierarchical + Full-Context Retrieval

A document-processing and retrieval system that answers questions over a **heterogeneous**
knowledge base — PDFs (native and scanned), spreadsheets, Word, PowerPoint and images — by
deciding *how much context* to give the LLM per query, and reading only what's needed.

Internal codename: **"The Librarian"**.

## TL;DR (with real numbers)

- Documents are processed once into structured layers: **type → structure → chapters → visual
  descriptions → summaries → tags → catalog**. One real spreadsheet was ingested as **154 parts /
  15.4M characters** in a single resumable pass.
- Queries use a **two-strategy** approach decided by document size
  (`FULL_CONTEXT_MAX_PAGES = 80`): *full-context* for small/visual docs, *hierarchical
  narrowing* for large/complex ones.
- A recorded cross-document query touched **5 → 4 documents → 9 candidate chapters → 8 read**,
  answered in **88.5 s / 7 API calls / 44,691 tokens**, with **8 traceable source references**.
- Deliberately **no vector database**: retrieval is driven by catalog metadata + LLM selection.
  (Embeddings were built into the pipeline but disabled — see [context-strategy](context-strategy.md).)

## Review this case study in 5 minutes

1. This file (you're here) — the what and why, with real numbers.
2. [`demo/example_output.txt`](demo/example_output.txt) — the demo's output without running anything.
3. [`context-strategy.md`](context-strategy.md) — the core decision (dual strategy; metadata-first, and when I'd add vector search).
4. [`the-bug-i-fixed.md`](the-bug-i-fixed.md) — a real failure, root cause and fix.
5. [`artifacts/`](artifacts/) — the real, sanitized catalog and query traces behind the numbers.

## The real problem

Not "chat with a PDF". The hard part is **assembling the right context** out of a large, mixed
repository where:

- you can't send everything to the model;
- naive vector search misses tables, diagrams and scanned layouts;
- chunking destroys document structure;
- some documents are best sent whole;
- some questions need evidence from several documents at once.

## My role

I designed and built the whole thing: the WAT architecture (Workflows / Agents / Tools), the
document-processing pipeline, the dual retrieval strategy, the query workflow ("The Librarian"),
the reliability mechanisms, and the iterative fixes.

## Evidence in this case study

| File | What it is |
|------|-----------|
| [architecture.md](architecture.md) | Components, layers and the real tool inventory |
| [context-strategy.md](context-strategy.md) | The dual strategy + why there is no vector DB |
| [retrieval-flow.md](retrieval-flow.md) | "The Librarian" 4-step flow, annotated with real trace numbers |
| [reliability-and-evaluation.md](reliability-and-evaluation.md) | Reliability mechanisms + how I evaluate, with real runs |
| [EVALUATION.md](EVALUATION.md) | Case matrix (incl. the not-yet-recorded "no answer" case) and what a real eval suite needs |
| [the-bug-i-fixed.md](the-bug-i-fixed.md) | A real failure (corrupt scanned-PDF TOC) and the fix |
| [lessons-learned.md](lessons-learned.md) | What I'd keep and what I'd change |
| [artifacts/](artifacts/) | **Real, sanitized** catalog, query traces and ingestion log |
| [demo/](demo/) | `python run_demo.py` — an **offline trace-replay + Step-1 pre-filter** demo (not the full engine) |

## What is real / replayed / simulated

Being precise about this is the point — it's what separates evidence from a pretty demo.

| Element | Status | Notes |
|---|---|---|
| Catalog, query traces, ingestion log ([`artifacts/`](artifacts/)) | **Real** (sanitized) | Actual system outputs; only client/site/brand names changed |
| Funnel + cost/latency/token metrics | **Real, replayed** | Read straight from the recorded traces; not recomputed |
| Step 1 in the demo (catalog pre-filter) | **Simulated** | Deterministic keyword overlap approximating (not replaying) the real LLM selection, so it runs offline; may pass a different candidate count than the recorded run |
| Steps 2–5 (chapter selection, reading, synthesis) | **Not run in the demo** | LLM-driven in the real system; represented only by the recorded metrics |
| `FULL_CONTEXT_MAX_PAGES = 80`, tool names, the bug & fix | **Real** | From the actual codebase |

## Stack

Python · Google Gemini (Flash for filtering, Pro for synthesis, Vision for page reading) ·
PyMuPDF · pdfplumber · pandas · openpyxl · python-docx · python-pptx · Pillow · fpdf2 ·
`ThreadPoolExecutor` for parallel ingestion. Designed to deploy as an n8n-integrated tool
("The Librarian" / DocBot).

## Status

Internal framework / advanced prototype. Ingestion pipeline, performance optimization and the
dual retrieval strategy are **complete and exercised on real documents**; the query system is
functional with selective visual reading and report expansion. A formal evaluation set is the
main open item (see [reliability-and-evaluation.md](reliability-and-evaluation.md)).

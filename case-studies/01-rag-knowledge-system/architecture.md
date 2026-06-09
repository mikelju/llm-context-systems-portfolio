# Architecture

## Pattern: WAT (Workflows · Agents · Tools)

- **Workflows** define the high-level process (ingest a document; answer a query).
- **Agents / LLM calls** do the parts that need judgment: filtering, selection, synthesis.
- **Tools** are deterministic Python: parsing, rendering, extraction, catalog building, state.

The guiding rule: *the LLM is used where it adds judgment; everything repeatable, structured or
verifiable is a deterministic tool.* That keeps the system debuggable and cheap.

## Ingestion pipeline (real tools)

Each document is processed **once**, offline, into reusable artifacts. The actual tools:

| Phase | Tool | Output |
|------:|------|--------|
| 1 | `detect_document_type.py` | type: `pdf_text` / `pdf_mixed` / `pdf_scanned` / `excel` / `docx` / `pptx` / `image` |
| 2 | `extract_structure.py` | document structure / chapter index (native TOC → heuristics → Gemini Vision fallback) |
| 3 | `extract_content.py`, `extract_visuals.py` | chapter text + descriptions of figures/tables/diagrams |
| 4 | `generate_analysis.py` (`generate_summary.py` + `generate_tags.py`) | per-chapter & global summaries + tags |
| 5 | `generate_embeddings.py` | embeddings — *currently disabled by design (see context-strategy)* |
| 6 | `build_catalog.py` | the searchable `catalog.json` entry |
| — | `process_batch.py` | orchestrator; `state_manager.py` | thread-safe, resumable state |

Phases 3–4 run on a `ThreadPoolExecutor` (default **3 workers**). Ingestion is **resumable**:
state is persisted per chapter, so a crash resumes mid-document instead of restarting.

> Real ingestion log (sanitized): [`artifacts/processing-log.sample.txt`](artifacts/processing-log.sample.txt)
> — a 15.4M-character spreadsheet processed as 154 parts / 52 analysis passes.

## The knowledge base

Each processed document produces structured artifacts stored under `knowledge_base/<id>/`:

- global metadata, summary and tags;
- chapter index + per-chapter summaries;
- visual descriptions (so figures/tables are searchable as text);
- rendered page images (when needed for visual reading);
- the catalog entry.

> Real catalog (sanitized): [`artifacts/catalog.sample.json`](artifacts/catalog.sample.json).

## Query system ("The Librarian")

A staged retrieval process that progressively narrows context before any expensive reading:

```
catalog → candidate documents → indexes/summaries → selected chapters/pages → LLM synthesis
```

Full step-by-step with real trace numbers: [retrieval-flow.md](retrieval-flow.md).

## Design principle

> The model should not receive everything. It should receive the **smallest useful context** that
> still contains enough evidence to answer — and a pointer back to the source for traceability.

See the diagrams: [assets/architecture-diagram.md](assets/architecture-diagram.md) ·
[assets/retrieval-sequence.md](assets/retrieval-sequence.md).

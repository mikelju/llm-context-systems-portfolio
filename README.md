# LLM Context Systems — Engineering Portfolio

**Mikel Ugarte · AI Knowledge Systems Engineer** — RAG, context engineering, document intelligence, agentic workflows, MCP/tooling.

I build the layer between an LLM and real, messy company information: how documents get
processed, how the *right* context is selected, how agents call deterministic tools, and how
cost, latency and traceability stay under control. This repository documents real systems I
designed and built for client and internal projects.

> **Why a documentation portfolio instead of source dumps?**
> These were client/internal projects, so the code stays private. Instead of a repo full of
> "trust me", each case study shows the architecture, the technical decisions and the tradeoffs —
> and, where possible, **real sanitized artifacts and a runnable demo**, so the claims are backed
> by evidence rather than adjectives.

## What makes this portfolio different

- **Real artifacts, not just prose** — sanitized catalogs, recorded query traces with real token/latency numbers, and ingestion logs taken from the actual system.
- **A runnable demo** — `python run_demo.py` replays recorded real-system traces and reproduces the Step-1 pre-filter offline (no API key, no network).
- **Honest scope** — every case study states what is *built*, what is *measured*, and what is *not* (yet).

## Focus areas

RAG & context engineering · hierarchical + full-context (CAG-style) retrieval · metadata-first
retrieval · document intelligence (PDF / Excel / Word / PPT / images, vision models) · agentic
workflows · MCP & agent tooling · cost / latency / traceability as first-class concerns ·
human-in-the-loop.

## Case studies

| # | Case study | Status |
|---|-----------|--------|
| 1 | **[RAG Knowledge System — Hierarchical + Full-Context Retrieval](case-studies/01-rag-knowledge-system/)** | ✅ Documented · real artifacts · runnable demo |
| 2 | **[Multimodal RAG over Technical Manuals — page-as-image embeddings + vision LLM](case-studies/02-multimodal-rag-technical-manuals/)** | ✅ Documented · real artifacts · runnable offline vector search |
| 3 | **[Agentic Document Q&A Bot — n8n + Gemini File API + memory](case-studies/03-agentic-document-qa-bot/)** | ✅ Documented · real artifacts · runnable offline demo |
| 4 | Document Intelligence — Manufacturer-Report Extraction (vision → structured JSON, HITL) | 🔜 |
| 5 | MCP Server / Agent Tooling (Executor Agent) | 🔜 |
| 6 | Applied-AI Product 0→1 — Voice-to-Order (vector/semantic search, cloud) | 🔜 |
| 7 | Agentic Workflow — Company Prospecting (workflows + agent + deterministic tools) | 🔜 |

> Case study **01 is the reference standard**. The remaining six will follow the same
> evidence-backed format (architecture → context strategy → retrieval flow → reliability/eval →
> a real bug → sanitized artifacts → runnable demo).

## Authoring standard

Every case study follows a single contract so quality and anonymization are consistent:
[`case-studies/CASE_STUDY_SPEC.md`](case-studies/CASE_STUDY_SPEC.md). It ships with a copy-from
scaffold ([`case-studies/_TEMPLATE/`](case-studies/_TEMPLATE/)) and an automated acceptance gate
([`case-studies/_scripts/verify_case_study.py`](case-studies/_scripts/verify_case_study.py)) that
checks artifact/metric integrity, traceability, the offline demo, and leak/secret sweeps.

## Confidentiality

Client names, datasets, credentials, production URLs and personally identifiable information have
been removed or generalized. Artifacts are *sanitized copies of real outputs*; each
`artifacts/README.md` states exactly what was changed.

## Contact

- **LinkedIn:** [mikel-ugarte-gil](https://www.linkedin.com/in/mikel-ugarte-gil/)
- **Email:** [mikelju@gmail.com](mailto:mikelju@gmail.com)
- **GitHub:** [github.com/mikelju](https://github.com/mikelju)

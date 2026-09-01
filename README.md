# LLM Context Systems — Engineering Portfolio

**Mikel Ugarte · AI Knowledge Systems Engineer** — RAG, context engineering, document intelligence, agentic workflows, agent tooling.

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
- **One of them you can run yourself** — case study 06 also ships as a standalone public repo that
  boots with Docker and two commands on real anonymized data:
  [`voice-to-order`](https://github.com/mikelju/voice-to-order).

## Focus areas

RAG & context engineering · hierarchical + full-context (CAG-style) retrieval · metadata-first
retrieval · document intelligence (PDF / Excel / Word / PPT / images, vision models) · agentic
workflows · agent tooling · cost / latency / traceability as first-class concerns ·
human-in-the-loop.

## Case studies

| Case study | What it demonstrates | Evidence |
|---|---|---|
| **[RAG Knowledge System — hierarchical + full-context retrieval](case-studies/01-rag-knowledge-system/)** | Choosing the right context *before* the model sees it: a metadata-first catalog, hierarchical selection, and when full-context beats chunking | Real artifacts · runnable offline demo |
| **[Multimodal RAG over Technical Manuals](case-studies/02-multimodal-rag-technical-manuals/)** | Retrieval when the meaning lives in schematics rather than prose: page-as-image embeddings + a vision LLM over 6,896 pages | Real artifacts · runnable offline vector search |
| **[Agentic Document Q&A Bot](case-studies/03-agentic-document-qa-bot/)** | Where deterministic tooling ends and LLM judgment begins — the tool-vs-LLM boundary, and refusing instead of guessing | Real artifacts · runnable offline demo |
| **[Document Intelligence — scanned manufacturer reports](case-studies/04-document-intelligence-extraction/)** | Reading a 134-page scanned bilingual report into a 293-field inspection schema, scored as a confusion matrix — where *correctly left empty* is the majority-correct answer | Real artifacts · runnable offline demo |
| **[Applied-AI Product 0→1 — Voice-to-Order](case-studies/06-voice-to-order/)** | Productionizing: ~30 concurrent model/DB calls per order made fast, bounded and safe, over a 31,070-row catalog and a learned memory | Real artifacts · offline demo · **[full runnable replica](https://github.com/mikelju/voice-to-order)** |

> Case study **01 is the reference standard**. Every case follows the same evidence-backed format
> (architecture → core decision → reliability/eval → a real bug → sanitized artifacts → runnable
> demo), enforced by an automated acceptance gate. More case studies are in progress.

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

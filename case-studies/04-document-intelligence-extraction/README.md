# Document Intelligence — Extracting Quality Data from Scanned Manufacturer Reports

A pilot pipeline that reads a **134-page scanned, bilingual (Chinese/English) manufacturer quality
report** with Gemini Vision and fills a client's **293-field inspection schema** (dimensional
measurements, OK/NOK results, certificates, NDT/weld records) — one filled Excel per inspected part.
Built for a wind-energy components manufacturer (client).

## TL;DR (with real numbers)

- Input: **134 scanned pages**, **131/134 bilingual**, across 9 document types (test/NDT reports,
  certificates, drawings, dimension records…). Plain text extraction is hopeless here → **Vision**.
- Target: the client's Excel inspection record (INR) flattened into a **293-field schema** (212
  numeric, 81 boolean) across 11 tabs.
- Extraction run: **134/134 pages, 0 failed, ~9 min, 46 Vision calls** (batch 3 × 4 workers, resumable).
- Quality, measured as a **confusion matrix** over the 293 fields: **precision 69%, recall 67%**, and
  **specificity 83%** — and only **37%** of the fields are even *present* in this report, so "correctly
  left empty" (153 fields) matters as much as "extracted" (72).
- Two recorded Vision runs, same model and same documents, opposite questions: **targeted** (12 named
  cells the spreadsheet itself could not compute → **12 of 12** resolved) vs **blind** (134 pages read,
  0 failed — but the matching afterwards produced all **32** false positives).

## Review this case study in 5 minutes

1. [`demo/example_output.txt`](demo/example_output.txt) — the confusion matrix + quality, recomputed offline.
2. [`schema-first-extraction.md`](schema-first-extraction.md) — the signature decision.
3. [`the-bug-i-fixed.md`](the-bug-i-fixed.md) — 12 tolerances no parser could read, and how they were recovered.
4. [`artifacts/`](artifacts/) — the real schema structure, the coverage matrix, the run stats.

## The real problem

A quality engineer must transcribe data from a supplier's **scanned, bilingual, 134-page** report
into a rigid 293-field Excel — measurements, tolerances, OK/NOK, certificate checks — for every
manufactured part. It's slow, error-prone, and most of the report is tables, stamps and drawings.
The hard part isn't OCR; it's **knowing exactly which of 293 fields each page answers, and not
inventing the ~63% of fields the report never mentions.**

## My role

I designed and built the whole pilot: flattening the Excel into a schema, the Vision extraction
pipeline, the page-catalog "Librarian" matching, the multi-part logic, the **coverage analysis**, and
the Excel write-back. **Off-the-shelf:** Gemini Vision, PyMuPDF, openpyxl. **What I did NOT build:**
the vision model — the engineering is the schema-first framing, the matching, and turning extraction
quality into a measurable confusion matrix.

## Evidence in this case study

| File | What it is |
|------|-----------|
| [architecture.md](architecture.md) | the flatten → render → extract → match → write pipeline (real tools) |
| [schema-first-extraction.md](schema-first-extraction.md) | the signature decision + when I'd scale it |
| [extraction-flow.md](extraction-flow.md) | the per-page → per-field flow, with real numbers |
| [reliability-and-evaluation.md](reliability-and-evaluation.md) | resumability + the confusion-matrix evaluation |
| [EVALUATION.md](EVALUATION.md) | the matrix as the eval; the **recorded** "don't invent absent fields" case, and the 32 invented ones |
| [the-bug-i-fixed.md](the-bug-i-fixed.md) | 12 GD&T tolerances that cached as `#VALUE!` — recovered with targeted Vision, and tagged with their provenance |
| [lessons-learned.md](lessons-learned.md) | 8 lessons, including why diagnosing the quality gap is not closing it |
| [artifacts/](artifacts/) | real schema structure, coverage matrix, run stats, fill report |
| [demo/](demo/) | offline demo that recomputes precision/recall from the real matrix |

## What is real / replayed / simulated

| Element | Status | Note |
|---|---|---|
| schema structure, coverage matrix, both run records, fill report | **Real** (sanitized) | actual pilot outputs; client measurements/serials/names removed |
| precision / recall / specificity in the demo | **Real, recomputed live (offline)** | derived from the real confusion-matrix counts; no API |
| the 134-page Vision extraction | **Not run here** | used the live API; represented by the recorded run stats |
| code tools, the `#VALUE!` bug and its fix | **Real** | from the actual codebase and the phase plans |
| the false-positive diagnosis (32 fields) | **Real finding, NOT fixed** | root-caused and prioritised in the project's phase-3 deviation note; the remediation was never implemented — see [EVALUATION.md](EVALUATION.md) |

## Stack

Python · `google-genai` (Gemini Vision) · PyMuPDF (PDF→PNG @200 DPI) · pywin32 + openpyxl (Excel I/O) ·
`ThreadPoolExecutor` (parallel extraction). The "Librarian" page-catalog matcher is the same idea as
[case 01](../01-rag-knowledge-system/), reused here for field→page mapping.

## Status

**Pilot — Phases 1–4 complete on one real report (3 parts).** Phases 5–6 (automatic page
segmentation, multi-manufacturer robustness, a human-in-the-loop traffic-light review UI) are
pending. The pilot's 67% recall / 32 false positives are *not* production quality yet, and the diagnosed
remediation was **not implemented** — the top open item. What it is and what it would take are in
[EVALUATION.md](EVALUATION.md) and [lessons-learned.md](lessons-learned.md).

## Contact

See the [root README](../../README.md#contact).

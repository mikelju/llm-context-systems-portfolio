# Architecture

A linear pilot pipeline: define the target, read the document, match, write back.

## Components (real tools)

| Stage | Tool | What it does |
|------|------|--------------|
| **1. Flatten the target** | `flatten_excel.py`, `enrich_schema_vision.py` | Renders the 11-tab Excel INR to images, extracts **293 fields** (212 numeric, 81 boolean) into a JSON schema; Vision resolves 12 `#VALUE!` GD&T-tolerance cells → 0 unresolved |
| **2. Render the report** | `render_pdf_pages.py` | 134 PDF pages → PNG at **200 DPI** |
| **3. Extract per page** | `extract_pdf_pages.py`, `gemini_client.py` | Each page → Gemini Vision → `{document_type, language, title, content, metadata}`; **batch 3 × 4 workers, resumable** via a checkpoint |
| **4. Catalog ("The Librarian")** | `build_page_catalog.py` | Indexes the 134 page extractions so fields can be located by page |
| **5. Map field → page** | `map_schema_to_pages.py` | For each of the 293 fields, finds the page(s) likely to hold it |
| **6. Fine extraction** | `extract_matched_data.py` | Per-tab focused extraction of the actual value/OK-NOK; multi-part output `{pieces[], common_data}` |
| **7. Measure** | `analyze_coverage.py` | Classifies every field present/absent × extracted/empty → a **confusion matrix** |
| **8. Write back** | `write_to_excel.py` | One filled Excel per part (serial number in COVER); the Excel's own OK/NOK formulas then compute |

## Why this shape

- **Deterministic vs. model.** Rendering, cataloguing, the coverage maths and the Excel write-back are
  deterministic; the model does the reading (page extraction) and the field-level value extraction.
- **The schema comes first.** Flattening the Excel into a precise field list (stage 1) is what lets
  every later stage be specific — and lets stage 7 know what *should* be absent. See
  [schema-first-extraction.md](schema-first-extraction.md).
- **Resumable by construction.** A 46-call, multi-minute Vision run over scanned pages will hit a
  quota or a flaky page eventually; the checkpoint means it resumes, never restarts.

## Design principle

> Don't ask "what's on this page?" in a vacuum. Flatten the **target form** first, then ask, per
> field, "is this answered, where, and — if not — is it correctly absent?"

Diagrams: [assets/architecture-diagram.md](assets/architecture-diagram.md) ·
[assets/extraction-sequence.md](assets/extraction-sequence.md).

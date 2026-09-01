# Reliability and Evaluation

## Reliability mechanisms (in the real system)

| Mechanism | Where | Why |
|---|---|---|
| **Resumable extraction checkpoint** | `extract_pdf_pages.py` — thread-safe `extraction_state.json` | a multi-minute Vision sweep over scanned pages will eventually hit a quota or a flaky page; the run resumes instead of restarting |
| **Bounded parallelism** | `extract_pdf_pages.py` — batches of 3 × 4 workers (`ThreadPoolExecutor`) | keeps the 134-page sweep inside rate limits while still finishing in ~9 min |
| **Provenance tagging on repaired fields** | `enrich_schema_vision.py:172` / `:178` — `tolerance_source = "vision"` | a value a model read off an image is never indistinguishable from a value the file contained ([the-bug-i-fixed.md](the-bug-i-fixed.md)) |
| **Cached values, not formulas** | `flatten_excel.py` — `openpyxl(data_only=True)` | the schema records what the sheet *evaluates to*, not what it computes |
| **Header-row autodetection** | `flatten_excel.py` — searches for `"Id." + "Operation Description"` | the data header sits anywhere between rows 18 and 36 depending on the tab; a hard-coded row would silently mis-read entire sheets |
| **Id disambiguation** | `flatten_excel.py` — `number_format`-aware formatting, letter suffixes (`4.1`, `4.1b`) | float rounding makes `1.10` and `1.1` collide, and the same id is reused across sections of one tab; colliding ids would overwrite each other's values |
| **`find_data_end()` scans columns A,B,C,F–J** | `flatten_excel.py` | one tab has multi-position rows with no id in column A; scanning only column A truncated the sheet early |
| **Vision fallback for text-missed fields** | Phase 3 matching | when the page catalog can't locate a field in extracted text, the page image is consulted rather than giving up |
| **Coverage analysis as a quality gate** | `analyze_coverage.py` | every field is classified present/absent × extracted/empty — the run is not "done" until it is *measured* |
| **Write to a copy, never the template** | `write_to_excel.py` | one output workbook per part; the template stays pristine and the sheet's own OK/NOK formulas do the judging |
| **Multi-part split** | Phase 3 — `{pieces[], common_data}` | shared data captured once, per-part measurements separated by serial, so one part's values can never leak into another's record |

## How I evaluate

Quality is measured as a **confusion matrix over all 293 schema fields**
([`artifacts/coverage-matrix.json`](artifacts/coverage-matrix.json)) rather than as a count of fields
extracted — because only **37%** of the fields are present in this report, which makes "correctly left
empty" the majority-correct behaviour and the naive metric meaningless. The full case matrix, the
recorded negative case and the declared gaps are in **[EVALUATION.md](EVALUATION.md)**.

## Known limitations

- **One report.** Everything here is a single 134-page report covering 3 parts, from one
  manufacturer. Robustness across suppliers is Phase 5 and is not evidenced.
- **No automated eval suite.** The confusion matrix is produced by a real tool on real output, but
  there is no labelled regression set and no before/after harness — which is exactly what the
  diagnosed improvements would need in order to be *proven* rather than assumed.
- **The quality gap is diagnosed, not closed.** 32 false positives and 36 misses, with root causes
  identified per bucket; the remediation was planned and prioritised but not implemented in the pilot.
- **No human-in-the-loop yet.** Values are written to the output Excel without an approval step. For
  quality-control data that is a hard requirement before any real use — it is Phase 6, and the pilot's
  69% precision is nowhere near good enough to skip it.
- **Ground truth is the coverage analysis itself.** "Present in the report" is determined by the same
  pipeline whose accuracy is being measured, so the matrix is a self-assessment, not an independent
  audit. A labelled set produced by a quality engineer is the missing piece.

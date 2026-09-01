# Artifacts — real outputs (sanitized)

Real outputs of the pilot: the client's inspection schema as flattened from their Excel, the two
recorded Vision runs, the coverage analysis, and the write-back report. Every file carries a
`_provenance` block naming the tool that produced it and the month it ran.

| File | What it is | Real? | Sanitized? |
|------|-----------|:----:|:----------:|
| [`schema-structure.json`](schema-structure.json) | The client's inspection record flattened into the extraction schema: **11 tabs, 293 fields (212 numeric, 81 boolean)**, with each tab's field count | ✅ | dimensions, tolerances, serials and people removed — counts and tab structure only |
| [`schema-build-run.json`](schema-build-run.json) | **Recorded run 1 (targeted Vision):** the Phase-1 schema build, including the 12 unreadable GD&T tolerance cells resolved by focused Vision calls → 0 | ✅ | nothing to change (counts only) |
| [`extraction-stats.json`](extraction-stats.json) | **Recorded run 2 (blind Vision):** the Phase-2 page sweep — **134 pages, 0 failed, 46 calls, ~9 min**, batch 3 × 4 workers, plus the real page-type and language breakdown | ✅ | nothing to change (counts only) |
| [`coverage-matrix.json`](coverage-matrix.json) | The confusion matrix over all 293 fields, in total and per tab: true positives, misses, false positives, correctly-empty | ✅ | per-field reasoning removed (it quoted real measurements); counts kept |
| [`fill-report.json`](fill-report.json) | The Phase-4 write-back: one workbook per part, **175 of 293 cells filled** each, 0 out of tolerance | ✅ | serial numbers → `Piece A/B/C` |
| [`raw-page-example.json`](raw-page-example.json) | One page's raw Vision extraction, **structure only** — shows the per-page schema the model returns | ✅ shape | all content redacted to type markers (`[text]`, `[3 items]`) |

## What "sanitized" changed

- **Client identity:** the client (a wind-energy components manufacturer) and its product line never
  appear in these files; the case study refers to them generically in prose only.
- **Document identifier:** the inspection-record number in every `sheet_id` is replaced with a
  constant placeholder (`INR-0000-R00`). The tab names themselves — *Flange Reception*, *Tube Weld*,
  *Welding*, *Finishing*… — are generic manufacturing-process vocabulary and are kept, because the
  distribution of fields across process stages is the evidence that the schema is real.
- **Serial numbers:** the 3 real part serials → `Piece A`, `Piece B`, `Piece C`.
- **Measurements:** every actual measured value, tolerance, certificate number, company name, date and
  signature is removed. This is the significant deletion in this case study: the artifacts carry the
  *shape and the counts* of the data, never the data.
- **Page content:** `raw-page-example.json` keeps the response schema and the metadata flags
  (`has_stamp`, `has_signature`) and redacts everything else.

## What is NOT changed (this is the evidence)

- **The counts.** 293 fields · 212 numeric / 81 boolean · 11 tabs · 134 pages · 0 failed · 46 Vision
  calls · 12 → 0 unreadable tolerance cells · 108 present / 185 absent · 72 / 36 / 32 / 153 · 175 of
  293 cells filled per part.
- **The run parameters** copied from the real code path: 200 DPI rendering, batches of 3, 4 workers,
  resumable checkpoint.
- **The per-tab distribution** in `coverage-matrix.json`, which is what makes the failure pattern
  legible (see [../EVALUATION.md](../EVALUATION.md)): the tabs with zero false positives and the three
  that concentrate 27 of the 32.

## Note on per-field provenance (the honest gap)

There is **no archived value→page trace**. The running system does map each field to its candidate
pages (`map_schema_to_pages.py`) and extract against them, but that mapping was not exported, and the
per-field reasoning that *was* exported had to be removed because it quoted real measurements
verbatim. So this case study can show the aggregate quality of the extraction but cannot show a worked
"this value came from page N" citation. The exact steps to record it are stated in
[../EVALUATION.md](../EVALUATION.md); it is not reconstructed or approximated here.

> Confidentiality: no credentials, API keys, client names, personal names or measured values appear in
> any artifact. Written only after `verify_case_study.py` passes.

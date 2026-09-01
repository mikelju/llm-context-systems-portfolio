# The bug I fixed: 12 tolerances the spreadsheet itself could not compute

## Symptom

Phase 1 flattens the client's 11-tab Excel inspection record into the 293-field extraction schema.
The flattening "worked" — 293 fields, 212 numeric, 81 boolean — but **12 numeric fields came out with
`#VALUE!` where their tolerance should be**.

That is worse than it looks. A dimensional field without a tolerance is not a half-filled field, it is
an **unusable** one: the whole point of the pipeline is to write a measurement into the Excel and let
the sheet's own formulas decide OK/NOK. With no tolerance there is nothing to decide against. Twelve
fields would have been extracted, written, and then silently evaluated against garbage.

## Root cause

`flatten_excel.py` reads the workbook with `openpyxl` and `data_only=True` — that is, it asks for the
*cached computed value* of each cell rather than the formula. Correct choice, and it works for 281 of
the 293 fields.

Those 12 cells hold GD&T (geometric dimensioning and tolerancing) tolerances, and their formulas
don't produce a number: they **render a graphical symbol**. Excel displays the symbol; the cached
value it stores is the error `#VALUE!`.

So the bug was not in the reader. **The number genuinely is not in the file.** No Excel parser —
openpyxl, pandas, a different library — could have recovered it, because there is nothing to recover.
The information exists only as pixels, in a sheet that renders correctly for a human and returns an
error to a program.

The tempting fixes were both wrong: fall back to the nominal value (invents data into a quality
record) or leave the field empty (drops 12 real requirements and makes the coverage analysis lie
about what the report *should* contain).

## The fix

Don't fix the reader — **change the question**. If the value is only visible, ask something that can
see, and ask it as narrowly as possible.

`enrich_schema_vision.py` runs as a second pass over the flattened schema:

| Step | Where | What it does |
|---|---|---|
| find the damage | `enrich_schema_vision.py:24` — `find_broken_fields()` | scans the schema for `"#VALUE"` in a value (`:32`) and groups the hits **by sheet** |
| narrow the input | `:40` — `find_images_for_sheet()` | selects only the rendered PNGs of the affected sheets, not the 23 sheet images |
| ask precisely | `:59` — `build_enrichment_prompt()` | a prompt naming the specific fields: *read the exact values shown in the cells for these specific fields that have formula errors in the digital file* |
| read | `:129` — `call_gemini_vision()` | ~3 focused Vision calls, not one per sheet |
| **record where it came from** | `:172` / `:178` | writes `tolerance_source = "vision"` / `dimension_source = "vision"` on every field it repaired |

That last row is the part I would keep in any future version. The repaired values are not silently
merged into the schema as if the spreadsheet had provided them: each one is **tagged with its
provenance**, so anything downstream — and any auditor — can tell a value the file contained from a
value a model read off an image.

## Result

**12 unreadable tolerance cells → 0.** Recorded in
[`artifacts/schema-build-run.json`](artifacts/schema-build-run.json)
(`unreadable_tolerance_cells_before: 12`, `unreadable_tolerance_cells_after: 0`,
`vision_calls_focused: 3`), and confirmed by the phase's cross-validation step, which checks the
schema for unique ids and zero remaining `#VALUE!` fields.

The 293-field schema every later phase depends on is therefore complete — and the 12 values that came
from a model rather than from the file are marked as such.

## Why it's a good story

It is a bug that **only real, messy data produces**. Nobody writes a test fixture whose formulas draw
symbols; you meet this on a template that has been in production use at a client for years, where a
convention that renders beautifully in Excel is invisible to every program that opens it.

It also rehearses, in miniature, the argument the whole case study makes. Two ways of pointing the
same vision model at the same client's documents, both recorded:

- **targeted** — *what is the tolerance of these 12 specific cells?* → 12 of 12 resolved, ~3 calls;
- **blind** — *what is on this page?* × 134 pages → every page read, but the values then had to be
  matched back to fields, and that is exactly where the **32 false positives** came from
  ([EVALUATION.md](EVALUATION.md)).

Same model, same documents, opposite failure profile. The difference is whether the schema was known
*before* the question was asked. That is the case study's core decision
([schema-first-extraction.md](schema-first-extraction.md)), and this bug is where it first paid off.

> **Honest scope.** This is the bug that was *fixed*. The larger quality problem — 32 hallucinated
> fields and 36 misses — was measured and diagnosed down to root cause and file, but the remediation
> was **not implemented** in the pilot. It is documented as an open gap in
> [EVALUATION.md](EVALUATION.md), not as a fix.

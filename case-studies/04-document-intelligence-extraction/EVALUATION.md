# Evaluation

The evaluation *is* the confusion matrix. Every one of the 293 schema fields is classified along two
axes — **is it present in the report?** × **did the pipeline extract a value?** — which yields the
four buckets below. Source of truth:
[`artifacts/coverage-matrix.json`](artifacts/coverage-matrix.json), produced by `analyze_coverage.py`
on the real pilot run.

|  | extracted a value | left empty |
|---|---|---|
| **field IS in the report** (108) | **72** true positive | **36** missed |
| **field NOT in the report** (185) | **32** hallucinated | **153** correctly empty |

precision **69%** · recall **67%** · specificity **83%** · only **37%** of the schema is answerable
from this report at all.

## The case matrix

| # | Scenario | Why it matters | Status | Evidence |
|---|---|---|---|---|
| 1 | **Field present → correct value extracted** | the base case | ✅ recorded | 72 fields; `extracted_ok` |
| 2 | **Field absent → left empty** (the domain negative case) | the majority-correct behaviour: 185 of 293 fields are not in this report at all | ✅ **recorded** | 153 fields; `correctly_empty`. Cleanest instances: the two *Plate Cutting & Bevelling* tabs, **12 of 12 absent fields left empty with 0 false positives** each, and *Finishing*, **17 of 17** |
| 3 | **Field absent → value invented** | the dangerous failure: a fabricated measurement in a quality record | ✅ recorded | 32 fields; concentrated in three tabs — *Tube Weld* (10), *Welding* (9), *Flange Reception* (8). In *Packaging & Storage*, where **nothing** is present, 1 of 5 absent fields still got a value |
| 4 | **Field present → missed** | lost work; the engineer still has to fill it by hand | ✅ recorded | 36 fields, root-caused into 14 uninferred certificate booleans + 7 vocabulary mismatches + 15 others |
| 5 | **Source cell unreadable by any parser** | the template's GD&T formulas render symbols; the value exists only as pixels | ✅ recorded, **fixed** | 12 → 0 via focused Vision; [`schema-build-run.json`](artifacts/schema-build-run.json), [the-bug-i-fixed.md](the-bug-i-fixed.md) |
| 6 | **Multi-part report → one record per part** | the report covers 3 parts by serial; a value from part A in part B's record is a QC incident | ✅ recorded | `{pieces[], common_data}`; 3 workbooks, 175/293 filled each — [`fill-report.json`](artifacts/fill-report.json) |
| 7 | **Extracted value outside tolerance** | the sheet's own formulas must flag NOK | ⚠️ recorded, but **never triggered** | `out_of_tolerance: 0` across all 3 parts. The path is exercised by the Excel formulas, not by this pipeline; no NOK case was observed in this report |
| 8 | **A second manufacturer's report** | vocabulary, layout and page order all change | ❌ pending | Phase 5; would need ≥3 reports |
| 9 | **Human approves before write-back** | 69% precision must not reach an official record unreviewed | ❌ pending | Phase 6 (traffic-light HITL) |

Seven of nine recorded; the two pending are unbuilt phases, not untested code.

## The negative case, in detail

For extraction, the negative case is **"the field is not in the document → return nothing"**, and it
is the one an LLM fails by construction: handed a form, a model fills it. This pilot records both
sides of that behaviour.

Where it works — two tabs are perfect negatives:

| Tab | fields | present | absent | correctly empty | false positives |
|---|---|---|---|---|---|
| Plate Cutting & Bevelling (×2) | 16 | 4 | 12 | **12** | **0** |
| Finishing | 19 | 2 | 17 | **17** | **0** |

Where it fails — the same behaviour, inverted:

| Tab | fields | absent | correctly empty | false positives |
|---|---|---|---|---|
| Flange Reception | 28 | 14 | 6 | **8** |
| Tube Weld | 66 | 53 | 43 | **10** |
| Packaging & Storage | 5 | 5 | 4 | **1** |

The pattern is legible: the model invents where the report contains *adjacent, similar-looking* data
— a straightness figure in mm offered for a field asking mm/m, a diameter assigned to a height — and
behaves perfectly where the report has nothing resembling the field at all. Not random hallucination:
**forced matching**. That is why the diagnosed remediation is a post-extraction validation step (unit
and tolerance agreement, `needs_review` instead of silent acceptance) rather than a better prompt.

## Faithfulness mapping (claim → source)

Every number published in this case study resolves to a field in a real artifact:

| Claim | Source field |
|---|---|
| 134 pages read, 0 failed | `extraction-stats.json` → `metrics.pages`, `metrics.pages_failed` |
| 46 Vision calls, batch 3 × 4 workers | `extraction-stats.json` → `metrics.api_calls`, `batch_size`, `workers` |
| 131 of 134 pages bilingual | `extraction-stats.json` → `pages_by_language.bilingual` |
| 293 fields (212 numeric, 81 boolean), 11 tabs | `schema-structure.json` → `summary` |
| 12 unreadable tolerance cells → 0 | `schema-build-run.json` → `metrics.unreadable_tolerance_cells_before/after` |
| 72 / 36 / 32 / 153 and the three rates | `coverage-matrix.json` → `metrics`; rates recomputed live by the demo |
| 175 of 293 cells filled per part, 0 out of tolerance | `fill-report.json` → `pieces[]` |

**The gap, stated plainly:** the per-field provenance chain — *this value came from page N* — exists in
the running system (`map_schema_to_pages.py` maps each field to its candidate pages, and
`extract_matched_data.py` extracts against them) but **was not archived as an artifact**, so this case
study cannot show a worked value→page citation. To record it, one would re-run Phase 3 with the
per-field page ids retained in the output JSON and sanitize the measurements out, keeping ids only.
That is the single most valuable artifact this case study is missing, and it is not fabricated here.

## What a real eval suite needs

1. **A labelled ground truth** produced by a quality engineer, not by the pipeline. Today "present in
   the report" is decided by the same system being measured — the matrix is a self-assessment.
2. **≥3 reports from different manufacturers**, so vocabulary drift is measured rather than assumed.
3. **A before/after harness** on the same labelled set, so the three diagnosed improvements
   (certificate-boolean inference, a synonym dictionary, post-extraction validation) are *proven* to
   move precision and recall instead of being expected to.
4. **Per-field provenance in the output**, which makes every extracted value auditable and turns
   spot-checking into a bounded task.
5. **A NOK case.** This report produced zero out-of-tolerance values, so the branch that matters most
   to a quality engineer has never actually fired.

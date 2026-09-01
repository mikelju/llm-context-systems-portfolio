# The signature decision: schema-first extraction + measure it as a confusion matrix

## The problem

The naive approach — "send the pages to a vision model and ask it to pull out the data" — fails on a
134-page bilingual scanned report in two opposite ways:

- it **misses** fields that are there but phrased differently (the client's INR says "External
  Diameter"; the supplier's translated report says "Outside Diameter" or "Point 13"), and
- it **invents** fields that aren't there at all, because an LLM asked to fill a form will force a
  plausible-looking match rather than say "absent".

## The choice + why

**Flatten the target Excel into a precise 293-field schema first, then extract against it — and treat
the result as a classification problem, not a free-form read.**

- **Schema-first** (`flatten_excel.py`): you know the exact 293 fields (212 numeric with units and
  tolerances, 81 boolean OK/NOK), their tabs, and which ones a given report *should* contain. Vision
  even resolves the 12 `#VALUE!` GD&T-tolerance cells the Excel itself couldn't compute.
- **Per-field matching** via the page-catalog "Librarian" (the same pattern reused from
  [case 01](../01-rag-knowledge-system/)): locate the page(s) for each field, then extract focused.
- **Measure as a confusion matrix** (`analyze_coverage.py`): every field is `present/absent` in the
  report × `extracted/empty`, giving true positives, **false positives (hallucinations)**, misses, and
  — crucially — **true negatives (correctly left empty)**. Only **37%** of the 293 fields are present
  in this report, so "correctly empty" (153 fields) is the majority-correct behaviour, not an
  afterthought. (Real numbers: precision 69%, recall 67%, specificity 83%.)

This reframes "extract the data" as "for each known field, decide present-and-correct /
absent-and-empty / mistake" — which is both more accurate **and** measurable.

## When I would do it differently / scale it

The pilot ran one report (3 parts) end-to-end. To process hundreds across suppliers (Phases 5–6):

- **Trigger:** the 134-page, 46-call extraction is fine for one report; at scale the cost is the
  per-page Vision call, so add **automatic page segmentation** (classify + group pages, extract
  sections not 134 raw pages) before anything else.
- **Measure first:** the confusion matrix already exists — expand it into a labelled set across **≥3
  manufacturers** and track precision/recall *before* and *after* the false-positive fix
  ([the-bug-i-fixed.md](the-bug-i-fixed.md)), so improvements are proven, not assumed.
- **Then:** a human-in-the-loop traffic-light review (green=safe OK / yellow=doubtful / red=NOK) so an
  engineer approves before anything is written to the official Excel — non-negotiable for QC data.

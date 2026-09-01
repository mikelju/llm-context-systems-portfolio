# Lessons learned

## 1. Flatten the target form before you read the document

The instinct is to start with the 134-page PDF. Starting with the **Excel** instead — turning 11 tabs
into an explicit 293-field list with units, tolerances and types — is what makes every later stage
specific: the matcher knows what to look for, the extractor knows what shape the answer has, and the
coverage analysis knows what *should* be absent. Reading the document first would have produced a pile
of correct facts that nobody could map to a form.

## 2. "Fields extracted" is a vanity metric when most fields are absent

Only **37%** of the 293 fields are present in this report. A pipeline that extracted nothing at all
would be 63% "correct" on any naive measure. Framing extraction as a **confusion matrix** — with
`correctly_empty` (153) as a first-class outcome — is what turned a subjective "it seems to work"
into precision 69% / recall 67% / specificity 83%, and it is what made the 32 false positives visible
at all.

## 3. A model handed a form will fill the form

The 32 hallucinations are not random: they cluster exactly where the report contains *adjacent,
plausible* data — a straightness value in mm offered for a field asking mm/m, a diameter assigned to
a flange height. Tabs where the report holds nothing resembling the field scored **zero** false
positives. Absence has to be an explicit, rewarded answer, not the default that happens when the
model finds nothing. That is a validation-step problem, not a prompt-wording problem.

## 4. Ask narrow questions when you can afford to

The two recorded Vision runs point the same model at the same client's documents with opposite
framings: **targeted** (12 named cells → 12 of 12 resolved, ~3 calls) and **blind** (134 pages →
every page read, but the values then had to be matched back to fields, which is where the false
positives entered). Narrow questions were both cheaper and more accurate. The catch is that you can
only ask them once you know the schema — see lesson 1.

## 5. Real client templates break every reader

None of these were in the plan: 12 tolerance cells whose formulas render **graphical symbols** and
therefore cache as `#VALUE!`; header rows that sit anywhere between rows 18 and 36 depending on the
tab; ids that collide because `1.10` and `1.1` are the same float; a tab with multi-position rows that
carry no id in column A and truncated the sheet early. A template that has been in daily use at a
client for years encodes years of human convention — all of it invisible to a parser. Budget for it.

## 6. Tag where a value came from

The Vision-repaired tolerances are written back with `tolerance_source = "vision"`
(`enrich_schema_vision.py:172`). Two lines of code, and the dataset stops being uniform: a human can
always separate what the file contained from what a model read off an image. In a quality-control
context that distinction is the difference between an auditable record and an unauditable one — and
it is the cheapest thing in this entire pipeline.

## 7. Make long model runs resumable before you need it

The 134-page sweep is 46 calls over scanned images, batched 3 × 4 workers. Quotas, timeouts and one
unreadable page are certainties, not risks. A thread-safe checkpoint (`extraction_state.json`) written
from the start meant every interruption cost a page, never the run.

## 8. A diagnosis is not a repair, and the write-up must say so

The coverage analysis produced a clean root-cause split of the 36 misses (14 uninferred certificate
booleans, 7 vocabulary mismatches) and of the 32 false positives (forced matching), with an
implementation order chosen by impact-over-effort and an expected recovery to ~86% efficiency. **None
of it was implemented.** It is tempting to present a diagnosis as an outcome; the honest version is
that this pilot ends with a measured problem, a named cause and an untested plan.

## What I'd do next

1. **Post-extraction validation** — compare each extracted value against the field's unit and
   tolerance, and mark suspicious values `needs_review` instead of accepting them. Diagnosed as the
   highest impact-per-effort change, and it attacks the dangerous failure (invented values in a QC
   record) rather than the merely annoying one.
2. **Certificate-boolean inference** — teach the extractor that the *existence* of a conforming
   certificate is itself the evidence for "Chemical Composition: OK"; 14 of the 36 misses are this
   single rule.
3. **Measure both on a labelled set before adopting either** — the confusion matrix already exists, so
   the before/after comparison is cheap. Without it, "86% expected" stays an estimate.
4. **Then** human-in-the-loop review (green/amber/red per field) before anything reaches an official
   inspection record. At 69% precision this is not optional, and no amount of prompt tuning replaces it.

<!-- Spec §5/§6. Declare every artifact; disclose every change beyond token substitution. -->
# Artifacts — real outputs (sanitized)

Real outputs from the actual system, not mock-ups. Identifiers/labels sanitized; the **measured
evidence** (counts, timings, tokens, funnel, answer text) is untouched.

| File | What it is | Real? | Sanitized? |
|------|-----------|:----:|:----------:|
| `<state>.json` | <structured state: catalog/schema/index> | ✅ | <what changed> |
| `<trace-a>.json` | <run trace: steps, references, metrics> | ✅ | <what changed> |
| `<trace-b>.json` | <a CONTRASTING run (different path)> | ✅ | <what changed> |

Produced by `<real module>.py`; see each file's `_provenance`.

## What "sanitized" changed
<!-- client names, sites, brands, quasi-identifiers (band numeric specs), internal paths, dates coarsened, ids regenerated -->

## Corrections disclosed (field-level)
<!-- ONLY id regeneration or a field derivable from another field in the same artifact. before→after. NEVER metrics/funnel/answer. -->

> **Cross-artifact consistency:** every `document_id` in a trace exists in the state artifact; every
> `references[]` entry resolves to a read entry with a non-empty id. (`verify_case_study.py` checks this.)

## What is NOT changed
The metrics block, funnel counts, answer text, and counts.

> Confidentiality: no credentials, API keys, production URLs or PII appear in any artifact. Written
> only after `verify_case_study.py` passes.

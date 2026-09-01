# Extraction flow

## The funnel (real pilot numbers)

```
134 scanned pages ──Vision──> 134 page extractions      (0 failed, ~9 min, 46 calls)
        │
293 schema fields ──match──>  108 present in the report  +  185 absent
        │                            │                          │
        │                       72 extracted_ok            153 correctly empty   (good)
        │                       36 missed                   32 hallucinated      (errors)
        ▼
   write back  ──>  one Excel per part (3 parts), 175/293 cells filled
```

So the pipeline narrows **293 target fields → 108 actually answerable → 72 captured**, while keeping
**153 of the 185 absent fields correctly empty**. The two error buckets are the 36 misses and the 32
false positives (see [the-bug-i-fixed.md](the-bug-i-fixed.md)).

## The two recorded runs, side by side

The core decision — know the schema *before* asking — is visible in the two Vision runs the pilot
recorded. Same model, same client's documents, opposite framing:

| | **Run 1 — targeted** (Phase 1) | **Run 2 — blind** (Phase 2) |
|---|---|---|
| Question asked | "what is the tolerance of *these 12 named cells*?" | "what is on this page?" × 134 |
| Schema known first? | **yes** — the 293 fields already existed | no — the schema is not consulted |
| Input | 12 cells across 23 rendered sheet images | 134 scanned pages at 200 DPI |
| Vision calls | **3** (focused) | **46** (batch 3 × 4 workers, resumable) |
| Direct result | **12 of 12 resolved**, 0 left unreadable | **134 of 134 read**, 0 failed, ~9 min |
| What happened next | values written back **tagged** `tolerance_source = "vision"` | values still had to be matched to fields — **all 32 false positives enter here** |
| Source | [`artifacts/schema-build-run.json`](artifacts/schema-build-run.json) | [`artifacts/extraction-stats.json`](artifacts/extraction-stats.json) |

**Why it matters.** The blind run is not the failure — it read every page it was given. The failure is
structural: reading first and matching afterwards asks a model to decide, with no schema in hand,
which of 293 fields a page answers, and a model handed a form fills the form. The targeted run
never faces that question, which is why it is both cheaper and cleaner. The pilot needs both, but
the more of the work that can be moved into the targeted shape, the fewer invented values reach a
quality record. That is the whole argument of
[schema-first-extraction.md](schema-first-extraction.md).

## The confusion matrix (the real evidence)

|  | extracted a value | left empty |
|---|---|---|
| **field IS in the report** | 72 ✅ true positive | 36 ⚠️ missed |
| **field NOT in the report** | 32 ❌ hallucinated | 153 ✅ correctly empty |

- **precision** = 72/(72+32) = **69%** · **recall** = 72/(72+36) = **67%** · **specificity** =
  153/(153+32) = **83%**.
- The demo recomputes these live from [`artifacts/coverage-matrix.json`](artifacts/coverage-matrix.json).

## Per-page reality (why Vision, not text)

The 134 pages span **9 document types** — `test_report` (33), `ndt_report` (33), `certificate` (24),
`drawing` (20), `dimension_record` (12), `material_cert` (5), `cover` (3), `welding_record` (1) — and
**131/134 are bilingual (Chinese/English), scanned**. Stamps, hand-filled tables and drawings carry
the data; that's why each page is read as an image, not extracted as text. Source:
[`artifacts/extraction-stats.json`](artifacts/extraction-stats.json).

## Multi-part

The report covers several manufactured parts (serial numbers); extraction produces
`{pieces[], common_data}` so shared data is captured once and per-part data (e.g. dimensional
measurements) is split per serial — one output Excel each.

Diagram: [assets/extraction-sequence.md](assets/extraction-sequence.md).

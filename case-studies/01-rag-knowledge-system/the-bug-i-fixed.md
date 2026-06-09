# A Real Bug I Fixed — Corrupt TOC on a Scanned PDF

A portfolio of happy paths proves nothing. Here is a concrete failure, its root cause, and the
fix — the kind of thing that only shows up when you run a real pipeline on real documents.

## Symptom

Processing a **322-page scanned book** produced an `index.json` with **5 chapters all titled
"Página en blanco" ("blank page")** and nonsensical page ranges:

```
[1, 'Página en blanco', 2]
[1, 'Página en blanco', 1]
[1, 'Página en blanco', 1]
[1, 'Página en blanco', 320]
[1, 'Página en blanco', 8]
```

With this garbage structure, content extraction and every downstream analysis step were useless.

## Root cause

The PDF shipped a **corrupt native TOC (bookmarks)**. `extract_pdf_structure()` had a 3-attempt
strategy (native TOC → heuristics → Gemini Vision), but **Attempt 1 trusted the native TOC
without any quality check**, so it "succeeded" with junk and **never reached Attempt 3 (Vision)**,
which would have read the book's real printed index on pages 6–7.

A second, latent bug: Attempt 3 only sent the first 5 + last 3 pages to Vision — not enough to
catch an index that starts after page 5.

## The fix (4 parts)

1. **Validate the native TOC before trusting it** (`extract_structure.py:59–76`). Require that at
   least **50% of titles are real** (not in a known junk set: "página en blanco", "blank page",
   "untitled", …). If it fails validation, log it and fall through to the next attempt.
2. **Send more pages to Vision for long scans** (`extract_structure.py:130–140`). For scanned PDFs
   over 20 pages, send the first **15** pages (not 5) + last 3 — covering where indexes usually live.
3. **Better Vision prompt** (`extract_structure.py:146–164`). Explicitly ask it to find a table of
   contents and use the page numbers exactly as printed.
4. **UTF-8 stdout on Windows** (`process_batch.py:11–13`). A side issue surfaced while debugging:
   special characters/emoji crashed the console with `UnicodeEncodeError`. Forcing UTF-8 stdout
   fixed it. *(The same class of fix is applied in the [demo](demo/run_demo.py).)*

## Result

The document now processes correctly into **39 chapters** with real titles and correct page ranges
matching the printed index.

## Why it's a good story

- It's a **quality-gate** lesson: an upstream component returning *plausible-but-wrong* data is
  worse than one that fails loudly. The fix was to **distrust** the easy path and verify it.
- It shows the value of a **layered fallback** (native → heuristic → Vision) *with validation
  between layers*, not just a try/except chain.
- It's the kind of bug you only hit with **real, messy, scanned documents** — exactly the
  environment these systems run in.

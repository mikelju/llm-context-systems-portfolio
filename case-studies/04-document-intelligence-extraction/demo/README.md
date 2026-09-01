# Runnable demo — offline

Runs **offline, no API key, no network, no model call**, from the sanitized artifacts in
[`../artifacts`](../artifacts).

## What it does

1. **A — the input.** The real Phase-2 sweep: 134 scanned pages, 0 failed, 46 Vision calls, ~9 min,
   the page-type breakdown and the fact that 131 of 134 pages are bilingual and scanned — which is
   why the pipeline reads pages as images instead of extracting text.
2. **B — the target.** The client's inspection record as flattened: 11 tabs, 293 fields (212 numeric,
   81 boolean).
3. **C — the live step.** The funnel and the confusion matrix, **recomputed in the process you are
   running** from the real counts in `coverage-matrix.json`: precision, recall and specificity are
   divided out on the spot, not read from a file. This is the arithmetic that turns "it extracted
   some fields" into a measurable claim, and it is deterministic, so you can check it by hand.
4. **D — the write-back.** The Phase-4 result: one workbook per part, 175 of 293 cells filled, 0 out
   of tolerance.

> **Honesty note.** The extraction itself — 134 scanned pages sent to Gemini Vision — used the live
> API and is **not run here**; neither is the Excel write-back. What you see are the recorded pilot
> results, with the quality metrics recomputed offline from the real confusion matrix. It is **not**
> the full pipeline.

## Run it

```bash
python run_demo.py                 # stdlib only
pip install -r requirements.txt    # optional — only `rich`, for the boxed table
```

The demo degrades cleanly without `rich` (plain-text table, same numbers). Re-capture the expected
output after any change: `python run_demo.py > example_output.txt`.

## Expected output

See [`example_output.txt`](example_output.txt). The line worth reading twice is the last one in
section C: only **37%** of the 293 fields are present in this report at all, so the 153 fields the
pipeline correctly left empty matter as much as the 72 it filled — a system that scored well by
extracting everything would be worse, not better.

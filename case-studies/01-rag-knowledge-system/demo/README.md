# Runnable demo — "The Librarian" retrieval flow

This makes the case study **executable**. It runs **offline, with no API key and no network**,
using the real sanitized artifacts in [`../artifacts`](../artifacts).

## What it does

1. **Knowledge base overview** — prints the catalog (documents, type, strategy, chapters/pages).
2. **Step 1 reproduced live** — a deterministic catalog pre-filter that ranks candidate documents
   for a query from their titles/tags/summaries. This is the only step reproduced in code; it
   needs no model.
3. **Real recorded runs** — loads two recorded real-system query traces and prints the retrieval
   **funnel** (docs selected → confirmed → candidate chapters → chapters read) and the **real
   cost/latency metrics** (seconds, API calls, tokens, source references).

> **Honesty note.** In the real system, Steps 2–5 (chapter selection, reading, synthesis) are
> LLM-driven. The demo does **not** call any model — it reproduces the deterministic control flow
> (Step 1) and reports the *recorded* metrics of the LLM steps. The numbers were produced by the
> real system, not invented for the portfolio.
>
> The deterministic pre-filter is an **offline approximation of Step 1**, not a replay of the
> exact LLM selection — so it may pass a different number of candidates than the recorded run
> (e.g. 3 vs. the 5 the real system selected for the safety query). The funnel/metrics shown for
> the recorded runs are the real ones; the pre-filter just illustrates the *kind* of decision
> Step 1 makes.

## Run it

```bash
# from this folder
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt      # optional — only installs `rich` for prettier output
python run_demo.py
```

`rich` is optional: the script falls back to plain text if it isn't installed, so
`python run_demo.py` works with **zero dependencies** too.

## Expected output

A captured run is in [`example_output.txt`](example_output.txt). Excerpt:

```
Run 2 - 'safety measures' (cross-document over 4 manuals, hierarchical)
  funnel : catalog -> 5 docs selected -> 4 confirmed -> 9 candidate chapters -> 8 chapters read
  cost   : 88.5s | 7 API calls | 37,898 in + 6,793 out = 44,691 tokens
  context: only 8/9 candidate chapters were actually read (89% kept)
  sources: answer cites 8 traceable (document -> chapter) references
```

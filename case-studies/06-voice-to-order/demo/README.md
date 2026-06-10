# Runnable demo — offline

Runs **offline, no API key, no network, no model call**, using the sanitized artifacts in
[`../artifacts`](../artifacts).

## What it does
1. **State overview** — the real corpus (31,070-row catalog, 1,001-mapping learned memory), the
   models, and the concurrency bounds.
2. Two **live deterministic steps**, both genuinely part of the system:
   - **Step 4's memory-first rule**: dictated phrases looked up in the real learned-memory rows, the
     hit pinned above catalog candidates, the dedup rule, and the real **re-rank fallback ordering**
     (`Historical_match desc, Score desc`) — note the memory hit outranking a higher-scoring catalog
     row;
   - **Step 7's degradation matrix**: the real `SIMULATE_FAILURE` semantics (3 injection points) →
     per-channel status lights.
3. **Recorded evidence** replayed verbatim: a hand-validated extraction pair (1 of 47), the 21-line
   high-volume pair, and the fix-1 measurements.

> **Honesty note.** The real Step 4 matches by **embedding similarity** (pgvector/HNSW); the demo's
> lookup is a token-overlap **approximation** and prints that divergence. The model steps (whisper-1,
> gemini-2.5-flash extraction and re-ranking) and the live DB/ERP are **not run**. It is **not** the
> full engine.

## Run it
```bash
python run_demo.py                 # stdlib only
pip install -r requirements.txt    # optional — only `rich` for prettier output
```
Self-test (both must exit 0 and print the caveat): `python run_demo.py` and a no-`rich` run
(`python -c "import sys;sys.modules['rich']=None;import runpy;runpy.run_path('run_demo.py',run_name='__main__')"`).
Re-capture before done: `python run_demo.py > example_output.txt`.

## Expected output
See [`example_output.txt`](example_output.txt) — note the memory hit beating a higher similarity
score (the real sort key) and the degradation matrix keeping orders deliverable with the ERP down.

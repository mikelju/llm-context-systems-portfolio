# Runnable demo — offline

Runs the **real vector retrieval offline** (no API key, no network) over a 120-page sample of the real
embedding index, and replays the full-index nearest-neighbour results.

## What it does
1. Prints the real index stats (122 docs, 6,896 pages, `gemini-embedding-2`, dim 1536).
2. **Live cosine top-K** over the 120-page real-embedding sample (the actual retrieval algorithm,
   seeded from an indexed page) — real similarity scores.
3. Replays the full-index nearest-neighbour results from `../artifacts/retrieval-example.json`.

> **Honesty note.** This demo runs the retrieval **core** on real data. It does **not** run the
> natural-language path (embedding the question + answering with a vision LLM) — that needs the live
> API and was not archived — so it seeds the search from an indexed page to show the vector space
> itself. It is **not** the full system.

## Run it
```bash
python run_demo.py                 # zero dependencies (stdlib .npy reader + pure-Python cosine)
pip install -r requirements.txt    # optional — only `rich` for prettier tables
```
Self-test: `python run_demo.py` and a no-`rich` run must both exit 0 and print the honesty caveat.
Re-capture: `python run_demo.py > example_output.txt`.

## Expected output
See [`example_output.txt`](example_output.txt) — note how the nearest pages cluster by boiler
model/topic (the embedding space working).

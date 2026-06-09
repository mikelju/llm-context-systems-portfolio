# Architecture

Two small Python files do the work; the agent/UI lives in n8n + Telegram.

## Components (real modules)

| Part | File | What it does |
|------|------|--------------|
| **Indexer** | `prueba.py` | Renders every PDF page to a PNG (PyMuPDF, `ZOOM=2.0`), embeds each page **as an image** (`gemini-embedding-2`, `DIM=1536`), and caches the vectors to disk. Resumable + retry/backoff. |
| **Retrieval server** | `server.py` | FastAPI. Loads the cache at startup (no API call), exposes `POST /consultar`: embed the question → cosine top-K → send the labelled page images to a vision LLM → return the answer + the **source page image URL** + candidates + timings + tokens. |
| **Agent / UI** | n8n Cloud + Telegram | The "DocBot" agent calls `/consultar` as a tool (via an ngrok tunnel) and sends the answer + the page photo back to the technician. |

## The page-as-image pipeline

```
PDF → render page → PNG → embed image (gemini-embedding-2, 1536-dim) → cache (vector + file/page/path)
                                                                         │
question → embed text (same model) → cosine vs. all page vectors → top-5 pages
                                                                         │
        labelled page images → vision LLM → JSON {answer, pages used} → answer + source page image
```

- **Vectors in memory + a disk cache.** The index is a list of `{file, page, path, vec}`; the server
  just loads it (`load_index`) and never calls the API on startup, so it boots instantly and can't be
  taken down by a quota error.
- **Deterministic vs. model.** Rendering, caching, cosine search and JSON parsing are deterministic;
  the embedding and the answer are the model's job. The retrieval (the part this case study is about)
  is fully deterministic and runs offline — see the [demo](demo/).

## Design principle

> Don't flatten the page to text and lose the table. Embed the page **as it looks**, retrieve by
> visual+textual similarity, and hand the technician the actual page.

Diagrams: [assets/architecture-diagram.md](assets/architecture-diagram.md) ·
[assets/retrieval-sequence.md](assets/retrieval-sequence.md).

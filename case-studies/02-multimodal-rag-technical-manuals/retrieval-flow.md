# Retrieval flow

## The steps (`POST /consultar`)

1. **Embed the question** with `gemini-embedding-2` (same model as the pages), L2-normalize.
2. **Cosine search** — one dot-product of the query vector against the page matrix; take **top-5**.
   Sub-millisecond over 6,896 pages.
3. **Answer with vision** — send the 5 page images, each labelled `[PAGE n]`, to a vision LLM and ask
   for **JSON**: `{"respuesta": ..., "paginas": [n, ...]}` (the answer **and** which pages it used).
4. **Return** the answer + the **source page image URL** (the first page the LLM said it used; else the
   top-scored page) + the candidate list (with scores) + per-stage timings + token usage.

The response is intentionally inspectable — it carries `candidatas` (top-K with scores),
`paginas_usadas` (what the model cited), `tiempos_seg` (embed / search / llm / total) and `tokens`.

## What's deterministic vs. model-driven

Steps 1's normalization, **step 2's cosine search**, and the JSON parsing are deterministic. The
embedding (step 1) and the answer (step 3) are the model. **The retrieval core (step 2) is what the
[demo](demo/) runs live, offline, over the real embeddings.**

## Recorded retrieval evidence (real, offline)

I did not archive natural-language `/consultar` runs (they went through the live API). What I *can*
show, computed offline from the real index, is the **vector space itself** — for a seed page, its
nearest pages by real cosine similarity:

| Seed page | Nearest (real cosine) |
|---|---|
| `DEDIETRICH_GT-430_…MONTAJE` p13 | the sister model `GT-530` montage pages (0.77 / 0.75 / 0.74) |
| `DEDIETRICH_C310_MANUAL-CONDENSACION` p8 | other condensing-boiler maintenance pages (0.86 / 0.81) |
| `DEDIETRICH_REGULACION-ISYSTEM…` p32 | the **same regulation topic across models** (0.96 / 0.93) |

Source: [`artifacts/retrieval-example.json`](artifacts/retrieval-example.json). The clustering by
model/topic is the signal that the page-as-image embeddings capture the right structure.

> Honest gap: this shows retrieval quality *qualitatively*. A labelled query→expected-page set
> (precision/recall) is the pending evaluation — see [EVALUATION.md](EVALUATION.md).

Diagram: [assets/retrieval-sequence.md](assets/retrieval-sequence.md).

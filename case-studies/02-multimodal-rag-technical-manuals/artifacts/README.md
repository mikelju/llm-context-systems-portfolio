# Artifacts — real outputs (sanitized)

Real data from the multimodal-RAG PoC. The document corpus is **public boiler manufacturer manuals**
(De Dietrich, BAXI, ADISA, Bosch, Buderus, …) — not client-confidential — so the main sanitization is
removing the client/bot identity around the system, not the corpus.

| File | What it is | Real? | Sanitized? |
|------|-----------|:----:|:----------:|
| [`index-sample.json`](index-sample.json) | Index stats (122 docs, 6,896 pages, `gemini-embedding-2`, dim 1536) + a 40-page sample | ✅ | client/bot identity removed; raw vectors omitted |
| [`retrieval-example.json`](retrieval-example.json) | Real **offline** nearest-neighbour results over the full index (page → most similar pages, real cosine) | ✅ | none needed (public corpus) |
| [`retrieval-demo-vectors.npy`](retrieval-demo-vectors.npy) | A 120-page sample of the **real** L2-normalized embeddings (float32, 120×1536) so the demo runs real cosine offline | ✅ | sample of public-manual page vectors |
| [`retrieval-demo-meta.json`](retrieval-demo-meta.json) | `file`/`page` for each row of the `.npy` (row i ↔ rows[i]) | ✅ | none |
| [`security-audit-summary.md`](security-audit-summary.md) | The real security-audit findings (0C/1H/2M/2L) | ✅ | client/bot identity removed |

Produced by the real system (`prueba.py` indexer; cosine computed offline from the real index). See
each JSON's `_provenance`.

## What "sanitized" changed

- The **client** (a heating-systems field-service company) and the **bot product names** (→ DocBot /
  FieldBot) are removed/renamed in prose. They do not appear in these artifacts.
- **Raw vectors** are omitted from `index-sample.json`; a 120-page sample ships separately for the demo.
- **Kept (public):** manufacturer/model names in filenames — these are public manuals, kept for
  authenticity, and identify no client.

## What is NOT changed

The index **counts** (122 / 6,896), the embedding **model/dim**, and the **cosine scores** in the
nearest-neighbour results. Those are the evidence.

## Note on the natural-language query path

There is no `query-trace.*.json` here: end-to-end `/consultar` runs went through the live API and were
not archived, and I won't fabricate one (see [../EVALUATION.md](../EVALUATION.md)). The
`retrieval-example.json` is real **image→image** nearest-neighbour over the index, computed offline —
it shows the vector space, not a chat answer.

> Confidentiality: no credentials, API keys, ngrok URLs or PII appear in any artifact.

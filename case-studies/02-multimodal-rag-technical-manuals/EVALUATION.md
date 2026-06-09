# Evaluation

## Case matrix

| # | Scenario | Why it matters | Status | Evidence |
|---|----------|----------------|--------|----------|
| 1 | **Retrieval clusters by model/topic** | the page-as-image embeddings capture the right structure | ✅ Recorded (offline) | [`artifacts/retrieval-example.json`](artifacts/retrieval-example.json) — real cosine, e.g. same regulation topic across models at 0.96 |
| 2 | NL question → answer + source page | the full end-to-end value | ⏳ Not archived | needs the live API; the PoC is frozen pending client validation |
| 3 | **No answer in the corpus → refuse** | must not invent a fault code / pressure value | ⚙️ Built-in, trace pending | the prompt instructs *"if the answer isn't in the pages, say so clearly"* (`server.py` `INSTRUCCION`); a recorded refusal trace needs the live API |

## On the negative case (refusal)

Refusal is **designed into the prompt**, not an afterthought — the model is told to answer **only**
from the attached page images and to say so when the answer isn't there. I'm not shipping a recorded
refusal trace because the honest blocker is real: the PoC runs against the live API and was frozen
awaiting the client's go/no-go on retrieval quality, and I won't fabricate a trace to fill the row.
**To record it:** re-enable the API key, query something absent from the corpus (e.g. a warranty
clause), and capture the `/consultar` response — a ~10-minute task once the project is unfrozen.

## What would make this a real eval suite

1. A small **labelled set**: ~20–30 technician questions × the expected source page(s).
2. **Recall@5 / MRR** of the page retrieval, and a **faithfulness** check (does the answer match the
   returned page?), measured at `DIM` = 768 vs 1536 vs 3072 to settle the accuracy/size tradeoff.
3. One recorded **refusal** run (case 3 above).

This labelled validation is exactly the gate the client was asked to help define — the project's
status is *blocked on it by design*, not an oversight.

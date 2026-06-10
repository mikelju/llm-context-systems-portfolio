# The signature decision: where the model sits — and *not* a vector store

This case has one decision with two faces: **how much of the work the LLM does** (the agent/tool
boundary) and **how retrieval works inside the tool** (full-context vs a vector store). They are the
same decision — "use the model only where judgment is irreducible" — applied twice.

## The problem

On n8n Cloud there is no Python and no database, the documents are **visual** (boiler manuals are
diagrams and tables, not prose), and the audience is **field technicians who act on the answer** — so a
wrong or unsourced answer is worse than no answer. I had to decide what the model is allowed to do, and
how the right pages reach it.

## Choice 1 — the LLM does judgment only

In `WF-DocBot-Tool` there are **19 functional nodes and exactly 2 call the model**: `HTTP - Gemini
SELECT documents` (which docs are relevant) and `HTTP - Gemini ANSWER (full context)` (the grounded
answer). Everything between and around them is deterministic JavaScript:

| Boundary | Count | Nodes |
|---|---|---|
| **LLM (judgment)** | **2** | select documents · answer from full PDFs |
| deterministic | 10 | parse catalog · build selection prompt · evaluate selection · IF any-docs · no-results · the PDF loop · init poll · IF ACTIVE · build Gemini body · format response |
| io | 7 | Drive (find/download catalog, download PDF) · Gemini File-API upload + state poll · Wait · trigger |

*(verbatim from [`artifacts/tool-structure.json`](artifacts/tool-structure.json))*

The **agent** enforces the same boundary from the other side. Its system prompt makes it *tool-first by
construction*:

> "Tu única función es responder consultando los documentos… **NUNCA respondes desde tu conocimiento
> propio.** Cada respuesta se basa exclusivamente en lo que devuelve `<consultar_biblioteca>`."

So the model is a router-of-judgment, not the system: it decides *which* documents and *what* the answer
is, and a forced `Think` step after every tool call decides whether the result is sufficient. The catalog
parsing, the selection loop, the File-API polling, the Telegram formatting — none of it is the model's
job, which is what keeps the flow debuggable on a visual canvas and the cost bounded to two calls.

## Choice 2 — full-context, no vector store

The tool reads **whole PDFs** through the Gemini File API. The library is a `catalog.json` on Drive (15
documents, 13–14 pages each); the model picks the relevant ones from the catalog and reads them
complete. **No chunking, no embeddings, no vector database.** Why, at this scale:

- The information is **visual** — a vector search over extracted *text* drops the diagrams and tables
  that the answer usually lives in (the exact failure mode that pushed [case 02](../02-multimodal-rag-technical-manuals/)
  to page-as-image embeddings; here, full-context sidesteps it without an index at all).
- The documents are **small** (the 20-page cap means each fits comfortably in the model's context), so
  the thing a vector store buys you — narrowing a huge corpus — isn't needed yet.
- It collapses the stack to **one paid API** (Gemini) and **one agent + one tool**. The alternative I'd
  built for a prior client (**ClientA**) used a classic vector store (pgvector + a separate embeddings
  API) with one agent *per category* — four near-duplicate subgraphs to maintain. Full-context is one
  flow that scales by adding a row to `catalog.json`.

**Cost of the choice (estimate, not a measured trace):** reading full PDFs is roughly an order of
magnitude more input per query than a 10-chunk vector lookup — about **$0.007 per query vs ~$0.0005**
from the published Gemini pricing, i.e. on the order of **$10/month vs ~$1/month** at the expected
volume. At this scale that delta is negligible against the engineering and quality it buys. (Per-query
token counts were not archived — see [EVALUATION.md](EVALUATION.md) — so this is an estimate, labelled
as such, never presented as a recorded number.)

## When I would do it differently / scale it

I'd move retrieval to a **vector store** (the ClientA pattern, or the page-image embeddings of case 02
for visual recall) when **any** of these crosses a threshold — and I'd *measure the trigger before
adopting it*, not switch on a hunch:

- **(a) Corpus / document size.** Past **~1,000 pages per document** or a few hundred documents,
  full-context stops fitting and per-query cost stops being negligible. The metric I'd watch first:
  **median input tokens per query** and **p95 latency** — when latency creeps past the under-30-seconds
  technicians tolerate, or input tokens approach the context window, that's the signal, not the raw page
  count. The failure it addresses: full-context **can't narrow** a large corpus, so it either overruns
  context or pays for pages it didn't need.
- **(b) Query cost at volume.** If usage rose ~50× (to thousands of queries a day), the ~$10/month
  estimate becomes material; the metric to justify a vector store is **measured monthly API spend vs the
  one-off embedding + pgvector cost**, not the per-query ratio in isolation.
- **(c) Re-read waste.** The Gemini File API expires uploads after ~48 hours, so every query re-uploads
  its PDFs. If logs showed the **same documents re-read many times per day**, a persistent index (or a
  File-API cache within the 48-hour window) would pay for itself — the metric being **re-read count per
  document per day**.

Until one of those is *measured*, a vector store would be more moving parts (an embeddings API, an index
to keep in sync with Drive, chunk-boundary tuning) for no win at 15 small visual documents.

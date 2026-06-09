# Retrieval Flow — "The Librarian"

The query tool (`query_library.py`) runs a 4-step funnel. Below, each step is annotated with the
**real numbers from two recorded runs** shipped in [`artifacts/`](artifacts/):

- **Run A** — *"physiological power zones"* over a single 59-chapter book (English).
- **Run B** — *"safety measures"* across multiple Spanish boiler manuals (cross-document).

## The 4 steps

**Step 1 — Catalog filtering.** Pick candidate documents from the catalog using titles, summaries
and tags.
- Run A: selected **1** document. Run B: selected **5** documents.
- *(This step is reproduced live and offline in the [demo](demo/).)*

**Step 2 — Index inspection.** Read the structure of the candidates; confirm which are actually
relevant and enumerate candidate chapters.
- Run A: **1** confirmed, **6** candidate chapters. Run B: **4** confirmed (one dropped), **9**
  candidate chapters.

**Step 3 — Summary/visual filtering → selective reading.** Use chapter summaries and visual
descriptions to choose what to read, then read only those chapters/pages. When a page is visual,
it is rendered and sent to a vision model rather than flattened to text.
- Run A: read **5/6** chapters. Run B: read **8/9** chapters.

**Step 4 — Synthesis (with iteration guard).** Answer using only the selected evidence. The step
returns `needs_more_info`; if true, the loop widens and repeats.
- Both runs: `needs_more_info = false`, **1 iteration**.

## The funnel, side by side (real metrics)

| | Run A (single book) | Run B (cross-document) |
|---|---|---|
| Docs selected → confirmed | 1 → 1 | 5 → **4** |
| Candidate → read chapters | 6 → **5** | 9 → **8** |
| Iterations | 1 | 1 |
| Wall-clock | **73.7 s** | **88.5 s** |
| API calls | 6 | 7 |
| Tokens (in / out / total) | 47,677 / 5,109 / **52,786** | 37,898 / 6,793 / **44,691** |
| Traceable source refs | 5 | 8 |

Traces: [`artifacts/query-trace.power-zones.json`](artifacts/query-trace.power-zones.json) ·
[`artifacts/query-trace.safety.json`](artifacts/query-trace.safety.json).

## Why this matters

- **Bounded cost.** Whatever the repository size, a query reads a handful of chapters, not the
  whole KB. The funnel is visible and measurable per run.
- **Traceability.** Every answer carries `references` (document → chapter), so a user can verify
  the source. Run B's answer cites 8.
- **Visual fidelity.** Selected pages can be sent as images, preserving tables and diagrams that
  text extraction would mangle.

## Model selection by task

Different models for different jobs (configured via `GEMINI_MODEL_FAST` / `GEMINI_MODEL_PRO`):

- **Flash** — cheap/fast filtering and selection (Steps 1–3);
- **Pro** — final synthesis (Step 4);
- **Vision** — page-level reading when a page is visual.

## Metrics are first-class

`gemini_client.py` tracks usage (`_track_usage` / `get_usage`), so every query reports
end-to-end time, API calls and input/output tokens — the numbers in the table above come straight
from that instrumentation. Without it, you can't improve retrieval systematically.

Sequence diagram: [assets/retrieval-sequence.md](assets/retrieval-sequence.md).

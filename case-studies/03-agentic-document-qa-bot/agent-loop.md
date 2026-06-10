# The agent loop

One question becomes an answer in **6 steps**. The same numbering is used in the README, the
[sequence diagram](assets/agent-sequence.md) and `demo/run_demo.py`.

## The 6 steps

**Step 1 — Route (deterministic).** `WF-Principal` reads the per-user mode from n8n **Static Data**.
`/start` or `/menu` shows the inline-keyboard menu; a `mode_docbot` callback sets the mode; the next
message is handed to the **DocBot agent**. The model does not decide the route.

**Step 2 — Agent receives (tool-first).** The DocBot agent (GPT-4.1-mini + window-buffer memory) reads
the message. Its protocol forbids answering from its own knowledge, so unless the question is too vague
(then it asks one clarifying question) it **calls `consultar_biblioteca`** with the technician's question.

**Step 3 — Select documents (model call 1 of 2).** Inside `WF-DocBot-Tool`: `Code - Parse catalog`
loads the 15-document `catalog.json` (titles, summaries, tags), `Code - Build selection prompt` frames
it, and `HTTP - Gemini SELECT documents` asks the model which documents are relevant. `Code - Evaluate
selection` parses the returned ids; `IF - Any documents?` branches to **Step 6 (refuse)** when the set
is empty.

**Step 4 — Read the full PDFs (io).** `Loop - Selected PDFs` iterates the chosen documents: `Drive -
Download PDF` → `HTTP - Gemini UPLOAD PDF (File API)` → `Init poll` → `Wait` → `HTTP - Check File API
state` until **ACTIVE** (a 30-second absolute timeout guards it). **2 File-API io calls per selected
document.** No chunking — the whole PDF, diagrams and tables included.

**Step 5 — Answer (model call 2 of 2).** `Code - Build Gemini body` assembles the question plus every
ACTIVE file handle, and `HTTP - Gemini ANSWER (full context)` produces a grounded answer with
**document + page citations**. `Code - Format response` returns plain text to the agent.

**Step 6 — Reflect and emit.** The agent runs a forced `Think` step (is this sufficient? gaps?), then
emits structured `{respuesta, conversation_ended}`. If Step 3 found nothing it **refuses** — "no
document on that; ask the office to upload it" — with no hallucination. The shared output pipeline splits
the answer over Telegram's 4096-character limit and renders Markdown.

So the model is touched **twice per query** (select, answer); steps 1, 2 (routing/loop control), 4
(File-API IO) and 6 (formatting) are deterministic.

## The funnel, side by side (two recorded runs)

The axis the signature decision controls is **tool-path vs no-tool refuse** — so the two contrasting
runs are an in-domain answer and an off-topic refusal, both from the Phase-4 validation battery.

| | Run A — tool-path (P1) | Run B — refuse-path (P10) |
|---|---|---|
| query | "boilers at the Site B installation?" | "how to change a split A/C filter?" |
| in the document domain | yes | no |
| `consultar_biblioteca` invoked | yes | yes |
| documents selected (Step 3) | the relevant subset | **0** |
| full PDFs read (Step 4) | the selected subset | none |
| model calls (Steps 3 + 5) | **2** | 1 (select returns empty; no answer call) |
| File-API io calls (Step 4) | 2 per selected document | 0 |
| outcome | answer with document + page citation | clean refusal, no hallucination |
| verdict | pass | pass |

Source: [`artifacts/query-runs.json`](artifacts/query-runs.json) ·
[`artifacts/validation-battery.json`](artifacts/validation-battery.json). **Honest gap:** per-query
*token counts* and *wall-clock latency* were not archived (n8n retention was reduced for privacy —
SEC-208); the library size and the call counts above are real / derived from the workflow structure, and
the only latency figures I have are typical ranges (under 30 seconds with 1–3 documents, under 60 seconds
with 5+). I won't invent a token trace — see [EVALUATION.md](EVALUATION.md).

## Why this matters

The boundary is what makes the system safe *and* cheap *and* legible at once. Bounding the model to two
calls caps cost and latency; routing every answer through the tool (Step 2's tool-first rule) is what
makes Run B **refuse instead of guess** — the off-topic question never reaches an answer call, because
selection returned nothing. That is the signature decision operating: judgment at Steps 3 and 5,
determinism everywhere else.

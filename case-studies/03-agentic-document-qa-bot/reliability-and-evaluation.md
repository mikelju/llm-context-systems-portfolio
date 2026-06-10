# Reliability and Evaluation

## Reliability mechanisms (in the real system)

| Mechanism | Where | Why |
|---|---|---|
| **Tool-first protocol** | DocBot agent `systemMessage` | the agent may not answer from its own knowledge — every reply cites a document or refuses (grounding by construction). |
| **Refuse on empty selection** | `IF - Any documents?` → `Code - No results` | when selection returns no document, the flow returns a "no documentation" message instead of an answer call — the off-topic negative case. |
| **Forced reflection** | `Think_DocBot` (`toolThink`) | after every tool call the agent must assess sufficiency/gaps before answering, reducing partial-evidence answers. |
| **File-API readiness poll + timeout** | `Init poll` → `Wait` → `Check File API state` → `IF - ACTIVE?` | a freshly uploaded PDF can still be `PROCESSING`; the loop waits for **ACTIVE** with a **30-second absolute timeout** so a stuck upload fails cleanly instead of hanging. |
| **Structured output parser** | `JSON_parser_DocBot` | forces `{respuesta, conversation_ended}` so a malformed model reply degrades predictably. |
| **Telegram length + Markdown safety** | `Dividir Texto` + `Split In Batches` | answers over 4096 characters are batched so Telegram never rejects a long reply. |
| **Processing guardrails** | `WF-Procesado` — size/page validation, SHA-256 dedup, orphan cleanup | only valid PDFs (≤20 pages, ≤50 MB, not duplicates) ever reach the catalog; deletions self-clean. |

## How I evaluate

The Phase-4 validation battery ([`artifacts/validation-battery.json`](artifacts/validation-battery.json))
is the concrete eval: 10 questions over the real 15-document library, **9 pass / 1 fail**, with **2
recorded negative cases** (off-topic → clean refusal). The two contrasting runs (tool-path / refuse-path)
and a claim→source faithfulness mapping are in **[EVALUATION.md](EVALUATION.md)**.

Honest gap: this is **human pass/fail judgement, not an automated scorer**, and there is **no archived
per-query token/latency trace** (n8n retention reduced for privacy — SEC-208). The cost figures are an
estimate from published pricing, not a measurement.

## Known limitations

- **One real failure (P7):** a maintenance-frequency question where the model misread a periodicity
  table — open, see [EVALUATION.md](EVALUATION.md).
- **Ephemeral memory:** window-buffer memory is per-session and lost on redeploy (a deliberate
  simplicity choice; the prior ClientA bot used persistent Postgres memory).
- **Prompt-injection exposure (SEC-201):** the user query is concatenated into the Gemini prompts
  without delimiters; mitigated by the internal/authenticated threat model, hardening recommended.
- **Re-upload every query:** Gemini File API uploads expire after ~48 hours, so PDFs are re-read each
  query (acceptable at this scale; see the scale trigger in [tool-vs-llm-boundary.md](tool-vs-llm-boundary.md)).

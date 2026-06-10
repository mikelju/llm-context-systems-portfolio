# Agentic Document Q&A Bot — n8n + Gemini File API + memory

A two-mode Telegram bot for a heating-systems field-service company (client). The existing bot
("**FieldBot**") looks up intervention histories; I added "**DocBot**", a documentation assistant that
answers a field technician's questions from the company's PDF manuals, protocols and inventories — with
a **document + page citation** on every answer. Built entirely in **n8n Cloud** (no Python runtime, no
vector database): a deterministic router, an LLM agent with **window-buffer memory** and a single
retrieval **tool**, and a tool that selects documents and reads the **full PDFs** through the Gemini
File API. This is the agentic capstone of a trilogy with
[case 01](../01-rag-knowledge-system/) (metadata-first RAG) and
[case 02](../02-multimodal-rag-technical-manuals/) (page-as-image embeddings).

## TL;DR (with real numbers)

- The retrieval **tool is 19 functional n8n nodes; exactly 2 of them call the model** (pick the
  documents, then answer). The other 10 deterministic nodes + 7 io nodes do catalog parsing, selection
  evaluation, the PDF loop, File-API polling and response formatting — the model never touches them.
  *(`artifacts/tool-structure.json`)*
- **No vector store.** The library is a 15-document `catalog.json` on Google Drive (14 manuals of
  13–14 pages + 1 one-page protocol); the model selects the relevant docs and reads the **complete
  PDFs** — diagrams, tables and all. Two over-limit controller manuals (88 and 44 pages) are rejected by
  the 20-page rule before they ever reach the catalog. *(`artifacts/catalog-sample.json`)*
- The agent is **tool-first by construction**: its system prompt forbids answering from its own
  knowledge — every reply either cites a document or refuses. The Phase-4 validation battery passed
  **9 of 10** questions over the real library, with **2 recorded negative cases** (off-topic → clean
  refusal, no hallucination). *(`artifacts/validation-battery.json`)*
- **Security-audited** (Phase 2): 0 Critical / 0 High / 2 Medium / 4 Low / 4 Info; the prompt-injection
  finding (SEC-201) is the headline. *(`artifacts/security-audit-summary.md`)*

## Review this case study in 5 minutes

1. [`demo/example_output.txt`](demo/example_output.txt) — the **real router state machine** and the
   **real tool boundary**, run offline, plus the recorded runs (no API key, nothing fabricated).
2. [`tool-vs-llm-boundary.md`](tool-vs-llm-boundary.md) — the signature decision (LLM = judgment only;
   full-context over a vector store) + when I'd change it.
3. [`the-bug-i-fixed.md`](the-bug-i-fixed.md) — an empty-`candidates[]` TypeError that real Gemini
   safety filters surfaced as "Unknown error" to a technician.
4. [`artifacts/`](artifacts/) — the tool/agent structure, the catalog, the validation battery.

## The real problem

The client already had a production Telegram bot the technicians trusted (FieldBot). The brief was to
add a documentation assistant **without breaking it**, on the same no-code platform (n8n Cloud), where
there is no Python, no pip, and no database — only JavaScript Code nodes and HTTP. Two hard parts: (1)
**where to put the model** so that answers stay grounded and cheap and the flow stays debuggable on a
visual canvas; and (2) **retrieval over visual documents** (boiler manuals are diagrams and tables, not
prose) at a small scale where a vector store would be more machinery than the problem warrants.

## My role

I designed and built the whole DocBot side: the n8n **router** (menu + per-user mode in Static Data),
the **agent** (model + window-buffer memory + the `consultar_biblioteca` tool + a Think step), the
**tool** (catalog → LLM selection → full-PDF read via Gemini File API → formatted answer), the
**processing pipeline** (Drive trigger → File-API analysis → `catalog.json`, with dedup and orphan
cleanup), the prompts, and the security-audit response. **Off-the-shelf:** n8n Cloud, Gemini (File API +
Flash) and GPT-4.1-mini, Telegram, Google Drive, Supabase auth. **What I did NOT build:** the models or
n8n itself — the engineering is the architecture, the deterministic/LLM boundary, and making it
serviceable for non-technical office staff. FieldBot's intervention agent is pre-existing; I integrated
it unchanged.

## Evidence in this case study

| File | What it is |
|------|-----------|
| [architecture.md](architecture.md) | router + agent + tool + processing pipeline, with the real workflow/node names |
| [tool-vs-llm-boundary.md](tool-vs-llm-boundary.md) | the signature decision + the vector-store trigger I'd watch for |
| [agent-loop.md](agent-loop.md) | the 6-step loop, with the tool-path vs refuse-path runs side by side |
| [reliability-and-evaluation.md](reliability-and-evaluation.md) | reliability mechanisms tied to real nodes + the security audit + eval honesty |
| [EVALUATION.md](EVALUATION.md) | the case matrix incl. the recorded refusal + a faithfulness mapping |
| [the-bug-i-fixed.md](the-bug-i-fixed.md) | SEC-205: empty `candidates[]` → uncaught TypeError → fix |
| [artifacts/](artifacts/) | tool/agent structure, catalog sample, query runs, validation battery, audit |
| [demo/](demo/) | offline demo running the **real routing rule** and the **real boundary classifier** |

## What is real / replayed / simulated

| Element | Status | Note |
|---|---|---|
| tool/agent structure, catalog, validation battery, audit | **Real** (sanitized) | extracted from the real workflows + the Phase-4 run; only identifiers/labels changed |
| the router state machine + the tool boundary split in the demo | **Real, run live (offline)** | the actual deterministic rules, no API |
| the two contrasting runs (tool-path / refuse-path) | **Real, replayed** | recorded verdicts; calls derived from the workflow structure |
| document selection + File-API upload + full-context answer | **Not run in the demo** | the 2 model calls + File-API IO; represented by the recorded outcomes |
| per-query token/latency | **Not archived** | n8n retention was reduced for privacy (SEC-208); see EVALUATION.md |
| node counts / tool names / prompts / the bug | **Real** | from the actual codebase + audit |

## Stack

n8n Cloud (JavaScript Code nodes, no Python runtime) · **OpenAI GPT-4.1-mini** (the DocBot/FieldBot
agents) · **Google Gemini 2.5 Flash + File API** (document selection + full-PDF answering) · Google
Drive (`catalog.json` + the PDF library) · Telegram Bot API · Supabase (FieldBot auth, reused).
**Active:** all of the above. **Present-but-deliberately-absent:** any vector database / embeddings —
the full-context design makes them unnecessary at this scale (see
[tool-vs-llm-boundary.md](tool-vs-llm-boundary.md)).

## Status

**Working system** (exercised on the client's real documents in Phase-4 validation, not yet handed to
the full user base). Top open item: the single failing validation question (**P7**, a maintenance-table
frequency the model misread) needs a prompt/selection fix before delivery — tracked in
[EVALUATION.md](EVALUATION.md).

## Contact

See the [root README](../../README.md#contact).

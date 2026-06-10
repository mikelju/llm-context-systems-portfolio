# Architecture

## Pattern

A **router → agent → tool** stack, all on n8n Cloud. One Telegram bot, two modes; the model is used
only where it adds judgment, and every repeatable/structured step is a deterministic n8n node.

```
Telegram ─► WF-Principal (router: menu + Switch + per-user mode in Static Data)
                ├─ FieldBot mode ─► FieldBot agent (interventions)  [pre-existing, unchanged]
                └─ DocBot mode  ─► DocBot agent (GPT-4.1-mini + window memory + Think)
                                        └─ tool: consultar_biblioteca ─► WF-DocBot-Tool
                                                   catalog → LLM select → full-PDF read → answer
WF-Procesado (Drive trigger): new PDF ─► Gemini File API analysis ─► catalog.json on Drive
```

## Components (real workflows / nodes)

| Layer | Real workflow / node | What it does |
|------|----------------------|--------------|
| Router | `WF-Principal` — `Switch_agent` / `Switch_Menu` / `Switch_FieldBot` / `Switch_DocBot` (Code) + Telegram inline keyboard + n8n **Static Data** | `/start`,`/menu` show the menu; a `mode_*` callback sets the per-user mode; subsequent messages route to the chosen agent. The model does **not** decide the route. |
| Agent (DocBot) | `WF-Principal` — `DocBot_Agent` (`@n8n/...agent`) + `GPT 4.1 mini` + `Window Memory` (`memoryBufferWindow`) + `JSON_parser_DocBot` | tool-first conversational agent; emits structured `{respuesta, conversation_ended}`. |
| Tool | `consultar_biblioteca` (`toolWorkflow`) → `WF-DocBot-Tool` (19 functional nodes) | the retrieval engine — see [agent-loop.md](agent-loop.md). |
| Reasoning | `Think_DocBot` (`toolThink`) | a forced internal reflection step after every tool call (sufficiency / gaps / next step). |
| Processing | `WF-Procesado` (`2.0`, 76 nodes) — `Drive Trigger` → page/size validation → `HTTP - Gemini upload` + poll → `Code - Merge catalog` | turns a PDF dropped in Drive `input/` into a `catalog.json` entry; dedup by name + SHA-256; orphan cleanup. |
| Output | `Dividir Texto` (`function`) + `Split In Batches` + `Tlgm Text Setter` (Code) | shared pipeline that splits answers over Telegram's 4096-character limit and renders Markdown. |

The split between deterministic nodes and model calls is itself an artifact:
[`artifacts/tool-structure.json`](artifacts/tool-structure.json) (tool) and
[`artifacts/agent-architecture.json`](artifacts/agent-architecture.json) (router + agents).

## Why n8n Cloud constrains the design

There is **no Python runtime, no pip, no database** — only JavaScript Code nodes and HTTP Request. That
ruled out an in-process vector library and pushed the design toward *catalog-on-Drive + full-context*
(see [tool-vs-llm-boundary.md](tool-vs-llm-boundary.md)). It also means each Code node must stay small
and visual: heavy logic is split across nodes so the canvas stays debuggable.

## Design principle

> Put the model on the two decisions that need judgment — *which documents* and *the answer* — and make
> everything else a deterministic node you can read off the canvas.

Diagrams: [assets/architecture-diagram.md](assets/architecture-diagram.md) ·
[assets/agent-sequence.md](assets/agent-sequence.md)

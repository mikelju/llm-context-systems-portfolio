# Architecture

Two layers, split along one question: **does this step require judgment, or does it require being
right every time?**

## Components (real tools)

| Layer | Stage | Tool | What it does |
|---|---|---|---|
| Agent | **1. Orchestrate** | `prospeccion_empresa.md` | the master workflow: input, protocol order, dependencies, error handling |
| Agent | **2. Research** | `search_protocols/01…08_*.md` | eight protocol files the agent follows step by step, each producing one JSON |
| Agent | **3. Obey the contract** | `search_protocols/CLAUDE.md` | the shared anti-hallucination rules, auto-loaded as context for every protocol in that folder |
| Agent | **4. See what fetch can't** | `browser.py` | Playwright browser: screenshot a page the HTTP fetch is blocked from, and read it visually ([the-bug-i-fixed.md](the-bug-i-fixed.md)) |
| Code | **5. Validate** | `validate_data.py` | required/recommended field presence per protocol, completeness %, and the ready/partial/insufficient verdict |
| Code | **6. Model the data** | `utils/schemas.py` | dataclasses for the research payloads and their provenance blocks |
| Code | **7. Build the deliverable** | `generate_report.py` + `utils/pdf_builder.py` + `utils/excel_builder.py` | one PDF, one Word and one Excel per company from the validated JSON |
| Code | **8. (Disabled) CRM** | `google_sheets.py` | a Sheets integration whose write path was never enabled — dry-run by design |

## Why this shape

- **The agent decides, the code guarantees.** Reading a filing, judging whether a news item is the
  same company, deciding a source is credible — that is judgment, and it belongs to the model.
  Counting filled fields, applying a threshold, laying out a table, writing a file — that must be
  right every time, so it is Python. Neither layer is asked to do the other's job.
- **The contract sits in the folder, not in the prompt.** The anti-hallucination rules live in a
  `CLAUDE.md` inside the protocols directory, so they load as context for any protocol executed
  there. A rule you have to remember to paste is a rule that will eventually not be pasted.
- **JSON is the seam.** Each protocol's only obligation is to produce a valid research JSON with its
  provenance blocks. That makes the agent's output inspectable before anything is built from it — and
  it is what made the aggregate analysis in [`artifacts/`](artifacts/) possible at all, two months
  after the fact.
- **The gate is deliberately dumb.** Completeness is field presence over field count. It cannot
  detect a wrong value — only a missing one. That limitation is stated rather than papered over: see
  [reliability-and-evaluation.md](reliability-and-evaluation.md).

## Design principle

> Let the model judge, and let code decide. Anything a salesperson would act on must survive a step
> that has no imagination.

Diagrams: [assets/architecture-diagram.md](assets/architecture-diagram.md) ·
[assets/workflow-sequence.md](assets/workflow-sequence.md).

# Case Study Standard — LLM Context Systems Portfolio

This document defines the required structure, scope, evidence level and quality bar for every case study in this repository.

The goal is to avoid prose-only portfolio entries. Each project must be evidence-backed, technically precise, anonymized, runnable where possible, and honest about what is real, replayed, simulated or pending.

---

## 1. Purpose of every case study

Each case study must help a technical reviewer answer three questions quickly:

1. **What hard AI/context problem did this system solve?**
2. **What did Mikel design/build that demonstrates fit for RAG, context engineering, document intelligence, agents or production LLM systems?**
3. **What evidence proves the claims?**

A case study is not a sales page. It is a technical artifact. It must show architecture, tradeoffs, traces, metrics, artifacts and limitations.

---

## 2. Required folder structure

Every project folder must follow this structure unless there is a strong reason not to.

```text
case-studies/NN-project-slug/
├── README.md
├── architecture.md
├── context-strategy.md
├── retrieval-flow.md              # or workflow-flow.md / processing-flow.md when not a RAG case
├── reliability-and-evaluation.md
├── EVALUATION.md
├── the-bug-i-fixed.md             # or real-failure.md if there are several
├── lessons-learned.md
├── artifacts/
│   ├── README.md
│   ├── catalog.sample.json         # when applicable
│   ├── query-trace.*.json          # when applicable
│   ├── processing-log.sample.txt   # when applicable
│   └── other sanitized outputs
├── demo/
│   ├── README.md
│   ├── run_demo.py                 # or equivalent conventional entry point
│   ├── requirements.txt            # optional dependencies only if needed
│   └── example_output.txt
└── assets/
    ├── architecture-diagram.md
    └── sequence-diagram.md         # or equivalent Mermaid diagrams
```

Not every project will have true retrieval traces. In those cases, use equivalent evidence: extraction outputs, workflow traces, API logs, schedule runs, tool calls, generated JSON, before/after examples, latency/cost logs or screenshots converted to sanitized text.

---

## 3. Mandatory README.md structure

Each case README must be readable in five minutes and include:

### 3.1 Title

Format:

```md
# Project Name — Technical Differentiator
```

Examples:

- `Multimodal RAG over Technical Manuals — Page-as-Image Retrieval`
- `MCP Agent Tooling — Executor Agent for WAT Projects`
- `Voice-to-Order — Production LLM System with Semantic Catalog Search`

### 3.2 One-paragraph summary

Explain what the system does, what kind of inputs it handles, and why it is technically relevant.

### 3.3 TL;DR with real numbers

Required. Use 3–5 bullets with concrete evidence.

Good examples:

- `Processed 134 scanned PDF pages into 134 structured JSON files in ~9 min / 46 API calls.`
- `Query selected 5 documents → confirmed 4 → considered 9 chapters → read 8 → answered in 88.5s / 44,691 tokens.`
- `Indexed each page as an image and returned the source page image with the answer.`

Avoid vague claims:

- `Very scalable`
- `Advanced AI`
- `Accurate results`
- `Production-ready` without proof

### 3.4 Review this case study in 5 minutes

Provide a short navigation section pointing reviewers to the highest-signal files.

### 3.5 The real problem

Explain the actual technical/business difficulty. Avoid framing everything as “chat with documents”. Focus on the hard part: context selection, heterogeneous information, OCR/vision, traceability, latency, cost, tool orchestration, edge cases or operational constraints.

### 3.6 My role

State clearly what Mikel designed and built. Do not overclaim if parts were generated with assistants or based on existing systems. The wording should emphasize ownership of architecture, implementation, iteration, debugging and evaluation.

### 3.7 Evidence table

Required table:

```md
| File | What it proves |
|------|----------------|
| architecture.md | Components, boundaries, tool inventory |
| context-strategy.md | How context is selected and why |
| artifacts/ | Real sanitized outputs and traces |
| demo/ | Runnable/replayable demonstration |
```

### 3.8 What is real / replayed / simulated

Required. This protects credibility.

Use this format:

```md
| Element | Status | Notes |
|---|---|---|
| Catalog / traces / logs | Real, sanitized | Taken from actual system outputs |
| Metrics | Real, replayed | Loaded from recorded traces, not recomputed |
| Offline demo Step 1 | Simulated approximation | Deterministic substitute for an LLM/tool step |
| Full production system | Not included | Code/client data private |
```

### 3.9 Stack

List only relevant technologies. Do not keyword-stuff.

### 3.10 Status

Use precise status wording:

- `Production system`
- `Working internal prototype`
- `Proof of concept validated end-to-end`
- `Client pilot awaiting validation`
- `Framework complete; formal eval pending`

Do not use `production` unless it really served live users or production workflows.

---

## 4. Architecture document standard

`architecture.md` must explain:

1. The architectural pattern.
2. Main components.
3. Data/artifact lifecycle.
4. Tool/agent/model boundaries.
5. Why the architecture is debuggable and maintainable.

For LLM systems, always separate:

- deterministic tools;
- LLM reasoning/selection/synthesis;
- storage/artifacts;
- orchestration;
- user interface/integration.

Preferred framing:

> The LLM is used where judgment is needed. Deterministic tools handle parsing, rendering, schema validation, state, file movement, API calls and repeatable transformations.

Include a Mermaid diagram in `assets/architecture-diagram.md` and link to it.

---

## 5. Context strategy standard

Every case must explain how context is built, selected or constrained.

For RAG/document projects, include:

- document types handled;
- chunking or non-chunking choice;
- metadata strategy;
- full-context vs retrieval strategy;
- visual/page/image strategy;
- embeddings/vector search strategy;
- reranking strategy if any;
- how source traceability is preserved;
- when the current strategy stops scaling.

For agent/tool projects, include:

- what context the agent receives;
- what tools it can inspect;
- what memory/state is available;
- how tool outputs are fed back into the model;
- what context is deliberately excluded;
- safety/permission boundaries.

Every context-strategy file must include a tradeoff section:

```md
## Key tradeoff

The goal is not to maximize context. The goal is to provide the cheapest context that preserves answer/action quality and source traceability.
```

When a common technique is not used, explain why and when it would be added. Example: no vector DB for dozens of documents, but hybrid retrieval + pgvector + reranker when the corpus reaches hundreds/thousands.

---

## 6. Flow document standard

Use `retrieval-flow.md`, `workflow-flow.md` or `processing-flow.md` depending on the project.

It must contain:

1. A step-by-step flow.
2. What each step receives.
3. What each step outputs.
4. Which steps are deterministic and which are LLM-driven.
5. Real numbers from at least one run when available.
6. Failure or widening/iteration logic.
7. Link to a sequence diagram in `assets/`.

For RAG, the minimum flow is:

```text
user query → document selection → section/page selection → content reading → synthesis → references
```

For extraction/document intelligence:

```text
input document → rendering/OCR/vision → extraction → schema validation → matching → human review → final output
```

For agents/tools:

```text
user intent → context loading → tool selection → tool execution → tool result interpretation → final response/action
```

---

## 7. Reliability and evaluation standard

`reliability-and-evaluation.md` must include:

- retries/backoff;
- resumability/idempotency;
- schema validation;
- source traceability;
- logging/tracing;
- cost and latency tracking;
- known failure modes;
- what is currently measured;
- what is not yet measured.

Do not invent evaluation results.

Required honesty rule:

> If there is no labeled eval set, say so explicitly. Show recorded examples as evidence of measurability, not as formal precision/recall results.

---

## 8. EVALUATION.md standard

Every case must include a small evaluation matrix.

Format:

```md
# Evaluation

| # | Case type | Why it matters | Status | Evidence |
|---|-----------|----------------|--------|----------|
| 1 | Happy path | Basic functionality | Recorded | artifact link |
| 2 | Cross-document / complex case | Harder retrieval or reasoning | Recorded | artifact link |
| 3 | No-answer / refusal / failure case | Prevent hallucination or unsafe action | Pending or recorded | artifact link or explanation |
| 4 | Distractor / edge case | Robustness | Pending or recorded | artifact link |
```

Pending cases are acceptable. Fake traces are not.

---

## 9. Real bug / failure standard

Every case must include `the-bug-i-fixed.md` or `real-failure.md`.

Required sections:

1. Symptom.
2. Root cause.
3. Why it mattered.
4. Fix.
5. Result.
6. Lesson.

A good bug is better than a generic success story. It proves the project touched messy real-world data.

Acceptable examples:

- corrupt PDF table of contents;
- JSON truncation under LLM load;
- duplicate document IDs in references;
- API rate limit failure;
- OCR/vision mismatch;
- schema drift;
- workflow race condition;
- hallucinated tool selection;
- user/session state bug.

---

## 10. Artifacts standard

`artifacts/` is the evidence folder. It must contain real outputs whenever possible.

Acceptable artifacts:

- sanitized `catalog.sample.json`;
- query traces;
- extraction JSON;
- processing logs;
- tool execution logs;
- before/after examples;
- schema examples;
- generated report samples with sensitive fields removed;
- API response samples;
- evaluation cases;
- screenshots converted to sanitized markdown/text where needed.

`artifacts/README.md` is mandatory and must state:

1. What each artifact is.
2. Whether it is real, replayed or synthetic.
3. What was sanitized.
4. What was not changed.
5. Whether any corrections were made after export.
6. Whether source documents are included or not.

### Rule: no invented metrics

Never fabricate latency, token counts, accuracy, number of files, API calls or user volume.

Allowed:

- real metrics from logs;
- estimates clearly marked as estimates;
- pending rows where no evidence exists.

Not allowed:

- fake traces;
- fake evaluation metrics;
- simulated outputs presented as real;
- claiming production usage without evidence.

---

## 11. Demo standard

Every case should include a demo when possible.

The demo may be one of:

- offline trace replay;
- deterministic subset of the real workflow;
- sample extraction runner using sanitized input;
- static visualization of recorded tool calls;
- CLI showing artifacts and metrics;
- notebook-free Python script.

Required files:

```text
demo/
├── README.md
├── run_demo.py
├── requirements.txt        # optional dependencies; can be empty or minimal
└── example_output.txt
```

`demo/README.md` must state:

- what the demo does;
- what it does not do;
- whether it calls APIs;
- whether it needs credentials;
- what is real, replayed or simulated;
- how to run it;
- where to see expected output.

Prefer `run_demo.py` as the conventional entry point. Do not rename it to overly precise names if that adds friction; instead, document honestly inside the README and script docstring.

The demo should run offline with zero required external services whenever possible.

---

## 12. Metrics standard

Each project should expose the metrics that matter for its type.

### RAG/context systems

- documents selected;
- documents confirmed;
- candidate chunks/chapters/pages;
- chunks/chapters/pages actually read;
- iterations;
- wall-clock seconds;
- API calls;
- input/output/total tokens;
- number of cited references;
- no-answer/refusal behavior if recorded.

### Document intelligence/extraction

- pages processed;
- files processed;
- fields extracted;
- schema fields matched;
- completion rate;
- invalid/missing fields;
- human-review flags;
- processing time;
- API calls;
- retry count;
- cost/tokens if available.

### Agent/tool/MCP systems

- tools discovered;
- tools executed;
- workflows executed;
- success/failure status;
- execution time;
- user/session isolation behavior;
- logs/traces;
- permission boundaries;
- scheduled/chain execution if relevant.

### Production LLM systems

- latency per main flow;
- concurrency/rate-limit strategy;
- retry behavior;
- failure handling;
- cost/tokens;
- before/after performance improvement;
- number of users/orders/files/tasks where discloseable.

---

## 13. Anonymization standard

Anonymization must preserve technical evidence while removing sensitive data.

Remove or generalize:

- client names;
- person names;
- emails;
- phone numbers;
- addresses;
- production URLs;
- API keys/secrets;
- internal domains;
- exact customer/project identifiers;
- proprietary prices or contractual terms;
- filenames that reveal clients, unless safe/public;
- screenshots containing personal or client data.

Preserve when safe:

- document counts;
- page counts;
- chapter counts;
- processing dates if not sensitive;
- token usage;
- elapsed time;
- API call counts;
- strategy decisions;
- anonymized IDs if they identify nothing;
- structure of JSON/logs;
- error types;
- tool names when not sensitive.

Every artifact folder must disclose the anonymization:

```md
## What changed
- Client name → ClientA
- Site/city → Site A/B/C
- Brand/model → generic equipment name

## What did not change
- Counts
- Metrics
- Retrieval funnel
- Strategy decisions
- Error/fix details
```

When a correction is made after export, disclose it. Example: `references[].document_id` reconciled against authoritative `chapters_read` while metrics and answer remained unchanged.

---

## 14. Writing standard

Tone:

- precise;
- evidence-first;
- technically confident;
- honest about limits;
- no hype.

Avoid:

- “advanced”, “powerful”, “robust”, “production-ready” without proof;
- generic AI buzzwords;
- overstating demos;
- hiding pending evaluation work;
- saying “RAG” when the system is really a trace replay or metadata selector.

Preferred phrases:

- `recorded real-system run` instead of `production run` unless it was production;
- `offline trace-replay demo` instead of `full RAG demo`;
- `metadata-first retrieval at this corpus size` instead of `no vector DB` as a boast;
- `formal eval pending` instead of pretending recorded examples are full evaluation.

---

## 15. Definition of done for a case study

A case study is done only when:

- README is understandable in five minutes.
- There is at least one real artifact or a clear explanation of why not.
- Metrics are real or explicitly marked as estimates/pending.
- Demo runs offline or clearly explains required services.
- `example_output.txt` exists when there is a demo.
- Anonymization is documented.
- At least one real failure/bug/edge case is described.
- Evaluation gaps are explicit.
- Claims in README are backed by artifacts or source documentation.
- The project adds a distinct capability to the overall portfolio.

---

## 16. Case study creation workflow

Before writing a new case study:

1. Inspect the source repo plan/README/docs.
2. Identify 3–5 strongest technical claims.
3. Find or generate sanitized evidence for each claim.
4. Decide what kind of demo is honest and feasible.
5. Create artifacts first, README second.
6. Add metrics only from real logs/traces.
7. Add the failure/bug story.
8. Add evaluation matrix.
9. Review for overclaiming.
10. Review anonymization.

The final output should require no back-and-forth to establish credibility. Review cycles should focus on polish, not on fixing missing evidence.

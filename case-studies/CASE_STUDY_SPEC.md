# Case Study Authoring Standard (v1)

The contract every case study in this portfolio must satisfy. It exists so that a new case study
comes out right **on the first pass**, with no multi-round review. Case study `01-rag-knowledge-system`
is the reference implementation — when in doubt, copy its shape.

> One-line philosophy: **evidence over prose, honest about limits.** A reviewer should be able to
> *verify* the claims (real artifacts, real numbers, a runnable demo), not just read adjectives.

---

## 1. Non-negotiables (the principles every rule below serves)

1. **Show, don't tell.** Every capability claim is backed by a real artifact, a real number, or
   runnable code. No "advanced RAG system" without proof.
2. **Real data only.** Artifacts are *real, sanitized outputs of the actual system*. **Never
   fabricate** a metric, trace, or log. A declared gap beats an invented artifact.
3. **Anonymize completely.** Zero client-identifying data — names, sites, domains, emails, URLs,
   brands, PII, secrets — in files, code, IDs, filenames, or git history.
4. **State what is real vs replayed vs simulated.** No artifact or demo may imply it does more
   than it does.
5. **Disclose corrections.** If you clean or reconcile a real artifact, say so in that artifact's
   README and keep metrics untouched.
6. **Honest scope.** Each case study states what is built, what is measured, and what is *not yet*.
7. **Map to the target role.** Every case study must visibly support the positioning
   *AI Knowledge Systems Engineer (RAG · context · document intelligence · agents/MCP)*.
8. **Wording discipline.** It's a *prototype / working system*, not "production". The demo is
   *not* the engine. Don't over-claim.

---

## 2. Canonical folder & file structure

Folder name: `case-studies/NN-short-slug/` (`NN` = zero-padded order, `slug` = kebab-case).

```
case-studies/NN-short-slug/
├── README.md                     # REQUIRED — overview, the 5-minute entry point
├── architecture.md               # REQUIRED — components, layers, real tool/file names
├── <core-decision>.md            # REQUIRED — the one signature technical decision (see §3.3)
├── <main-flow>.md                # REQUIRED — the system's main loop, annotated with REAL metrics
├── reliability-and-evaluation.md # REQUIRED — reliability mechanisms + how it's evaluated
├── EVALUATION.md                 # REQUIRED — case matrix incl. the negative/failure case
├── the-bug-i-fixed.md            # REQUIRED — one real bug: symptom, root cause, fix, result
├── lessons-learned.md            # REQUIRED — specific, grounded; no generic platitudes
├── artifacts/                    # REQUIRED — real, sanitized system outputs
│   ├── README.md                 #   what each artifact is, what's real vs sanitized, disclosures
│   └── <real sanitized files>    #   catalog/trace/log/output JSON/TXT (≥2 substantive artifacts)
├── assets/                       # REQUIRED — diagrams (mermaid, render on GitHub)
│   ├── architecture-diagram.md   #   flowchart of the system
│   └── <sequence-or-flow>.md     #   sequence/flow diagram annotated with real numbers
└── demo/                         # REQUIRED — runnable, offline, no API key
    ├── run_demo.py               #   stdlib-only core; optional `rich`; UTF-8 stdout
    ├── requirements.txt          #   optional deps only (e.g. rich); demo must run without them
    ├── README.md                 #   how to run + honesty caveats
    └── example_output.txt        #   captured real output, so nobody has to run it to see it
```

**Naming:** `<core-decision>` and `<main-flow>` are renamed per project type (see §11). Artifact
files use `kind.descriptor.ext` (e.g. `query-trace.safety.json`, `catalog.sample.json`).
Never invent files that have no analog in the real project.

---

## 3. Per-file content spec

### 3.1 `README.md` (case study) — the entry point
Required sections, in order:
1. **Title + one-paragraph what-it-is** + internal codename if any.
2. **TL;DR with real numbers** — 3–5 bullets, each carrying a concrete figure (threshold,
   latency, tokens, counts). No vague bullets.
3. **Review this case study in 5 minutes** — an ordered list pointing to the 4–5 files worth
   reading, starting with `demo/example_output.txt`.
4. **The real problem** — the *non-obvious* engineering problem (not "chat with X").
5. **My role** — first person, what *you* designed/built.
6. **Evidence in this case study** — a table linking every file with a one-line "what it is".
7. **What is real / replayed / simulated** — a table (see §5).
8. **Stack** — concrete libraries/models/services.
9. **Status** — prototype/working-system honesty + the main open item.

### 3.2 `architecture.md`
Components and the **WAT split** (Workflows / Agents / Tools) or the project's equivalent. Name
the **real tool/module files** (e.g. `extract_structure.py`). Include the design principle in one
quotable line. Link the diagrams.

### 3.3 `<core-decision>.md` — the signature decision
Each case study has **one** decision that shows judgment, argued with tradeoffs (e.g. case 01:
*metadata-first, no vector DB yet*). Must include:
- the problem the decision addresses;
- the choice + why, with the real parameter from code (e.g. `FULL_CONTEXT_MAX_PAGES = 80`);
- a **"When I would do it differently / scale it"** subsection (shows you know the limits, not
  dogma).

### 3.4 `<main-flow>.md` — the loop, with real numbers
Step-by-step of the core loop (retrieval / agent / extraction). **Every step annotated with real
trace numbers.** Include a side-by-side table of ≥2 recorded runs (see §4) and link the traces.

### 3.5 `reliability-and-evaluation.md`
A table of **real reliability mechanisms** (retry/backoff, resumability, validation, dedup, model
selection, metrics) each tied to a real file. An evaluation section that links `EVALUATION.md`.

### 3.6 `EVALUATION.md`
A **case matrix** (question/scenario types × why it matters × status × evidence) that MUST include
the **negative case** for the domain (RAG: "no answer in the library → refuse"; extraction:
"field absent → don't hallucinate"; agent: "tool fails → recover"). State honestly which cases are
recorded vs pending, and **why a pending case is not faked.** End with "what a real eval suite needs".

### 3.7 `the-bug-i-fixed.md`
One real bug: **symptom → root cause → fix (with `file:line` refs) → result**. Prefer a bug that
only shows up on real, messy data. Close with "why it's a good story" (what judgment it shows).

### 3.8 `lessons-learned.md`
6–8 lessons, each **specific to this project** (reference your real decisions/bugs). Ban generic
RAG truisms unless tied to a concrete thing you did. End with "what I'd do next".

---

## 4. Metrics standard (what MUST be visualized)

Every case study must surface, for ≥2 real recorded runs, and in BOTH the `<main-flow>.md` table
and the demo output:

- **The funnel** — how the candidate set narrows at each stage (e.g. docs selected → confirmed →
  candidates → used). The project-specific analog is fine, but the *narrowing* must be visible.
- **Cost/latency** — wall-clock seconds, number of model/API calls.
- **Tokens** — input / output / total (or the closest real measure the system records).
- **Traceability** — count (and ideally list) of cited sources / produced records, so outputs are
  auditable.
- **A reduction/efficiency figure** — e.g. "8/9 candidates actually used", "context kept %".

Rule: these numbers come **straight from recorded traces**; never recompute or estimate them and
present them as measured. If a number is an estimate, label it.

---

## 5. Data & artifacts standard

- **≥2 substantive artifacts**, real and sanitized: at minimum (a) a structured state artifact
  (catalog / schema / index) and (b) a run trace (query/agent/extraction trace) with a `metrics`
  block. Add a processing/ingestion log when relevant.
- **`artifacts/README.md` must declare, per file:** what it is, **Real?**, **Sanitized?** (what
  changed), and any **disclosed correction**.
- **The real / replayed / simulated table** (in the case README) classifies every moving part:

  | Element | Status | Note |
  |---|---|---|
  | artifacts (catalog/traces/logs) | **Real** (sanitized) | actual outputs; only identifiers changed |
  | funnel + cost/latency/token metrics | **Real, replayed** | read from recorded traces, not recomputed |
  | the demo's live step | **Simulated** | a deterministic stand-in for the real LLM step, offline |
  | non-demo LLM steps | **Not run in the demo** | represented only by recorded metrics |
  | code constants / tool names / the bug | **Real** | from the actual codebase |

- **Never fabricate.** If a desirable artifact doesn't exist (e.g. a "no-answer" trace), declare it
  pending in `EVALUATION.md` rather than inventing one. If you must show an *illustrative* (non-real)
  artifact, it must be unmistakably labeled `synthetic` and carry no fake metrics.
- **Disclosed corrections:** reconciling a real artifact's buggy derived field is allowed *if*
  (a) the authoritative source is used, (b) metrics/answers are untouched, (c) it's disclosed in
  `artifacts/README.md`.

---

## 6. Anonymization standard

**Keep (translate prose, keep the proper nouns):**
- The author's own brand (Biar Tech) and own internal project codenames.
- Public institutions / programs / standards (e.g. RITE), generic public tech
  (Python, Gemini, FastAPI, Supabase, n8n, …).
- Public, published sources (books, papers) — include **metadata + derived traces only**, never
  the source file, and add a note that the source is not distributed.

**Remove / generalize (consistently, via a per-case glossary):**
- Client / company names → role-descriptors or stable tokens (`ClientCo`, `an industrial
  plumbing/HVAC supplier (client)`).
- People → roles (`the authorized representative`, `the founder`).
- Sites / locations → `Site A/B/C`, `[location]`.
- Equipment / product brands that point to a client → generic (`a major boiler brand`).
- Domains, emails, URLs, IPs → `client@example.com`, removed, or `[redacted]`.
- **Identifiers that embed names** — filenames, document_ids, folder names, code symbols
  (`boton_piramide` → `boton_clientco`), window titles, XPaths matching a client name.
- **PII** — national IDs, tax IDs, full names, phone numbers.
- **Secrets** — API keys, tokens, `.env` values, connection strings (never commit; `.env` in
  `.gitignore`).

**Process (do it the same way every time):**
1. Copy the real artifact into `artifacts/`.
2. Apply the glossary (script the replacements; keep a consistent mapping across all files of the
   case study).
3. **Verify with a grep sweep** for every client term (and lowercase/underscore variants) across
   the whole case folder — must return empty.
4. **Validate** that JSON still parses and the demo still runs.
5. Confirm **no secrets** and **no `.venv`/`__pycache__`** are staged; ensure repo `.gitignore`
   covers them.
6. Remember **git history**: never commit a real (un-sanitized) file even once — history is public
   if the repo ever goes public. When in doubt, build in a fresh clone.

**Confidentiality note:** every case folder's `artifacts/README.md` ends with a line asserting no
credentials, production URLs, or PII appear in any artifact.

---

## 7. Honesty & credibility rules

- No fabricated numbers, traces, or logs — ever.
- Demo is labeled as *not the engine*; its live step is an *approximation*, not a replay.
- "prototype / working system", never "production" (except the standard phrases "production URLs"
  in confidentiality notes).
- Acknowledge the domain's negative case (refuse / don't hallucinate / recover) even if pending.
- Disclose any artifact correction.
- Prefer "I deliberately chose X for this scale, and here's when I'd change it" over "X is unnecessary".

---

## 8. The runnable demo standard

`demo/run_demo.py` must:
- run **offline**: no API key, no network, no client data;
- work on the **standard library alone**; `rich` (or similar) is optional with a graceful fallback;
- set **UTF-8 stdout** (Windows-safe) so accented/emoji output never crashes or mojibakes;
- read only the **sanitized artifacts** in `../artifacts`;
- print three things: (a) the state/knowledge-base overview, (b) **one live deterministic step**
  (clearly labeled an approximation of the real LLM step), (c) the **funnel + real metrics** read
  from the recorded traces;
- carry an in-output **honesty caveat** (not the engine; live step approximates, doesn't replay).
- ship a captured **`example_output.txt`** and document the run in `demo/README.md`.

---

## 9. Tone & writing rules

- Concise and **evidence-dense**; every paragraph earns its place with a specific fact or number.
- First person ownership ("I designed/built/fixed").
- Ban generic RAG/AI platitudes unless tied to a concrete thing you did.
- Use the role's vocabulary (retrieval, context budget, traceability, eval, tool use, MCP).
- Match the existing voice of case 01.

---

## 10. Acceptance checklist (the gate before "done")

A case study is done only when ALL of these pass:

- [ ] Folder/file layout matches §2; required files present.
- [ ] README has all §3.1 sections, incl. TL;DR-with-numbers, 5-minute guide, real/replayed/simulated table.
- [ ] ≥2 real sanitized artifacts with a `metrics` block; `artifacts/README.md` declares real/sanitized/disclosures.
- [ ] `<main-flow>.md` shows the funnel + cost/latency/tokens/traceability for ≥2 recorded runs.
- [ ] `EVALUATION.md` includes the domain negative case (recorded or honestly pending).
- [ ] `the-bug-i-fixed.md` has symptom→root cause→fix(`file:line`)→result.
- [ ] `demo/run_demo.py` runs offline, with and without optional deps; `example_output.txt` is current.
- [ ] **Anti-leak grep is empty** across the case folder (clients, sites, brands, people, domains, PII).
- [ ] No secrets; no `.venv`/`__pycache__`; `.env` ignored.
- [ ] No fabricated metrics; any correction disclosed.
- [ ] Wording: "prototype/working system", demo ≠ engine, no over-claim.
- [ ] Maps clearly to the target role; mentioned/linked from the root README.

---

## 11. What varies by project type

The skeleton is constant; the `<core-decision>`, `<main-flow>`, metrics and artifacts adapt:

| Project type | `<core-decision>.md` | `<main-flow>.md` | Key artifacts | Funnel / metrics | Negative case |
|---|---|---|---|---|---|
| **RAG / retrieval** (01, 02, 03) | context strategy (e.g. hierarchical vs full-context; metadata-first) | `retrieval-flow.md` | catalog + query traces | docs→chapters narrowing, tokens, latency, cited sources | "no answer → refuse" |
| **Document intelligence / extraction** (e.g. manufacturer reports) | extraction strategy (schema-first, vision vs text, matching) | `extraction-flow.md` | input schema + extraction-result JSON + coverage report | fields found/total, coverage %, per-page cost, HITL flags | "field absent → leave empty, no hallucination" |
| **Agentic workflow / MCP** (e.g. executor agent, prospecting) | tool-vs-LLM boundary; orchestration | `agent-loop.md` | run trace (tool calls), tool I/O samples | steps, tool calls, success/retry, tokens | "tool fails / ambiguous → recover or ask" |
| **Applied-AI product** (e.g. voice-to-order) | the productionization decision (latency, concurrency, integration) | `request-flow.md` | request/response trace, perf log | end-to-end latency, throughput, error rate | "bad input → graceful degradation" |

Each remaining case study (02–07) must pick its row, keep the skeleton, and meet §4–§8.

---

## 12. Definition of done (review rubric)

Score each before publishing: **Evidence** (real artifacts + numbers), **Honesty** (real/replayed
table, disclosures, negative case), **Anonymization** (grep-clean, no secrets/history),
**Runnability** (demo offline, example output), **Role fit** (signature decision + vocabulary).
A case study ships only when all five are green.

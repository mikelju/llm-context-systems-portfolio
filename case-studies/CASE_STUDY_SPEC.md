# Case Study Authoring Standard (v2)

The contract every case study in this portfolio must satisfy, so a new one comes out right **on the
first pass**. Case study `01-rag-knowledge-system` is the reference implementation.

> Philosophy: **evidence over prose, honest about limits, verified by scripts not by self-assertion.**
> A reviewer must be able to *verify* claims (real artifacts, real numbers, a runnable demo, a
> passing checker), not just read adjectives.

## 0. Quick start & ground rules

```
cp -r case-studies/_TEMPLATE case-studies/NN-slug      # 1. scaffold (slug from the root README)
# 2. write _glossary.json (real_term -> token) — see §6; keep the real values OUT of git
python case-studies/_scripts/sanitize.py NN-slug        # 3. apply glossary to copied artifacts
# 4. write the docs + drop in real sanitized artifacts + wire the demo
python case-studies/_scripts/verify_case_study.py NN-slug   # 5. GATE — must exit 0
```

**Threat model (what anonymization is for).** In scope to remove: anything identifying **clients**,
their people, sites, PII, and secrets. Deliberately kept (a reviewed branding choice): the author's
own brand (Biar Tech), public institutions/standards, generic public tech, and public published
sources (metadata only). A contributor must confirm the kept set is intentional, not accidental.

**Maturity vocabulary (pick one per case, use consistently).**
- `prototype` = built and run, **not** deployed.
- `working system` = exercised on **real data**, not productionized.
Never call a case study `production`/`production-grade`/`production-ready`.

---

## 1. Non-negotiables

1. **Show, don't tell.** Every capability claim is backed by a real artifact, a real number, or
   runnable code.
2. **Real data only.** Artifacts are real, sanitized outputs of the actual system. **Never fabricate**
   a metric, trace, or log. A declared gap beats an invented artifact.
3. **Anonymize completely, and prove it.** Zero client-identifying data anywhere (files, code, IDs,
   filenames, free text, git history, binaries). The proof is `verify_case_study.py` exiting 0, not
   a promise.
4. **Label real vs replayed vs simulated.** No artifact or demo may imply it does more than it does.
5. **Disclose every change beyond token substitution** (field-level, before→after) in
   `artifacts/README.md`.
6. **Honest scope.** State what is built, what is measured, what is *not yet* — with a concrete blocker.
7. **Map to the target role:** *AI Knowledge Systems Engineer (RAG · context · document intelligence ·
   agents/MCP)*.
8. **Wording discipline.** Use the maturity vocabulary above; the demo is *not* the engine; banned
   adjectives (§9) must be earned in the same sentence.

---

## 2. Canonical folder & file structure

`case-studies/NN-short-slug/` — `NN` zero-padded, slug from the **root README case index** (do not
invent a topic; the next case's number/slug/scope is pre-assigned there).

```
NN-short-slug/
├── README.md                     # overview + 5-minute entry point + real/replayed table + contact
├── architecture.md               # components, layers, real tool/module names
├── <core-decision>.md            # the ONE signature decision (renamed per §11; e.g. context-strategy.md)
├── <main-flow>.md                # the core loop, annotated with REAL metrics (renamed per §11)
├── reliability-and-evaluation.md # reliability mechanisms table + 2-3 line eval summary (links EVALUATION)
├── EVALUATION.md                 # full case matrix incl. the negative case + faithfulness mapping
├── the-bug-i-fixed.md            # one real bug: symptom -> root cause -> fix(file:line) -> result
├── lessons-learned.md            # specific, grounded; no platitudes
├── _glossary.json                # token vocabulary only (NO real terms if repo is/will be public)
├── artifacts/                    # real, sanitized outputs (>=2 substantive; see §5)
│   ├── README.md                 #   per-file real/sanitized + disclosed corrections + provenance
│   └── <files>.json/.txt
├── assets/
│   ├── architecture-diagram.md   #   mermaid flowchart
│   └── <sequence-or-flow>.md     #   mermaid sequence/flow with real numbers
└── demo/
    ├── run_demo.py               #   offline; stdlib + optional rich; UTF-8 stdout
    ├── requirements.txt          #   optional deps only
    ├── README.md                 #   how to run + honesty caveats + self-test recipe
    └── example_output.txt        #   byte-for-byte capture of the current run
```

Shared tooling lives at `case-studies/_scripts/` (`sanitize.py`, `verify_case_study.py`) and
`case-studies/_TEMPLATE/` (copy-from scaffold). The repo **root** `.gitignore` already covers
`.venv/`, `__pycache__/`, `.env` — do not re-add per case.

**Root README governance.** The portfolio root `README.md` must carry: the positioning line, the
case index (number/slug/scope/status for 01–07), a confidentiality note, and a complete, consistent
**Contact** (name/brand, email, ≥1 profile link). The same author identity/brand must be used in the
root and every case README.

---

## 3. Per-file content spec

Each file: meet the required sections AND the **minimum bar**; when unsure of shape, copy the heading
structure from case 01's same file.

### 3.1 `README.md` (case) — required sections, in order
1. Title + one-paragraph what-it-is (+ internal codename if any, confirmed not client-derived).
2. **TL;DR with real numbers** — 3–5 bullets, each with a concrete figure copied from an artifact.
3. **Review this case study in 5 minutes** — ordered list; lead with `demo/example_output.txt`, then
   the core-decision file, the bug, and the artifacts.
4. **The real problem** — the non-obvious engineering problem.
5. **My role** — first person; **draw the boundary**: what you designed/built vs off-the-shelf
   (model/library/managed service) vs AI-assisted. A one-line "what I did NOT build" is encouraged.
6. **Evidence in this case study** — table linking every file.
7. **What is real / replayed / simulated** — the §5 table.
8. **Stack** — concrete; mark components **active** vs **present-but-disabled-by-design** (must not
   contradict the core-decision file).
9. **Status** — maturity label (§0) + the top open item.
10. **Contact** — or an explicit link to the root README's contact.

### 3.2 `architecture.md`
Components + the Workflows/Agents/Tools split (or the project's equivalent), naming the **real
tool/module files**. One quotable design-principle line. Link both diagrams.

### 3.3 `<core-decision>.md` — the signature decision
The one decision that shows judgment, argued with tradeoffs. Must include: the problem; the choice +
why, citing the **real parameter from code**; and a **"When I would do it differently / scale it"**
subsection with **(a) a concrete numeric trigger** ("past ~N because <measured symptom>"), **(b) the
metric that would justify the change *before* adopting it** (measurement-first), and **(c) the
specific failure of the current approach it addresses**. Bare technology lists ("add embeddings /
reranker / pgvector") without a trigger + metric are banned.

### 3.4 `<main-flow>.md` — the loop, with real numbers
Number the loop steps **once**; use the same numbering in this file, the README, the sequence
diagram, and `run_demo.py` output. Each step annotated with a real trace number. Include a
side-by-side table of the **≥2 recorded runs**, which **must differ along the axis the core decision
controls** (e.g. full_context vs hierarchical; tool-path vs LLM-path; 1- vs multi-iteration) — two
interchangeable runs do not satisfy this. Min bar: N numbered steps + the ≥2-run table + a one-paragraph "why it matters".

### 3.5 `reliability-and-evaluation.md`
A table of **real reliability mechanisms**, each tied to a real file. Then a **2–3 line** eval
summary that **links** `EVALUATION.md`. **Do not duplicate** the case matrix here.

### 3.6 `EVALUATION.md`
The full **case matrix** (scenario types × why it matters × status × evidence) including the domain
**negative case** (RAG: "no answer → refuse"; extraction: "field absent → empty, no hallucination";
agent: "tool fails → recover/ask"; product: "bad input → graceful degradation"). Plus a worked
**faithfulness mapping** (≥1 recorded answer: claim → cited source). Rules: **at least one negative
case must be RECORDED** unless genuinely infeasible offline, in which case state the concrete blocker
+ the exact steps to record it; **at most half** the matrix may be `pending`; never fake a trace to
fill it. End with "what a real eval suite needs".

### 3.7 `the-bug-i-fixed.md`
One real bug: symptom → root cause → fix (`file:line`) → result. Prefer a bug only real, messy data
surfaces. Close with "why it's a good story".

### 3.8 `lessons-learned.md`
6–8 lessons, each specific to this project (reference your real decisions/bugs). Ban generic
truisms. End with "what I'd do next".

---

## 4. Metrics standard

**Single source of truth.** The artifact JSON is authoritative for every number. Any figure restated
anywhere (README, main-flow, EVALUATION, diagrams, demo) must be **byte-identical** to the trace
field it comes from, and should cite the trace file. `verify_case_study.py` diffs restated numbers
against the traces.

**Measured vs derived.**
- *Measured* quantities (seconds, api_calls, token counts, funnel-stage counts) are copied **verbatim**
  from the trace — never recomputed or estimated.
- A *derived* ratio (e.g. read/candidate %) is allowed **only** if both operands are verbatim trace
  fields; it must be **labelled "derived"**, shown with its operands, and never blended with measured costs.
- Anything else must be labelled **"estimate"**.

**Two-tier requirement** (the funnel/tokens are RAG-shaped; adapt per §11):
- *Mandatory core, every case:* cost/latency (seconds, calls), **traceability of produced records**,
  and the **≥2 contrasting recorded runs** shown side by side.
- *Project-appropriate analog:* the **funnel** (how the candidate/work set narrows), a token count
  **only when the system is LLM-token-metered**, and a reduction/efficiency figure. §11 gives the
  concrete analog per project type.

**Traceability must RESOLVE.** Every entry in a references/citations array must resolve to a real,
distinct read source (matching `document_id` present in `chapters_read`/`steps_log` **and** a
non-empty `chapter_id`). The reported source count is the number of **valid** references, not array
length. Add at least a lightweight **correctness** note on the funnel: state the expected/relevant
sources and that the read set covers them; justify any drop (was the dropped item a true negative?).

---

## 5. Data & artifacts standard

- **≥2 substantive artifacts**, real and sanitized: (a) a structured-state artifact (catalog / schema
  / index) and (b) a run trace with a `metrics` block. At least one artifact should expose **decision
  evidence** (per-candidate selection rationale, the criteria/prompt used, or the validation that
  rejected a bad input), not just outcome counts. Add a processing/ingestion log when relevant.
- **Provenance (in-file).** Each trace/log records minimal `_provenance`: the producing
  module/function from the real codebase and the run month. The artifact schema must match what the
  real system emits (same keys). `artifacts/README.md` names which code path produced each artifact —
  this is what lets a reviewer judge "Real?" instead of trusting a checkbox.
- **Cross-artifact identifier consistency.** The same real record carries the **same sanitized id** in
  every artifact (catalog, traces, logs). Every `document_id`/`chapter_id` in a trace must resolve in
  the catalog. (`verify_case_study.py` checks this.)
- **The real/replayed/simulated table** (in the case README):

  | Element | Status | Note |
  |---|---|---|
  | artifacts (catalog/traces/logs) | **Real** (sanitized) | actual outputs; only identifiers/labels changed |
  | funnel + cost/latency/token metrics | **Real, replayed** | read verbatim from recorded traces |
  | the demo's live step | **Simulated** | a deterministic stand-in for the real step, offline |
  | non-demo model steps | **Not run in the demo** | represented only by recorded metrics |
  | code constants / tool names / the bug | **Real** | from the actual codebase |

- **Disclosed corrections.** Any change to an artifact **beyond glossary-token substitution** is a
  correction. Allowed only for: (i) a field mechanically derivable from another field in the **same**
  artifact (e.g. references rebuilt from `chapters_read`), or (ii) identifier regeneration/unification.
  **Forbidden:** changing any metric, funnel count, or answer text. Disclosure (in `artifacts/README.md`
  **and** an in-file `_note`/`_corrections`) must state the exact field, before→after (or a
  reproducible description), and the authoritative source. Title/label normalization that alters
  meaning is a correction, not sanitization.
- **Synthetic artifacts** (discouraged — prefer declaring the gap): must carry `SYNTHETIC` in the
  **filename** AND an in-file `"_synthetic": true` AND the README row; contain **no metrics block**;
  be **excluded from the demo and from every §4 count**; and total **at most one per case**.
- **Fewer than 2 real runs?** Ship the ones you have, declare the shortfall as pending in
  `EVALUATION.md`, and **do not synthesize** a second run. Minimum that still passes: 1 state artifact
  + 1 trace.
- **Verbatim-source cap.** Derived answers must not reproduce substantial verbatim passages of any
  non-distributed source (client or published). Abridge answer bodies to what's needed to show the
  funnel/metrics; note the abridgement (it is not a fabricated metric).

---

## 6. Anonymization standard (scripted & gated)

**Keep** (translate prose; keep the proper nouns): the author's own brand and internal codenames
(confirm each codename is not client-derived); public institutions/programs/standards; generic public
tech; public published sources (metadata + derived trace only, source file never committed, with a note).

**Remove / generalize** — consistently, via the committed `_glossary.json` token vocabulary:
- Client/company names → role descriptors (`an industrial plumbing/HVAC supplier (client)`).
- People → roles. Sites/locations → `Site A/B/C`, `[location]`. Domains/emails/URLs/IPs → removed or `client@example.com`.
- Brands that point to a client → generic.
- **Identifiers** (filenames, document_ids, folder names, code symbols, window titles, XPaths): any id
  that is human-readable or derived from a name/path → opaque token. **Real content-hash ids are NOT
  automatically safe** (reversible fingerprints) → **regenerate** deterministically from the sanitized
  label, and keep the same entity's id identical across artifacts.
- **Quasi-identifiers (re-identification pass):** generalize/band distinctive numeric specs
  (`405 kW` → `~400 kW` or `>70 kW`), drop sector+region+capacity tuples, and review **free-text**
  answer/summary bodies — not just titles/ids. Test: *"could someone who knows the industry narrow
  this to one client from the residual facts?"*
- **Internal paths / storage layout / original filenames / OS usernames / drive letters / .tmp & cache
  strings** inside artifact bodies and logs → generalize (`[storage]/<id>/original/source.xlsx`).
- **Dates:** keep durations/elapsed times (metrics); **coarsen absolute calendar dates** to month or
  quarter when they could pinpoint an engagement. Coarsening a date is not a fabricated metric and
  needs no correction disclosure.
- **Secrets:** API keys, tokens, `.env` values, connection strings, private keys — never commit.
- **Binaries** (PDF/image/office): strip metadata (`exiftool -all=`) and visually inspect; **forbid**
  box-over-text redaction (rasterize+flatten or delete text); prefer SVG/mermaid over screenshots; a
  needed screenshot must be re-rendered from sanitized data.

**The glossary is the source of truth for the leak sweep.** `_glossary.json` lists every removed term
→ token. The sweep (in `verify_case_study.py`) is **derived from it**, auto-generating variants
(lowercase, de-accented, snake_case, CamelCase, hyphen/space, URL/percent-encoded) and a **negative
control**. The real→token mapping with the **real terms must live OUTSIDE the repo** (the in-repo
`_glossary.json` holds only the token vocabulary + reasons if the repo is or will be public);
consistent pseudonyms preserve relational structure, so one leaked mapping de-anonymizes the corpus.

**Gated checks (all enforced by `verify_case_study.py` / the §10 checklist):**
1. Glossary-derived term sweep (with variants + negative control) over the case folder → empty.
2. **git-history sweep**: `git log --all -p -S"<real term>"` and `git log --all --name-only` show no
   real terms or original source filenames. If history is dirty, the only fix is a fresh repo/orphan
   branch (`git checkout --orphan`) or `git filter-repo` + force-push, then re-verify — **before** push.
3. **Secret scan** over working tree AND history (gitleaks/trufflehog, or the documented regex set:
   `AKIA…`, `Bearer …`, `sk-…`, Google API keys, JWTs, `postgres://`/`mongodb://`, `-----BEGIN … KEY`).
4. Identifier checks: opaque-id pattern, cross-artifact id consistency, references resolve.
5. JSON validity; binaries metadata-stripped; author git email/name is the intended public identity.

The confidentiality note in `artifacts/README.md` may only be written **after** these pass.

---

## 7. Honesty & credibility rules

- No fabricated numbers/traces/logs. SSOT for numbers (§4); demo replays, never recomputes measured
  quantities (§8).
- Traceability counts only **resolvable** references (§4).
- **Negative case:** ≥1 recorded per case unless genuinely infeasible (then blocker + recording plan);
  ≤ half the eval matrix pending (§3.6).
- **Corrections** disclosed field-level with before→after (§5); never touch metrics/funnel/answer.
- **Synthetic** artifacts follow §5 (marked, no metrics, excluded from counts, ≤1).
- **Wording:** maturity label per §0; demo ≠ engine; **banned-until-earned adjectives** (§9).
- Prefer "I chose X for this scale, here's when I'd change it" over "X is unnecessary".

---

## 8. The runnable demo standard

`demo/run_demo.py` must:
- run **offline** (no API key, no network, no client data);
- work on the **standard library alone**; `rich` optional with graceful fallback;
- set **UTF-8 stdout** (Windows-safe) so accented/emoji output never crashes or mojibakes;
- read only the **sanitized artifacts** in `../artifacts`;
- print: (a) the state/KB overview; (b) **one live deterministic step whose logic is genuinely part
  of the system** (the real catalog-pruning rule, the validator, the strategy threshold — *not* a
  generic keyword match presented as the real selection) and clearly labelled an approximation;
  (c) the **funnel + metrics read verbatim from the recorded traces**;
- **enumerate the steps it does NOT run**, visually separate live-step output from replayed metrics,
  and when the live step diverges from the recorded run shown beside it, **print the divergence
  inline** (do not cherry-pick a query that hides the gap; state that any coincidental match is not a
  replay of the model step);
- carry an in-output honesty caveat;
- ship a byte-for-byte **`example_output.txt`** (re-capture before done: `python run_demo.py > example_output.txt`).

**Self-test** (both must exit 0 and print the caveat): `python run_demo.py` (with `rich`) and a
no-`rich` run (e.g. `python -c "import sys;sys.modules['rich']=None;import runpy;runpy.run_path('run_demo.py',run_name='__main__')"`).

---

## 9. Tone & writing rules

- Concise, **evidence-dense**, first-person ownership. Role vocabulary must describe something you
  actually did, never decorate aspirations.
- **Banned-until-earned adjectives** (only if a number/artifact backs them in the same sentence):
  *advanced, sophisticated, cutting-edge, robust, enterprise-grade, scalable, real-time,
  state-of-the-art, battle-tested.*
- Specific, not generic. Example —
  - BAD: "RAG quality depends on good chunking."
  - GOOD: "Fixed-token chunking destroyed the boiler manuals' chapter structure, so I switched to
    structure-aware chapters (see context-strategy.md)."

---

## 10. Acceptance checklist (the gate — `verify_case_study.py` automates the starred items)

- [ ] Folder/file layout matches §2; required files present.
- [ ] README has all §3.1 sections (TL;DR-with-numbers, 5-min guide leading with example_output.txt,
      real/replayed table, role boundary, active-vs-disabled stack, maturity label, contact).
- [ ] ≥2 real sanitized artifacts with a `metrics` block + `_provenance`; ≥1 exposes decision evidence.
- [ ] `<main-flow>.md`: consistent step numbering across files*; funnel + core/analog metrics for the
      **≥2 contrasting runs**.
- [ ] All restated metrics are byte-identical to their source trace*; measured vs derived labelled.
- [ ] *Every cited reference resolves (document_id in chapters_read + non-empty chapter_id); reported
      count = valid references only.
- [ ] *Cross-artifact ids consistent (every trace id resolves in the catalog); ids are opaque tokens.
- [ ] `EVALUATION.md`: negative case **recorded** (or blocker+plan stated); ≤ half pending; faithfulness mapping present.
- [ ] `the-bug-i-fixed.md`: symptom→root cause→fix(`file:line`)→result.
- [ ] `demo/run_demo.py` runs offline with and without `rich`; example_output.txt re-captured*; live
      step is a real system rule + names un-run steps + reconciles divergence.
- [ ] *Glossary-derived leak sweep empty (variants + negative control); *no human-readable/derived ids.
- [ ] *git-history sweep clean; *secret scan clean (tree + history); binaries metadata-stripped.
- [ ] No `.venv`/`__pycache__`/`.env` staged (root .gitignore covers them); author git identity intended.
- [ ] No fabricated metrics; corrections disclosed field-level; synthetic artifacts marked & excluded.
- [ ] Wording: maturity label consistent; demo ≠ engine; no unearned banned adjectives.
- [ ] Listed in the root README case index; brand/identity consistent.

---

## 11. Per-project-type guidance (one row per planned build)

Keep the skeleton; adapt `<core-decision>`, `<main-flow>`, the funnel analog, metrics and the
negative case. Mini-example = the concrete funnel / live demo step / negative case for that type.

| Root case | Type | `<core-decision>` / `<main-flow>` | Funnel analog & metrics | Negative case (record ≥1) | Mini-example |
|---|---|---|---|---|---|
| 01 RAG (done) | retrieval | context-strategy / retrieval-flow | docs→chapters narrowing; tokens, latency, cited sources | no answer → refuse | funnel=docs→confirmed→chapters→read; live step=catalog pre-filter; neg=query outside corpus → "cannot answer" |
| 02 Multimodal RAG | retrieval (visual) | embedding/visual strategy (OCR-vs-vision, page-as-image, cross-modal) / retrieval-flow | pages/modalities→candidates→read; tokens, latency, cited pages | modality missing / OCR garbage → degrade, don't invent | live step=deterministic page/modality selector; neg=image-only page with no text → flag, don't hallucinate |
| 03 Agentic doc Q&A bot | agent+retrieval | tool-vs-LLM boundary / agent-loop | turns→tool-calls→successful-actions; calls, latency, tokens | tool/answer unavailable → say so | live step=the routing/menu rule; neg=question with no doc support → refuse |
| 04 Document extraction | extraction | schema-first / vision-vs-text / extraction-flow | pages→fields targeted→found→HITL-flagged; coverage %, per-page cost, **(tokens only if LLM-metered)** | field absent → leave empty, no hallucination | live step=deterministic field-presence/validation check; neg=missing field row left empty |
| 05 MCP executor agent | agent/MCP | tool boundary, sandboxing, idempotency / agent-loop | steps→tool-calls→successful/﻿retried actions; calls, latency | tool errors / unsafe action → recover / ask / refuse | live step=the deterministic dispatch/guard; neg=failing tool → recovery path |
| 06 Voice-to-order product | applied-AI product | productionization (latency, concurrency, integration) / request-flow | requests→parsed→validated→fulfilled; **latency percentiles, throughput, error rate** (tokens optional) | bad/no-match input → graceful degradation | live step=the deterministic validation/route; neg=unrecognized item → ask/deny |
| 07 Prospecting workflow | agentic workflow | enrichment/scoring/orchestration / workflow-run | leads→enriched→qualified→actioned; counts, latency | no qualified lead / enrichment gap → drop, don't fabricate a contact | live step=the deterministic scoring/dedupe rule; neg=unverifiable lead → dropped |

Tokens are required **only** when the system is LLM-token-metered; otherwise use the latency/throughput
analog. If a type has no offline-reproducible negative case, state the blocker (§3.6).

---

## 12. Definition of done (rubric)

Five axes, all green before publishing:
- **Evidence** — real artifacts + numbers; ≥2 contrasting runs; decision-evidence artifact.
- **Honesty** — real/replayed table; resolvable traceability; recorded negative case (or blocker);
  corrections disclosed; earned wording.
- **Anonymization** — `verify_case_study.py` exits 0 (sweep + history + secrets + ids + binaries).
- **Runnability** — demo offline with/without rich; example_output.txt fresh; numbers match traces.
- **Role fit** — signature decision with substance; role vocabulary tied to real work.

---

## 13. Authoring workflow (the path that avoids back-and-forth)

1. `cp -r case-studies/_TEMPLATE case-studies/NN-slug` (slug from the root README index).
2. Build `_glossary.json` from the real source (keep real terms in an **out-of-repo** map).
3. Copy the **real** artifacts into a working area; run `sanitize.py`; regenerate ids; coarsen dates;
   strip binary metadata.
4. Write the docs from the skeletons (copy heading shapes from case 01); drop in sanitized artifacts.
5. Wire `run_demo.py` (the plumbing is pre-written in the template; implement the system-true live
   step + trace loading); capture `example_output.txt`.
6. `python case-studies/_scripts/verify_case_study.py NN-slug` until it exits 0; walk the §10 checklist.
7. Commit only the sanitized case folder; confirm `git status` shows no originals; run the git-history
   + secret sweeps **before** the first push.

---

## Appendix A — Metrics menu by project type

Pick the metrics that matter for the type (per §4: cost/latency + traceability + ≥2 contrasting runs
are always mandatory; tokens only when LLM-token-metered).

- **RAG / context:** documents selected → confirmed → candidate chapters/pages → read; iterations;
  seconds; API calls; input/output/total tokens; count of **valid** cited references; refusal behavior.
- **Document intelligence / extraction:** pages/files processed; fields targeted → found → matched →
  HITL-flagged; completion/coverage %; invalid/missing fields; processing time; API calls; retries; tokens (if metered).
- **Agent / tool / MCP:** tools discovered → executed; success/failure/retry; steps per task;
  execution time; isolation/permission boundaries respected; chained/scheduled runs if relevant.
- **Applied-AI product:** latency percentiles per main flow; throughput/concurrency; rate-limit/retry
  behavior; error rate; before→after performance delta; cost/tokens; volume (users/orders/files) when discloseable.

## Appendix B — Quick examples (the bar)

- **TL;DR bullet (good):** "Query selected 5 docs → confirmed 4 → 9 candidate chapters → 8 read →
  answered in 88.5s / 44,691 tokens with 8 resolvable citations." **(bad):** "Very scalable, accurate RAG."
- **Status (good):** "Working system (exercised on real data, not productionized); formal eval pending."
  **(bad):** "Production-ready."
- **Wording (good):** "recorded real-system run", "offline trace-replay demo", "metadata-first at this
  corpus size". **(bad):** "production run", "full RAG demo", "no vector DB (because I'm smart)".

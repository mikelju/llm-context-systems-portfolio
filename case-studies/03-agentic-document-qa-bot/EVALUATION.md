# Evaluation

The evaluation is the **Phase-4 validation battery**: 10 questions run end-to-end over the real
15-document library via Telegram, plus a security-audit run. Verdicts are the real recorded OK/KO
([`artifacts/validation-battery.json`](artifacts/validation-battery.json)).

## Case matrix

| # | Scenario type | Why it matters | Status | Evidence |
|---|---------------|----------------|--------|----------|
| 1 | Tool-path answer (basic recall, P1) | baseline grounded answer with citation | ✅ Recorded (pass) | `validation-battery.json` P1 · `query-runs.json` R1 |
| 2 | Exact numeric (P2) | must lift a precise value, not paraphrase | ✅ Recorded (pass) | `validation-battery.json` P2 |
| 3 | Ordered procedure (P3) | steps in the right order, none skipped | ✅ Recorded (pass) | `validation-battery.json` P3 |
| 4 | Symptom diagnosis (P4) | reasoning over the protocol | ✅ Recorded (pass) | `validation-battery.json` P4 |
| 5 | Safety completeness (P5) | omitting an extinguisher type is unsafe | ✅ Recorded (pass) | `validation-battery.json` P5 |
| 6 | Multi-site, no data mixing (P8) | must not attribute Site B's data to Site C | ✅ Recorded (pass) | `validation-battery.json` P8 |
| 7 | Cross-document (P9) | scan all docs, cite the right one, invent none | ✅ Recorded (pass) | `validation-battery.json` P9 |
| 8 | **Off-topic → refuse (P10)** | **must not hallucinate when no doc supports it** | ✅ Recorded (pass) | `validation-battery.json` P10 · `query-runs.json` R2 |
| 9 | **Off-topic → refuse (paella, audit run)** | second recorded refusal, different query | ✅ Recorded (pass) | `security-audit-summary.md` (SEC-210 note) |
| 10 | Maintenance frequency (P7) | misread a periodicity table | ❌ Recorded (**fail** — open) | `validation-battery.json` P7 |
| 11 | Automated scorer over a labelled set | regression safety | ⏳ Pending | none — see below |

10 of 11 rows are **recorded** (8 pass, 1 fail, plus 2 negative cases); 1 is pending — within the
"at most half pending" rule.

## Faithfulness — claim → source (run P1, tool-path)

The agent's prompt requires a `(Document, page)` citation on every datum, and P1's verdict was "exact
data with a page citation". Mapping the verified answer to its sources:

| Claim in the answer | Cited source |
|---|---|
| boiler #1 make / model | Site B manual → equipment page |
| boiler #1 output (kW) | Site B manual → equipment page |
| boiler #2 make / model / output | Site B manual → equipment page |

> Honesty note: the **verbatim answer text was not archived**, so this maps the *citation contract the
> system enforces* (validated by P1's pass), not a quoted reply. Every datum resolved to the **Site B**
> manual — none to another site — which is what makes P8 (no data mixing) a meaningful separate test.

## The negative case (recorded)

Intended behaviour: when no document supports the question, **refuse — do not answer from general
knowledge**. This is enforced two ways: `IF - Any documents?` short-circuits to a "no documentation"
message when selection is empty, and the agent prompt's "Caso B" forbids invented answers. **Two
recorded runs** exercise it: P10 (split-A/C-filter, off-topic) and the audit's paella query — both
refused cleanly with no hallucination. This is the agent-flavoured negative case from the spec ("tool /
answer unavailable → say so").

## The open failure (P7)

The one KO: "how often must the expansion vessel be checked?" The answer should be **monthly**, read from
a preventive-maintenance **table**; the model returned the wrong periodicity. Likely cause: the relevant
table spans a page boundary or the wrong manual was selected at Step 3. Fix path before delivery: tighten
the selection prompt for table-heavy queries and add P7 as a regression case. Tracked as the top open
item in the [README](README.md#status).

## What would make this a real eval suite

1. A small **labelled set** (question × expected document/page × expected value) — start from the 10
   battery questions plus P7.
2. An **automated scorer**: selection precision/recall (did Step 3 pick the right docs?) and answer
   faithfulness (does every datum cite a real page?).
3. **Archive per-query metrics** (tokens, latency, selected-doc count) behind a privacy-safe redaction so
   the cost/latency gap in this case closes.
4. Run it **before/after every prompt change**, with P7 as the canary.

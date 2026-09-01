# Agentic Prospecting Workflow — research 38 companies without inventing a single fact

A workflow that turns *"prospect this company"* into a sourced, human-readable report. An agent runs
**8 web-search protocols** per company under an explicit anti-hallucination contract — every figure
carries its source, URL, date and reliability, and anything not found is written as an explicit
`null` — and then **deterministic Python** validates completeness and builds the PDF/Excel/Word
deliverable. Built to find automation prospects for my own consultancy.

## TL;DR (with real numbers)

- **38 companies researched**, 37 identified, **27 fully enriched** through all 8 protocols, **27
  with a generated report** (27 PDF, 27 Word, 23 Excel) — 228 research JSON files in total.
- **The contract is measurable:** 12,309 recorded values, of which **1,215 (9.9%) are an explicit
  "not found"** rather than a guess; **1,178 sources logged and 1,161 carry a URL (98.6%)**; every
  rated figure is tagged high (70) / medium (141) / low (12) reliability.
- **The negative case, recorded:** across 54 contact slots, **15 were left empty (27.8%)** because no
  verifiable contact existed. The protocol forbids deducing a LinkedIn URL from a person's name, so
  an unverifiable contact is dropped, never constructed.
- **Two real leads, opposite outcomes:** one resolved **100%** of the required fields from 49 sources;
  another reached **68.4%** from 8 and was labelled *partial* by the validator rather than padded.
  Corpus mean **87.7%**, median 92.1% — 21 ready, 6 partial, 0 insufficient.
- **Where the contract leaked:** the protocol specifies **3** allowed values for a source outcome; the
  corpus contains **19**. No code validated the enum — measured here, not fixed.

## Review this case study in 5 minutes

1. [`demo/example_output.txt`](demo/example_output.txt) — the funnel, the provenance rates and the
   validator's verdict, recomputed offline.
2. [`provenance-contract.md`](provenance-contract.md) — the signature decision.
3. [`the-bug-i-fixed.md`](the-bug-i-fixed.md) — the sources that matter most are the ones that block you.
4. [`artifacts/`](artifacts/) — the real funnel, provenance stats, the negative case, two contrasting runs.

## The real problem

Prospecting research is the kind of task an LLM does *fluently and badly*. Ask a model for a
company's turnover, headcount and the name of its administration manager and you will get all
three — confidently, plausibly, and sometimes wrong. In a sales context the failure is expensive and
invisible: a fabricated contact is acted on, it bounces, and the lead is burned.

So the engineering problem is not "can the agent find company data". It is **making absence
representable, and making every claim carry its evidence** — while still ending up with a document a
human can read in five minutes.

## My role

I designed and built the whole workflow: the 8 search protocols and the shared anti-hallucination
contract they all obey, the JSON schema that carries provenance per field, the deterministic
validator and its readiness thresholds, the PDF/Excel builders, and the browser fallback for sources
that block automated fetching. **Off-the-shelf:** Claude (as the agent running the protocols),
Playwright, fpdf2, openpyxl. **What I did NOT build:** the model or the search engine — the
engineering here is the contract, the boundary between agent judgment and deterministic code, and
turning "did it make things up?" into a number.

## Evidence in this case study

| File | What it is |
|------|-----------|
| [architecture.md](architecture.md) | the two-layer shape: protocol-driven agent + deterministic tools |
| [provenance-contract.md](provenance-contract.md) | the signature decision + where it leaked + when I'd change it |
| [workflow-run.md](workflow-run.md) | the 8-protocol run, the funnel, and two contrasting real leads |
| [reliability-and-evaluation.md](reliability-and-evaluation.md) | the real mechanisms, and what is genuinely not measured |
| [EVALUATION.md](EVALUATION.md) | the case matrix and the recorded negative case |
| [the-bug-i-fixed.md](the-bug-i-fixed.md) | LinkedIn returns 999 to automated fetches — the visual fallback |
| [lessons-learned.md](lessons-learned.md) | 8 lessons, including why a contract in prose drifts |
| [artifacts/](artifacts/) | funnel, provenance stats, negative case, two runs, protocol structure |
| [demo/](demo/) | offline demo recomputing the validator's rule over the real corpus |

## What is real / replayed / simulated

| Element | Status | Note |
|---|---|---|
| funnel, provenance stats, negative case, two runs, protocol structure | **Real** (aggregated) | computed from the real research corpus; only counts and shapes, never a value |
| the rates in the demo (null %, URL %, empty %) | **Real, recomputed live (offline)** | divided out from the recorded counts, no network |
| the validator's verdict in the demo | **Real rule, re-executed** | the same >=80 / >=50 thresholds as the deployed tool, checked against the recorded verdict |
| the research itself (8 protocols per company) | **Not run here** | it queried the live public web at a point in time and cannot be replayed offline |
| the browser fallback and its fix | **Real** | from the actual codebase and the project's phase plans |
| every company, person, contact and URL | **Removed** | no lead identity appears anywhere in this case study |

## Stack

Claude running markdown search protocols (WebSearch / WebFetch) · Python 3 · Playwright (visual
fallback for sources that block fetching) · fpdf2 (PDF) · openpyxl (Excel) · dataclass schemas ·
a deterministic validator. **Present but disabled by design:** a Google Sheets CRM integration
(`google_sheets.py`) exists but its write path was never switched on — see
[reliability-and-evaluation.md](reliability-and-evaluation.md).

## Status

**Working system** — run over real data: 38 companies researched and 27 reports generated across two
months. Not a product: there is no scheduler, no queue and no CRM write-back. The top open item is
the contract drift measured in [`artifacts/provenance-stats.json`](artifacts/provenance-stats.json) —
the anti-hallucination rules live in prose and nothing enforces them mechanically.

## Contact

See the [root README](../../README.md#contact).

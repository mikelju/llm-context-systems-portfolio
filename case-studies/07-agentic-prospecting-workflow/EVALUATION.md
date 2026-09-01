# Evaluation

This system does not promise correct facts — no automated prospecting system honestly can. It
promises that **every claim carries its evidence and every gap is visible**. That is what is measured
here, over the whole real corpus: 38 companies, 228 research files, 12,309 recorded values.

## The case matrix

| # | Scenario | Why it matters | Status | Evidence |
|---|---|---|---|---|
| 1 | **Data found → recorded with source, URL, date, reliability** | the base case; a claim without provenance cannot be checked | ✅ recorded | 1,178 sources logged, **1,161 with a URL (98.6%)**; ratings 70 high / 141 medium / 12 low — [`provenance-stats.json`](artifacts/provenance-stats.json) |
| 2 | **Data not found → explicit `null`** (the domain negative case) | the failure an unconstrained agent makes by default | ✅ **recorded** | **1,215 of 12,309 values (9.9%)** are an explicit "not found" |
| 3 | **No verifiable contact → slot left empty** | a fabricated contact is acted on, bounces, and burns the lead | ✅ **recorded** | **15 of 54 contact slots (27.8%) left empty** — [`contact-negative-case.json`](artifacts/contact-negative-case.json) |
| 4 | **Thinly-documented company → thinner report, labelled** | where a model's plausible fiction is most tempting | ✅ recorded | Lead B: 68.4% complete, verdict `partial`, 12 nulls, 8 sources all with URLs — [`two-runs.json`](artifacts/two-runs.json) |
| 5 | **Enrichment incomplete → lead stops, is not completed by guesswork** | the funnel must fail by stopping, not by inventing | ✅ recorded | **10 of 37 identified leads** never reached full enrichment and were left as partial research — [`funnel.json`](artifacts/funnel.json) |
| 6 | **Source blocks automated access → read visually, still verified** | the pages holding people data are the ones that block fetching | ✅ recorded | 84 blocked/failed fetches; visual fallback in protocols 04 and 08 — [`browser-fallback.json`](artifacts/browser-fallback.json), [the-bug-i-fixed.md](the-bug-i-fixed.md) |
| 7 | **Sources disagree → both recorded** | silently picking a winner destroys the human's ability to judge | ⚠️ rule in force, **not counted** | the protocols mandate it and contradictory figures do appear in the corpus, but no aggregate count was extracted; not claimed as a number |
| 8 | **Value recorded but wrong** | the gap that matters most commercially | ❌ **not evaluated** | no accuracy audit exists — see below |
| 9 | **Contract violated → rejected at write time** | the enum drift shows why | ❌ pending | nothing enforces the schema mechanically; measured at 22 off-contract occurrences |

Six of nine recorded, one partial, two open — and the two open ones are stated as gaps rather than
softened.

## The negative case, in detail

For prospecting, the negative case is **"there is no verifiable contact → write nothing"**. It is the
one an agent fails by default, because the alternative is so easy: contact URLs on the main
professional network are formulaic, so a plausible one can be constructed from a person's name
without consulting anything.

The protocol forbids exactly that — *only URLs seen directly in search results; never build one by
deduction* — and the corpus shows the rule surviving contact with reality:

| | count | share |
|---|---|---|
| Contact slots across 27 fully-enriched leads (a manager + an admin lead each) | 54 | |
| With at least one reachable channel (email, phone or a **seen** profile) | 39 | 72.2% |
| **Left empty — no verifiable contact existed** | **15** | **27.8%** |

More than one slot in four was left blank in a document whose entire purpose is to enable a sales
call. That is the cost of the rule, paid 15 times, and it is the right trade: a blank tells the
salesperson to do 5 minutes of work, while a plausible wrong one wastes the lead.

## Faithfulness mapping (claim → source)

| Claim | Source field |
|---|---|
| 38 researched, 37 identified, 27 enriched, 27 actioned | `funnel.json` → `metrics`, `stages[]` |
| 228 research JSON files, 8 protocols per lead | `funnel.json` → `metrics.research_json_files`, `protocols_per_lead` |
| 12,309 values, 1,215 explicit nulls (9.9%) | `provenance-stats.json` → `metrics` |
| 1,178 sources, 1,161 with URL (98.6%) | `provenance-stats.json` → `metrics` |
| reliability 70 / 141 / 12 | `provenance-stats.json` → `metrics.reliability_*` |
| 3 specified values vs 19 observed, 22 off contract | `provenance-stats.json` → `contract_drift` |
| 54 contact slots, 39 reachable, 15 empty | `contact-negative-case.json` → `metrics` |
| 100.0% / 68.4%, mean 87.7%, median 92.1%, 21 / 6 / 0 | `two-runs.json` → `metrics`, `runs[]` |
| 84 blocked fetches, 11 captures, 2 protocols with fallback | `browser-fallback.json` → `metrics` |

Every figure in this case study is an aggregate over the real corpus, recomputed by script. The demo
re-derives the rates and the validator's verdict offline so the arithmetic is checkable rather than
asserted.

**The gap, stated plainly:** there is no worked *claim → primary source* citation for an individual
company, because that would require publishing a real company's researched data, and every lead
identity is deliberately absent from this case study. The provenance chain exists per field in the
real system — every figure carries its own source name, URL and consultation date — but showing one
end to end would defeat the anonymization. What is published instead is the *rate* at which that
chain is complete: 98.6%.

## What a real eval suite needs

1. **An accuracy audit.** Re-verify a stratified sample of figures — say 30 across high/medium/low
   reliability — against their cited sources by hand. This is the missing measurement, and it is the
   only one that would let the system claim more than "traceable".
2. **Schema enforcement as a test.** Validate every research JSON against a strict schema (the enum,
   the provenance quartet, `null` vs `"N/A"`) and treat violations as failures. Target: 0
   off-contract occurrences **with the null rate unchanged** — a drop in nulls would mean the agent
   learned to guess in the accepted format.
3. **A contradiction counter.** The rule that both sides of a disagreement are recorded is in force
   but unmeasured; counting them turns case 7 from a claim into evidence.
4. **A second operator.** The protocols were written and run by the same person. Whether they work
   when someone else runs them is the real test of a protocol-driven design.
5. **Outcome data.** The commercial question — do `ready` leads convert better than `partial` ones? —
   needs CRM outcomes joined back to completeness scores. The CRM integration exists but its write
   path was never enabled, so this has never been measurable.

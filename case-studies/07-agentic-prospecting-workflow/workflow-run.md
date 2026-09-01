# The workflow run

## The 8 protocols

One command — *"prospect this company"* — expands into eight protocol files the agent follows in
order. Each writes one JSON into the company's research folder, under the shared provenance contract.

| # | Protocol | What it establishes | Required fields (checked by the validator) |
|---|---|---|---|
| 1 | Identification | legal name, tax id, legal form, address, activity code | 8 |
| 2 | Financial | turnover and net result over 5 years, growth trend | 1 (a multi-year series) |
| 3 | Employees | headcount evolution, job postings, productivity ratio | 1 |
| 4 | Admin department | does it exist, how many people, which tools/ERP | 2 |
| 5 | Profile | main activity, products, value proposition | 3 |
| 6 | Competitors | top competitors regionally and nationally | 2 |
| 7 | News | coverage in the last 2 years, timing signals | 1 |
| 8 | Contacts | the manager and the admin lead: phone, email, LinkedIn | 2 |

**Order is not cosmetic.** Protocol 1 runs alone first because every later protocol interpolates what
it produces — the legal name, tax id, activity code and locality become the search variables for the
rest. Then 2, 3, 5 and 7 can run in parallel; 4 depends on the employee data from 3; 6 depends on the
sector from 1 and 5; and 8 runs last so it can reuse names surfaced by the news and profile searches.
Source: [`artifacts/protocol-structure.json`](artifacts/protocol-structure.json).

## The funnel (real corpus)

```
38 companies researched      a folder opened, at least one protocol run
        │
        ▼  1 dropped
37 identified                protocol 01 resolved the legal identity
        │
        ▼  10 dropped
27 fully enriched            all 8 protocols completed  (228 research JSON files)
        │
        ▼  0 dropped
27 actioned                  a report generated: 27 PDF, 27 Word, 23 Excel
```

The interesting drop is the middle one. **Ten identified companies never reached full enrichment** —
and they were left as partial research rather than completed with unverified data. That is the funnel
behaving as designed: the workflow's failure mode is *stopping*, not *inventing*.

The last stage has no drop at all, and that is deliberate too: once a company is fully enriched, the
report generation is pure deterministic Python, so it either runs or crashes — it cannot half-succeed.

## The two recorded runs, side by side

Same eight protocols, same contract, two real companies at opposite ends of the completeness
distribution. This is the axis the provenance contract controls: **how much of what was asked could
actually be sourced** — and what the system does about the rest.

| | **Lead A — best-sourced** | **Lead B — thinly-sourced** |
|---|---|---|
| Completeness | **100.0%** | **68.4%** |
| Validator verdict | `ready` | `partial` |
| Values recorded | 798 | 150 |
| Explicit nulls | 25 | 12 |
| Sources logged | 49 (49 with URL) | 8 (8 with URL) |
| Source outcomes | 49 `datos_encontrados` | 8 `datos_encontrados` |
| What the human receives | a full report | a visibly thinner report, marked *partial* |

Source: [`artifacts/two-runs.json`](artifacts/two-runs.json).

**Why it matters.** Lead B is the case that would break a naive prospecting agent. A company with
little public footprint gives the model almost nothing to work with — which is exactly the situation
where an unconstrained model produces its most plausible fiction, because plausibility is all it has
left. Here it produced 150 values with 12 explicit "not found" and a `partial` label, from 8 sources
that all carry a URL.

Neither report is wrong. One is thinner, and **the system says so, in a number, before a human reads
a word of it**. Across the corpus: mean 87.7% complete, median 92.1%, with 21 leads `ready`, 6
`partial` and 0 `insufficient`.

## The deterministic gate

Between the agent's research and the deliverable sits one rule, and it is the step the demo
re-executes live:

```
completeness = filled required+recommended fields / total, across all 8 protocols

  >= 80%  ->  ready         "listo para generar informe"
  >= 50%  ->  partial       "el informe tendra huecos"
   < 50%  ->  insufficient  "se recomienda completar protocolos"
```

It is deliberately dumb arithmetic over field presence — no model, no judgment, reproducible by hand.
That is the property that makes it trustworthy as a gate: the layer that decides whether research is
good enough to act on must not share the failure modes of the layer that produced it.

Diagram: [assets/workflow-sequence.md](assets/workflow-sequence.md).

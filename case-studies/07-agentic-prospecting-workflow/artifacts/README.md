# Artifacts — real outputs (aggregated)

These are computed from the real prospecting corpus: 38 company research folders, 228 JSON files
produced by the agent between March and April 2026. Every file here is an **aggregate** — counts,
rates and shapes. Unlike the other case studies in this portfolio, no sample rows are published,
because in this project every row is a real company or a real person.

| File | What it is | Real? | Sanitized? |
|------|-----------|:----:|:----------:|
| [`funnel.json`](funnel.json) | The 4-stage funnel — 38 researched → 37 identified → 27 fully enriched → 27 with a deliverable — with what each stage means and where leads dropped | ✅ | counts only |
| [`provenance-stats.json`](provenance-stats.json) | The anti-hallucination contract measured: 12,309 values, 1,215 explicit nulls, 1,178 sources (1,161 with URL), the reliability split, and the contract drift | ✅ | counts only |
| [`contact-negative-case.json`](contact-negative-case.json) | The domain negative case: 54 contact slots, 39 reachable, **15 left empty**, plus the rule that produces that outcome | ✅ | counts only |
| [`two-runs.json`](two-runs.json) | Two real leads at the extremes of the completeness distribution (100.0% and 68.4%), with their value, null and source counts | ✅ | identities replaced by `Lead A` / `Lead B` |
| [`browser-fallback.json`](browser-fallback.json) | The blocked-source problem and its visual fallback: 84 blocked/failed fetches of 1,178, 11 captures, 2 protocols wired | ✅ | counts only; no URL or captured content |
| [`protocol-structure.json`](protocol-structure.json) | The 8 protocols, the fields the validator requires from each, the thresholds and the execution order | ✅ | structure only |

## What "sanitized" changed

This case study's threat model is unusual: the *data* is the identity. A prospecting corpus is a list
of real companies with real people's contact details, so the sanitization is not redaction of a few
fields — it is a decision to publish **only aggregates**.

- **No company appears anywhere.** Not as a name, a tax id, a slug, a domain, a locality or a sector
  label narrow enough to identify one. The two leads in `two-runs.json` are `Lead A` and `Lead B`.
- **No person appears anywhere.** No names, roles, emails, phone numbers or profile URLs — the
  contact protocol's output is represented purely as "slot filled / slot empty".
- **No source URLs.** The corpus logs 1,161 URLs; publishing them would reconstruct the company list.
  Only the *rate* at which sources carry a URL is published.
- **No values.** No turnover, headcount, competitor list or news item. Where a shape had to be shown,
  it is described in prose rather than exemplified.
- **No CRM identifiers**, no spreadsheet ids, no credentials.

## What is NOT changed (this is the evidence)

- **The counts**: 38 / 37 / 27 / 27 · 228 files · 12,309 values · 1,215 nulls · 1,178 sources · 1,161
  URLs · 70 / 141 / 12 reliability · 22 off-contract of 19 distinct values · 54 / 39 / 15 contact
  slots · 84 blocked fetches · 11 captures.
- **The two leads' real metrics** (completeness, values, nulls, sources) — only the identities were
  replaced.
- **The system's own rules and thresholds**: the 80 / 50 readiness bands, the required-field lists per
  protocol, the execution order, the three-value source enum.

## Note on what is missing (the honest gap)

There is **no worked per-field provenance example** — no "this figure came from that filing on that
date" — even though the real system records exactly that for every figure. Showing one end to end
would identify the company, which is the one thing this case study cannot do. What is published
instead is the rate at which that chain is complete (98.6% of sources carry a URL) and the shape of
the contract that produces it. See [../EVALUATION.md](../EVALUATION.md).

> Confidentiality: no company, person, contact detail, URL, credential or researched value appears in
> any artifact. Written only after `verify_case_study.py` passes with the out-of-repo term list.

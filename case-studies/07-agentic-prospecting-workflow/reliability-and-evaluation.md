# Reliability and Evaluation

## Reliability mechanisms (in the real system)

| Mechanism | Where | Why |
|---|---|---|
| **The shared anti-hallucination contract** | `search_protocols/CLAUDE.md`, auto-loaded for every protocol in that folder | absence is representable (`null`), evidence is mandatory, estimates must announce themselves — a rule you must remember to paste is a rule that eventually isn't |
| **Provenance quartet per figure** | every protocol's JSON schema — `fuente`, `url`, `fecha_consulta`, `fiabilidad` | a claim without a source cannot be written in the first place; 1,161 of 1,178 logged sources carry a URL |
| **`null` vs `"N/A"`** | protocol schemas | "not found" and "confirmed not applicable" are different facts about the world; collapsing them hides whether the research failed |
| **Contradictions preserved** | protocol rules | two sources disagreeing are both recorded with their sources; the workflow never silently picks a winner |
| **Deterministic completeness gate** | `validate_data.py` — required/recommended fields, thresholds 80 / 50 | the layer that decides whether research is good enough must not share the failure modes of the layer that produced it |
| **Protocol dependency order** | `prospeccion_empresa.md` | protocol 01 resolves the identity that every later search interpolates; running them out of order silently researches the wrong company |
| **Stale-contact rule** | protocol 08 | contact data older than 2 years is not recorded — a 3-year-old phone number is a liability, not an asset |
| **Visual fallback for blocked sources** | `browser.py`, wired into protocols 04 and 08 | public pages that refuse automated fetches are read as images rather than guessed at ([the-bug-i-fixed.md](the-bug-i-fixed.md)) |
| **Deterministic deliverable build** | `generate_report.py`, `pdf_builder.py`, `excel_builder.py` | report generation either runs or crashes; it cannot half-succeed or improvise a value |
| **CRM writes disabled** | `google_sheets.py` — dry-run by design | the integration exists but its write path was never switched on: nothing automated has ever modified the real CRM |

## How I evaluate

There is no labelled ground truth for "is this company's turnover correct" — verifying it would mean
re-doing the research by hand for 38 companies. So the evaluation measures **the property the system
actually promises**: not that every figure is right, but that **nothing is asserted without
evidence, and absence is recorded rather than filled in**. That is measurable from the corpus itself —
the null rate, the source-URL rate, the reliability split, and the empty-contact count — and it is
what [EVALUATION.md](EVALUATION.md) reports, together with the recorded negative case.

## Known limitations

- **Completeness is not correctness.** The gate counts filled fields. It cannot detect a *wrong*
  value, only a missing one — a confidently sourced but misattributed figure passes at 100%. This is
  the single biggest gap and no part of the system addresses it.
- **No accuracy audit.** Nobody re-verified a sample of figures against the primary sources. The
  honest claim is "sourced and traceable", never "verified correct".
- **The contract is only enforced where it is a shape.** 22 source outcomes drifted off their 3-value
  enum precisely because no code checks it ([provenance-contract.md](provenance-contract.md)).
- **No timing data.** Research is an interactive agent session; nothing recorded per-protocol latency
  or cost, so this case study reports counts only. There is no throughput or per-lead cost figure and
  none is estimated.
- **Reliability ratings are self-assigned.** The agent rates its own sources high/medium/low against
  written criteria. Reasonable in practice, and not independently audited.
- **One operator, one sector cluster, two months.** 38 companies in a regional market, researched by
  the person who wrote the protocols. Whether the contract holds with a different operator or in a
  market with thinner public data is untested.

<!-- Spec §3.6/§7. Include the domain NEGATIVE case. Record ≥1 negative case (or state the blocker+plan).
     At most half the matrix may be 'pending'. Never fake a trace. -->
# Evaluation

## Case matrix
| # | Scenario type | Why it matters | Status | Evidence |
|---|---------------|----------------|--------|----------|
| 1 | <happy path A> | baseline | ✅ Recorded | `artifacts/<trace-a>.json` |
| 2 | <contrasting path B> | the signature mechanism | ✅ Recorded | `artifacts/<trace-b>.json` |
| 3 | **<negative case>** (no answer / field absent / tool fails / bad input) | must not hallucinate / must recover | ✅ Recorded **or** ⏳ pending (blocker + plan) | ... |

## Faithfulness — claim → source (one recorded run)
| Claim in the answer | Cited source |
|---|---|
| ... | ... → ... |

## The negative case
<!-- intended behavior; if pending: the concrete blocker + exact steps to record it. Do NOT fabricate a trace. -->

## What would make this a real eval suite
1. A small labeled set (questions × expected sources).
2. An automated scorer (precision/recall + faithfulness).
3. Run before/after each change.

<!-- RENAME per spec §11 (retrieval-flow.md / extraction-flow.md / agent-loop.md / request-flow.md).
     Spec §3.4. Number the steps ONCE; use the same numbering in README, the diagram and run_demo.py. -->
# <Main flow>

## The N steps
<!-- each step annotated with a REAL trace number -->
**Step 1 — ...** ...
**Step 2 — ...** ...

## The funnel, side by side (real metrics)
<!-- ≥2 recorded runs that DIFFER along the axis the core decision controls (not two copies of the easy path).
     Copy every number verbatim from the trace; cite the trace file. -->
| | Run A (<path>) | Run B (<contrasting path>) |
|---|---|---|
| funnel stage counts | ... | ... |
| wall-clock / calls | ... | ... |
| tokens (if LLM-metered) | ... | ... |
| valid cited sources | ... | ... |

Traces: [`artifacts/<trace-a>.json`](artifacts/) · [`artifacts/<trace-b>.json`](artifacts/)

## Why this matters
<!-- one paragraph: bounded cost, traceability, the signature mechanism shown operating -->

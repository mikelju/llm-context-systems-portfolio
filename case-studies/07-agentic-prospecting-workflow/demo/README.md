# Runnable demo — offline

Runs **offline, no API key, no network, no model call, no web search**, from the aggregated artifacts
in [`../artifacts`](../artifacts).

## What it does

1. **A — the funnel.** 38 researched → 37 identified → 27 fully enriched → 27 actioned, with what
   each stage means and the 10 leads that stopped rather than being completed with unverified data.
2. **B — the provenance contract, recomputed.** The null rate (1,215 / 12,309) and the source-URL
   rate (1,161 / 1,178) are divided out in the process you are running, from the recorded counts.
3. **C — the negative case.** 54 contact slots, 39 reachable, **15 left empty**, with the rule that
   produces that outcome.
4. **D — the live deterministic step.** The real validator's readiness rule (`>= 80%` ready, `>= 50%`
   partial, below that insufficient) is **re-executed** over the two recorded leads, and the
   recomputed verdict is checked against the verdict the real tool recorded. They match — which is
   the point: this gate is plain arithmetic, reproducible by hand, and shares none of the failure
   modes of the agent whose work it judges.
5. **E — where the contract leaked.** 3 specified values, 19 observed, 22 occurrences off contract.

> **Honesty note.** The research itself — an agent running 8 web-search protocols per company against
> the live public web — is **not run here and cannot be**: it depended on what the web said at a point
> in time. No model is called and no page is fetched. What runs is the deterministic layer.

## Run it

```bash
python run_demo.py                 # stdlib only
pip install -r requirements.txt    # optional — only `rich`, for the boxed table
```

Degrades cleanly without `rich` (plain-text table, same numbers). Re-capture the expected output
after any change: `python run_demo.py > example_output.txt`.

## Expected output

See [`example_output.txt`](example_output.txt). The two lines worth reading twice are in section C —
more than one contact slot in four was left blank in a document whose whole purpose is to enable a
sales call — and the last line of section D: the thinly-sourced lead was labelled `partial` rather
than padded to look like the well-sourced one.

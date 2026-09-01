# Lessons learned

## 1. A data contract is worth what its *shape* is worth, not what its tone is worth

Every rule in this workflow was written with equal emphasis. The ones expressed as **structure** —
`null` for not-found, a mandatory source/URL/date/reliability block per figure — held across 12,309
values. The one expressed only as **prose** — "record the outcome as one of these three values" —
produced 19 distinct values instead of 3. Same document, same model, same care. The difference is
that something downstream depended on the shape of the first two and nothing checked the third.

## 2. Making absence representable is the design decision

The instinct is to treat a missing field as a failure to be minimised. Here it is a **first-class
answer**: 1,215 explicit "not found" values, 9.9% of everything recorded. Once absence has a
representation, "the agent didn't find it" and "the agent made something up" stop being
indistinguishable in the output — which is the only thing that makes the rest of the system
auditable.

## 3. The negative case has a price, and you pay it in the deliverable

**15 of 54 contact slots are empty** in documents whose entire purpose is to enable a sales call.
That is uncomfortable, it is visible to the person using the report, and it is correct: a blank costs
the salesperson five minutes, while a plausible wrong contact costs the lead. A negative case you
never actually pay for isn't a rule, it's a preference.

## 4. The deterministic layer is not the safe one by default

This architecture pushes work away from the model wherever it can — and then the deterministic route
was the one that broke, because the pages holding people data return HTTP 999 to anything automated.
Worse, the *most* deterministic option available was the catastrophic one: contact URLs on that
network are formulaic, so constructing one requires no model at all and would have produced
confident, unverified identities. Determinism is a property of the mechanism, not a guarantee about
the result.

## 5. Protocol order is part of the design, not an implementation detail

Protocol 01 runs alone and first because it resolves the legal identity that every later search
interpolates. Run out of order, the workflow doesn't error — it quietly researches a differently-named
company and returns a complete, well-sourced, entirely wrong report. The dependency graph is load
bearing precisely because violating it fails silently.

## 6. The gate must be dumber than the thing it judges

The readiness verdict is field presence over field count with two thresholds. It involves no model
and no judgment, which is exactly why it can be trusted to evaluate a layer that has both. Had I used
a model to score research quality, the score would share the failure modes of the research — a
confidently fabricated field would read as a well-filled one.

## 7. Say "completeness is not correctness" out loud, repeatedly

The gate counts filled fields. A misattributed but well-sourced figure scores 100%. Every number this
case study reports is about *traceability*, never about truth, and the temptation to let a
completeness score be read as a quality score is strong precisely because the number is so
presentable. The honest framing is less impressive and is the only defensible one.

## 8. Inspectable intermediate output is what makes analysis possible later

Every protocol writes plain JSON to disk before anything is built from it. Two months after the last
run, that made it possible to measure the null rate, the source-URL rate, the reliability split and
the contract drift across the whole corpus **without re-running a single search** — which is also how
the drift was discovered at all. Had the protocols streamed straight into the PDF builder, none of
this case study would exist.

## What I'd do next

1. **Enforce the schema at write time** — JSON Schema on every protocol output, with the enum, the
   provenance quartet and `null` vs `"N/A"` as hard constraints; the validator should reject, not
   merely score. Target: **0 off-contract occurrences with the null rate unchanged** — if enforcement
   reduces nulls, it taught the agent to guess in the accepted format instead.
2. **Audit accuracy on a sample** — 30 figures stratified by reliability rating, re-verified by hand
   against their cited sources. Until that exists, "traceable" is the only claim available.
3. **Count the contradictions.** The rule that both sides of a disagreement are recorded is in force
   but unmeasured.
4. **Have someone else run it.** A protocol-driven design that only works when its author drives it
   is a habit with extra steps.

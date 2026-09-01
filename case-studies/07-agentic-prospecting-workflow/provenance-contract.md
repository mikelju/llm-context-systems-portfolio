# The signature decision: make absence representable, and make every claim carry its evidence

## The problem

An agent asked to research a company will answer every question you ask it. That is the failure mode,
not the feature. Turnover, headcount, the administration manager's email — all three come back
fluent, plausible and occasionally invented, and nothing in the output distinguishes *"I found this
in the official register"* from *"this is roughly what a company like this usually looks like"*.

For prospecting, the cost is asymmetric. A missing field is an inconvenience: the salesperson looks
it up. **A fabricated field is acted on** — an email that bounces, a phone call to a person who
doesn't work there, a revenue figure quoted back to a prospect who knows it's wrong. The lead is
burned and you don't find out why.

## The choice + why

**Constrain the output shape, not the model's wording.** Every protocol writes into a schema where
absence and evidence are first-class:

- **`null` means "not found", and it is a legitimate answer.** The rule the protocols share is
  explicit: *if you don't find a datum, write `null`. An empty field is infinitely better than an
  invented one.* Measured across the corpus: **1,215 of 12,309 values (9.9%)** are an explicit null.
- **Every figure carries `fuente`, `url`, `fecha_consulta` and `fiabilidad`** — source name, direct
  link, consultation date, and a three-level reliability rating (official register = high, press or
  directory = medium, estimate or indirect = low). **1,178 sources logged, 1,161 with a URL (98.6%)**;
  ratings split 70 high / 141 medium / 12 low.
- **`null` and `"N/A"` mean different things.** Not-found versus confirmed-not-applicable. Collapsing
  them would hide whether the research failed or the company genuinely has no such department.
- **Estimates must announce themselves** (`"tipo": "estimado"` plus the basis of the estimate), and
  **contradictory sources are both recorded** rather than silently reconciled — the human decides.
- **No deduced identities.** LinkedIn URLs may only be included if seen directly in a search result;
  constructing `linkedin.com/in/firstname-lastname` is forbidden even though it usually works. This
  is what produces the recorded negative case: **15 of 54 contact slots left empty**.

The point is that none of these are instructions to "be accurate". They are **shape constraints**
that make a fabrication visibly different from a finding, so that a human — or a script — can tell
them apart afterwards.

## Where it leaked (measured)

The contract works where it is a *shape*, and drifts where it is *prose*.

Each source logged is supposed to record its outcome as one of three values:
`datos_encontrados`, `sin_datos`, `error_acceso`. The corpus contains **19 distinct values** across
1,178 logged sources — **22 occurrences off contract**, written as free text: partial results, counts
of profiles found, an HTTP status note. Small in volume, and revealing in kind.

The cause is not the model being careless. It is that **the enum lives in a protocol document and no
code checks it.** The deterministic validator verifies that required *fields are present*; it never
verifies that a value is one of the three allowed. So the one part of the contract with no mechanical
enforcement is exactly the part that drifted. Everything the validator does check — required fields,
source lists — held.

The number is small enough to be honest about and large enough to make the point: **a rule that only
exists in prose is a suggestion.**

## When I would do it differently / scale it

- **Trigger:** at ~19 distinct values for a 3-value field, the aggregate analysis I had to write to
  find this drift stops being a one-off. Past that, the drift is no longer detectable by reading
  files — which is precisely when it starts corrupting downstream filtering.
- **The change:** enforce the schema at write time — JSON Schema validation on every protocol output,
  with the enum, the required provenance quartet per figure, and the `null`-versus-`"N/A"`
  distinction as hard constraints. The validator already runs after every research batch; it should
  reject, not merely score.
- **Measure first:** the aggregate scan that produced
  [`artifacts/provenance-stats.json`](artifacts/provenance-stats.json) becomes the regression metric —
  off-contract occurrences must go to 0, and the explicit-null rate must **not** move. That second
  half matters: an enforcement layer that quietly reduces nulls does not repair the contract, it
  teaches the agent to guess in the accepted format.
- **The specific failure it addresses:** today a downstream filter that counted `error_acceso` to
  decide "should I retry this source?" would silently miss the 22 off-contract rows. That is the
  concrete cost of a contract nothing enforces.

# The bug I fixed: the sources that matter most are the ones that block you

## Symptom

Protocols 4 and 8 — *who works in this company's administration department* and *how do I reach
them* — kept coming back thin. Not wrong: **empty**. The contract was doing its job and writing
`null`, but the two protocols the entire prospecting exercise exists for were the two producing the
least.

Across the corpus, **84 of 1,178 logged source consultations (7.1%) ended in a blocked or failed
fetch** ([`artifacts/browser-fallback.json`](artifacts/browser-fallback.json)). They were not evenly
spread: they concentrated on exactly the pages that hold people data.

## Root cause

The professional network that holds most of that information **returns HTTP 999 to automated
fetches** — a non-standard status whose only meaning is *"I know you're a robot"*. No amount of
retrying, reformulating the query or switching user agent changes it.

And it was not one hostile site. The same class of failure came from pages that render their content
with JavaScript (the fetch returns a shell with no data) and pages that only reveal what you need
after a scroll or a click. What these have in common is that **the information is public and visible
to a human, and simply not present in the bytes an HTTP fetch receives.**

The tempting workaround was the one the contract explicitly forbids. Contact URLs on that network are
formulaic — first name, surname — so you can construct one without fetching anything, and it is right
often enough to feel like a solution. It is the single worst thing this system could do: a
constructed identity that looks verified, at the exact point where a human is about to act on it.

## The fix

Stop trying to *fetch* the page and start *looking* at it. `browser.py` drives a real browser via
Playwright — `screenshot`, `navigate`, `click`, `scroll`, `extract_text` — saves the capture, and the
agent then reads the **image** with its vision capability rather than parsing HTML that was never
sent.

The page that refuses to be scraped renders perfectly to a browser, because rendering to a browser is
its job.

Two details matter more than the tool itself:

- **It is wired in as a fallback, not a default** — declared in protocols 04 and 08 only. It is
  slower and heavier than a fetch, so it runs when a fetch has already failed, on the two protocols
  where the missing data is worth the cost.
- **It does not loosen the contract.** A profile *seen* in a capture is a verified sighting and can be
  recorded with its URL; a profile *inferred* from a name remains forbidden. The fallback widens what
  can be verified — it never lowers the bar for what counts as verified. That distinction is why the
  negative case survives: **15 of 54 contact slots are still empty** after the fallback existed,
  because for those companies nothing verifiable was ever seen.

## Result

The two protocols that were starved became answerable: all **27 fully-enriched leads** completed
protocol 08, and **39 of 54 contact slots carry a reachable channel**. Eleven captures are kept in the
real project as the evidence trail of pages read visually.

**What I cannot claim:** there is no before/after measurement. The fallback was built early and most
of the corpus was researched after it existed, so no controlled comparison exists — only the residual
84 blocked fetches, which are the cases where even the visual route was not attempted. Stated in the
artifact as `not_measured` rather than estimated.

## Why it's a good story

It is the moment the project's central boundary got tested. Everything else in this workflow pushes
work *away* from the model and *towards* deterministic code — that is the architecture's whole
argument. Here the deterministic route was the one that failed, and the fix was to give the model a
capability it hadn't been using: sight.

The lesson isn't "use a browser". It is that **the boundary between agent and code is not a
hierarchy** — one is not the fallback for the other. They fail at different things. HTTP fetching
fails at pages built for eyes; the model fails at arithmetic and consistency. The design job is
knowing which failure you are looking at, and the trap is assuming the deterministic layer is always
the safer one. Reaching for the formulaic URL would have been "deterministic", and it would have been
the worst decision in this case study.

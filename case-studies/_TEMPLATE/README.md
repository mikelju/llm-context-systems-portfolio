<!--
  Case-study README skeleton. Fill every section; delete the comments.
  Spec: ../CASE_STUDY_SPEC.md §3.1. Copy the heading shape from 01-rag-knowledge-system/README.md.
  Maturity label (pick one, use everywhere): "prototype" | "working system". Never "production".
-->
# <Case Title>

<!-- one paragraph: what it is, for whom, the non-obvious problem. + internal codename (confirm NOT client-derived). -->

## TL;DR (with real numbers)
<!-- 3–5 bullets, EACH with a concrete figure copied verbatim from an artifact (threshold, latency, tokens, counts). -->
- ...

## Review this case study in 5 minutes
<!-- ordered list; LEAD with demo/example_output.txt, then the core-decision file, the bug, the artifacts. -->
1. [`demo/example_output.txt`](demo/example_output.txt) — the demo output without running anything.
2. ...

## The real problem
<!-- the non-obvious engineering problem (not "chat with X"). -->

## My role
<!-- first person. DRAW THE BOUNDARY: what you designed/built vs off-the-shelf (model/lib/service) vs AI-assisted.
     A one-line "what I did NOT build" is encouraged. -->

## Evidence in this case study
| File | What it is |
|------|-----------|
| [architecture.md](architecture.md) | ... |
| [<core-decision>.md](#) | the signature decision + when I'd scale it |
| [<main-flow>.md](#) | the loop, annotated with real numbers |
| [reliability-and-evaluation.md](reliability-and-evaluation.md) | reliability mechanisms + eval summary |
| [EVALUATION.md](EVALUATION.md) | case matrix incl. the negative case + faithfulness mapping |
| [the-bug-i-fixed.md](the-bug-i-fixed.md) | a real failure and the fix |
| [artifacts/](artifacts/) | real, sanitized outputs |
| [demo/](demo/) | offline demo (not the full engine) |

## What is real / replayed / simulated
<!-- copy these rows from spec §5 and adapt the notes to this case. -->
| Element | Status | Note |
|---|---|---|
| artifacts (state/traces/logs) | **Real** (sanitized) | actual outputs; only identifiers/labels changed |
| funnel + cost/latency/token metrics | **Real, replayed** | read verbatim from recorded traces |
| the demo's live step | **Simulated** | deterministic stand-in for the real step, offline |
| non-demo model steps | **Not run in the demo** | represented only by recorded metrics |
| code constants / tool names / the bug | **Real** | from the actual codebase |

## Stack
<!-- concrete libs/models/services. Mark ACTIVE vs present-but-disabled-by-design; must not contradict <core-decision>. -->

## Status
<!-- maturity label (§0) + the single top open item. -->

## Contact
<!-- name/brand, email, ≥1 profile link — or link to the root README contact. Keep identity consistent. -->

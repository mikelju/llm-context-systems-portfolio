# Lessons Learned

## 1. Draw the LLM boundary first; it makes everything else fall out

Deciding up front that the model does **only** two things (select documents, answer) turned the rest of
`WF-DocBot-Tool` into 17 deterministic nodes I could reason about individually. On a visual platform that
is the difference between a debuggable canvas and a black box — and it's why cost is bounded to two model
calls per query, not "however many the agent felt like". The boundary is the architecture.

## 2. At 15 small visual documents, a vector store is the wrong default

The instinct for "RAG" is chunk → embed → vector search. Here it would have *lost* information (the
answers live in diagrams the text extractor drops) and added an embeddings API plus an index to keep in
sync with Drive — for a corpus the model can just read whole. I'd built the vector-store version for a
prior client (ClientA) and watched it become four near-duplicate subgraphs. Match the machinery to the
scale; write down the trigger (page count, query volume, re-read waste) at which the answer flips.

## 3. "The model always returns something" is the assumption that bit me

The [empty-`candidates[]` bug](the-bug-i-fixed.md) only appeared once real technician phrasing tripped a
Gemini safety filter. Every external boundary — Drive, the File API, *and the model* — can return
nothing, and on n8n an unguarded dereference becomes a useless "Unknown error". Now every model read uses
optional chaining and an empty response routes into the existing refuse path.

## 4. The File API is asynchronous — uploading is not "ready"

A freshly uploaded PDF can still be `PROCESSING`; querying its handle too early fails. The fix was a poll
loop (`Wait` → `Check File API state` → `IF - ACTIVE?`) with a **30-second absolute timeout** so a stuck
upload fails cleanly instead of hanging the execution forever. "Call the API" is two states, not one.

## 5. Grounding is a prompt rule *plus* a structural path, never just a prompt

The agent prompt says "never answer from your own knowledge" — but the audit (SEC-210) correctly flagged
that a prompt alone is not a guarantee. What actually enforces it is the **structure**: the agent must
call the tool, and `IF - Any documents?` makes "no document" a different branch from "answer". Belt
(prompt) and braces (control flow).

## 6. Integrating into a live system is a constraint, not a footnote

FieldBot was already in production and trusted; DocBot had to attach without disturbing it. That dictated
real choices: reuse the existing auth and output pipeline, keep FieldBot's agent unchanged, store the
per-user mode in Static Data, and treat "don't break the working bot" as a first-class requirement (the
project's `CLAUDE.md` lists modifying FieldBot as *ask-first*). The menu/router exists because of this
constraint.

## 7. Reduce what you retain, then live with the gap honestly

We cut n8n execution retention for privacy (SEC-208) — the right call — which is exactly why this case
has **no per-query token/latency trace**. I'd rather ship that gap declared than back-fill an invented
number. Next time I'd add a **redacted** metrics sink (tokens, latency, selected-doc count, no query
text) so privacy and measurability aren't in tension.

## What I'd do next

- Fix the one failing case (**P7**, the misread maintenance table) and add it as a regression test.
- Stand up the automated scorer from [EVALUATION.md](EVALUATION.md) (selection precision/recall +
  citation faithfulness) and run it before every prompt change.
- Apply SEC-201 (delimit the user query in the Gemini prompts) and SEC-202 (validate `catalog.json`
  after parse) before a wider rollout.
- Add a privacy-safe metrics sink so the cost/latency gap closes for the next case.

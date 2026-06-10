# A Real Bug I Fixed — Gemini returned no `candidates`, and the tool crashed with "Unknown error"

## Symptom

Intermittently, a technician's question came back not as an answer and not as a clean refusal, but as a
raw n8n failure: the `WF-DocBot-Tool` execution went red with **"Unknown error"** in the task runner.
No citation, no "I don't have that document" — just a broken bot. It only happened on *some* queries,
which made it look random.

## Root cause

Two of the tool's Code nodes read the Gemini response like this:

```js
const responseText = $json.candidates[0].content.parts[0].text;
let parsed;
try { parsed = JSON.parse(responseText); } catch (e) { parsed = { selected_ids: [] }; }
```

The `try/catch` guards `JSON.parse` — but the crash was *upstream of it*. Gemini does not always return a
candidate: when its **safety or recitation filter** fires (which real, varied technician phrasing
triggers sometimes), the response is `{ "candidates": [] }`. Then `candidates[0]` is `undefined`,
`.content` throws a `TypeError`, and because that throw is **outside** the `try`, it surfaced as n8n's
generic "Unknown error". The code had assumed the model always answers — an assumption only messy real
inputs disprove. (Logged as **SEC-205** in the Phase-2 security audit.)

## The fix

Guard the access with optional chaining and turn the empty case into a real, friendly outcome —
in both `Code - Evaluate selection` and `Code - Format response`:

```js
const responseText = $json.candidates?.[0]?.content?.parts?.[0]?.text || '';
if (!responseText) {
  return [{ json: { noResults: true, query,
    respuesta: 'No pude procesar la respuesta del modelo. Reformula la pregunta o reinténtalo.' } }];
}
let parsed;
try { parsed = JSON.parse(responseText); } catch (e) { parsed = { selected_ids: [] }; }
```

An empty `candidates[]` now flows into the **same refuse path** as "no relevant document" (`IF - Any
documents?` → `Code - No results`) instead of throwing.

## Result

A filtered/empty model response now degrades into a graceful message the technician can act on, not a red
execution. It folds the failure into the system's existing negative-case behaviour (refuse, don't guess),
so the bug fix and the [off-topic refusal](EVALUATION.md#the-negative-case-recorded) share one code path.

## Why it's a good story

It is the classic gap between a happy-path integration and a real one: the model *usually* returns a
candidate, so the bug is invisible in testing and only appears once real users phrase things in ways that
trip a safety filter. The fix is small, but the judgment is the point — **every external boundary (a
model included) can return nothing, and "nothing" must have a defined, friendly path**, not an
uncaught dereference. It also shows the value of the security audit catching a *reliability* bug, not
just a security one.

# A real finding I fixed — SEC-003: unbounded query → cost/DoS

Not a crash — a **security finding** from the project's own audit. It's the better kind of "bug" for
a public, paid-API endpoint: cheap to exploit, easy to miss, trivial to close once seen.

## Symptom

`POST /consultar` accepted a `query` of **any length**. A request with an arbitrarily large body was
embedded (cost proportional to size) **and** concatenated into the vision-LLM prompt — amplifying the
cost/DoS exposure of an endpoint that (per SEC-001) is public and unauthenticated.

## Root cause

The Pydantic model declared `query: str` with **no length bound** (`server.py`), so nothing capped the
input before the two paid calls (`embed_text`, `generate_content`).

## Why it mattered

Combined with the public, no-auth endpoint (SEC-001, High), an attacker maximizes damage **per
request**: one big query = one oversized embedding + one oversized vision prompt = real money.

## The fix

```python
# server.py
class Consulta(BaseModel):
    query: str = Field(min_length=1, max_length=2000)   # was: query: str
```

FastAPI now rejects an empty or oversized query with **422 at the input layer — before any API call is
made**. Legitimate technician questions sit far below 2000 chars, so there's zero UX cost.

## Result

Closed SEC-003. Two regression tests added (`tests/test_server.py`: empty query → 422, `>2000` chars →
422), part of the 22-test suite.

## Why it's a good story

It shows the project was treated like a real service, not a toy: it got a **written security audit**
(CWE-770 / CWE-400) and the response was a **minimal, validated, tested** change at the right layer —
plus an explicit, documented decision to defer the deeper High finding (SEC-001) while the PoC is
frozen, rather than pretend it's production-safe.

# Reliability and Evaluation

## Reliability mechanisms (in the real system)

| Mechanism | Where | Why |
|---|---|---|
| Retry + exponential backoff on embedding calls | `prueba.py` (`embed_with_retry`) | 429 quota / 5xx / network errors are normal; only the permanent 4xx (400/401/403/404/413) are not retried |
| Resumable indexing | `prueba.py` (`build_index`) | A run cut off by a quota error resumes from the next page; nothing re-embedded (content-hash cache) |
| Atomic cache writes | `prueba.py` (`_save_cache`: tmp + `os.replace`) | The 43 MB cache can't be corrupted by an interrupted write |
| Load-only server | `server.py` (`load_index`) | Boots from the cache without any API call, so a quota outage can't take the endpoint down |
| Query length bound | `server.py` (`Field(max_length=2000)`) | Caps cost/DoS — see [the-bug-i-fixed.md](the-bug-i-fixed.md) |
| UTF-8 stdout on Windows | `server.py` | Logs the full (accented) answer without `charmap` crashes |
| Test suite | `tests/` (22 tests) | Regression cover incl. the SEC-003 query-length fix |

## Security audit (real)

The PoC's public endpoint was audited (`/8-auditar`, 2026-06-01): **0 Critical / 1 High / 2 Medium /
2 Low**. Summary: [`artifacts/security-audit-summary.md`](artifacts/security-audit-summary.md).

- **SEC-001 (High)** — `/consultar` is public with no auth / rate limiting; anyone who finds the ngrok
  URL spends paid API quota. **Consciously deferred**: the PoC is frozen awaiting client validation and
  the ngrok URL is ephemeral; the shared-secret + rate-limit (DEF-001) ships before any stable deploy.
- **SEC-002 (Medium)** — `pickle.load` of the cache is an RCE vector (CWE-502); closed at Phase 3 by
  replacing pickle with pgvector + JSON.
- **SEC-003 (Medium)** — unbounded `query` length; **fixed** (see the bug write-up) + 2 regression tests.
- **SEC-004/005 (Low)** — plaintext Q&A logging, silent `try/except/pass`; backlog.

That a frozen PoC got a written audit with CWE/OWASP tags and an explicit risk-acceptance decision is
itself the point: security posture was a deliberate, documented choice, not an afterthought.

## How I evaluate

The recorded nearest-neighbour results ([retrieval-flow.md](retrieval-flow.md)) show the embedding
space clusters by model/topic — qualitative evidence the retrieval works. The **case matrix** and the
pending labelled-eval plan are in **[EVALUATION.md](EVALUATION.md)**.

Honest gap: there is **no labelled query→expected-page set yet**, and natural-language `/consultar`
runs were not archived. The whole project is, by design, **blocked on the client validating retrieval
quality** with this preview embedding model — that validation *is* the next evaluation step.

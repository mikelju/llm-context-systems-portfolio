# Security audit — summary (real, sanitized)

Audit of the PoC (`/8-auditar`, 2026-06-01). Severity: **0 Critical / 1 High / 2 Medium / 2 Low**.
Client/bot identity removed; findings, CWE tags and decisions are the real ones.

| ID | Sev | Component | Finding | Status |
|----|-----|-----------|---------|--------|
| **SEC-001** | High | `/consultar` (public) | No auth / no rate limiting (CWE-306 + CWE-770): anyone who finds the tunnel URL spends paid API quota. | **Deferred (conscious)** — PoC frozen pending client validation; URL ephemeral; DEF-001 (shared secret + rate limit) before any stable deploy |
| **SEC-002** | Medium | `prueba.py` / `server.py` | `pickle.load` of the cache is an RCE vector (CWE-502) if the `.pkl` is attacker-writable. | Closed at Phase 3 (pgvector + JSON; never load external `.pkl`) |
| **SEC-003** | Medium | `/consultar` | `query` had no length bound → cost/DoS amplification (CWE-400/770). | **Fixed** — `Field(max_length=2000)` + 2 regression tests |
| **SEC-004** | Low | logging | Full question + answer logged in clear. | Backlog |
| **SEC-005** | Low | `server.py` | Silent `try/except/pass` around stdout reconfigure. | Backlog |

**Defense-in-depth:** DEF-001 (shared secret + rate limit on `/consultar`), DEF-002 (replace pickle as
the interchange format). **Not reviewed:** the n8n-side orchestration (the agent, Telegram sanitization,
the HTTP tool) lives outside this repo — the SEC-001 secret must be added there too.

> The point: a frozen PoC still got a written audit with CWE/OWASP tags and an explicit risk-acceptance
> decision — security as a documented choice, not an afterthought.

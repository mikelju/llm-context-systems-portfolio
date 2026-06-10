# Security audit summary — Phase 2 (document querying)

Sanitized summary of the real security audit run on the DocBot query path (WF-DocBot-Tool + the
DocBot agent) on **2026-04**. Method: manual review of the 7 JavaScript Code nodes and 4 HTTP nodes,
plus the agent's system prompt, against OWASP Top 10 + OWASP LLM Top 10.

**Verdict:** 0 Critical, 0 High, 2 Medium, 4 Low, 4 Info. The phase could close; SEC-201 and SEC-202
recommended before a wider rollout.

| ID | Severity | Title | Where |
|----|----------|-------|-------|
| SEC-201 | Medium | Prompt injection via the user query (concatenated into the Gemini prompts without delimiters) | `Code - Build selection prompt`, `Code - Build Gemini body` |
| SEC-202 | Medium | `catalog.json` parsed with no structure/content validation after `JSON.parse` | `Code - Parse catalog` |
| SEC-203 | Low | Indirect prompt injection via PDF content sent to Gemini | `Code - Build Gemini body` |
| SEC-204 | Low | No timeout on the 4 Gemini HTTP calls (`options: {}`) | the 4 HTTP nodes |
| SEC-205 | Low | Gemini response accessed without optional chaining (empty `candidates[]` → uncaught TypeError) | `Code - Evaluate selection`, `Code - Format response` |
| SEC-206 | Low | No length cap on the user query (token-cost amplification) | `Code - Parse catalog` |
| SEC-207 | Info | Gemini API key sent as a URL query string (standard for the API; HTTPS-encrypted) | the 4 HTTP nodes |
| SEC-208 | Info | User queries persist in n8n execution history (retention reduced as mitigation) | n8n Cloud config |
| SEC-209 | Info | Static Data used to pass File-API URIs between Code nodes (race under concurrency) | `Code - Init poll`, `Code - Build Gemini body` |
| SEC-210 | Info | "Never answer from own knowledge" enforced only by the system prompt | DocBot agent `systemMessage` |

**Threat model.** Internal authenticated technicians (Supabase auth) over Telegram. No public
endpoint, no public frontend. Confidentiality impact of most findings is low (every document is
visible to every technician by design); the real concern is integrity (an altered answer could drive a
wrong field decision) — hence SEC-201/202 are the ones worth hardening.

**Note on SEC-205** — this is the finding the case's [the-bug-i-fixed.md](../the-bug-i-fixed.md)
expands: Gemini occasionally returns an empty `candidates[]` (safety/recitation filter), and the
original code dereferenced `candidates[0].content...` directly, surfacing a confusing "Unknown error"
to the technician.

*Findings sanitized; node names translated. Severities, counts and IDs are the real audit's.*

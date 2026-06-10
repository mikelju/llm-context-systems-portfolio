# The agent loop — Sequence

Step numbers match [agent-loop.md](../agent-loop.md), the README and `demo/run_demo.py`.

```mermaid
sequenceDiagram
    autonumber
    actor T as Technician (Telegram)
    participant R as Router (WF-Principal)
    participant A as DocBot agent (+memory)
    participant TL as WF-DocBot-Tool
    participant G as Gemini (Flash + File API)
    participant D as Google Drive

    T->>R: question (DocBot mode)
    Note over R: Step 1 — route by per-user mode (Static Data), deterministic
    R->>A: hand message to the agent
    Note over A: Step 2 — tool-first: must call the tool
    A->>TL: consultar_biblioteca(question)
    TL->>D: read catalog.json (15 docs)
    TL->>G: Step 3 — SELECT relevant docs  (model call 1/2)
    alt no relevant document
        TL-->>A: Step 6 — no results → refuse
    else documents selected
        loop each selected PDF — Step 4 (io)
            TL->>D: download PDF
            TL->>G: upload (File API) + poll until ACTIVE (30s timeout)
        end
        TL->>G: Step 5 — ANSWER from full PDFs  (model call 2/2)
        G-->>TL: answer + document/page citations
        TL-->>A: formatted answer
    end
    Note over A: Step 6 — Think (sufficient?) → emit {respuesta, conversation_ended}
    A-->>T: answer with citations (or clean refusal), split for Telegram
    Note over A,G: model touched exactly twice per answered query (Steps 3 + 5)
```

Recorded runs (tool-path vs refuse-path) and the honest metric gap:
[`artifacts/query-runs.json`](../artifacts/query-runs.json).

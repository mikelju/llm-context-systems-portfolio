# The request flow — Sequence

Step numbers match [request-flow.md](../request-flow.md), the README and `demo/run_demo.py`.

```mermaid
sequenceDiagram
    autonumber
    actor T as Technician
    participant FE as React UI
    participant API as FastAPI (Cloud Run)
    participant W as whisper-1
    participant G as gemini-2.5-flash
    participant DB as Supabase (pgvector HNSW)
    participant ERP as ERP-X

    T->>FE: Step 1 - record/upload audio
    FE->>API: process-audio (JWT)
    API->>W: Step 2 - transcribe
    API->>G: Step 3 - extract order JSON (retry x3, backoff 2s·attempt)
    Note over API,DB: warmup query fires here - HNSW warms while the human reads

    par one task per dictated line (asyncio.gather, semaphores LLM=10 / DB=10)
        API->>DB: Step 4 - buscar_historicos (memory, thr 0.75)
        API->>DB: Step 4 - buscar_articulos (catalog, thr 0.5, top 25, CTE x3)
        API->>G: Step 5 - re-rank candidates
        Note over API: LLM fails? deterministic fallback:<br/>sort (Historical_match desc, Score desc)
    end

    API-->>FE: ranked options per line
    T->>FE: Step 6 - review, edit, confirm (HITL)
    FE->>API: finalize + send

    par three independent channels
        API->>ERP: Step 7a - order to ERP-X
        API->>API: Step 7b - PDF + O365 email (cutoff 14h)
        API->>DB: Step 7c - historico upsert (memory++)
    end
    API-->>FE: per-channel status lights
```

Real recorded run for Steps 2–3: the 21-line dictated order in
[`artifacts/extraction-examples.json`](../artifacts/extraction-examples.json). Per-request latency was
not archived — see [../EVALUATION.md](../EVALUATION.md).

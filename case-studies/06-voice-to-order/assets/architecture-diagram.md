# Architecture Diagram

```mermaid
flowchart TD
    T[Technician - phone browser] --> FE[React multi-step UI\nNetlify]
    FE -->|JWT| API[FastAPI backend\nCloud Run - Docker, VPC + static IP]

    subgraph API_FLOW[Per order]
        TR[transcription_service\nwhisper-1] --> EX[order_processing_service\ngemini-2.5-flash · retry x3]
        EX --> SR[search_service\nasyncio.gather - 1 task per line]
    end

    subgraph SEARCH[Per line · semaphores LLM=10 / DB=10]
        H[buscar_historicos\nmemory first · thr 0.75] --> C[buscar_articulos\ncatalog · thr 0.5 · top 25]
        C --> RR[re-rank gemini-2.5-flash\nfallback: sort by match+score]
    end

    SR --> SEARCH
    SEARCH --> REV[Step 6 - human review\nedit / add / delete / decimals]

    REV --> D1[ERP-X API]
    REV --> D2[PDF + O365 email\ncutoff 14h]
    REV --> D3[historico upsert\nthe learning loop]

    DB[(Supabase\ncatalogo 31,070 · embeddings HNSW\nhistorico 1,001 · Auth/RLS)]
    H -.-> DB
    C -.-> DB
    D3 -.-> DB
    SYNC[GitHub Actions - nightly\nERP-X catalog + embeddings sync] -.-> DB

    style D1 fill:#fdd
    style D2 fill:#dfd
    style D3 fill:#ddf
```

The three delivery channels (bottom) fail independently — each has its own status light and its own
`SIMULATE_FAILURE` injection point ([`artifacts/chaos-degradation.json`](../artifacts/chaos-degradation.json)).

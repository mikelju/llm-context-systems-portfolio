# Retrieval — Sequence

```mermaid
sequenceDiagram
    autonumber
    actor T as Technician (Telegram)
    participant N as DocBot (n8n)
    participant S as server.py (/consultar)
    participant M as Gemini (embed + vision)

    T->>N: question
    N->>S: POST /consultar {query}
    S->>M: embed_text(query)            %% gemini-embedding-2, 1536-dim
    M-->>S: query vector
    S->>S: cosine top-5 over 6,896 page vectors   %% sub-millisecond, deterministic
    S->>M: 5 labelled page IMAGES + ask for JSON {answer, pages}
    M-->>S: {respuesta, paginas}
    S-->>N: answer + SOURCE PAGE IMAGE url + candidates + timings + tokens
    N-->>T: answer + the page photo

    Note over S: deterministic core (cosine) runs offline in the demo;<br/>embed + vision steps need the live API
```

# Retrieval Sequence — "The Librarian"

The 4-step query funnel, annotated with the real numbers from **Run B** (the cross-document
*"safety measures"* query). Source: [`../artifacts/query-trace.safety.json`](../artifacts/query-trace.safety.json).

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant L as The Librarian<br/>(query_library.py)
    participant C as Catalog
    participant KB as knowledge_base
    participant M as Gemini<br/>(Flash / Pro / Vision)

    U->>L: "What safety measures do the manuals require?"
    L->>C: Step 1 — filter catalog by title/summary/tags
    C-->>L: 5 candidate documents
    L->>KB: Step 2 — inspect indexes of candidates
    KB-->>L: 4 confirmed · 9 candidate chapters
    L->>M: Step 3 — select chapters (Flash)
    M-->>L: 8 chapters selected
    L->>KB: read the 8 selected chapters (text / page-images)
    KB-->>L: chapter content
    L->>M: Step 4 — synthesize from selected evidence (Pro)
    M-->>L: answer + needs_more_info = false
    L-->>U: grounded answer + 8 source references

    Note over L,M: 1 iteration · 7 API calls · 88.5 s<br/>37,898 in + 6,793 out = 44,691 tokens
```

Run A (single 59-chapter book, *"power zones"*) follows the same path with a narrower funnel:
1 → 1 document, 6 → 5 chapters, 6 API calls, 73.7 s, 52,786 tokens. See
[`../retrieval-flow.md`](../retrieval-flow.md) for both side by side.

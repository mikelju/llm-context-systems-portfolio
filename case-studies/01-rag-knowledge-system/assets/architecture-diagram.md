# Architecture Diagram

Ingestion (run once, offline) on the left; query path (per question) on the right. Strategy is
chosen by document size: `FULL_CONTEXT_MAX_PAGES = 80`.

```mermaid
flowchart TD
    subgraph IN[Ingestion — once per document]
        A[Input documents<br/>PDF native/scanned, Word, Excel, PPT, images] --> B[Type detection]
        B --> C[Structure extraction<br/>native TOC → heuristics → Vision]
        C --> D[Chapter content extraction]
        C --> E[Visual extraction + descriptions]
        D --> F[Summaries + tags]
        E --> F
        F --> G[(catalog.json<br/>+ knowledge_base/&lt;id&gt;)]
        E2[Embeddings phase<br/><i>disabled by design</i>] -.-> G
    end

    subgraph Q[Query — "The Librarian"]
        H{Strategy?<br/>pages ≤ 80?}
        H -->|small / visual| I[Full-context route<br/>send whole document]
        H -->|large / complex| J[Hierarchical route]
        J --> K[Step 1: catalog filtering]
        K --> L[Step 2: index inspection]
        L --> M[Step 3: summary/visual filter → selective read]
        M --> N[Vision reading when a page is visual]
        I --> O[Step 4: LLM synthesis]
        N --> O
        O --> P[Answer + traceable references]
        O --> R[Optional expanded PDF report]
    end

    G --> H

    classDef disabled fill:#eee,stroke:#999,stroke-dasharray:4 3,color:#666;
    class E2 disabled;
```

> The embeddings phase exists in code but is intentionally disabled: retrieval is metadata-first
> (catalog + LLM selection), not vector-similarity. See [../context-strategy.md](../context-strategy.md).

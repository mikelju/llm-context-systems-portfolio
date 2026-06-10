# Architecture Diagram

The boundary in colour: blue = deterministic n8n nodes, red = the 2 model calls, grey = io.

```mermaid
flowchart TD
    TG[Telegram message] --> R{{WF-Principal router\nmenu + Switch + Static Data}}
    R -->|FieldBot mode| FB[FieldBot agent\n interventions — unchanged]
    R -->|DocBot mode| AG[DocBot agent\nGPT-4.1-mini + window memory]

    AG -->|tool-first| TOOL[consultar_biblioteca\nWF-DocBot-Tool]

    subgraph TOOL_FLOW[WF-DocBot-Tool · 2 model calls, the rest deterministic]
        PC[Code - Parse catalog] --> SP[Code - Build selection prompt]
        SP --> SEL[[HTTP - Gemini SELECT docs]]
        SEL --> EV[Code - Evaluate selection]
        EV --> IF{IF - Any documents?}
        IF -->|no| NR[Code - No results → refuse]
        IF -->|yes| LOOP[Loop - Selected PDFs]
        LOOP --> DL[Drive - Download PDF]
        DL --> UP[(HTTP - Gemini UPLOAD · File API)]
        UP --> POLL[(Wait + Check state → IF ACTIVE?\n30s timeout)]
        POLL --> BODY[Code - Build Gemini body]
        BODY --> ANS[[HTTP - Gemini ANSWER · full context]]
        ANS --> FMT[Code - Format response]
    end

    TOOL --> PC
    FMT --> AG
    NR --> AG
    AG --> THINK[Think → emit JSON\nanswer w/ citations or refuse]
    THINK --> OUT[Split over 4096 chars → Telegram]

    CAT[(catalog.json on Drive\n15 docs)] -.read.-> PC
    PROC[WF-Procesado\nDrive trigger → File API analysis] -.writes.-> CAT
```

Legend: `[[ ]]` = the **2 LLM judgment calls** · `( )` = io / File API · `{{ }}` `{ }` = deterministic
routing. Full per-node boundary table:
[`artifacts/tool-structure.json`](../artifacts/tool-structure.json).

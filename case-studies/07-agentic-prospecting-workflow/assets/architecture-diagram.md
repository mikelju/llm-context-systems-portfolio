# Architecture Diagram

```mermaid
flowchart TD
    U[User: prospect this company]
    U --> W[prospeccion_empresa.md\nmaster workflow: order + dependencies]

    subgraph AGENT[Agent layer - judgment]
        C[search_protocols/CLAUDE.md\nthe anti-hallucination contract\nauto-loaded for every protocol]
        P1[01 identification\nresolves the identity everything else interpolates]
        PAR[02 financial · 03 employees\n05 profile · 07 news\nparallel]
        P4[04 admin department\nneeds employee data]
        P6[06 competitors\nneeds sector]
        P8[08 contacts\nlast: reuses names seen earlier]
        BR[browser.py - Playwright\nvisual fallback when a fetch is blocked]
        P1 --> PAR --> P4 --> P6 --> P8
        BR -.fallback.-> P4
        BR -.fallback.-> P8
    end

    W --> AGENT
    C -.governs.-> P1
    C -.governs.-> PAR
    C -.governs.-> P8

    AGENT --> J[(8 research JSON per company\nevery figure carries\nsource · url · date · reliability\nnot found = explicit null)]

    subgraph CODE[Deterministic layer - guarantees]
        V[validate_data.py\nrequired fields present?\ncompleteness %]
        G{{">= 80% ready\n>= 50% partial\nbelow: insufficient"}}
        R[generate_report.py\npdf_builder · excel_builder]
        V --> G --> R
    end

    J --> CODE
    R --> OUT[(27 PDF · 27 Word · 23 Excel)]
    CRM[google_sheets.py\nwrite path never enabled]:::off
    OUT -.- CRM

    classDef off fill:#eee,stroke:#999,stroke-dasharray: 5 5,color:#666
    style C fill:#e8f5e9
    style G fill:#e3f2fd
    style BR fill:#fff3e0
```

**Green** is the contract — it governs every protocol because it lives in the protocols' own folder,
not in a prompt someone has to remember. **Blue** is the gate: dumb arithmetic over field presence,
deliberately sharing none of the failure modes of the layer it judges. **Orange** is the fallback
that exists because the sources holding people data refuse automated fetches.

The greyed box is real and deliberately inert: the CRM integration was built but its write path was
never switched on, so nothing automated has ever modified the real CRM.

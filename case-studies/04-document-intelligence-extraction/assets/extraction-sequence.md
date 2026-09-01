# Extraction Sequence

```mermaid
sequenceDiagram
    autonumber
    participant QE as Quality engineer
    participant SC as Schema (293 fields)
    participant LIB as The Librarian\n(page catalog)
    participant V as Gemini Vision
    participant COV as analyze_coverage.py
    participant XL as Output workbook

    QE->>SC: flatten the 11-tab inspection record
    SC-->>SC: 293 fields · 212 numeric / 81 boolean
    Note over SC,V: 12 GD&T tolerances cache as #VALUE! - the value exists only as pixels
    SC->>V: TARGETED - read these 12 named cells (3 focused calls)
    V-->>SC: 12 of 12 resolved · tagged tolerance_source = vision

    Note over LIB,V: Phase 2 - the document has not been consulted yet
    loop 134 pages, batches of 3 x 4 workers (resumable)
        LIB->>V: BLIND - what is on this page?
        V-->>LIB: document_type · text · tables · measurements · certificates
    end
    LIB-->>LIB: 134 of 134 read, 0 failed, 46 calls, ~9 min

    loop for each of the 293 fields
        SC->>LIB: which page(s) could answer this field?
        LIB-->>SC: candidate pages (or none)
        SC->>V: focused extraction against those pages
        V-->>SC: value, or nothing
    end

    SC->>COV: every field, present/absent x extracted/empty
    COV-->>QE: 72 correct · 36 missed · 32 invented · 153 correctly empty
    Note over COV,QE: precision 69% · recall 67% · specificity 83%\n185 of 293 fields are not in this report at all

    SC->>XL: write one workbook per part (3 parts, 175 of 293 cells)
    XL-->>QE: Excel's own formulas compute OK/NOK · 0 out of tolerance
    Note over QE,XL: Phase 6 would insert a green/amber/red human approval here - it does not exist yet
```

The two Vision interactions are deliberately drawn differently. The **targeted** one names its
fields and resolves 12 of 12. The **blind** one reads every page and succeeds at reading — but the
values still have to be matched back to fields afterwards, and that later matching step is where all
32 false positives are produced. Knowing the schema before asking the question is the difference.

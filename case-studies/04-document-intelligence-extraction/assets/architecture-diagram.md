# Architecture Diagram

```mermaid
flowchart TD
    XL[(Client inspection record\n11 tabs · Excel)]
    PDF[(Manufacturer report\n134 scanned pages · bilingual)]

    subgraph P1[Phase 1 - flatten the target]
        R1[render_excel_sheets.py\npywin32 COM to PDF to PNG\n23 sheet images]
        F1[flatten_excel.py\nopenpyxl data_only\n293 fields · 212 num / 81 bool]
        E1[enrich_schema_vision.py\nTARGETED Vision · 12 broken cells\ntolerance_source = vision]
        R1 --> F1 --> E1
    end

    subgraph P2[Phase 2 - read the document]
        R2[render_pdf_pages.py\n134 pages at 200 DPI]
        X2[extract_pdf_pages.py\nBLIND Vision · batch 3 x 4 workers\nresumable checkpoint · 46 calls]
        R2 --> X2
    end

    subgraph P3[Phase 3 - the Librarian]
        C3[build_page_catalog.py\nindex the 134 page extractions]
        M3[map_schema_to_pages.py\nfield to candidate pages]
        X3[extract_matched_data.py\nfocused per-tab extraction\npieces + common_data]
        C3 --> M3 --> X3
    end

    subgraph P4[Phase 4 - close the loop]
        A4[analyze_coverage.py\nconfusion matrix over 293 fields]
        W4[write_to_excel.py\none workbook per part]
    end

    XL --> P1
    PDF --> P2
    E1 -->|the schema| M3
    X2 -->|page extractions| C3
    X3 --> A4
    X3 --> W4
    W4 --> OUT[(3 filled workbooks\n175 of 293 cells each\nExcel formulas compute OK/NOK)]
    A4 --> Q[[precision 69% · recall 67%\nspecificity 83%]]

    style E1 fill:#e8f5e9
    style X2 fill:#fff3e0
    style A4 fill:#e3f2fd
```

**Green** is the targeted Vision run, **orange** the blind one — the same model asked two different
questions, with opposite failure profiles ([../the-bug-i-fixed.md](../the-bug-i-fixed.md)). **Blue**
is the step that makes the whole thing measurable rather than merely finished: nothing is "done"
until the coverage matrix classifies every one of the 293 fields.

Deterministic stages (rendering, cataloguing, the coverage arithmetic, the Excel write-back) are
separated from the two model-driven stages on purpose; the model reads, the code decides.

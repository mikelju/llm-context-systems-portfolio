# Workflow Sequence

```mermaid
sequenceDiagram
    autonumber
    participant S as Salesperson
    participant A as Agent (protocols)
    participant W as Public web
    participant B as browser.py
    participant J as Research JSON
    participant V as validate_data.py
    participant D as Deliverable

    S->>A: prospect this company
    A->>W: protocol 01 - legal identity
    W-->>A: filings, directory entries
    A->>J: identity + source, url, date, reliability
    Note over A,J: every later protocol interpolates this identity<br/>running out of order researches the wrong company, silently

    par protocols 02, 03, 05, 07
        A->>W: financials, headcount, profile, news
        W-->>A: results, or nothing
        A->>J: values found, or explicit null
    end

    A->>W: protocol 04 - who works in administration
    W-->>A: HTTP 999 - automated access refused
    A->>B: screenshot the page instead
    B-->>A: image of a page that renders fine for a human
    A->>J: what was SEEN, with its url

    A->>W: protocol 08 - reachable contacts
    Note over A,J: a profile seen in a result is recorded<br/>a profile deduced from a name is forbidden
    A->>J: 39 of 54 slots filled - 15 left empty

    J->>V: all 8 protocol files
    V-->>V: required fields present? completeness %
    alt >= 80%
        V->>D: ready - generate the report
    else >= 50%
        V->>D: partial - generate, visibly thinner
    else < 50%
        V-->>S: insufficient - complete the protocols first
    end
    D-->>S: PDF + Word + Excel, every figure carrying its source
```

The two moments that define this workflow are steps 8–11 and the `alt` block. In the first, the
deterministic route fails and the agent is given sight rather than permission to guess. In the
second, a piece of arithmetic that knows nothing about companies decides whether a human should act
on what the agent produced.

# Context Strategy

## Problem

Large document repositories create a context-selection problem:

- sending all documents is expensive or impossible;
- naive vector search can miss tables, diagrams or cross-document context;
- chunking can destroy structure;
- some documents are better handled as complete documents;
- some questions require selective reading across several sources.

## Strategy

The system uses a dual strategy:

### 1. Full-context strategy

Used for smaller documents where sending the full document is feasible.

Best for:

- short manuals;
- visually rich documents;
- documents where chunking may lose context;
- cases where simplicity and visual fidelity matter.

### 2. Hierarchical strategy

Used for large, tabular or complex documents.

The system progressively narrows context:

```text
catalog → document index → summaries/tags → selected chapters/pages → LLM synthesis
```

Best for:

- long documents;
- multi-chapter manuals;
- repositories with many files;
- questions requiring targeted evidence;
- cost-sensitive queries.

## Key tradeoff

The goal is not to always minimize context. The goal is to choose the cheapest context strategy that preserves answer quality.

Sometimes full-context is better. Sometimes hierarchical retrieval is better. The system makes this an architectural decision rather than a fixed assumption.

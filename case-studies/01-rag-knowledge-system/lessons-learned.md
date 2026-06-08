# Lessons Learned

## 1. RAG is mostly a context-selection problem

The hardest part is not calling the LLM. The hard part is deciding what information should be placed in context.

## 2. Chunking is not always the right abstraction

For technical documents, tables, diagrams and scanned pages, chunking can destroy important structure. Page-level visual reading and full-context strategies can be better.

## 3. Metadata matters before embeddings

Metadata, summaries and tags can reduce the search space before expensive semantic or visual retrieval.

## 4. Full-context can be the best strategy for small documents

For small manuals, sending the entire document can be simpler and more reliable than building a complex vector pipeline.

## 5. Hierarchical retrieval is useful for scale

Large repositories require progressive narrowing: catalog, index, summaries, chapters, pages, synthesis.

## 6. Cost and latency need to be first-class metrics

A useful RAG system should expose timing, API calls and token usage. Otherwise, it is hard to improve systematically.

# Architecture

## Architectural pattern

The system follows a WAT architecture:

- **Workflows** define the high-level process.
- **Agents / LLM calls** coordinate reasoning, filtering and synthesis.
- **Tools** execute deterministic operations: parsing, rendering, extraction, embedding generation, state management and catalog building.

## Main components

### Document processing pipeline

1. Detect document type.
2. Extract document structure.
3. Extract chapter-level content.
4. Extract and describe visual elements.
5. Generate summaries.
6. Generate tags.
7. Generate embeddings.
8. Build a searchable catalog.
9. Store processing state for resumable execution.

### Knowledge base

Each processed document generates structured artifacts:

- global metadata;
- chapter index;
- chapter summaries;
- tags;
- visual descriptions;
- embeddings;
- rendered pages when needed;
- catalog entry.

### Query system

The query system uses a staged retrieval process:

1. Select potentially relevant documents from the catalog.
2. Inspect indexes and summaries.
3. Select chapters or pages.
4. Read only the most relevant content.
5. Use the LLM for final synthesis.
6. Optionally expand the answer into a report with figures.

## Design principle

The LLM should not receive everything. It should receive the smallest useful context that preserves enough evidence to answer reliably.

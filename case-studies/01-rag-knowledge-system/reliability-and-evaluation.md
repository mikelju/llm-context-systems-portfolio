# Reliability and Evaluation

## Reliability mechanisms

The system includes several reliability-oriented decisions:

- retry and exponential backoff for LLM calls;
- resumable document processing;
- thread-safe state management;
- filtering of low-value chapters;
- selective Step 1 filtering to avoid over-including documents;
- page deduplication with hashes in full-context queries;
- task-specific model selection;
- query metrics for cost and latency analysis.

## Evaluation plan

The system should be evaluated with three types of questions:

1. Questions answered inside a single document.
2. Questions requiring evidence across multiple documents.
3. Questions with no answer in the library.

## Main evaluation dimensions

- retrieval precision;
- retrieval recall;
- answer faithfulness;
- source traceability;
- latency;
- cost;
- robustness with scanned or visually rich documents.

## Known limitations

- The system depends on good document-level metadata.
- Some queries may require multiple retrieval iterations.
- Visual reading improves quality but increases cost and latency.
- Mixed full-context + hierarchical queries require careful orchestration.

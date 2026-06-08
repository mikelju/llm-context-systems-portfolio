# RAG Knowledge System — Hierarchical + Full-Context Retrieval

## Summary

A document-processing and retrieval system designed to answer questions over heterogeneous knowledge bases containing PDFs, spreadsheets, Word documents, PowerPoint files and images.

The system processes documents into structured layers — document index, chapters, summaries, tags, visual descriptions and embeddings — and then uses a multi-step retrieval flow to select the most relevant information before calling the LLM.

## Why this project matters

The core challenge was not simply “chat with documents”, but deciding how to assemble the right context for the LLM from a large and heterogeneous document repository.

The system explores two complementary strategies:

- **Hierarchical retrieval** for large or complex documents.
- **Full-context retrieval** for smaller documents where sending the complete document is cheaper, simpler and more reliable.

## My role

I designed the architecture, retrieval strategy, document-processing pipeline, query workflow, implementation plan and iterative improvements.

## Main technical themes

- RAG
- Context engineering
- Metadata-first retrieval
- Hierarchical document processing
- Full-context / CAG-style strategy
- Visual page reading
- Gemini Vision
- Embeddings
- WAT architecture: Workflows, Agents, Tools
- Cost/latency-aware LLM orchestration

## Status

Internal framework / advanced prototype. Core processing pipeline, performance optimization and dual retrieval strategy completed. Query system in progress, with selective visual reading and reporting already implemented.

## Files in this case study

- [Architecture](architecture.md)
- [Context strategy](context-strategy.md)
- [Retrieval flow](retrieval-flow.md)
- [Reliability and evaluation](reliability-and-evaluation.md)
- [Lessons learned](lessons-learned.md)
- [Architecture diagram](assets/architecture-diagram.md)

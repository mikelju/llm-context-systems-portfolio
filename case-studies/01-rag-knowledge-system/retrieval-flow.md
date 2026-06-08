# Retrieval Flow — “The Librarian”

## Query flow

The query tool follows a multi-step process:

1. **Catalog filtering**  
   Select candidate documents based on metadata, summaries and tags.

2. **Index inspection**  
   Read document structure to identify relevant sections.

3. **Summary and visual filtering**  
   Use chapter summaries and visual descriptions to decide what should be read.

4. **Selective reading**  
   Read selected chapters or pages. When needed, send PDF pages as images to a vision-capable model.

5. **Synthesis**  
   Generate the final answer using only the selected evidence.

6. **Optional report expansion**  
   Expand the answer into a PDF-style report with supporting figures.

## Visual reading

A key part of the system is selective visual reading. Instead of extracting only raw text, selected PDF pages can be rendered as images and sent to a vision model.

This preserves:

- tables;
- figures;
- diagrams;
- layouts;
- visual instructions;
- scanned-page context.

## Model selection

Different models can be used for different tasks:

- faster/cheaper models for filtering;
- stronger models for final synthesis;
- vision-capable models for page-level visual reading.

## Metrics

The query system tracks:

- end-to-end time;
- API calls;
- input tokens;
- output tokens;
- total token usage.

These metrics make retrieval quality, latency and cost visible.

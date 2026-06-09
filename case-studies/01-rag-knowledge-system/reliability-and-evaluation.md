# Reliability and Evaluation

## Reliability mechanisms (in the real system)

| Mechanism | Where | Why |
|---|---|---|
| Retry + exponential backoff on LLM calls | `gemini_client.py` | Transient 429/5xx/network errors are normal at scale |
| Resumable ingestion, thread-safe state | `state_manager.py`, `process_batch.py` | A crash mid-document resumes instead of restarting (a 154-part doc is expensive to redo) |
| Native-TOC quality validation | `extract_structure.py` | Corrupt scanned-PDF TOCs are rejected, not trusted — see [the-bug-i-fixed.md](the-bug-i-fixed.md) |
| Low-value chapter filtering (`<100 words`) | ingestion | Drops covers/copyright/index pages so they don't pollute retrieval |
| Selective Step 1 (not inclusive) | `query_library.py` | Avoid over-selecting documents into the funnel |
| Page deduplication by hash (MD5) | full-context queries | Don't pay twice for the same page image |
| Task-specific model selection | Flash vs Pro vs Vision | Cost/quality fit per step |
| Per-query metrics (time, calls, tokens) | `gemini_client.py` | Makes cost/latency regressions visible |
| UTF-8 stdout on Windows | `process_batch.py` | Prevents `UnicodeEncodeError` crashes on Spanish/emoji output |

## How I evaluate (and what's real vs pending)

> Full case matrix and the plan for a real eval suite: **[EVALUATION.md](EVALUATION.md)**.

**What I run today — worked, recorded examples.** Each query trace is a concrete evaluation case:
the funnel, the chapters read, the **token/latency cost**, and the **source references** are all
captured. The two shipped traces cover two of the three question types below:

1. **Single-document** question → Run A (power zones): 1 doc, 5 chapters, 5 cited refs, 52.8k tokens.
2. **Cross-document** question → Run B (safety): 4 docs, 8 chapters, 8 cited refs, 44.7k tokens.
3. **No-answer-in-the-library** question → *not yet recorded* (the honest gap).

**Evaluation dimensions I care about:**

- retrieval precision & recall (did Step 1–3 select the right documents/chapters?);
- **answer faithfulness** + **source traceability** (every claim points to a chapter);
- latency and token cost per query;
- robustness on scanned / visually rich documents.

**The honest gap.** This is a prototype: there is **no formal labeled eval set yet**. The traces
prove the system works and is *measurable*, but precision/recall numbers would require a curated
question→expected-source set. Building that — plus the "no answer" refusal case and an automated
faithfulness check (does every sentence map to a cited chapter?) — is the top item on the
roadmap. I'd rather state that than dress an evaluation *plan* up as results.

## Known limitations

- Retrieval quality depends on good document-level metadata (titles/summaries/tags).
- Some queries need more than one iteration (the Step 4 loop handles it, at extra cost).
- Visual reading improves quality but increases latency and tokens.
- Mixed full-context + hierarchical queries need careful orchestration.
- No vector search yet — fine at this scale (dozens of docs), revisited at hundreds.

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

## How I evaluate

The two shipped query traces are concrete, recorded evaluation cases (funnel + token/latency cost
+ resolvable source references); a worked **claim→source faithfulness mapping** is shown for one
answer. The full **case matrix**, the **negative ("no answer") case** status, and the plan for a
labeled eval suite live in **[EVALUATION.md](EVALUATION.md)** — not duplicated here.

Honest gap: there is **no formal labeled eval set yet** (precision/recall vs. a curated
question→expected-source set), and the negative case is not yet recorded. Both are the top roadmap
items in EVALUATION.md.

## Known limitations

- Retrieval quality depends on good document-level metadata (titles/summaries/tags).
- Some queries need more than one iteration (the Step 4 loop handles it, at extra cost).
- Visual reading improves quality but increases latency and tokens.
- Mixed full-context + hierarchical queries need careful orchestration.
- No vector search yet — fine at this scale (dozens of docs), revisited at hundreds.

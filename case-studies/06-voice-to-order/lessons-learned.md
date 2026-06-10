# Lessons Learned

This project is also where my documentation discipline was born: the SDD process (spec → plan →
implement → verify, plus numbered fixes) that the rest of this portfolio's projects follow was created
*during* this build — which is why the early phases are thinly documented and the late ones (11, 12,
the fixes) are forensic. The repository's archaeology below is real: the discarded code is still in
the repo.

## 1. "It works in dev" can mean "the planner chose differently in dev"

The fix-1 timeout was invisible locally for two compounding reasons: the dev connection used the
`postgres` role (2min timeout) while production used `authenticated` (8s), and a small local table
makes a sequential scan cheap. Since then I treat **`EXPLAIN ANALYZE` output and role-level config as
part of the deploy checklist** for any vector-search change, not as debugging tools of last resort.

## 2. Parallelize, then bound — in that order, with names

The search went sequential → naive `gather` → semaphores → true-async, each step forced by a
production symptom (rate limits, `httpx.ReadError` socket exhaustion, a missed `await`). The lesson
isn't "use semaphores"; it's that **every shared resource a fan-out touches needs an explicit, named
limit** (LLM=10, DB=10) — and that a *half*-async stack is worse than a sync one, because it hides
where the pressure builds.

## 3. The best memory system was a Postgres table

I trialled **mem0** (the repo clone is still in the project) for remembering technician phrasing. What
shipped instead is the `historico` table: dictated phrase → confirmed article + frequency + last-used,
fed by every confirmed order and searched memory-first (threshold 0.75) ahead of the 31,070-row
catalog. It's queryable with the same pgvector machinery, auditable row by row, and improves with use —
a learning loop with zero extra infrastructure.

## 4. Fine-tuning lost to a prompt with domain knowledge in it

The repo still has the **47-pair fine-tuning dataset** built to train extraction. It was never
deployed: the extraction prompt — abbreviations (DN, INOX, M, H/MH/HH), material rules, dictation
patterns, coreference handling — reached the needed quality and stays editable in minutes when a new
pattern appears. Those 47 pairs turned out to be worth more as **evaluation data** than as training
data ([EVALUATION.md](EVALUATION.md)).

## 5. Provider-agnostic plumbing paid for itself in one incident

`llm_wrapper.py` routes by model-name prefix (`gpt-` / `claude-` / `gemini-`) — written early, when the
project was experimenting with Claude 3 prompts (still in the repo). When the preview Gemini model
started returning truncated JSON under load (fix-4), the remedy — retry ×3 with backoff **and a model
swap to the GA release** — was a config change plus one constant, deployed in hours. The earlier
swaps (BERT experiments → OpenAI embeddings; gpt-4o → gemini-2.5-flash) went the same way.

## 6. Failure isolation is a product feature, not an ops detail

Delivery is three independent channels (ERP, email+PDF, memory upsert), each with its own status light
and its own chaos-injection point (`SIMULATE_FAILURE`). When the ERP is down, the office still gets
the order by email and nothing is lost. Designing the failure UX *first* — what the technician sees per
channel — is what made the chaos switch worth building.

## 7. The stack archaeology: every discard was a migration with a reason

Still visible in the repo: the **Streamlit** app (root `main.py`, a Heroku `Procfile` that launches
it) → rebuilt as FastAPI + React when the product needed auth, a phone-first multi-step flow and a
deployable API; **Heroku** → **Cloud Run** when it needed Docker control and a **static IP** (VPC +
NAT) to talk to the client's ERP; **FAISS pickled indexes** → **Supabase pgvector** when vectors had to
live where auth, RLS and the synced catalog already lived; **IVFFlat** → **HNSW** (during fix-1). None
of these was a rewrite for taste — each was triggered by a capability the previous stack couldn't
offer.

## 8. Declare the metric you failed to capture

The one thing this production system can't show is the thing a product case most wants: latency
percentiles. The logs rotated before I exported them. The honest move — recording the stress-test
outcome as a qualitative claim and listing the export as the top open item — costs less credibility
than a reconstructed number would. (It's also why the portfolio's later projects archive their traces
as they run.)

## What I'd do next

- Add the **latency/token export** (BigQuery sink or a per-request `latency_ms` write) and publish
  the percentiles this case is missing.
- Build the **extraction scorer** over the 47 recorded pairs and the **retrieval benchmark** over the
  1,001 learned mappings (a free labelled set), run on every prompt/model change.
- Record one **chaos-run log per failure mode** per release.
- Apply the measured-trigger upgrades documented in fix-1 when the data justifies them
  (`min-instances 1`, scheduled HNSW warmup).

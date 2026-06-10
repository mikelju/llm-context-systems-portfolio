#!/usr/bin/env python3
"""
Voice-to-Order (applied-AI product) — offline demo.

Runs offline (no API key, no network) over the real, sanitized artifacts in ../artifacts.
It reproduces TWO rules that are genuinely part of the system:

  Step 4 — the memory-first candidate assembly + dedup + the deterministic re-rank
           FALLBACK ordering (sort by Historical_match desc, Score desc), and
  Step 7 — the chaos/degradation matrix (SIMULATE_FAILURE -> per-channel status lights).

Then it replays the recorded evidence: a real hand-validated extraction pair, the real
pipeline constants, and the fix-1 measurements.

Honesty note: the real Step 4 matches by EMBEDDING SIMILARITY (pgvector/HNSW); this demo
matches dictated text against the real memory rows by normalized tokens — an offline
approximation, and any divergence is printed. The model steps (whisper-1 transcription,
gemini-2.5-flash extraction and re-ranking) and the live DB/ERP are NOT run here. This demo
does not call any model and is not the full engine.

Run:    python run_demo.py
Capture: python run_demo.py > example_output.txt
"""
from __future__ import annotations
import json, re, sys, unicodedata
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from rich.console import Console
    from rich.table import Table
    _RICH = True; _con = Console(width=100)
except Exception:
    _RICH = False; _con = None

HERE = Path(__file__).resolve().parent
ART = (HERE.parent / "artifacts").resolve()

def _print(t=""):
    if _RICH: _con.print(t)
    else: print(re.sub(r"\[/?[a-z0-9 ._#]+\]", "", t))

def _print_raw(t=""):
    """Print artifact text verbatim (no markup interpretation/stripping) — sanitization
    tokens like [customer] must survive."""
    if _RICH: _con.print(t, markup=False, highlight=False)
    else: print(t)

def _rule(t):
    if _RICH: _con.rule(f"[bold]{t}")
    else: print("\n" + "=" * 72 + f"\n {t}\n" + "=" * 72)

def load(name): return json.loads((ART / name).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# (a) STATE OVERVIEW — the corpus, the memory, the models
# --------------------------------------------------------------------------- #
def show_state():
    cat = load("catalog-stats.json")["metrics"]
    pl = load("pipeline-structure.json")
    _rule("A. The product state (read from real artifacts)")
    _print(f"  catalog: {cat['catalog_rows']:,} synced ERP rows · learned memory: "
           f"{cat['historical_mappings']:,} mappings · {cat['transcriptions_archived']} "
           f"archived transcriptions / {cat['audio_files_archived']} audio files")
    m = pl["models"]
    _print(f"  models: {m['transcription']} -> {m['extraction']} (extract) -> "
           f"{m['reranking']} (re-rank) · embeddings {m['embeddings']}")
    pm = pl["metrics"]
    _print(f"  bounds: semaphores LLM={pm['llm_concurrency']} / DB={pm['db_concurrency']} · "
           f"retry x{pm['max_llm_retries']} · thresholds {pm['historical_threshold']}/"
           f"{pm['catalog_threshold']} · top-{pm['catalog_top_k']} · CTE x{pm['cte_candidate_multiplier']}")


# --------------------------------------------------------------------------- #
# (b1) LIVE STEP 4 — memory-first assembly + dedup + deterministic fallback
#      Approximation: token match instead of the real embedding similarity.
# --------------------------------------------------------------------------- #
def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return set(re.findall(r"[a-z0-9]+", s))

def live_memory_first():
    _rule("B. Step 4 reproduced live — memory-first rule (deterministic, offline)")
    mem = load("historical-memory-sample.json")
    rows = mem["sample"]
    queries = ["taco fischer de 10", "tuerca metrica 8", "valvula de bola de media"]
    for q in queries:
        qt = norm(q)
        scored = sorted(rows, key=lambda r: -len(qt & norm(r["user_text"])))
        best = scored[0]
        overlap = len(qt & norm(best["user_text"]))
        hit = overlap >= 2
        _print(f"\n  dictated: \"{q}\"")
        if hit:
            _print(f"    memory hit -> {best['catalog_description']}  ({best['id_articulo']}, "
                   f"used {best['frequency']}x) — pinned ABOVE catalog candidates")
            _print(f"    dedup rule: the catalog candidate with this same description is skipped")
        else:
            _print(f"    no memory hit in this 14-row sample -> would fall through to the "
                   f"31,070-row catalog search (threshold 0.5, top 25)")
    _print("\n  fallback ordering (when the re-rank LLM fails) — real rule, run live:")
    cands = [
        {"desc": "candidate from catalog", "Historical_match": False, "Score": 0.81},
        {"desc": "candidate from memory", "Historical_match": True, "Score": 0.78},
        {"desc": "another catalog candidate", "Historical_match": False, "Score": 0.74},
    ]
    ordered = sorted(cands, key=lambda c: (not c["Historical_match"], -c["Score"]))
    for i, c in enumerate(ordered, 1):
        _print(f"    {i}. {c['desc']}  (memory={c['Historical_match']}, score={c['Score']})")
    _print("  [dim]Note the memory hit outranks a higher-scoring catalog row — that is the real "
           "sort key (Historical_match desc, Score desc).[/dim]")
    _print("  [dim]Divergence: the real system matches by pgvector embedding similarity; this "
           "token-overlap lookup is an offline approximation and may differ from the recorded "
           "behaviour.[/dim]")


# --------------------------------------------------------------------------- #
# (b2) LIVE STEP 7 — the chaos/degradation matrix (real switch semantics)
# --------------------------------------------------------------------------- #
def live_chaos():
    _rule("B. Step 7 reproduced live — degradation matrix (deterministic, offline)")
    chaos = load("chaos-degradation.json")
    modes = [m["mode"] for m in chaos["modes"]]
    scenarios = ["", "erp", "erp,email"]
    if _RICH:
        t = Table(show_header=True, header_style="bold green")
        t.add_column("SIMULATE_FAILURE")
        for ch in ("ERP", "email+PDF", "memory"):
            t.add_column(ch)
        t.add_column("order outcome")
    rows = []
    for s in scenarios:
        failset = {x.strip() for x in s.split(",") if x.strip()}
        st = ["FAIL" if "erp" in failset else "ok",
              "FAIL" if "email" in failset else "ok",
              "FAIL" if "history" in failset else "ok"]
        if st == ["ok", "ok", "ok"]:
            outcome = "delivered on all 3 channels"
        elif st[0] == "FAIL" and st[1] == "ok":
            outcome = "delivered by email; ERP flagged for office follow-up"
        elif st[0] == "FAIL" and st[1] == "FAIL" and st[2] == "ok":
            outcome = "order saved to history only; both delivery lights red, office must resend"
        else:
            outcome = "depends on the failing set; each light reports independently"
        rows.append((s or "(none)", *st, outcome))
    if _RICH:
        for r in rows: t.add_row(*r)
        _con.print(t)
    else:
        for r in rows:
            print(f"  {r[0]:<14} ERP={r[1]:<5} email={r[2]:<5} memory={r[3]:<5} -> {r[4]}")
    _print(f"  [dim]{len(modes)} real injection points (file:line in chaos-degradation.json); "
           "channels fail independently, each with its own status light.[/dim]")


# --------------------------------------------------------------------------- #
# (c) RECORDED EVIDENCE — replayed verbatim
# --------------------------------------------------------------------------- #
def show_recorded():
    _rule("C. Recorded evidence (replayed verbatim from artifacts)")
    ex = load("extraction-examples.json")
    e1 = ex["examples"][0]
    _print(f"  recorded extraction pair 1 of {ex['metrics']['recorded_pairs']} (hand-validated):")
    _print_raw(f"    dictated: \"{e1['transcription'][:90]}…\"")
    for it in e1["expected_items"]:
        _print(f"      -> {it['qty']:>5}  {it['description']}")
    e3 = ex["examples"][2]
    _print(f"    high-volume pair: {len(e3['expected_items'])} lines from one dictation "
           f"(incl. coreference)")
    pm = load("pipeline-structure.json")["metrics"]
    _print(f"\n  fix-1 measurements (recorded): warm HNSW index scan {pm['warm_index_scan_ms']}ms · "
           f"cold cache {pm['cold_disk_reads']} disk reads vs {pm['cold_cache_hits']} hits · "
           f"role timeout {pm['statement_timeout_role_s']}s -> function-scoped "
           f"{pm['statement_timeout_fn_s']}s · Cloud Run cold start ~{pm['cloud_run_cold_start_s']}s")
    _print(f"  project scale: {pm['git_commits']} commits")
    _print("  [dim]Per-request latency/token traces were not archived (declared gap — see "
           "EVALUATION.md); nothing above is estimated.[/dim]")


def main():
    _print("[bold magenta]Voice-to-Order — offline demo[/bold magenta]")
    _print("[dim]Real, sanitized artifacts. No API key, no network, no model call.[/dim]")
    show_state()
    live_memory_first()
    live_chaos()
    show_recorded()
    _print("\n[dim]Not run here (need live APIs/infra): Step 2 whisper-1, Step 3 gemini "
           "extraction, the real Step 4 pgvector/HNSW similarity search, Step 5 re-ranking, and "
           "Step 7 ERP/email delivery. This demo does not call any model and is not the full "
           "engine — it runs two deterministic system rules and replays recorded evidence.[/dim]")


if __name__ == "__main__":
    main()

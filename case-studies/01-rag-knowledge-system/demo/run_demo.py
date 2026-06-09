#!/usr/bin/env python3
"""
The Librarian - offline retrieval-flow demo
============================================

This script makes the case study *runnable*. It does two things, using only the
real, sanitized artifacts shipped in ../artifacts:

  1. Reproduces Step 1 of the retrieval flow LIVE and offline: a deterministic
     catalog pre-filter that ranks candidate documents for a query using their
     titles, tags and summaries (no API key, no network).

  2. Renders the retrieval funnel and the real cost/latency metrics from two
     RECORDED real-system runs (query traces), so the numbers you see were
     actually produced by the system, not invented for the portfolio.

Honesty note: in the real system, Steps 2-5 (chapter selection, reading,
synthesis) are performed by an LLM. This demo does NOT call any model and is
NOT the full RAG engine. It reproduces the deterministic control flow (Step 1,
as an offline approximation) and reports the recorded metrics of the LLM-driven
steps. That separation is the point: the expensive part is bounded and measurable.

Run:
    python run_demo.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Windows consoles default to a legacy code page; force UTF-8 so accented text
# (the corpus is partly Spanish) survives being printed or piped to a file.
# This is the same class of fix as the one described in ../the-bug-i-fixed.md.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

# Optional pretty output. Falls back to plain text if `rich` is not installed,
# so the demo runs with zero dependencies too.
try:
    from rich.console import Console
    from rich.table import Table
    _RICH = True
    _con = Console(width=100)
except Exception:  # pragma: no cover - cosmetic only
    _RICH = False
    _con = None

HERE = Path(__file__).resolve().parent
ART = (HERE.parent / "artifacts").resolve()

_WORD = re.compile(r"[a-záéíóúñ0-9]+", re.IGNORECASE)


def _print(text: str = "") -> None:
    if _RICH:
        _con.print(text)
    else:
        print(re.sub(r"\[/?[a-z0-9 ._#]+\]", "", text))  # strip rich markup


def _rule(title: str) -> None:
    if _RICH:
        _con.rule(f"[bold]{title}")
    else:
        print("\n" + "=" * 72 + f"\n {title}\n" + "=" * 72)


def load(name: str) -> dict:
    return json.loads((ART / name).read_text(encoding="utf-8"))


def tokens(text: str) -> set[str]:
    return {w.lower() for w in _WORD.findall(text or "")}


# --------------------------------------------------------------------------- #
# Section A - Knowledge base overview
# --------------------------------------------------------------------------- #
def show_catalog(catalog: dict) -> list[dict]:
    docs = catalog["documents"]
    _rule("A. Knowledge base (catalog.sample.json)")
    if _RICH:
        t = Table(show_header=True, header_style="bold cyan")
        for c in ("Title", "Type", "Strategy", "Chapters", "Pages", "Lang"):
            t.add_column(c)
        for d in docs:
            t.add_row(
                d.get("title", "")[:38],
                d.get("document_type", ""),
                d.get("strategy", ""),
                str(d.get("total_chapters", "-")),
                str(d.get("page_count", "-")),
                d.get("language", ""),
            )
        _con.print(t)
    else:
        for d in docs:
            print(f"  - {d.get('title','')[:40]:42} {d.get('strategy',''):12} "
                  f"chapters={d.get('total_chapters','-')} pages={d.get('page_count','-')}")
    n_hier = sum(1 for d in docs if d.get("strategy") == "hierarchical")
    n_full = sum(1 for d in docs if d.get("strategy") == "full_context")
    _print(f"\n[dim]{len(docs)} documents | {n_hier} hierarchical, {n_full} full_context "
           f"(threshold: FULL_CONTEXT_MAX_PAGES = 80)[/dim]")
    return docs


# --------------------------------------------------------------------------- #
# Section B - Step 1 reproduced live, offline
# --------------------------------------------------------------------------- #
def prefilter(docs: list[dict], query: str, top: int = 3) -> None:
    q = tokens(query)
    scored = []
    for d in docs:
        bag = tokens(d.get("title", "")) | set(
            t.lower() for t in d.get("tags_global", [])
        ) | tokens(d.get("summary_global", ""))
        hits = q & bag
        scored.append((len(hits), sorted(hits), d))
    scored.sort(key=lambda x: x[0], reverse=True)

    _print(f"\n[bold]Query:[/bold] \"{query}\"")
    if _RICH:
        t = Table(show_header=True, header_style="bold green")
        for c in ("Rank", "Score", "Document", "Matched terms"):
            t.add_column(c)
        for i, (score, hits, d) in enumerate(scored, 1):
            mark = " <- selected" if score > 0 and i <= top else ""
            t.add_row(str(i), str(score), d.get("title", "")[:34] + mark,
                      ", ".join(hits)[:46])
        _con.print(t)
    else:
        for i, (score, hits, d) in enumerate(scored, 1):
            mark = " <- selected" if score > 0 and i <= top else ""
            print(f"  {i}. score={score} {d.get('title','')[:34]:36}{mark}  [{', '.join(hits)}]")
    passed = [d for s, _, d in scored if s > 0][:top]
    _print(f"[dim]Step 1 passes {len(passed)} candidate document(s) to the LLM stages.[/dim]")


# --------------------------------------------------------------------------- #
# Section C - Real recorded runs: funnel + metrics
# --------------------------------------------------------------------------- #
def show_trace(trace: dict, label: str) -> None:
    log = {s["step"]: s for s in trace["steps_log"]}
    m = trace["metrics"]
    sel = log[1].get("documents_selected", "-")
    conf = log[2].get("documents_confirmed", "-")
    cand = log[2].get("total_candidate_chapters", "-")
    read = trace.get("total_chapters_read", "-")

    _print(f"\n[bold]{label}[/bold]")
    _print(f"  funnel : catalog -> [b]{sel}[/b] docs selected -> [b]{conf}[/b] confirmed "
           f"-> [b]{cand}[/b] candidate chapters -> [b]{read}[/b] chapters read")
    _print(f"  cost   : {m['elapsed_seconds']}s | {m['api_calls']} API calls | "
           f"{m['input_tokens']:,} in + {m['output_tokens']:,} out = {m['total_tokens']:,} tokens")
    if isinstance(cand, int) and isinstance(read, int) and cand:
        kept = 100 * read / cand
        _print(f"  context: only {read}/{cand} candidate chapters were actually read "
               f"({kept:.0f}% kept) - the rest never reached the synthesis prompt")
    refs = trace.get("references", [])
    _print(f"  sources: answer cites {len(refs)} traceable (document -> chapter) references")


def main() -> None:
    catalog = load("catalog.sample.json")
    safety = load("query-trace.safety.json")
    power = load("query-trace.power-zones.json")

    _print("[bold magenta]The Librarian - offline retrieval-flow demo[/bold magenta]")
    _print("[dim]Real, sanitized artifacts. No API key required.[/dim]")

    docs = show_catalog(catalog)

    _rule("B. Step 1 reproduced live (deterministic catalog pre-filter)")
    # Queries mirror the real recorded runs: the boiler corpus is Spanish, the book is English.
    prefilter(docs, "seguridad mantenimiento caldera gasoil instalación térmica")
    prefilter(docs, "cycling power zones ftp vo2max training")
    _print("\n[dim]This pre-filter is an offline approximation of Step 1, not a replay of the exact "
           "LLM selection — it may pass a different number of candidates than the recorded run "
           "(here 3 vs. the real run's 5 for the safety query).[/dim]")

    _rule("C. Real recorded runs (metrics produced by the system)")
    show_trace(power, "Run 1 - 'physiological power zones' (single large book, hierarchical)")
    show_trace(safety, "Run 2 - 'safety measures' (cross-document over 4 manuals, hierarchical)")

    _print("\n[dim]Steps 2-5 are LLM-driven in the real system; the metrics above are from "
           "recorded runs. Step 1 is reproduced here deterministically and offline. "
           "This is a trace-replay + pre-filter demo, not the full RAG engine.[/dim]")


if __name__ == "__main__":
    main()

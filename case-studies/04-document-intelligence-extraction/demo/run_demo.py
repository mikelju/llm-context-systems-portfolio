#!/usr/bin/env python3
"""
Document-intelligence extraction — offline demo.

Replays the real pilot run from the sanitized artifacts and, **live and offline**,
recomputes the extraction quality (precision / recall / specificity) from the real
confusion matrix in ../artifacts/coverage-matrix.json. No API key, no network.

Honesty note: the extraction itself sent 134 scanned pages to Gemini Vision (live
API) and is not run here. These are the recorded aggregate results; the demo's live
step is the deterministic quality computation over the real coverage counts.

Run:    python run_demo.py
Capture: python run_demo.py > example_output.txt
"""
from __future__ import annotations
import json, re, sys
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

ART = (Path(__file__).resolve().parent.parent / "artifacts").resolve()

def _print(t=""):
    if _RICH: _con.print(t)
    else: print(re.sub(r"\[/?[a-z0-9 ._#]+\]", "", t))

def _rule(t):
    if _RICH: _con.rule(f"[bold]{t}")
    else: print("\n" + "=" * 72 + f"\n {t}\n" + "=" * 72)

def load(name): return json.loads((ART / name).read_text(encoding="utf-8"))


def main():
    _print("[bold magenta]Document-intelligence extraction — offline demo[/bold magenta]")
    _print("[dim]Real pilot results, recomputed offline. No API key required.[/dim]")

    # A — the input
    st = load("extraction-stats.json")
    r = st["metrics"]
    _rule("A. The input — a scanned manufacturer quality report")
    _print(f"  {r['pages']} pages, {r['pages_failed']} failed · rendered at {r['render_dpi']} DPI · "
           f"{r['api_calls']} Vision calls · {r['wall_clock']} (batch {r['batch_size']} × {r['workers']} workers, resumable)")
    byl = st["pages_by_language"]; bil = byl.get("bilingual", 0)
    _print(f"  [dim]{bil}/{r['pages']} pages are bilingual (Chinese/English), scanned — text extraction is hopeless here.[/dim]")
    _print(f"  page types: " + ", ".join(f"{k}={v}" for k, v in st["pages_by_document_type"].items()))

    # B — the target schema
    sc = load("schema-structure.json")["summary"]
    _rule("B. The target — the client's INR quality schema (flattened from Excel)")
    _print(f"  {sc['total_sheets']} inspection tabs · [b]{sc['total_fields']}[/b] fields "
           f"({sc['numeric_fields']} numeric, {sc['boolean_fields']} boolean) to fill")

    # C — the funnel + confusion matrix + LIVE recompute
    cov = load("coverage-matrix.json")["metrics"]
    tp, fp, fn, tn = cov["extracted_ok"], cov["false_positives"], cov["extraction_failures"], cov["correctly_empty"]
    present, absent = cov["present_in_report"], cov["absent_from_report"]
    _rule("C. The funnel + confusion matrix (recomputed live from real counts)")
    _print(f"  {cov['total_fields']} schema fields  ->  [b]{present}[/b] present in the report  +  {absent} absent")
    if _RICH:
        t = Table(show_header=True, header_style="bold cyan")
        for c in ("", "extracted a value", "left empty"): t.add_column(c)
        t.add_row("field IS in report", f"[green]{tp}[/green] correct (TP)", f"[yellow]{fn}[/yellow] missed (FN)")
        t.add_row("field NOT in report", f"[red]{fp}[/red] hallucinated (FP)", f"[green]{tn}[/green] correct (TN)")
        _con.print(t)
    else:
        print(f"    in-report:  {tp} correct (TP) | {fn} missed (FN)")
        print(f"    not-in-rep: {fp} hallucinated (FP) | {tn} correctly empty (TN)")
    prec, rec, spec = tp / (tp + fp), tp / (tp + fn), tn / (tn + fp)
    _print(f"\n  [b]precision[/b] (claims that were real) = {tp}/({tp}+{fp}) = [b]{prec:.1%}[/b]")
    _print(f"  [b]recall[/b]    (real fields captured)   = {tp}/({tp}+{fn}) = [b]{rec:.1%}[/b]")
    _print(f"  [b]specificity[/b] (absent fields left empty) = {tn}/({tn}+{fp}) = [b]{spec:.1%}[/b]")
    _print(f"  [dim]Only {cov['theoretical_max_rate']:.0%} of the 293 fields are even present in this report — "
           f"'correctly empty' ({tn}) is as important as 'extracted' ({tp}): the system must NOT invent the rest.[/dim]")

    # D — write-back
    fr = load("fill-report.json")
    _rule("D. Phase 4 — values written back to one Excel per part")
    for p in fr["pieces"]:
        _print(f"  {p['piece']}: {p['total_filled']}/{p['total_fields']} filled · {p['out_of_tolerance']} out of tolerance")

    _print("\n[dim]The 134-page Vision extraction used the live API and is not run here. The numbers above "
           "are the recorded pilot results; the quality metrics are recomputed offline from the real "
           "confusion matrix. Not the full pipeline.[/dim]")


if __name__ == "__main__":
    main()

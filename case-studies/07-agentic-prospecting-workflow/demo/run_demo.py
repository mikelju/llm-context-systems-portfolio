#!/usr/bin/env python3
"""
Agentic prospecting workflow -- offline demo.

Replays the real corpus from the sanitized artifacts and, **live and offline**, recomputes
the deterministic parts of the system: the validator's completeness verdict (the >=80 / >=50
thresholds the real tool applies), the provenance rates, and the contract-drift count.
No API key, no network, no model call, no web search.

Honesty note: the research itself was an agent running 8 web-search protocols per company,
live. That is not run here and cannot be: it depends on the public web at a point in time.
What runs here is the deterministic layer -- the arithmetic and the rules that decide whether
a researched lead is good enough to act on.

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


def load(name):
    return json.loads((ART / name).read_text(encoding="utf-8"))


# The real validator's rule, reimplemented verbatim (tools/validate_data.py).
READY, PARTIAL = 80.0, 50.0


def verdict(completeness_pct: float) -> str:
    if completeness_pct >= READY:
        return "ready"
    if completeness_pct >= PARTIAL:
        return "partial"
    return "insufficient"


def main():
    _print("[bold magenta]Agentic prospecting workflow -- offline demo[/bold magenta]")
    _print("[dim]Real corpus, deterministic layer recomputed live. No API key required.[/dim]")

    # A -- the funnel
    fn = load("funnel.json")
    m = fn["metrics"]
    _rule("A. The funnel -- what the workflow actually produced")
    for s in fn["stages"]:
        bar = "#" * max(1, round(s["count"] / 2))
        _print(f"  {s['stage']}. {s['name']:<16} {s['count']:>3}  {bar}")
        _print(f"     [dim]{s['meaning']}[/dim]")
    drop = fn["drop_off"]["identified_to_enriched"]
    _print(f"\n  {m['research_json_files']} research JSON files, {m['protocols_per_lead']} protocols per lead.")
    _print(f"  [dim]{drop} identified leads never reached full enrichment -- left as partial[/dim]")
    _print(f"  [dim]research rather than completed with unverified data.[/dim]")

    # B -- the provenance contract, rates recomputed live
    pv = load("provenance-stats.json")["metrics"]
    _rule("B. The provenance contract (rates recomputed live from the counts)")
    null_rate = pv["explicit_nulls"] / pv["leaf_values"]
    url_rate = pv["sources_with_url"] / pv["sources_logged"]
    _print(f"  {pv['leaf_values']} values recorded across the corpus")
    _print(f"    [b]{pv['explicit_nulls']}[/b] are an explicit 'not found' = "
           f"{pv['explicit_nulls']}/{pv['leaf_values']} = [b]{null_rate:.1%}[/b] "
           f"[dim](written instead of a guess)[/dim]")
    _print(f"  {pv['sources_logged']} sources logged, {pv['sources_with_url']} carry a URL = "
           f"[b]{url_rate:.1%}[/b] traceable")
    _print(f"  reliability ratings: high={pv['reliability_high']}, "
           f"medium={pv['reliability_medium']}, low={pv['reliability_low']}")

    # C -- the negative case
    ng = load("contact-negative-case.json")
    nm = ng["metrics"]
    _rule("C. The negative case -- an unverifiable contact is dropped, never invented")
    empty_rate = nm["slots_left_empty"] / nm["contact_slots"]
    _print(f"  {nm['contact_slots']} contact slots across {nm['leads_considered']} leads "
           f"(a manager and an admin lead per company)")
    _print(f"    [green]{nm['slots_with_reachable_channel']}[/green] have a reachable channel")
    _print(f"    [yellow]{nm['slots_left_empty']}[/yellow] left empty = "
           f"{nm['slots_left_empty']}/{nm['contact_slots']} = [b]{empty_rate:.1%}[/b]")
    _print(f"  [dim]Rule: {ng['the_rule']['verbatim_intent']}.[/dim]")
    _print(f"  [dim]{ng['the_rule']['why_it_matters']}.[/dim]")

    # D -- LIVE deterministic step: the validator's verdict
    tr = load("two-runs.json")
    _rule("D. LIVE step -- the validator's rule, recomputed and checked")
    _print(f"  [dim]rule: >= {READY:.0f}% complete -> ready | >= {PARTIAL:.0f}% -> partial | "
           f"below -> insufficient[/dim]\n")
    if _RICH:
        t = Table(show_header=True, header_style="bold cyan")
        for c in ("lead", "complete", "recomputed", "recorded", "nulls", "sources"):
            t.add_column(c)
    ok = True
    for r in tr["runs"]:
        got = verdict(r["completeness_pct"])
        match = got == r["validator_verdict"]
        ok = ok and match
        if _RICH:
            t.add_row(r["lead"], f"{r['completeness_pct']:.1f}%", got, r["validator_verdict"],
                      str(r["explicit_nulls"]), str(r["sources_logged"]))
        else:
            print(f"    {r['lead']:<26} {r['completeness_pct']:>6.1f}%  -> {got:<12} "
                  f"(recorded: {r['validator_verdict']}) nulls={r['explicit_nulls']} "
                  f"sources={r['sources_logged']}")
    if _RICH:
        _con.print(t)
    _print(f"\n  recomputed verdicts match the recorded ones: [b]{'yes' if ok else 'NO'}[/b]")
    tm = tr["metrics"]
    _print(f"  corpus: mean {tm['corpus_mean_completeness_pct']}% complete, "
           f"median {tm['corpus_median_completeness_pct']}% -- "
           f"{tm['leads_ready']} ready, {tm['leads_partial']} partial, "
           f"{tm['leads_insufficient']} insufficient")
    _print(f"  [dim]{tr['what_this_shows']}[/dim]")

    # E -- where the contract leaked
    dr = load("provenance-stats.json")["contract_drift"]
    _rule("E. Where the contract leaked (measured, not fixed)")
    _print(f"  the protocol specifies {len(dr['specified_values'])} allowed values for a source outcome: "
           f"{', '.join(dr['specified_values'])}")
    _print(f"  the corpus contains [b]{dr['observed_distinct_values']}[/b] distinct values -- "
           f"{dr['off_contract_occurrences']} occurrences off contract")
    _print(f"  [dim]{dr['why_it_happened']}.[/dim]")

    _print("\n[dim]The research itself -- an agent running 8 web-search protocols per company against "
           "the live web -- is not run here and does not call any model. What ran above is the "
           "deterministic layer: the validator's thresholds and the arithmetic over the recorded "
           "corpus. It is not the full workflow.[/dim]")


if __name__ == "__main__":
    main()

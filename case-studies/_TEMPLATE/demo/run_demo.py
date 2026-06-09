#!/usr/bin/env python3
"""
<CASE> — offline demo.   (Template: keep the plumbing; implement the 3 stubbed sections.)

Per CASE_STUDY_SPEC.md §8 the demo must: run offline (no API key/network), work on the stdlib
alone (rich optional), set UTF-8 stdout, read only ../artifacts, print (a) a state overview,
(b) ONE live deterministic step whose logic is genuinely part of the system (NOT a generic
keyword match dressed as the real selection), and (c) the funnel + metrics read VERBATIM from
the recorded traces. It must name the steps it does NOT run, reconcile any live-step vs recorded
divergence inline, and carry an honesty caveat.

Run:    python run_demo.py
Capture: python run_demo.py > example_output.txt
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

# UTF-8 stdout so accented/emoji output survives Windows consoles and pipes.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Optional pretty output; falls back to plain text so the demo runs with zero deps.
try:
    from rich.console import Console
    from rich.table import Table
    _RICH = True
    _con = Console(width=100)
except Exception:
    _RICH = False
    _con = None

HERE = Path(__file__).resolve().parent
ART = (HERE.parent / "artifacts").resolve()

def _print(text: str = "") -> None:
    if _RICH: _con.print(text)
    else: print(re.sub(r"\[/?[a-z0-9 ._#]+\]", "", text))

def _rule(title: str) -> None:
    if _RICH: _con.rule(f"[bold]{title}")
    else: print("\n" + "=" * 72 + f"\n {title}\n" + "=" * 72)

def load(name: str) -> dict:
    return json.loads((ART / name).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# (a) STATE OVERVIEW — TODO: print the catalog/schema/index (real, sanitized)
# --------------------------------------------------------------------------- #
def show_state(state: dict) -> None:
    _rule("A. State overview (<artifact>.json)")
    # TODO: render the structured-state artifact (e.g. a table of documents/fields/tools).
    raise NotImplementedError("implement show_state")


# --------------------------------------------------------------------------- #
# (b) LIVE DETERMINISTIC STEP — TODO: reproduce a step whose logic is REALLY in
#     the system (the catalog-pruning rule, a validator, a strategy threshold).
#     Label it an approximation; do not present it as the real model selection.
# --------------------------------------------------------------------------- #
def live_step(state: dict, query: str) -> None:
    _rule("B. <name> reproduced live (deterministic, offline)")
    # TODO: implement the real deterministic rule; print its result.
    raise NotImplementedError("implement live_step")


# --------------------------------------------------------------------------- #
# (c) RECORDED RUNS — read the funnel + metrics VERBATIM from a trace.
# --------------------------------------------------------------------------- #
def show_trace(trace: dict, label: str) -> None:
    m = trace.get("metrics", {})
    _print(f"\n[bold]{label}[/bold]")
    # TODO: print the project's funnel from trace['steps_log'] (counts copied verbatim).
    # Example cost line (adapt keys to your trace schema; copy values verbatim):
    if m:
        parts = " | ".join(f"{k}={v:,}" if isinstance(v, (int, float)) else f"{k}={v}" for k, v in m.items())
        _print(f"  metrics: {parts}")
    refs = trace.get("references", [])
    _print(f"  sources: answer cites {len(refs)} traceable references")


def main() -> None:
    _print("[bold magenta]<CASE> — offline demo[/bold magenta]")
    _print("[dim]Real, sanitized artifacts. No API key required.[/dim]")

    # state = load("<state>.json")
    # show_state(state)

    _rule("B. Step reproduced live (deterministic)")
    # live_step(state, "<a representative query>")
    _print("[dim]This is an offline approximation of <Step 1>, not a replay of the real model "
           "selection — it may differ from the recorded run.[/dim]")

    _rule("C. Real recorded runs (metrics read verbatim from traces)")
    # show_trace(load("<trace-a>.json"), "Run A — ...")
    # show_trace(load("<trace-b>.json"), "Run B — ...")

    _print("\n[dim]In the real system the model-driven steps are <list them>; this demo runs none "
           "of them — it shows one deterministic step and replays recorded metrics. "
           "Not the full engine.[/dim]")


if __name__ == "__main__":
    main()

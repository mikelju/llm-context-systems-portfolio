#!/usr/bin/env python3
"""
Agentic Document Q&A Bot (n8n + Gemini File API + memory) — offline demo.

Runs offline (no API key, no network) over the real, sanitized artifacts in ../artifacts.
It reproduces TWO deterministic rules that are genuinely part of the system:

  Step 1 — the router/menu state machine (per-user mode in n8n Static Data), and
           the tool-first boundary classifier (which nodes call the model).

Then it replays the recorded runs (tool-path vs refuse-path) and the Phase-4 validation
battery, with numbers read verbatim from the traces.

Honesty note: this demo DOES NOT call any model and needs no API key. The 3 model/File-API
steps (Gemini SELECT, File-API upload/poll, Gemini ANSWER) are not run here — they are
represented only by the recorded outcomes. It is not the full engine.

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

HERE = Path(__file__).resolve().parent
ART = (HERE.parent / "artifacts").resolve()

def _print(t=""):
    if _RICH: _con.print(t)
    else: print(re.sub(r"\[/?[a-z0-9 ._#]+\]", "", t))

def _rule(t):
    if _RICH: _con.rule(f"[bold]{t}")
    else: print("\n" + "=" * 72 + f"\n {t}\n" + "=" * 72)

def load(name): return json.loads((ART / name).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# (a) STATE OVERVIEW — the catalog + the agent, read from artifacts
# --------------------------------------------------------------------------- #
def show_state():
    cat = load("catalog-sample.json")
    docs = cat["documents"]
    pages = sum(d["page_count"] for d in docs)
    _rule("A. The library (catalog.json) + the agent")
    _print(f"  {len(docs)} documents in the catalog · {pages} pages total · "
           f"{len(cat['_rejected_examples'])} over-limit PDFs rejected (20-page rule)")
    _print(f"  [dim]e.g. {docs[0]['title']} — {docs[0]['page_count']} pages · "
           f"id {docs[0]['document_id']}[/dim]")
    arch = load("agent-architecture.json")
    a = arch["agents"][0]
    _print(f"  agent: {a['model']} · memory: {a['memory'].split('(')[0].strip()} · "
           f"tools: {', '.join(t.split(' (')[0] for t in a['tools'])}")
    _print(f"  router: {arch['router']['type']} — {arch['router']['mechanism']}")


# --------------------------------------------------------------------------- #
# (b1) LIVE STEP 1a — the real router/menu state machine (deterministic)
#      Reproduces the per-user mode logic stored in n8n Static Data.
# --------------------------------------------------------------------------- #
def route(mode, kind, payload):
    """The deterministic routing rule (WF-Principal Switch_Menu/FieldBot/DocBot + Static Data)."""
    if kind == "command" and payload in ("/start", "/menu"):
        return None, "show menu (reset mode)"
    if kind == "callback" and payload.startswith("mode_"):
        m = payload.split("_", 1)[1]
        return m, f"set per-user mode = {m}; send confirmation"
    if kind == "text":
        if mode == "docbot":
            return mode, "route -> DocBot agent -> consultar_biblioteca (Steps 2-6)"
        if mode == "fieldbot":
            return mode, "route -> FieldBot agent (intervention history)"
        return None, "no mode set -> show menu"
    return mode, "ignore"

def live_router():
    _rule("B. Step 1 reproduced live — router/menu state machine (deterministic, offline)")
    events = [
        ("command", "/start"),
        ("callback", "mode_docbot"),
        ("text", "boilers at the Site B installation?"),
        ("callback", "mode_fieldbot"),
        ("text", "last intervention at Site C?"),
        ("command", "/menu"),
    ]
    mode = None
    rows = []
    for kind, payload in events:
        mode, action = route(mode, kind, payload)
        rows.append((f"{kind}:{payload}", str(mode), action))
    if _RICH:
        t = Table(show_header=True, header_style="bold green")
        for c in ("event", "mode after", "deterministic route"): t.add_column(c)
        for r in rows: t.add_row(*r)
        _con.print(t)
    else:
        for ev, md, ac in rows:
            print(f"  {ev:<32} mode={md:<9} {ac}")
    _print("  [dim]The model does NOT decide the route — it is plain Code + Switch + Static Data.[/dim]")


# --------------------------------------------------------------------------- #
# (b2) LIVE STEP 1b — the tool-first boundary classifier (deterministic)
#      Reads the real node list and proves the model is called exactly twice.
# --------------------------------------------------------------------------- #
def live_boundary():
    _rule("B. Step 1 reproduced live — the LLM boundary, counted from the real nodes")
    tool = load("tool-structure.json")
    nodes = tool["nodes"]
    by = {"deterministic": 0, "llm": 0, "io": 0}
    llm_nodes = []
    for n in nodes:
        by[n["boundary"]] += 1
        if n["boundary"] == "llm": llm_nodes.append(n["name"])
    _print(f"  WF-DocBot-Tool: {len(nodes)} functional nodes -> "
           f"{by['deterministic']} deterministic · {by['llm']} LLM · {by['io']} io")
    _print(f"  the {by['llm']} model calls are the ONLY judgment steps:")
    for nm in llm_nodes:
        _print(f"    - {nm}")
    m = tool["metrics"]
    assert m["llm_judgment_calls"] == by["llm"] == 2, "boundary mismatch"
    _print("  [dim]Recomputed live from the artifact and matches the recorded metric "
           f"(llm_judgment_calls={m['llm_judgment_calls']}).[/dim]")


# --------------------------------------------------------------------------- #
# (c) RECORDED RUNS — funnel + metrics read verbatim from the traces
# --------------------------------------------------------------------------- #
def show_runs():
    _rule("C. Recorded runs (read verbatim from the traces)")
    qr = load("query-runs.json")
    _print(f"  library: {qr['library_docs']} documents")
    for r in qr["runs"]:
        _print(f"\n  [bold]{r['id']}[/bold] — \"{r['query']}\"")
        _print(f"    in-domain={r['in_domain']} · tool_invoked={r['tool_invoked']} · "
               f"outcome: {r['outcome']}")
    m = qr["metrics"]
    _print(f"\n  per query: {m['llm_judgment_calls_per_query']} model calls (select + answer) · "
           f"{m['fileapi_io_calls_per_selected_doc']} File-API io per selected doc")
    _print(f"  typical latency: under {m['latency_typical_small_lib_seconds']} seconds (1-3 docs), "
           f"under {m['latency_typical_large_lib_seconds']} seconds (5+ docs)")

    vb = load("validation-battery.json")["metrics"]
    _print(f"\n  Phase-4 battery: {vb['passed']}/{vb['total_cases']} pass "
           f"({vb['failed']} fail) over {vb['library_docs']} docs · "
           f"{vb['negative_cases_recorded']} negative cases recorded (off-topic -> clean refusal)")


def main():
    _print("[bold magenta]Agentic Document Q&A Bot — offline demo[/bold magenta]")
    _print("[dim]Real, sanitized artifacts. No API key, no network, no model call.[/dim]")
    show_state()
    live_router()
    live_boundary()
    show_runs()
    _print("\n[dim]Not run here (need the live API): Step 3 Gemini SELECT, Step 4 File-API "
           "upload/poll, Step 5 Gemini ANSWER. This demo does not call any model and is "
           "not the full engine — it runs the deterministic rules and replays recorded metrics.[/dim]")


if __name__ == "__main__":
    main()

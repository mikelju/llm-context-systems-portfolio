# Runnable demo — offline

Runs **offline, no API key, no network, no model call**, using the sanitized artifacts in
[`../artifacts`](../artifacts).

## What it does
1. **State overview** — the catalog (15 docs, real page counts) and the agent (model, memory, tools).
2. Two **live deterministic steps**, both genuinely part of the system (labelled offline reproductions):
   - the **router/menu state machine** (per-user mode in n8n Static Data) — Step 1 of the loop;
   - the **boundary classifier** — reads the real node list and proves the model is called **exactly
     twice** in `WF-DocBot-Tool`.
3. The **recorded runs** (tool-path vs refuse-path) + the Phase-4 battery (9/10), read verbatim.

> **Honesty note.** The model-driven steps are Step 3 (Gemini SELECT), Step 4 (File-API upload/poll) and
> Step 5 (Gemini ANSWER). The demo runs **none** of them; it reproduces the deterministic routing/boundary
> rules and replays recorded metrics. It **does not call any model** and is **not** the full engine.

## Run it
```bash
python -m venv .venv && . .venv/Scripts/activate   # (or source .venv/bin/activate)
pip install -r requirements.txt                    # optional — only `rich` for prettier output
python run_demo.py
```
Self-test (both must exit 0 and print the caveat): `python run_demo.py` and a no-`rich` run
(`python -c "import sys;sys.modules['rich']=None;import runpy;runpy.run_path('run_demo.py',run_name='__main__')"`).
Re-capture before done: `python run_demo.py > example_output.txt`.

## Expected output
See [`example_output.txt`](example_output.txt) — note the router transitions and that the boundary
classifier recomputes `2` model calls and matches the recorded metric.

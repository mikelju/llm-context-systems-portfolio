<!-- Spec §8. -->
# Runnable demo — offline

Runs **offline, no API key, no network**, using the sanitized artifacts in [`../artifacts`](../artifacts).

## What it does
1. State overview (from the structured artifact).
2. One **live deterministic step** — a rule genuinely in the system (NOT a generic stand-in),
   labelled an approximation.
3. The **funnel + real metrics** read verbatim from the recorded traces.

> **Honesty note.** The model-driven steps are <list>. The demo runs none of them; it reproduces one
> deterministic step and replays recorded metrics. It is **not** the full engine. When the live step
> diverges from the recorded run, the divergence is printed inline.

## Run it
```bash
python -m venv .venv && . .venv/Scripts/activate   # (or source .venv/bin/activate)
pip install -r requirements.txt                    # optional — only `rich` for prettier output
python run_demo.py
```
Self-test (both must exit 0 and print the caveat): `python run_demo.py` and a no-`rich` run.
Re-capture before done: `python run_demo.py > example_output.txt`.

## Expected output
See [`example_output.txt`](example_output.txt).

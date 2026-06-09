#!/usr/bin/env python3
"""
sanitize.py — apply an out-of-repo glossary to a case study's text artifacts.

The mapping {real_term: replacement} MUST live OUTSIDE the repo (it contains the real
client terms). This script reads it, applies every replacement (longest first, so
multi-word terms win), to every text file under a target folder, in place.

Usage:
    python case-studies/_scripts/sanitize.py 01-rag-knowledge-system ../private/map.json
    # map.json: {"Real Client S.L.": "an industrial supplier (client)", "Pamplona": "[location]"}

After running, ALWAYS run verify_case_study.py (with --real-terms pointing at the map's
keys, and --history) before committing. This script does NOT regenerate ids, coarsen dates,
or strip binary metadata — do those per CASE_STUDY_SPEC.md §6.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEXT_EXT = {".md", ".py", ".json", ".txt", ".yml", ".yaml", ".ini", ".cfg", ".toml"}

def main():
    if len(sys.argv) != 3:
        print("usage: sanitize.py <case-slug-or-path> <out-of-repo-map.json>"); sys.exit(2)
    target = Path(sys.argv[1])
    if not target.is_dir():
        target = ROOT / "case-studies" / sys.argv[1]
    mapping = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    # longest keys first so 'Foo Bar S.L.' is replaced before 'Foo'
    pairs = sorted(mapping.items(), key=lambda kv: len(kv[0]), reverse=True)
    changed = 0
    for p in target.rglob("*"):
        if not (p.is_file() and p.suffix.lower() in TEXT_EXT): continue
        if ".venv" in p.parts or "__pycache__" in p.parts: continue
        body = p.read_text(encoding="utf-8")
        new = body
        for real, repl in pairs:
            new = new.replace(real, repl)
        if new != body:
            p.write_text(new, encoding="utf-8"); changed += 1
            print(f"  sanitized {p.relative_to(target)}")
    print(f"\n{changed} file(s) changed. Now: regenerate ids, coarsen dates, strip binaries, then verify.")

if __name__ == "__main__":
    main()

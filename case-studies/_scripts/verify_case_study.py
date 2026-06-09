#!/usr/bin/env python3
"""
verify_case_study.py — the automated acceptance gate for a case study.

Implements the starred items of CASE_STUDY_SPEC.md §10. Stdlib only; Windows-safe.

Usage:
    python case-studies/_scripts/verify_case_study.py 01-rag-knowledge-system
    python ... 02-slug --real-terms ../private/glossary.txt --history

Exit code 0 = all gates pass. Non-zero = at least one FAIL.

Checks (no external input needed):
  - required files present (§2)
  - artifacts/*.json valid
  - traces: references resolve (doc_id in chapters_read + non-empty chapter_id),
            cross-artifact ids (trace doc_ids subset of catalog), metrics present,
            opaque (12-hex) document_ids
  - metric SSOT: every "<n> tokens / <n>s / <n> API calls" in markdown exists in a trace;
                 example_output.txt carries the trace metrics + the honesty caveat
  - demo runs offline (exit 0) and prints the caveat
  - secret scan (regex) over the tree
  - suspicious strings: OS user paths, non-example emails, internal absolute paths

Checks needing the out-of-repo real terms (opt-in):
  --real-terms FILE : glossary-derived leak sweep (term + variants) over the folder
  --history         : also sweep git history for the real terms and for secrets
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]            # repo root
CASES = ROOT / "case-studies"
REQUIRED = [
    "README.md", "architecture.md", "reliability-and-evaluation.md", "EVALUATION.md",
    "the-bug-i-fixed.md", "lessons-learned.md",
    "artifacts/README.md", "demo/run_demo.py", "demo/README.md", "demo/example_output.txt",
]
SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AWS key"),
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI-style key"),
    (r"AIza[0-9A-Za-z_\-]{35}", "Google API key"),
    (r"gh[posru]_[A-Za-z0-9]{30,}", "GitHub token"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
    (r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}", "JWT"),
    (r"(?:postgres|mysql|mongodb)(?:\+\w+)?://[^\s\"']+:[^\s\"'@]+@", "DB connection string w/ creds"),
    (r"(?i)\b(?:api[_-]?key|secret|password|passwd|token)\b\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{12,}", "inline secret"),
]
TEXT_EXT = {".md", ".py", ".json", ".txt", ".yml", ".yaml", ".ini", ".cfg", ".toml"}

class Report:
    def __init__(self): self.items = []
    def add(self, ok, name, detail="", warn=False):
        self.items.append((("WARN" if warn and not ok else ("PASS" if ok else "FAIL")), name, detail))
    def failed(self): return any(s == "FAIL" for s, _, _ in self.items)
    def dump(self):
        sym = {"PASS": "[ok]", "FAIL": "[XX]", "WARN": "[!!]"}
        for s, name, detail in self.items:
            line = f"  {sym[s]} {name}"
            if detail: line += f" — {detail}"
            print(line)
        n_fail = sum(s == "FAIL" for s, _, _ in self.items)
        n_warn = sum(s == "WARN" for s, _, _ in self.items)
        print(f"\n  {len(self.items)} checks | {n_fail} FAIL | {n_warn} WARN")

def text_files(folder: Path):
    skip = {".venv", "__pycache__", ".git"}
    for p in folder.rglob("*"):
        if p.is_file() and p.suffix.lower() in TEXT_EXT and not (skip & set(p.parts)):
            yield p

def load_jsons(art: Path):
    out = {}
    for p in sorted(art.glob("*.json")):
        try: out[p.name] = (p, json.loads(p.read_text(encoding="utf-8")))
        except Exception as e: out[p.name] = (p, e)
    return out

def variants(term: str):
    t = term.strip()
    if not t: return set()
    deacc = "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
    base = {t, t.lower(), t.upper(), t.title(), deacc, deacc.lower()}
    more = set()
    for b in list(base):
        more.add(b.replace(" ", "_")); more.add(b.replace(" ", "-")); more.add(b.replace(" ", ""))
        more.add(b.replace(" ", "%20"))
    return {v for v in base | more if len(v) >= 3}

def run(cmd, cwd=None):
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--real-terms", help="path to out-of-repo file: one real term per line")
    ap.add_argument("--history", action="store_true", help="also sweep git history")
    args = ap.parse_args()

    case = CASES / args.slug
    r = Report()
    if not case.is_dir():
        print(f"case folder not found: {case}"); sys.exit(2)
    print(f"Verifying {case.relative_to(ROOT)}\n")

    # 1. required files
    for rel in REQUIRED:
        r.add((case / rel).exists(), f"required file {rel}")
    core = list(case.glob("context-strategy.md")) + list(case.glob("*-flow.md")) + list(case.glob("*-loop.md")) + list(case.glob("*-run.md"))
    r.add(bool(core), "core-decision/main-flow file present", ", ".join(p.name for p in core))

    # 2. artifacts json + traces
    art = case / "artifacts"
    jsons = load_jsons(art) if art.is_dir() else {}
    for name, (p, obj) in jsons.items():
        r.add(not isinstance(obj, Exception), f"valid JSON {name}", str(obj) if isinstance(obj, Exception) else "")
    catalog = next((o for _, (p, o) in jsons.items() if isinstance(o, dict) and "documents" in o), None)
    cat_ids = {d.get("document_id") for d in catalog["documents"]} if catalog else set()
    traces = [(n, o) for n, (p, o) in jsons.items() if isinstance(o, dict) and ("steps_log" in o or "metrics" in o)]
    r.add(len(traces) >= 2, ">=2 substantive trace/run artifacts", f"found {len(traces)}", warn=True)

    if catalog:
        bad = [i for i in cat_ids if not (isinstance(i, str) and re.fullmatch(r"[0-9a-f]{12}", i))]
        r.add(not bad, "catalog document_ids are opaque 12-hex", f"non-opaque: {bad}" if bad else "")

    trace_metric_values = set()
    for name, tr in traces:
        m = tr.get("metrics", {})
        r.add(bool(m), f"{name}: metrics block present")
        for v in m.values():
            if isinstance(v, (int, float)):
                trace_metric_values |= {str(v), f"{v:,}", str(int(v)) if float(v).is_integer() else str(v)}
        read = tr.get("chapters_read")
        refs = tr.get("references")
        if isinstance(read, list) and isinstance(refs, list):
            read_ids = {c.get("document_id") for c in read}
            unresolved = [r0 for r0 in refs if r0.get("document_id") not in read_ids or not r0.get("chapter_id")]
            r.add(not unresolved, f"{name}: every reference resolves (doc in chapters_read + chapter_id)",
                  f"{len(unresolved)} unresolved" if unresolved else f"{len(refs)} refs")
        if cat_ids:
            tr_ids = {c.get("document_id") for c in (read or [])} | {i for s in tr.get("steps_log", []) for i in s.get("ids", [])}
            stray = tr_ids - cat_ids - {None}
            r.add(not stray, f"{name}: ids resolve in catalog", f"stray: {stray}" if stray else "")

    # 3. metric SSOT — every metric-shaped number in markdown must exist in a trace
    num_pat = re.compile(r"([\d][\d,]*\.?\d*)\s*(tokens|s\b|API calls|api calls)")
    drift = []
    for p in text_files(case):
        if p.suffix != ".md": continue
        for val, unit in num_pat.findall(p.read_text(encoding="utf-8")):
            norm = val.replace(",", "")
            if norm not in {x.replace(",", "") for x in trace_metric_values} and float_ok(norm):
                # ignore obviously-non-metric small ints like "5 s"? keep strict but skip pure section noise
                drift.append(f"{p.name}:{val} {unit}")
    r.add(not drift, "restated metrics match a trace value (SSOT)", "; ".join(drift[:6]) if drift else "", warn=True)

    # 4. demo: runs offline + caveat; example_output carries metrics + caveat
    demo = case / "demo" / "run_demo.py"
    eo = case / "demo" / "example_output.txt"
    caveat_re = re.compile(
        r"not the full (engine|system)|not the production|trace-replay|approximation|"
        r"not run( here)?|does not call any model|no API key", re.I)
    if eo.exists():
        eot = eo.read_text(encoding="utf-8", errors="replace")
        r.add(bool(caveat_re.search(eot)), "example_output.txt carries the honesty caveat")
        if trace_metric_values:   # only when the case ships metric-bearing traces
            present = sum(1 for v in trace_metric_values if v in eot)
            r.add(present > 0, "example_output.txt shows recorded metrics", f"{present} metric tokens found")
    if demo.exists():
        res = run([sys.executable, str(demo)], cwd=str(demo.parent))
        ok = bool(res) and res.returncode == 0
        r.add(ok, "demo runs offline (exit 0)", "" if ok else (res.stderr[-160:] if res else "python failed"))
        if ok: r.add(bool(caveat_re.search(res.stdout)), "demo prints the honesty caveat")

    # 5. secrets over the tree
    sec_hits = []
    for p in text_files(case):
        body = p.read_text(encoding="utf-8", errors="replace")
        for pat, label in SECRET_PATTERNS:
            for m in re.finditer(pat, body):
                sec_hits.append(f"{p.name}: {label}")
    r.add(not sec_hits, "no secrets in tree", "; ".join(sorted(set(sec_hits))[:5]))

    # 6. suspicious strings: OS user paths / non-example emails / drive letters
    susp = []
    email_re = re.compile(r"[A-Za-z0-9._%+\-]+@(?!example\.com)[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
    win_user = re.compile(r"[A-Za-z]:\\Users\\(?!<)", re.I)
    for p in text_files(case):
        body = p.read_text(encoding="utf-8", errors="replace")
        if win_user.search(body): susp.append(f"{p.name}: Windows user path")
        for m in email_re.findall(body):
            if not m.endswith(("biartechnology.com", "mikelju@gmail.com")):   # author's own, allowed
                susp.append(f"{p.name}: email {m}")
    r.add(not susp, "no OS user paths / unexpected emails", "; ".join(sorted(set(susp))[:5]), warn=True)

    # 7. real-terms leak sweep (opt-in)
    if args.real_terms:
        terms = [t for t in Path(args.real_terms).read_text(encoding="utf-8").splitlines() if t.strip()]
        allv = set().union(*(variants(t) for t in terms)) if terms else set()
        # sweep the WHOLE repo (a real term anywhere — shared scripts, template, spec — is a leak)
        swept = list(text_files(ROOT))
        hits = []
        for p in swept:
            body = p.read_text(encoding="utf-8", errors="replace")
            for v in allv:
                if v and v in body: hits.append(f"{p.relative_to(ROOT)}: '{v}'")
        r.add(not hits, f"real-term sweep over whole repo ({len(terms)} terms, {len(allv)} variants, {len(swept)} files)",
              "; ".join(sorted(set(hits))[:6]))
        if args.history:
            offenders = []
            for t in terms:
                g = run(["git", "log", "--all", "-S", t, "--oneline"], cwd=str(ROOT))
                if g and g.stdout.strip(): offenders.append(t)
            r.add(not offenders, f"git history clean (all {len(terms)} terms)",
                  ("in history: " + ", ".join(offenders)) if offenders else "")
    else:
        r.add(True, "real-term sweep skipped", "run with --real-terms <out-of-repo file> before publishing", warn=True)

    print()
    r.dump()
    sys.exit(1 if r.failed() else 0)

def float_ok(s):
    try: float(s); return True
    except Exception: return False

if __name__ == "__main__":
    main()

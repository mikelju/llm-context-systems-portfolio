#!/usr/bin/env python3
"""
Multimodal RAG (page-as-image) — offline demo.

Runs the REAL vector retrieval offline (no API key, no network) over a 120-page
sample of the real embedding index (public boiler manuals, gemini-embedding-2,
dim 1536, L2-normalized). It computes cosine top-K live, and replays the full-index
nearest-neighbour results recorded in ../artifacts/retrieval-example.json.

Honesty note: the natural-language query path (embed the question, then answer with
a vision LLM) needs the live API and was not archived. This demo seeds the search
from an INDEXED page to show the vector space itself; it does not call any model and
is not the full system.

Run:    python run_demo.py
Capture: python run_demo.py > example_output.txt
"""
from __future__ import annotations
import ast, array, json, re, sys
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

def load_npy(path: Path):
    """Minimal .npy reader (stdlib only) so the demo runs with zero dependencies."""
    with open(path, "rb") as f:
        assert f.read(6) == b"\x93NUMPY"
        f.read(2)                                    # version
        hlen = int.from_bytes(f.read(2), "little")
        header = ast.literal_eval(f.read(hlen).decode("latin1").strip())
        rows, cols = header["shape"]
        a = array.array("f"); a.frombytes(f.read())  # '<f4' little-endian float32
    return [a[i * cols:(i + 1) * cols] for i in range(rows)], rows, cols

def dot(a, b): return sum(x * y for x, y in zip(a, b))   # vectors are L2-normalized -> cosine

def top_k(vecs, seed, k=5):
    scores = [(dot(vecs[seed], vecs[j]), j) for j in range(len(vecs)) if j != seed]
    scores.sort(reverse=True)
    return scores[:k]


def main():
    _print("[bold magenta]Multimodal RAG (page-as-image) — offline demo[/bold magenta]")
    _print("[dim]Real embeddings, real cosine search. No API key required.[/dim]")

    stats = load("index-sample.json")["stats"]
    _rule("A. The real index")
    _print(f"  {stats['documents']} documents · {stats['pages_embedded']:,} pages embedded · "
           f"model={stats['embedding_model']} · dim={stats['dim']} · top_k={stats['top_k']}")
    _print("  [dim]Each page is embedded AS AN IMAGE (preserves tables/diagrams). "
           "Retrieval = cosine over the page vectors.[/dim]")

    meta = load("retrieval-demo-meta.json")["rows"]
    vecs, rows, cols = load_npy(ART / "retrieval-demo-vectors.npy")
    _rule(f"B. Live cosine top-K over a {rows}-page sample (offline, real vectors)")
    seed = 0
    s = meta[seed]
    _print(f"  seed page: {s['file']} (p{s['page']})")
    if _RICH:
        t = Table(show_header=True, header_style="bold green")
        for c in ("rank", "score", "file", "page"): t.add_column(c)
        for rank, (sc, j) in enumerate(top_k(vecs, seed), 1):
            t.add_row(str(rank), f"{sc:.3f}", meta[j]["file"][:48], str(meta[j]["page"]))
        _con.print(t)
    else:
        for rank, (sc, j) in enumerate(top_k(vecs, seed), 1):
            print(f"  {rank}. {sc:.3f}  {meta[j]['file'][:48]} p{meta[j]['page']}")
    _print("  [dim]Nearest pages cluster around the same model/topic — the vector space works.[/dim]")

    _rule("C. Recorded nearest-neighbour results over the FULL index (6,896 pages)")
    for ex in load("retrieval-example.json")["examples"]:
        sd = ex["seed"]
        _print(f"\n  seed: {sd['file']} (p{sd['page']})")
        for r in ex["nearest"]:
            _print(f"    {r['score']:.3f}  {r['file']} (p{r['page']})")

    _print("\n[dim]This shows the deterministic retrieval core on real data. The NL-query "
           "embedding and the vision-LLM answer step use the live API and are not run here. "
           "Not the full system.[/dim]")


if __name__ == "__main__":
    main()

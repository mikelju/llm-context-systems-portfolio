# Authoring scripts

Shared tooling for building and verifying a case study. See
[`../CASE_STUDY_SPEC.md`](../CASE_STUDY_SPEC.md).

## `sanitize.py` — apply the anonymization glossary

```bash
python case-studies/_scripts/sanitize.py <case-slug> <out-of-repo map.json>
```

The **real → token map** must live **outside the repo** (it contains the real client terms). Format:

```json
{
  "Real Client S.L.": "an industrial supplier (client)",
  "Pamplona": "[location]",
  "Real Site Name": "Site A"
}
```

It replaces longest keys first and rewrites text files in place. It does **not** regenerate ids,
coarsen dates, or strip binary metadata — do those per spec §6.

> The in-repo `_glossary.json` (committed) holds only the **token vocabulary** + reasons, never the
> real terms. The map above stays private.

## `verify_case_study.py` — the acceptance gate

```bash
python case-studies/_scripts/verify_case_study.py <case-slug>
# before publishing, add the leak/history sweeps with the out-of-repo terms:
python case-studies/_scripts/verify_case_study.py <case-slug> --real-terms ../private/terms.txt --history
```

Exit 0 = all gates pass. It checks: required files; JSON validity; trace reference resolution +
cross-artifact id consistency + opaque ids; metric single-source-of-truth; the demo runs offline and
prints the honesty caveat; a secret regex scan; suspicious paths/emails; and (with `--real-terms`)
the glossary-derived leak sweep + git-history sweep.

`--real-terms` file = one real term per line (out-of-repo). Run this pass **before the first push**.

## Typical flow

```bash
cp -r case-studies/_TEMPLATE case-studies/02-slug
python case-studies/_scripts/sanitize.py 02-slug ../private/map.json
# regenerate ids / coarsen dates / strip binaries; write docs; wire demo; capture example_output.txt
python case-studies/_scripts/verify_case_study.py 02-slug
```

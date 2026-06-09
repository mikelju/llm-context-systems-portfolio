# Case Study Standard → moved

The canonical authoring standard now lives at
**[`case-studies/CASE_STUDY_SPEC.md`](case-studies/CASE_STUDY_SPEC.md)**.

It supersedes and absorbs the earlier draft that lived here. The canonical version is **enforced by
tooling**, not prose alone:

- a copy-from scaffold: [`case-studies/_TEMPLATE/`](case-studies/_TEMPLATE/)
- an automated acceptance gate: [`case-studies/_scripts/verify_case_study.py`](case-studies/_scripts/verify_case_study.py)
- a glossary-driven sanitizer: [`case-studies/_scripts/sanitize.py`](case-studies/_scripts/sanitize.py)

It also tightens a few rules the earlier draft left loose (flagged by an adversarial review): IDs must
be **regenerated and consistent across artifacts** (not "kept if they identify nothing"); pinpoint
calendar **dates are coarsened**; the **negative/refusal case must be recorded** (not perpetually
pending); traceability counts only **resolvable** references; metrics have a **single source of
truth**; and anonymization is verified by **scripted git-history + secret + glossary sweeps**.

See [`case-studies/CASE_STUDY_SPEC.md`](case-studies/CASE_STUDY_SPEC.md).

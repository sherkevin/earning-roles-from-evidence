# S-518 AAMAS rebuild: execution record

Historical first-pass record. The user-requested consolidated [REQUIREMENTS.md](../../paper/aamas2027/REQUIREMENTS.md) and [AAMAS_TASKS.md](../../coordination/AAMAS_TASKS.md) now govern the project. They correct first-pass overclosure and design assumptions; the seven-card handoff below is superseded, and its old location redirects to the active ledger.

Date: 2026-09-16. Owner: scientist / writing lead. Status: DONE / INITIAL RECONSTRUCTION. Overall AAMAS empirical rebuild: OPEN. No submission-ready claim.

## Scope and preservation

The user requests a substantive revision after the EMNLP 2026 / ARR rejection and a move to AAMAS. The current target is AAMAS 2027, verified on the Warwick-hosted conference website. Existing uncommitted files and the original ACL manuscript are preserved. New manuscript work goes into `article/aamas2027/`; source downloads go into `references/aamas/`.

## Confirmed early findings

- Actual reviews were read from `EMNLP2026-OpenReview-审稿意见汇总.md`, separately from earlier internal simulated reviews. AC score: 2; reviewer overall scores: 3, 2.5, 1, 1.5.
- The old paper conflates scalar calibration, a task-tree mechanism, and three dataset-specific adaptive routers. Same backbone/context/scorer is not equal inference compute and does not isolate learned organization.
- `workspace/idea04_core/runner.py:63` limits persistent competence to `fixed_peer_calibrated` and `fixed_self_calibrated`. The per-sample initializer resets other methods. Cross-episode role emergence cannot be inferred from the headline adaptive-router table.
- `workspace/idea04_core/methods.py:2186` selects protocols from question type and dataset hint. This is evidence of a heuristic router, not by itself learned division of labor.
- The constant-step EMA claim in the old manuscript is false in general: nonzero observation noise leaves limiting variance `mu * sigma^2 / (2 - mu)`, rather than L2 convergence to the mean.
- The historical HotpotQA `.7641` row uses GPT-4.1-mini on 200 examples; the `.4324` headline uses Qwen2.5-3B on 7,405 examples. They are different evaluation populations/backbones.
- Existing Qwen component evidence includes neutral all-tools/random-tools/tool-history removals and a harmful isolated audit. These must be visible, not omitted from a necessity claim.

## Immediate schedule

Official main-track page: https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/call-for-main-track/

- OpenReview author registration: 2026-09-17 AoE.
- Abstract: 2026-10-01 AoE.
- Full paper: 2026-10-08 AoE (2026-10-09 19:59:59 Asia/Shanghai).
- Rebuttal: 2026-11-20 through 2026-11-24 AoE.
- Notification: 2026-12-21. Camera-ready: 2027-01-25.

## Delivered artifacts

- [Venue requirements and calendar](../../paper/aamas2027/VENUE_REQUIREMENTS.md): official 2027 rules, AoE conversions, GAAI placement, reciprocal reviewing, Findings, anonymity, and AI disclosure.
- [Downloaded sources](../../../references/aamas/README.md): 30 manifest entries with source URLs and SHA256 values, official template ZIP, 2024--2026 proceedings/awards, 12 full related-paper PDFs and extracted text.
- [Independent positioning memo](S-518_AAMAS_positioning_20260916.md): delegation as the scientific object, code-to-claim mismatch, closest alternatives, accepted-paper comparison, and falsifiable contribution.
- [Actual reviewer action matrix](S-518_reviewer_action_matrix_20260916.md): distinguishes completed writing/audit work from experimental requests still open.
- [New LaTeX manuscript and build instructions](../../../article/aamas2027/README.md): a six-page main draft and two-page supplement using the unmodified official class. Proposed title: *When Should an Agent Earn Delegation? Evidence, Reputation, and Coordination in Language-Agent Teams*.
- [Offline evidence audit](../../../artifacts/analysis/s518_aamas_audit_20260916/summary.md): 24,815 rows reproduced, component evidence, missing-cost boundaries, and an actual failed audit trace. Official HotpotQA rescoring changes six rows and the router F1 from 0.432403 to 0.432275; it does not establish official paired deltas until comparator outputs are recovered/rescored.
- [Engineering handoff](../handoffs/S-518_to_engineer_AAMAS_experiments_20260916.md): AAMAS-E01--E07, in order, with acceptance criteria and proposed schedule. These are written project tasks; no separate agent or external message was dispatched.
- [Submission gate](../../paper/aamas2027/submission_gate.json) and [AI assistance record](../../paper/aamas2027/AI_ASSISTANCE_RECORD.md): unresolved evidence/author fields are explicit. Format check is verified; scientific gates remain pending.

## Validation performed

Commands run from the repository root:

```powershell
python scripts/aamas_audit_evidence.py
python scripts/build_aamas2027.py
python scripts/build_aamas2027.py --submission
pdffonts article/aamas2027/build/main.pdf
pdffonts article/aamas2027/build/supplement.pdf
git diff --numstat -- article/latex/edo_paper.tex article/latex/edo_appendix.tex
```

The offline audit and normal build passed. The `--submission` command intentionally returned a nonzero result because the empirical and author metadata gates remain open. Main: 6 total pages; supplement: 2 pages. Both have zero unresolved references and zero overfull boxes; all fonts are embedded Type 1, with no Type 3 fonts. PDF author metadata is empty. The three official support files match the downloaded template byte for byte. All eight rendered pages were visually inspected, with no clipped or overlapping content. [Build verification](../../../article/aamas2027/build/verification.json) records PDF hashes and metadata.

The TeX Live 2024 build produces an incomplete `ifx` conditional warning from the official style and a column-balancing warning. The untouched official example reproduces the conditional warning in [the template smoke build](../../../artifacts/analysis/s518_aamas_audit_20260916/template_smoke/). PDFs compile and render correctly; no style patch was applied or warning-free build claimed.

All 30 archived source hashes were checked. Exact finite-outcome enumeration verified the EMA mean/variance formula for three parameter settings; this is a mathematical sanity check, not an experiment supporting delegation utility. [Math check](../../../artifacts/analysis/s518_aamas_audit_20260916/math_sanity_check.json). The original ACL paper/appendix show no diff attributable to this task. Pre-existing uncommitted work is preserved; no commit, push, external submission, paid inference, or remote benchmark was performed.

## Evidence boundary and next action

The deliverable is a substantive internal reconstruction, not a completed new empirical paper. The historical QA protocols and newly proposed persistent delegation protocol are different objects. Do not transfer the historical scores to the new method, describe planned interventions as results, or remove internal-status wording to create an appearance of readiness.

Next: AAMAS-E01 must reconcile scorer/data/runtime provenance and audit transitions; AAMAS-E02 must implement persistent local allocation state and complete budget accounting. Then execute matched frozen/shuffled/reset/direct/bandit and nearest-method comparisons over independently reset streams, followed by stronger-model and non-QA evidence. The author account deadline is Sep 17 AoE; account/reviewer/Findings decisions remain author-owned. Reassess the supported contribution by Sep 29 before committing the abstract. If the primary hypothesis fails, narrow or change the claim openly.

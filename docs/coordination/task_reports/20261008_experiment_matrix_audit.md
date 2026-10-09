# Task report — experiment-matrix audit and layout candidate

Date: 2026-10-08  
Status: partial — presentation candidate passes build checks; scientific
benchmark/baseline and results gates remain open.

## Objective

Check whether the experiment-matrix tables are comparable in role, density, and
evidence scale to strong recent AAMAS/ICML/ACL papers, then make a reversible
layout improvement without changing the benchmark, baseline, estimands, or
scientific Goal.

## Evidence reviewed

- Current source: `article/aamas2027/main.tex`, source snapshot recorded in
  `experiments/logs/experiment_matrix_audit_20261008/source_snapshot/`.
- Current canonical PDF: `artifacts/aamas2027/main.pdf`.
- Local compiled comparison samples: CollabLLM (ICML 2025 oral/best-gallery
  sample), MultiAgentBench (ACL 2025), and Cross-environment Cooperation (ICML
  2025). Their hashes and paths are in
  `experiments/logs/experiment_matrix_audit_20261008/config.json`.
- Visual review: current pages 5–7 and candidate page 7 rendered at 160 dpi.

No API, benchmark, GPU, or LLM experiment was run.

## Finding

The current Table 4 is scientifically broad but visually miscast. It combines
RQ routing, root identity, policy, fairness controls, metric lists, and an empty
result column in a six-column `\scriptsize` grid. Table 5 then repeats the empty
result state as three blank value columns. This produces a page that is dense in
prose but contains no empirical payload. The comparison papers instead use a
small setup/protocol description, a numeric hero table with grouped metrics and
best-value emphasis, and separate ablation/resource tables; implementation
detail is moved to an appendix or artifact.

The main gap is therefore table **role**, not the number of planned experiments.
The nine detailed cells are retained scientifically, but the main paper should
show a four-row RQ overview and reserve result-table space for measured values.
The exact nine-cell execution manifest is now preserved at
`docs/paper/aamas2027/EXPERIMENT_MATRIX_EXECUTION_MANIFEST_20261008.md`.

The scale check is concrete: the inspected CollabLLM table carries about 54
numeric cells (6 methods × 3 task groups × 3 metrics), and MultiAgentBench about
60 (5 models × 6 task groups × 2 metrics). The old matrix also occupied roughly
54 cells, but all were prose and 0 were measurements. Its visual size therefore
overstated its evidence scale.

## Candidate v2 → v3

The main source now uses:

1. a four-row, five-column overview (`RQ`, track/unit, contrast, primary
   endpoint, stress/split) at `\small` size;
2. a four-row primary endpoint contract (`H1`–`H4`) with direction and unit,
   rather than an empty RARE/control/difference table;
3. prose that explicitly states that confirmation cards expand the overview into
   the nine execution cells.

This removes 9 planned rows and 33 empty `\blank` cells from the main matrix
section while preserving the detailed manifest and all scientific requirements.
The candidate is materially more readable on page 7: no placeholder dashes, no
wrapped six-column execution prose, and the four RQs are visible at a glance.

## Verification

Candidate build directory: `article/aamas2027/build/experiment_matrix_20261008_v2/`

- 9 total PDF pages; 8 body pages; References starts on page 9.
- 0 unresolved citations.
- 0 overfull boxes.
- Official AAMAS template files unchanged.
- Candidate PDF SHA-256:
  `d87086489d5ed098c38a6a7b4add31d476bbf6cf20d4c05ef4383c5fe9e96218`.
- `submission_ready=false`; this is still an internal pre-results revision.

After one final terminology polish that spells out the exact
`contextual-trust-linear` arm, the active build was recompiled and reviewed.
The versioned and canonical PDFs are byte-identical at SHA-256
`1a89dd8472f1991b6812bba94d46c159a7512f4495aaee97f5d8bfb2dfb2e9de`; the
promotion receipt is
`artifacts/aamas2027/experiment_matrix_20261008_v3/promotion_receipt.json`.

The body count remains 8, so the candidate improves information density but does
not close the page-budget or scientific submission gate. Numeric result tables
cannot be filled until qualified roots, independent streams, matched baselines,
and real confirmation evidence exist.

## Next action

Promote this layout candidate to the canonical main PDF only after a final source
build and page review. Keep the execution manifest outside the main result table.
When confirmation data arrive, replace the endpoint contract with a grouped
numeric hero table containing fixed metrics, stream-level intervals, and
baseline rows; never replace the current empty cells with predicted numbers.

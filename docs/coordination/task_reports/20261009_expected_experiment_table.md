# Task report: expected experiment table v1

Date: 2026-10-09
Status: complete as a planning artifact; scientific closure remains open.

## Objective

Produce a clean, numerical expected-result matrix that corresponds one-to-one
with the archived paper-facing experiment matrix. The table is an explicit
target for later experiments, not an observed result.

## Work completed

1. Copied the archived matrix structure into a versioned expected-table source.
   The overview and Tables 2--4 keep the original policy/intervention rows and
   result-bearing cells. The labels for assignment change, state bytes, and
   coverage/UNKNOWN are clarified to match the active v5 semantics.
2. Filled the cells with conservative scenario targets: three structural roots,
   three independent streams per arm (`n=9`), `lambda=0.10`, and complete cost
   normalized to the no-update mean. The expected RARE advantage is modest and
   conditional; its service/state/cost overhead and negative regimes remain
   explicit.
3. Added a machine-readable JSON ledger with source-PDF hash, assumptions,
   implied-quality arithmetic, and interpretation. A validator checks all 21
   rows, arithmetic, intended win/loss pattern, and source correspondence.
4. Compiled the PDF with the AAMAS class and `EXPECTED --- NOT OBSERVED`
   watermark. Three pages are visually legible; the final log has zero overfull,
   zero fatal, and zero undefined-reference errors (five underfull warnings only).

## Receipts

- Versioned PDF: `artifacts/aamas2027/expected_experiment_matrix_v1_20261009/expected_experiment_matrix.pdf`
- Canonical PDF: `artifacts/aamas2027/expected_experiment_matrix.pdf`
- Source: `article/aamas2027/expected_experiment_matrix_v1_20261009/expected_experiment_matrix.tex`
- Values: `docs/paper/aamas2027/expected_experiment_matrix_v1_20261009/expected_results.json`
- Layout receipt: `experiments/logs/expected_experiment_matrix_v1_20261009/layout_receipt.json`
- Compile log: `experiments/logs/expected_experiment_matrix_v1_20261009/compile.log`
- Validation log: `experiments/logs/expected_experiment_matrix_v1_20261009/validation.json`
- Canonical registry: `artifacts/aamas2027/expected_experiment_matrix_master.json`

## Interpretation boundary

The targets are not fitted from the two limited real episodes and do not claim
that RARE wins. They encode a falsifiable expectation: a small gain against a
strong same-information contextual baseline only in the informative regime,
with higher update latency/backlog/state/cost and losses or ties in sparse,
stale, shifted, or high-load regimes. Actual cells must be populated from the
frozen live cards and retained even when they disagree with this guide.

The benchmark+baseline acceptance gate therefore remains **OPEN**. This task
delivered the clean target table; it did not create API, GPU, benchmark, or
scientific evidence.

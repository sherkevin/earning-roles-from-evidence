# Expected experiment matrix (v1, 2026-10-09; superseded)

This version is retained as an immutable history record. It is superseded by
[`expected_experiment_matrix_v2_20261009`](../expected_experiment_matrix_v2_20261009/README.md),
which scopes the values to R1 and repairs the owner-truth/UNKNOWN and strong-
control guard semantics.

This directory stores the **numerical expected-result table** used as a planning
target for the next confirmation runs. It is deliberately separate from the
paper-facing matrix and from every observed-result receipt.

## Correspondence

- Source matrix PDF: `artifacts/aamas2027/experiment_matrices_20261008_v3/experiment_matrices.pdf`
- Source SHA-256: `84ec43aa770787aea1d0c8cd5fcc799dc1b1e9584d55397b1f9cf984d289f316`
- Expected source: `article/aamas2027/expected_experiment_matrix_v1_20261009/expected_experiment_matrix.tex`
- Expected PDF: `artifacts/aamas2027/expected_experiment_matrix_v1_20261009/expected_experiment_matrix.pdf`
- Machine-readable values: `expected_results.json`

The expected PDF preserves the original overview and Tables 2--4, including the
policy/intervention rows and result-bearing columns. Two labels are clarified
for scientific use: assignment change is explicitly diagnostic, and the service
table separates coverage from UNKNOWN handling and marks state bytes as a
resource quantity. These clarifications do not add or remove a result cell.

## Meaning of the numbers

All displayed values are **scenario targets**, not observations, fits, estimates,
or evidence that a benchmark/baseline gate has passed. The `\pm` values are
expected between-stream variation, not confidence intervals. The planning
scenario assumes three structural roots, three independent streams per arm
(`n=9`), utility cost coefficient `lambda=0.10`, and complete cost normalized
to the no-update mean of `1.00`.

The targets encode a falsifiable pattern: RARE has a modest advantage over the
strong contextual baseline when typed evidence is informative, pays a measured
service/state/cost overhead, and is expected to lose or tie in sparse, stale,
shifted, or high-load regimes. Ownership and selected-only ablations may produce
more assignment changes while becoming less safe; assignment change is therefore
not a success metric.

Observed values must replace these cells only after the frozen experiment card,
raw event manifests, complete-cost accounting, independent scoring, and clean
replay pass. A real result that differs from this guide remains the real result;
the guide must never be edited to match it.

## Status

`GUIDE_EXPECTATION_NOT_OBSERVED`. This artifact contains no API calls, GPU jobs,
benchmark runs, or empirical result. It must remain watermarked
`EXPECTED --- NOT OBSERVED` and must not be imported into the submission PDF as
evidence.

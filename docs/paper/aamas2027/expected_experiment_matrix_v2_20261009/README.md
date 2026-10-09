# Expected experiment matrix (v2, 2026-10-09)

This directory stores the **numerical expected-result table** used as a planning
target for the next confirmation runs. It is deliberately separate from the
paper-facing matrix and from every observed-result receipt. Version 2 keeps v1
as history and makes the active regime and semantic guard conditions explicit.

## Correspondence

- Source matrix PDF: `artifacts/aamas2027/experiment_matrices_20261008_v3/experiment_matrices.pdf`
- Source SHA-256: `84ec43aa770787aea1d0c8cd5fcc799dc1b1e9584d55397b1f9cf984d289f316`
- Expected source: `article/aamas2027/expected_experiment_matrix_v1_20261009/expected_experiment_matrix.tex`
- Expected PDF: `artifacts/aamas2027/expected_experiment_matrix_v1_20261009/expected_experiment_matrix.pdf`
- Machine-readable values: `expected_results.json`

The expected PDF preserves the original overview and Tables 2--4, including the
policy/intervention rows and result-bearing columns. Labels are clarified for
scientific use: assignment change is explicitly diagnostic; state bytes are a
resource quantity; PeerSelect false attribution is N/A without owner truth; and
coverage is distinct from UNKNOWN/abstention in the machine-readable ledger.
These clarifications do not add or remove a result cell. The archived core
matrix does not contain task-conditioned ridge, matched-composition, or closest
published-adapter rows; v2 therefore records those as mandatory NO-GO guard
comparisons rather than silently treating contextual trust as the strongest
baseline.

## Meaning of the numbers

All displayed values are **R1 informative typed-evidence scenario targets**, not
observations, fits, estimates, or evidence that a benchmark/baseline gate has
passed. The `\pm` values are marginal between-stream planning variation, not
confidence intervals or a covariance model. The planning scenario assumes
three structural roots, three independent streams per arm (`n=9`), utility cost
coefficient `lambda=0.10`, and complete cost normalized to the no-update mean
of `1.00`. The RARE/context break-even cost coefficient is about `0.2167`; the
headline target is therefore not robust to arbitrary cost weights.

The targets encode a falsifiable R1 pattern: RARE has a modest advantage over the
contextual baseline when typed evidence is informative, pays a measured
service/state/cost overhead, and is expected to tie or lose against a qualified
task-conditioned ridge/matched-composition control in sparse, stale, shifted,
or high-load regimes. Ownership and selected-only ablations may produce more
assignment changes while becoming less safe; assignment change is therefore
not a success metric. The evidence × delayed-credit interaction is illustrative
for R1 only.

Observed values must replace these cells only after the frozen experiment card,
raw event manifests, complete-cost accounting, independent scoring, and clean
replay pass. A real result that differs from this guide remains the real result;
the guide must never be edited to match it.

## Status

`GUIDE_EXPECTATION_NOT_OBSERVED`. This artifact contains no API calls, GPU jobs,
benchmark runs, or empirical result. It must remain watermarked
`EXPECTED --- NOT OBSERVED` and must not be imported into the submission PDF as
evidence.

Version 1 is retained at `expected_experiment_matrix_v1_20261009/` and is
superseded by this version because it did not label R1-only scope or separate
owner-truth and UNKNOWN semantics.

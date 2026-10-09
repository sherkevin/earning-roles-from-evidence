> 历史版本：已被 [v5](../expected_experiment_matrix_v5_20261009/README.md) 取代；原始正文保留供追溯。

# Numeric expected experiment matrix v4 (2026-10-09)

This is the sole numerical expectation reference for the experiment matrix in `artifacts/aamas2027/main.pdf`.
It is `EXPECTED_NOT_OBSERVED`, not an empirical result and not evidence that the benchmark/baseline gate has closed.

## Construction

- Structure: current `main.pdf` four-row matrix expanded to the nine execution cells in `EXPERIMENT_MATRIX_EXECUTION_MANIFEST_20261008.md`.
- Numeric mother: expected v3 JSON (the v3 PDF is broken and is not reused).
- Uncertainty logic: guide v2 paired/root sensitivity model.
- Direction guards: guide v5, including deliberate sparse, stale, and high-load losses.
- Utility: `U = Y - 0.10 * C`; matched uniform complete cost is `1.00`.

## Files

- Source: `article/aamas2027/expected_experiment_matrix_v4_20261009/expected_experiment_matrix.tex`
- Values: `docs/paper/aamas2027/expected_experiment_matrix_v4_20261009/expected_results.json`
- Automatic audit: `docs/paper/aamas2027/expected_experiment_matrix_v4_20261009/numeric_audit.json`
- PDF: `artifacts/aamas2027/expected_experiment_matrix_v4_20261009/expected_experiment_matrix.pdf`

## Status

Automatic numeric audit: `True` (36/36 checks).
Scientific evidence gate: `OPEN` by design; benchmark runs = 0.

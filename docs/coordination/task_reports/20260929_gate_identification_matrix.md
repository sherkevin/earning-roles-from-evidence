# Task report — responsibility-gate identification matrix

- **Date**：2026-09-29
- **Status**：`done / candidate-only diagnostic`
- **Scope**：zero API, zero GPU; active method, benchmark and Goal unchanged

## Why this matrix was needed

The preceding three-event replay used a recipient-owned event with `raw=0`.
For the diagonal updater, that value changes only a denominator and leaves the
corresponding coefficient at zero, so the gate and ungated arms had identical
choices. That was an uninformative fixture, not evidence that attribution has
no value. The matrix therefore varies only the visible raw recipient signal;
features, updater, anchor, capacities, correction and selection are fixed.

The producer-safe arm marks the recipient-owned row `ineligible` with
`label=None`. The diagnostic ungated arm consumes the raw acceptance signal.
When the raw signal is missing, both arms use `UNKNOWN` and skip the update.

## Result

| case | gate vs ungated probabilities | interpretation |
|---|---:|---|
| positive raw signal, orthogonal feature | different; choice changes (`B` vs `A`) | gate value is identifiable in this contamination case |
| zero raw signal, orthogonal feature | identical | zero-valued signal is a degenerate fixture |
| missing raw signal | identical; both `UNKNOWN` | missingness is not encoded as label zero |
| positive raw signal, non-orthogonal feature | different probabilities, same choice | gate changes state even when the current menu does not flip |

The exact outputs, state digests and per-event dispositions are in the summary
JSON. Ten targeted tests passed.

## What this does and does not establish

This qualifies a necessary mechanism test: the responsibility gate can change
the state and assignment when an ineligible but visible positive raw signal
would otherwise be consumed. It does not establish that the signal is common
in real tasks, that the gate improves out-of-sample quality, or that the method
is novel relative to contextual trust/reputation systems. The ungated arm is a
pre-registered gate ablation, not yet the final closest published baseline.

The next scientific design must bind the raw signal to the public judgment
schema, independently score producer quality, and evaluate a later unseen
assignment with the same public ownership and arrival information. No API or
A800 run is justified by this diagnostic.

## Evidence

- Configuration: `experiments/logs/n03_gate_identification_matrix_20260929_v1/config.json`
- Summary: `experiments/logs/n03_gate_identification_matrix_20260929_v1/summary.json`
- Code: `scripts/peerrolebench_gate_identification_matrix.py`
- Tests: `tests/test_peerrolebench_gate_identification_matrix.py`

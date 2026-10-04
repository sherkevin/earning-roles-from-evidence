# Task report — canonical PIPE3 parity replay (v21)

Date: 2026-10-04
Status: `QUALIFIED_OFFLINE_PUBLIC_INPUT_PARITY` (reproducibility replay only)
Goal change requested: `false`

## Purpose

The v20 receipt passed the narrow public-input/schema gate, but the working
tree then received a final source-level edit to the canonical qualification
runner.  This replay binds the result to the exact current source hash rather
than treating the earlier receipt as if it covered later code.

## Execution identity

- Runner: `scripts/peerrolebench_canonical_pipe3_parity_qualification.py`
- Receipt: `experiments/logs/n03_canonical_pipe3_parity_20261004_v21/`
- Git commit recorded before execution: `3c24d2b1a8219e78bc4f06e72db733fcd6f81a4b`
- Current runner SHA-256: `b094416c9a11a5bd8eb8cf9bb02f533ed3f185ec904cd5345077f91ae3f195e6`
- API/LLM calls: `0`
- GPU jobs: `0`
- Python test regression: `13 passed` via `python3 -m pytest -q tests/test_peerrolebench_canonical_pipe3_parity.py tests/test_peerrolebench_policy_matrix_runner.py`

The source hash in `v21/config.json` equals the hash of the runner used for
the replay.  The earlier v1–v20 receipts, including failures, remain intact.

## Result

All pre-registered engineering checks passed:

- valid stream: all seven arms selected four times; public trace and
  read-cut-specific feature digests matched; re-visible prefix count was 2;
  replay and cross-arm state isolation passed;
- explicit UNKNOWN row: recorded in the denominator, produced zero eligible
  rows and zero policy updates;
- feedback after the frozen read cut: rejected before policy selection;
- mutated role-offer bundle digest: rejected by canonical reconstruction;
- all rejected cells: zero selections and zero updates.

The receipt status is therefore `QUALIFIED_OFFLINE_PUBLIC_INPUT_PARITY`.
`scientific_claim_allowed=false`, `benchmark_qualified=false`, and
`baseline_parity_scientific=false` remain false.

## Interpretation and remaining distance

This replay strengthens reproducibility of the public-input/schema seam only.
It does not qualify a benchmark, prove scientific same-information parity,
or measure quality, specialization, role learning, forgetting, latency,
cost, or later-use utility.  Positive raw-acceptance and terminal-only source
adapters, registry/history mutation cells, an authoritative second structural
root, independent live histories, a closest published adapter, complete
measured costs, and real API/A800 results remain open under the active
benchmark/baseline and method acceptance documents.

The next task is to design and zero-call qualify those missing positive source
adapters and mutation controls.  No real API or A800 job is authorized by
this receipt.

# Task report — canonical raw-acceptance adapter qualification

Date: 2026-10-04
Status: `QUALIFIED_OFFLINE_SOURCE_ADAPTERS`
Goal change requested: `false`

## Purpose

This task implements the first half of the canonical channel-adapter card. It
connects the native PIPE3 recipient judgment to the `raw_acceptance` arm
without passing through producer responsibility attribution. It does not
implement terminal-only mapping and does not claim scientific parity.

## Implementation and receipt

The new runner
`scripts/peerrolebench_canonical_raw_adapter_qualification.py` performs the
following order:

1. validate native selection `s0`, delivery `d0`, judgment `j0`, selected
   candidate `peer-b@v1`, artifact digest and candidate-registry digest;
2. build a `DecisionSidecar` bound to the native selection;
3. build a `RawAcceptanceSidecar` bound to the native judgment;
4. call `project_raw_acceptance`; and only then
5. construct the shared `MatrixOffer` stream and run all seven policy arms.

The authoritative replay is
`experiments/logs/n03_canonical_raw_adapter_20261004_v4/`. Its component
hashes are recorded in `config.json`, including runner SHA-256
`0ac367134d0e90e31610a0e8245119ae40d8f89dd46406884760da4b2ef505da`. The
earlier v2/v3 receipts remain preserved. The focused test
`tests/test_peerrolebench_canonical_raw_adapter.py` passed `7` tests.

## Results

The positive cell passed: `raw_acceptance` observed one eligible selected row
and made one update; the other six arms ignored that source and made zero
updates. All seven arms had identical visible-input digests and snapshot
replay passed. Re-visible prefixes did not create a second update.

Seven rejection cells all failed closed before the matrix runner started:
wrong canonical decision, wrong producer, wrong ledger digest, wrong registry
digest, duplicate sidecar, UNKNOWN decision and feedback after the frozen
read cut. Each recorded `runner_started=false`, zero selections, zero policy
updates and `false_accept=false`.

The receipt records `real_api_calls=0`, `gpu_jobs=0`,
`scientific_claim_allowed=false`, `benchmark_qualified=false` and
`baseline_parity_scientific=false`.

## Interpretation

This closes the raw-acceptance adapter reachability and preflight boundary. It
does not show that raw acceptance improves assignment quality, nor that the
raw and situated-judgment channels are a scientific same-information
comparison. The feature vectors remain deterministic parity fixtures and the
offline cost ledger is unmeasured.

Terminal-only remains open because the current `FeedbackSidecar` uses
responsibility-attribution fields whose semantics must not be silently reused
for an independent final-outcome control. The next task is to add a typed
terminal-outcome projection (or prove an equivalent provenance contract), then
run the same canonical seven-arm and preflight checks. Second-root authority,
independent live histories, later-use utility, measured cost, real API and
A800 work remain closed.

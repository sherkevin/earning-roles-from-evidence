# Task report — canonical terminal-only adapter qualification

Date: 2026-10-04
Status: `QUALIFIED_OFFLINE`
Goal change requested: `false`

## Purpose

This task completes the terminal half of the canonical channel-adapter card.
The terminal comparator now receives an independent outcome-provenance
projection.  It is deliberately separate from producer responsibility
attribution and from the older `FeedbackSidecar` type.

## Implementation

`scripts/peerrolebench_terminal_outcome_projection.py` adds
`TerminalOutcomeSidecar`, `TerminalOutcomeProjection` and
`project_terminal_outcome`.  The sidecar binds the native terminal record,
delivery record hash, selection, selected candidate and an explicit
`terminal-success-v1` mapping.  The only policy label is derived from the
sealed native `TerminalOutcome.success` field.  The projection excludes
`scorer_version`, `score_payload_sha256`, raw success and all
`AttributionGate`/producer-score fields.

`scripts/peerrolebench_canonical_terminal_adapter_qualification.py` performs
preflight before creating a `MatrixOffer` and then runs the shared seven-arm
stream.  The authoritative receipt is
`experiments/logs/n03_canonical_terminal_adapter_20261004_v5/`; v1–v4
attempts remain preserved.  The current projection and qualifier hashes are
recorded in `config.json`:

- projection: `67a4115d677e6814cde327295a14f0f727d5377f9ca1a498740e1cceb72bfc1d`
- qualifier: `0f7fff7938c66559e9167da2df593daf678925261b266337c323b1851120a937`

## Results

The positive cell passed: `terminal_only` observed one eligible row and made
one update; the other six arms ignored the terminal channel and made zero
updates.  All seven arms had equal visible-input digests, snapshot replay was
equal, and no private terminal fields crossed the projection boundary.

Eight negative cells—wrong outcome hash, wrong delivery, wrong delivery
record hash, wrong selection, wrong candidate, wrong mapping, UNKNOWN,
late-after-read-cut, plus duplicate feedback—were rejected before the matrix
runner.  Every rejected cell recorded `runner_started=false`, zero selections
and zero policy updates.

The terminal projection tests passed `7` focused tests; the projection,
sidecar and baseline regression set passed `45` tests.  The receipt has zero
API/LLM calls, zero GPU jobs, `scientific_claim_allowed=false`,
`benchmark_qualified=false` and `baseline_parity_scientific=false`.

## Interpretation and remaining distance

This closes the terminal channel's typed provenance and fail-closed adapter
seam.  It does not show that terminal feedback is a fair scientific baseline,
or that it improves quality, cost, specialization, real-time adaptation or
forgetting.  The feature vectors and offline costs remain engineering
fixtures.  Canonical public-input parity now has separate raw and terminal
adapter evidence, but scientific same-information comparison still requires
an actual frozen benchmark, independent live histories, later-use outcomes,
measured costs and a second structural root.  No real API or A800 work is
unlocked by this receipt.

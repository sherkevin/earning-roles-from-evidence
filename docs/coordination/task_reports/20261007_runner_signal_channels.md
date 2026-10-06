# Task report — versioned runner signal channels

Date: 2026-10-07
Status: `PARTIAL` (engineering prerequisite only)
Goal change requested: `false`
Scientific result: `none`

## Purpose

The native projection mutations are now qualified, but the live C1 runner still
returned one conflated `outcome` field. This task adds a versioned receipt
(`c1-signal-channels-v1`) to a new runner/card pair. Each episode now persists
`Qp`, recipient judgment `J`, action `A`, downstream adoption `D`, current
outcome `Y`, and assignment credit `L` under `signal_channels.json`.

The change is deliberately descriptive. It does not add a new ledger event,
change the policy updater, or alter historical v1/v2 cards and outputs.

## Frozen implementation and evidence

- Runner: [`peerrolebench_c1_pipe3_bounded_live.py`](../../../scripts/peerrolebench_c1_pipe3_bounded_live.py),
  version `c1-pipe3-bounded-live-v3-signal-channels`.
- Candidate card: [`n03_c1_parent_source_live_v2_signal_channels.json`](../../../configs/aamas2027/n03_c1_parent_source_live_v2_signal_channels.json).
  It is design-only and has not been used for a real API run.
- `A` is bound to the native `ConsumerAction` ledger event and action receipt.
  `D` is a scorer receipt with adoption checks, response digest and scorer
  version. No `AdoptionScore` protocol event is invented.
- The legacy `TerminalOutcome` needed for ledger replay is retained unchanged.
  The new scientific `Y` row is always `UNKNOWN`, carries the legacy
  `derived_status`/`derived_quality_score`, and records
  `derived_from=["D", "recipient"]` with
  `independent_terminal_measurement=false`. `L` is explicitly UNKNOWN because
  no native later assignment/peer-history credit is present in this card.
- Zero-call fixture evidence is in
  [`n03_signal_channels_runner_qualification_20261007_v3`](../../../experiments/logs/n03_signal_channels_runner_qualification_20261007_v3/summary.json):
  3 tests passed, 0 real API calls, 0 GPU jobs. The v3 receipt also carries
  delivery/artifact identifiers, action input/output digests, consumer identity,
  changed paths, repair cost, and explicit policy-visibility flags. Existing
  ledger replay and canonical cost checks still pass. The earlier v2 receipt is
  retained as a prior version rather than overwritten.

## What passed and what remains open

Passed at the engineering boundary:

- every target episode emits the same six channel keys and schema version;
- action receipt is recorded separately from adoption scorer output;
- derived current outcome cannot be mistaken for an independent terminal label;
- missing assignment credit remains UNKNOWN and does not update a policy;
- historical ledger/cost/replay assertions remain intact in the zero-call
  fixture.

Still open:

- the new card has not been run with a real API, independent root, or later
  assignment; no effect, regret, quality, cost, real-time, or forgetting result
  exists;
- the current scorer has no independent terminal/later-use worker, so the
  terminal-only arm remains an offline protocol control, not a live scientific
  comparator;
- `D` is a diagnostic receipt and is not a policy-visible feedback source in the
  existing sidecar contract;
- source/target provenance still needs the native sidecar/offer mutation matrix
  and an externally supplied seal before a confirmatory card.

## Goal reconciliation

ER-G1: `PARTIAL`; channel attribution is now explicit, but the complete future
assignment and downstream-effect chain is unmeasured.

ER-G2: `OPEN`; no online training, latency, drift, or forgetting result.

ER-G3: `PARTIAL`; channel parity is improved in the runner, while seven-arm live
  same-information parity and an independent Y remain open.

ER-G4: `PARTIAL`; the fixture is reproducible and real-run ready, but no real
  API comparison has been authorized.

ER-G5: prerequisite progress only; scientific submission gate remains closed.
No A800 job is justified.

ER-G6: no Goal change requested (`false`).

The next decision is whether to build an independent terminal/later-use scorer
or keep `Y` as a deliberately censored channel and focus the first live parity
card on `J` versus objective `Qp/D`. That is a scientific design choice and is
not silently made by this implementation task.

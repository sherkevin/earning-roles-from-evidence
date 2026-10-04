# Experiment card — canonical channel-adapter parity (design)

Date: 2026-10-04
Status: `DESIGN_FROZEN_BEFORE_EXECUTION`
Goal change requested: `false`

## Purpose and boundary

This card closes one engineering seam before any live API run: connect the
declared `raw_acceptance` and `terminal_only` comparators to the canonical
PIPE3 public stream.  It is not a benchmark freeze, a scientific
same-information comparison, or an efficacy experiment.  The run must use
zero LLM/API calls and zero GPU jobs.

## Shared stream contract

Both cells reuse the native canonical ledger, candidate registry, source
selection, selected candidate, menu order, RNG schedule, read cuts, arrival
indices, public feature schema, cost schema and seven policy namespaces from
the v21 public-input qualification.  The adapter must validate native ledger
record hash, source selection id, chosen candidate/version, registry digest
and event-time prefix **before** constructing `MatrixOffer`.  Every arm then
receives the same channel-specific public row and φ digest; the runner records
`runner_started`, selection count, update count, public-input digest and final
state digest per arm.

## Positive cells

### `raw-positive`

Construct a `RawAcceptanceSidecar` from the canonical recipient-judgment
record (`j0`) and pass it through the existing raw projection boundary.  The
public row has source `raw_acceptance`, action `accept` or `reject`, the
selected candidate, and an explicit mapping version.  The raw arm must record
one eligible row and one update; all other arms must ignore this channel and
make zero updates.  The row must remain selected-only and re-visible prefixes
must not count as second updates.

### `terminal-positive`

Construct an independent terminal-outcome projection from the canonical
outcome record (`o0`), bound to the selected delivery, action and source
selection.  Its public payload contains only feedback identity, selected
candidate, source `terminal_outcome`, action `use`, label mapping/version and
event-time fields.  It must not pass through producer-defect attribution or
expose scorer-private fields.  A new typed terminal projection is preferred;
reusing `FeedbackSidecar` is allowed only if its attribution metadata is
explicitly shown to mean selected-delivery outcome provenance rather than a
producer responsibility label.  The terminal arm must record one eligible row
and one update; the other arms must ignore this channel and make zero updates.

## Fail-closed cells

For each channel, run wrong ledger record hash, wrong source selection,
wrong producer/candidate, mapping/version mutation, duplicate feedback,
late-after-read-cut and UNKNOWN/no-label cases.  Adapter rejection must occur
before the matrix runner starts and record `runner_started=false`,
`selection_count=0`, `policy_update_count=0`, and an explicit UNKNOWN/INVALID
reason.  A rejected stream must never be made to pass by deleting its
denominator row.

Add registry and history controls:

- canonical registry reorder is valid only when its digest and candidate
  versions/source/model digests are unchanged;
- registry version/source/model/menu mutation is rejected before offer
  construction;
- history snapshot schema/version/state-digest, seal registry digest,
  candidate projection, scope, assignment/credit/delivery lineage mutations
  are rejected or classified UNKNOWN with zero policy updates;
- a legal history replay preserves the same public φ and selection digest.

## Required artifacts and stop rule

Write `config.json` before execution with commit, component hashes, registry,
channel mapping, read-cut/arrival/RNG digests and zero-call declaration.
Stream each cell to `raw.jsonl` and write per-cell and aggregate summaries.
Retain all failed attempts.  The only promotable status is
`QUALIFIED_OFFLINE_SOURCE_ADAPTERS`; it does not unlock real API, second-root
confirmation, or A800 work.  Any terminal attribution ambiguity, registry
lineage mismatch, missing selected-only binding, or nonzero update on a
rejected cell stops the task for repair.

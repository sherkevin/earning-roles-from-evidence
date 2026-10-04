# Experiment card — canonical PIPE3 public-input parity qualification

Date: 2026-10-04
Status: `DESIGN_FROZEN_BEFORE_EXECUTION`
Goal change requested: `false`

## Purpose

Close the next benchmark/baseline gate after canonical history provenance.  The
qualification must establish that every policy arm receives the same canonical
public information and timing.  It is a protocol/schema gate, not the live
scientific same-information baseline comparison and not an efficacy
experiment; it uses zero LLM/API calls and zero GPU jobs.

## Canonical input

One append-only PIPE3 ledger supplies a source selection, delivery, recipient
judgment, recipient action, terminal outcome and native role-evidence update.
`build_role_evidence_from_ledger` constructs the public `RoleEvidenceOffer`
from that ledger.  The offer is then projected into the existing public
assignment-row schema only after checking delivery selection lineage and the
candidate-registry digest.  A later target assignment/outcome is appended to a
copy of the same canonical ledger and passed through `append_history_after_credit`
to create the public `PeerHistoryV1` projection used at the next read cut.

The target menu, candidate versions, context, read cut, arrival schedule,
exploration seed, feature schema and cost schema are frozen once and hashed.
At each read cut, the shared `phi` input is a deterministic, bounded
64-dimensional encoding of exactly the canonical public projections available
at that cut, plus the candidate registry and menu.  The role projection is
limited to candidate, judgment, action and availability fields; terminal
`quality_score` and `outcome_status` remain in the operator-bound offer receipt
but are excluded from `phi`.  The vector is identical for all arms and
contains no artifact text, prompt, gold or private scorer field.

## Arms and parity checks

Run the existing seven policy arms: `uniform`, `no_update`, `raw_acceptance`,
`terminal_only`, `contextual_trust`, `pooled_controller`, and `RARE`.  Each arm
has an independent policy namespace and snapshot.  The valid stream publishes
one recipient-judgment row; raw-acceptance and terminal-only therefore test
their declared ignore behavior here, while their positive source adapters need
separate cells.  The common runner enforces
selected-only feedback, UNKNOWN no-update, duplicate/re-visible prefix
handling, late-arrival exclusion, exact menu/read-cut/arrival binding, and
replay restoration.

For every arm and decision record digests of the canonical role offer,
history projections, candidate menu, public `phi`, feedback rows, propensity,
selection, assignment input, policy state and measured cost.  The qualification
passes only when public input digests and schemas are equal across arms while
policy state namespaces remain distinct.

## Negative cells

Alongside the valid canonical stream, run three fail-closed cells: (i) an
UNKNOWN/no-evidence read, (ii) a tampered role-offer bundle digest, and (iii)
a feedback row made available after the frozen read cut.  Registry and history
projection mutations remain separate open adversarial qualifications.
Duplicate replay of the valid prefix is also required.  Mutation, late and
UNKNOWN cells must have zero false accepts, zero policy updates and no new
selection/assignment.  Resource/process errors are recorded as `UNKNOWN`, not
converted into labels.

## Pre-registered interpretation

`QUALIFIED_OFFLINE_PUBLIC_INPUT_PARITY` means only that the canonical
public-input/schema projection, namespace separation and fail-closed
boundaries are executable.  It does not establish that RARE and contextual
trust use the same information in a scientific comparison, unlock the
benchmark, prove RARE or any baseline superior, establish role specialization,
or justify a quality/cost claim.  If any parity or mutation check fails, do
not start live API, second-root or A800 work; first repair the specific seam
and preserve the failed artifacts.

## Required artifacts

Before execution write `config.json` with command, commit, component hashes,
seeds, registry/menu/read-cut/arrival/cost digests and zero-call declaration.
Stream canonical raw rows to `raw.jsonl`, write per-cell summaries and a final
`summary.json`, and add a task report mapping each result to the benchmark and
baseline acceptance requirements.  No historical result may be rewritten.

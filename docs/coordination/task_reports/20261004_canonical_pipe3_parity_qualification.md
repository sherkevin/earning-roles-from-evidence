# Task report — canonical PIPE3 public-input parity qualification

Date: 2026-10-04
Status: `QUALIFIED_OFFLINE_PUBLIC_INPUT_PARITY` (engineering gate only)
Goal change requested: `false`

## Purpose and gate

This task closes the next narrow gate after canonical history provenance.  The
question was whether the seven candidate policy arms can consume one canonical
public information stream with identical menu, timing, feature schema and
cost accounting, while malformed/late/unknown evidence fails closed.  It was
designed before execution in [the experiment card](20261004_canonical_pipe3_parity_card.md).

The run used zero LLM/API calls and zero GPU jobs.  It is not a benchmark
result, not a scientific same-information baseline comparison, and does not
estimate quality, specialization, role-learning benefit, real-time
performance or cost savings.

## What was executed

`scripts/peerrolebench_canonical_pipe3_parity_qualification.py` builds a native
PIPE3 ledger containing source selection → delivery → producer score →
recipient judgment → recipient action → terminal outcome → role evidence.  The
public `RoleEvidenceOffer` is constructed by
`build_role_evidence_from_ledger`, so candidate/version, artifact and event
lineage are not hand-entered in the public row.  A later assignment and target
outcome are then committed through `DelayedCreditLedger` and
`append_history_after_credit`; the resulting `PeerHistoryV1` projection is
available only at the later read cut.

The derived policy stream contains four selections.  The source role evidence
appears at arrival/read cut 5, the delayed history projection at read cut 12,
and the source row is re-visible twice as an immutable public prefix.  Each
arm receives the same versioned candidate menu, registry digest, event-time
schedule, read-cut prefix, public 64-dimensional bounded `phi` vectors and
cost schema.  The φ role projection contains only candidate, judgment, action
and availability fields; terminal `quality_score` and `outcome_status` remain
in the operator-bound offer receipt and are excluded from φ.  Policy snapshots
and digests are kept in separate namespaces.

The exact authoritative run is preserved at
`experiments/logs/n03_canonical_pipe3_parity_20261004_v20/` (the earlier v1–v19
failed/intermediate attempts remain untouched):

- `config.json` records commit, component hashes, command, Python/platform,
  arm list and zero-call declaration.
- `raw.jsonl` records the canonical fixture and all four cells.
- `summary.json` records checks, digests, per-arm metrics and interpretation.

## Results

All pre-registered checks passed:

| Cell/check | Result | Evidence |
|---|---:|---|
| Valid canonical stream | PASS | 4 selections per arm; public prefix re-visible twice; no unknown/unselected rows; snapshot replay equal |
| Independent policy namespaces | PASS | seven distinct final policy-state digests |
| UNKNOWN/no evidence | PASS | all arms selected four times, zero eligible rows and zero updates |
| Feedback after frozen read cut | PASS as `UNKNOWN` | rejected with `offer is unavailable at read_cut`; false accept 0 |
| Mutated canonical offer digest | PASS as `UNKNOWN` | rejected by `RoleEvidenceOffer`; false accept 0 |
| API/GPU/scientific result | intentionally absent | 0/0; `scientific_claim_allowed=false` |

The valid cell additionally checks that every arm's recorded public trace and
read-cut-specific feature vectors hash identically to the canonical input.
The valid cell publishes one recipient-judgment row: contextual-trust,
pooled-controller and RARE consume it, while raw-acceptance and terminal-only
correctly exercise their declared ignore behavior.  Their positive source
adapters are not qualified by this cell.  This confirms a public-input/schema
and timing boundary, not a strongest-same-information baseline comparison or
a performance ranking.

## Interpretation against the three acceptance documents

- **Storyline/innovation:** maintained.  The result supports the root-cause
  story's claim that responsibility-aware evidence can be published only
  through an explicit, versioned boundary; it adds no efficacy claim.
- **Method:** one protocol sub-gate is closed: canonical source lineage,
  read-cut visibility, selected-only handling, independent namespaces and
  fail-closed mutation/late/UNKNOWN behavior are executable together.  The
  three invariants remain protocol-level checks, not empirical lemmas.
- **Benchmark/baseline:** public-input/schema parity is now `PASS (offline)`.
  Scientific same-information parity, positive raw/terminal source adapters,
  benchmark authority, second independent structural root, closest published
  adapter and assignment-level outcome matrix remain open.  The active
  benchmark/baseline document is therefore still `NOT_READY`.

## Problems discovered and limits

The existing matrix runner originally exposed only trace/metric output, so the
qualification added final policy snapshots/state digests as an auditable
namespace check.  The public-row adapter has its own schema version
(`matrix-evidence-v1`) and is explicitly bound back to the native role-offer
version in `role_lineage`; these are two serialization layers, not two labels.
The first v18 review exposed a fairness bug: its φ hash included terminal
`quality_score/outcome_status`, which RARE used while contextual trust did not.
That result is retained as a failed/intermediate artifact.  v19 excluded those
fields and records the legal public φ scope; v20 additionally increments the
φ schema version and fixes the late-cell identifier for traceability.  The
hash-based encoder remains a
deterministic parity fixture, not the final scientific representation or a
learned model.  The mutation cell covers only a tampered offer bundle digest;
registry and history-projection mutations remain separate open qualifications.

The invalid v1–v16 attempts remain untouched.  In this run, no resource or
process failure was reclassified as a label.  No conclusion about real agent
quality or the suitability of TeamBench-derived tasks follows.

## Next step and stop rule

The next step is a documentation-only gate audit using this v20 receipt: bind
the public φ exposure contract and per-arm state namespace to the benchmark+
baseline evaluation document, then add positive raw/terminal source-adapter
cells and the adversarial registry/history mutation qualifications.  Do not
start another API stream, second-root live confirmation or A800 job until
those gates are complete.  A live stream still requires independent histories,
a responsibility-complete scorer, later-use outcomes, full cost accounting
and a separately qualified strongest same-information contextual baseline.

`goal_change_requested=false`.

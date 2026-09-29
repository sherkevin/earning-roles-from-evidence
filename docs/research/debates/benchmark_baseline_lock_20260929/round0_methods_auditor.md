# Round 0 — methods and baseline audit

- **Run:** `run_e313af962946` charter
- **Source:** independent read-only audit from `/root/round0_methods_auditor_retry`
- **Status:** received; not a consensus decision
- **Date:** 2026-09-29

## POSITION

`ArtifactRole/PeerRoleBench-TB` is the only current candidate that could carry the
complete paper claim. `PeerSelect/IPD` can qualify selector and online-update
mechanics, but cannot identify recipient artifact use, responsibility attribution,
adoption, and later assignment by itself.

## TARGET and reasoning

The target claim remains

```text
recipient situated judgment
→ attributable producer evidence
→ pre-execution assignment change
→ unseen quality and complete-cost change
```

ArtifactRole can observe this chain only after qualification. PeerSelect/IPD is useful
for local graphs, selected-only payoff, exploration, drift, latency, and forgetting;
its payoff has no artifact-use or responsibility variables. Shared event/update APIs
therefore do not imply shared labels or shared scientific conclusions.

## EVIDENCE

- `docs/coordination/GOAL.md` ER-G1/G3/G4 requires producer contract, recipient use/
  rework/reject, producer attribution, later assignment, unseen quality/full cost,
  `UNKNOWN`, real APIs, and strong same-information baselines.
- `docs/research/versions/benchmark-baseline/benchmark_baseline_v1.0_20260928.md`
  marks PeerRoleBench-TB as TeamBench-derived candidate; DIST1 has historical text
  leakage, and PIPE3 lacks complete runner/scorer/ledger/adoption/later-assignment
  qualification.
- `docs/research/versions/evaluation/benchmark-baseline/benchmark_baseline_v1.2_20260929_eval.md`
  requires producer contract, recipient action, sink adoption, later assignment, root
  independence, baseline parity, cell manifest, and precision gates.
- `docs/research/candidates/benchmark_track_decision_v0.1_20260929.md` recommends
  Track B primary and Track A secondary/mechanism qualification, but its status is
  `CANDIDATE_NOT_ACTIVE` and therefore requires a user decision gate.

## CURRENT GATES

Still open: authority, independent roots, contamination and clean replay; PIPE3
independent roots, later assignment, multi-stream and unified-runner parity; raw public
projection, RARE selection adapter, closest-published adapter, cell manifest, numeric
gates and statistical precision. Six zero-call comparator qualifications do not freeze
the baselines and no scientific effect number is identified.

## DECISION TESTS / KILL CRITERIA

1. Qualify authority, roots, contamination, and clean replay separately for both tracks.
2. For every ArtifactRole root, independently score producer contract, recipient action,
   adoption and later assignment while separating recipient-only errors.
3. Make raw/terminal, strong same-information contextual trust, closest published,
   RARE, and the unified runner executable under parity.
4. Freeze independent confirmation roots, live streams, complete cost, `UNKNOWN`
   denominators, and a precision note.
5. If RARE does not exceed strong contextual trust, or violates quality/cost/latency/
   `UNKNOWN` gates, stop expansion and A800.
6. Track A passing cannot rescue an ArtifactRole primary claim.

## CONFIDENCE

High for the document-state audit; medium-high for Track B as the eventual primary
candidate because the track decision remains explicitly inactive.

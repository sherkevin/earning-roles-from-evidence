# Task report — signal-channel and baseline-parity audit

Date: 2026-10-06
Status: `BLOCKED_BY_EVIDENCE`
Goal change requested: `false`
Scientific result: `none`

## Audit question

After the first parent-owned real smoke, can the current label and baseline
design identify the claimed mechanism? The audit uses the live receipt
[`n03_c1_parent_source_live_20261006_v1`](../../../experiments/logs/n03_c1_parent_source_live_20261006_v1/summary.json)
and the active benchmark/baseline contract. It does not change the active
method or freeze a new baseline.

## Evidence

The only live comparable arms are `no_update`,
`contextual_trust_linear`, and `RARE`. They share one parent source, candidate
menu, source digest, target artifact, scorer versions, and cost ledger; all
three target selections are `peer-b@v1`. The other named arms—`uniform`,
`raw_acceptance`, `terminal_only`, `pooled_controller`, and the old Beta
contextual policy—have offline policy/fixture qualifications only. They have
not yet executed the same parent source, recipient action, independent
scorers, target history, and complete cost path, so they cannot enter a live
baseline ranking.

The live receipt contains four separate signal channels:

| Channel | Observed live value | Interpretation |
|---|---:|---|
| recipient judgment | `accept`, label `1.0` in all three targets | situated opinion about the delivered artifact |
| producer contract score | `FAIL`, label `0`, `P2_iso_serialization` failed | objective producer contract result |
| recipient execution score | `PASS`, quality `1.0` | recipient processed the delivered artifact |
| downstream adoption `D` / current outcome field | adoption `FAIL`, current quality `0.5` | `Y_current` is derived from `D` subject to recipient completeness; it is not an independent terminal result |

`contextual_trust_linear` and `RARE` updated from the first channel only. Each
performed one selected-only update using label `1.0`, while the later objective
quality was `0.5`. Their post-update previews changed, but every arm retained
the same target and the same objective failure. The receipt therefore shows
that recipient judgment and downstream quality are not interchangeable labels.

The audit also found that the parent card's public `base_scores` are
`[0.0, 0.0]`. A uniform selector and a no-update selector would therefore be
distributionally tied under the current feature contract unless a nondegenerate
base-score schedule is frozen; adding both names without that schedule would
create a nominal, not identifiable, baseline contrast.

## Required next card gates

Before any baseline freeze, efficacy ranking, or A800 job, a new card must:

1. use one independently supplied parent source seal and project it into every
   arm with identical artifact/contract/registry/scorer/prompt/raw-response
   fingerprints;
2. execute the same menu, public feature vector, read cut, arrival schedule,
   propensity and cost budget for at least the seven named policy arms;
3. bind each policy to its own legal feedback channel: recipient judgment,
   raw acceptance, terminal outcome, or the responsibility-aware candidate;
4. preserve a joint record of judgment, producer contract, recipient use,
   adoption and an independent terminal outcome. Report calibration/information
   and downstream quality separately; the current derived `Y_current` remains
   diagnostic only and historical UNKNOWN is never relabelled;
5. include producer-defect, recipient-only, sink-only, mixed, scorer-failure,
   late/duplicate/correction and judged-role-disagreement negative cells. All
   unresolved cases remain ITT `UNKNOWN` and cannot update a policy;
6. provide an actually nondegenerate public base-score/initial-state schedule,
   or explicitly remove `uniform` from the identifiable comparison;
7. include at least one independent second root and independent live history
   before interpreting any change in post-update assignment as role learning.

## Goal reconciliation

This audit improves ER-G2/ER-G3 measurement clarity but supplies no efficacy
evidence. The current method remains a candidate; baseline freeze remains
open; second-root authority, independent histories, later assignment and full
quality-cost comparison remain unqualified. The Goal is unchanged and
`goal_change_requested=false`.

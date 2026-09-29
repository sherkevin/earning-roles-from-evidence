# Task report — candidate method lock and closest-method audit

- **Date**：2026-09-29
- **Status**：`partial / candidate only`
- **Scope**：zero API/GPU design work; active method, storyline and benchmark versions unchanged

## Completed

1. Wrote [method-lock card v0.1](../../research/candidates/method_lock_card_v0.1_20260929.md) with one immutable event input, explicit PIPE3 cases, independent target separation, bounded state, selection/assignment semantics, delayed correction and replay requirements.
2. Wrote [closest-method table v0.1](../../research/candidates/closest_method_table_v0.1_20260929.md) covering REM-style role coordination, task delegation, reputation/pooling, delayed contextual trust/bandit, raw/terminal signals and ordinary online optimizers.
3. Defined the minimum four-event same-information counterfactual: recipient-owned error, producer defect, delayed contradiction, and a different future owner choosing on an unseen context.
4. Ran the zero-call RARE-Anchor static audit. The candidate currently fails consolidation retention and bounded correction-queue requirements; details are in [the audit report](20260929_raresafe_anchor_static_audit.md).

## Goal comparison

- **ER-G2**：improved design specificity, but no qualified realtime/timeliness/stability algorithm; remains open.
- **ER-G3**：assignment event and evidence consumption are specified as a candidate, but no live unseen-root effect; remains open.
- **ER-G4**：closest-method threat is explicit, but novelty and benchmark/baseline parity are not established; remains open.

## What this does not establish

The card is not an active method, not a benchmark freeze, not a baseline result and not a scientific effect. It does not justify an API or A800 run. The RARE-Anchor candidate must first repair consolidation semantics and queue bounds, pass zero-call mutation/replay tests, and survive the same-information contextual trust comparison.

## Next gate

Complete the four-event counterfactual as a versioned offline runner with fixed labels and state digests, then independently review it under the benchmark v1.2 parity gates. Only a passing identification gate can justify a small real API diagnostic.

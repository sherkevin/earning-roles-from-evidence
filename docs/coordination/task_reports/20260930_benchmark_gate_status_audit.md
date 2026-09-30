# Task report — benchmark/baseline gate status audit (2026-09-30)

## Purpose

This is a read-only reconciliation of the active benchmark/baseline plan against
its strict evaluation document. It does not run an API, GPU job, or new scorer
episode, and it does not change the Goal or lower any gate.

## Evidence boundary

The audit uses the active benchmark plan and evaluation plus preserved
qualification receipts under `experiments/logs/n03_*` and
`docs/coordination/task_reports/`. Those receipts establish engineering
contracts. They are not independent live streams, benchmark results, or
evidence that RARE improves quality.

## Gate table

| Gate | State | What is established | What is still required |
|---|---|---|---|
| Primary track and claim separation | **PASS (document gate)** | `ArtifactRole` is primary and `PeerSelect` is secondary; labels, denominators and claims are separated. | Keep this separation in every experiment card and paper table. |
| One valid ArtifactRole root | **PARTIAL** | PIPE3 has material, producer/recipient/adoption scorer qualifications and a source-bound offline composition. | A complete versioned root manifest must pass task-text leakage, ownership, scorer, ledger and clean-replay checks together. |
| Two structurally independent roots | **OPEN** | DIST1 and PIPE3 are named candidates. | Prove structural independence and qualify a second root; renamed seeds do not count. |
| Responsibility-aware label | **PARTIAL** | Producer-defect and recipient-owned repair controls produce different eligibility outcomes; recipient-owned repair remains `UNKNOWN`. | Validate the same rule in independent live histories and measure producer contract correctness, recipient use, adoption and later outcome. |
| Baseline executability | **PARTIAL** | Seven-arm zero-call parity runner, raw-acceptance projection/replay, and RARE selection adapter pass offline seams. | Run the real versioned runner for uniform, no-update, raw, terminal, same-information contextual, pooled and RARE arms under identical budgets and menus. |
| Closest published comparison | **OPEN** | Meta-Team L2-style public/profile semantics are specified as a candidate adapter; no direct drop-in was found. | Implement and qualify public, original-info and profile-only cells, or record a justified `NO-GO` before a scientific comparison. |
| Independent live history | **OPEN** | Historical v6 is a bounded development witness only; current composition is deterministic and zero-call. | Freeze streams and run development cells without shared policy state or post-hoc labels. |
| Later assignment / next-episode effect | **PARTIAL** | Offline source-bound offer, isolated read and native `task_start` binding are qualified. | Show that eligible evidence changes a future assignment before execution and measure the later task outcome. |
| Complete cost and latency | **OPEN** | Receipt schema includes token/API/GPU fields; historical v6 has partial real-call accounting. | Report producer, recipient, judge, scorer, communication, retry, repair, state and wall-clock costs for every arm. |
| Statistical precision and confirmation split | **OPEN** | The evaluation document defines required denominators and intervals. | Freeze root/stream split, effect/precision gates, UNKNOWN handling and analysis before reading confirmation outcomes. |
| A800 / online training | **STOPPED BY GATE** | No new GPU result is claimed. | Only consider one bounded challenger after benchmark, baseline, signal and method gates pass. |

## Conclusion

The project has crossed an important **protocol qualification** boundary: a real
PIPE3 scorer/action output can now be routed through responsibility eligibility,
a source-bound public offer, isolated profile consumption and a native future
task-start record. It has not crossed the **scientific benchmark boundary**.
The remaining blockers are root independence, executable same-information
baselines, a fair closest published adapter, independent live histories,
later-use measurement, and complete cost/precision accounting.

Therefore the next allowed work is a bounded, zero-call implementation audit of
those missing gates (or a separately frozen, explicitly approved profile
generator qualification). A new real API episode or A800 job is premature under
the accepted benchmark-freeze decision.

## Reconciliation with Goal

No Goal requirement is downgraded. The audit records why the remaining distance
is methodological and evidential rather than an infrastructure failure:

1. protocol seams are increasingly qualified;
2. scientific comparison is still not executable under parity;
3. no efficacy, role-formation, real-time-training, or A800 claim is made.


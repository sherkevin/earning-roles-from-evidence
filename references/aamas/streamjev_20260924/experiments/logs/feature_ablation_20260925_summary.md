# Feature ablation (2026-09-25)

Same stationary selected-only world and epsilon-greedy policy; only the long-lived feature changes.

| feature mode | expected reward | regret | rank hit | entropy |
|---|---:|---:|---:|---:|
| full | 0.450058 | 0.028983 | 0.647475 | 0.349516 |
| candidate_only | 0.448583 | 0.030457 | 0.608125 | 0.349462 |

This tests shared-context dilution only; it does not test delayed regime switches.

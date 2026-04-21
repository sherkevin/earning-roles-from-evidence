# Figure 3 — Data provenance

Single source of truth for the bars rendered by `scripts/plot_fig3_stage2_vs_stage1_paired.py`.

Generation mode: **interim single-seed**

| Seed | Method | mean_f1 | mean_token | n |
|---|---|---:|---:|---:|
| 42 | fixed_peer_calibrated | 0.6823 | 4398 | 7405 |
| 42 | edo_stage2_chain | 0.6884 | 2332 | 7405 |

Interim mode: CI not available from single seed; will be computed once E-017 seed=43 + seed=44 complete and scripts/paired_bootstrap_ci.py runs.

Canonical source when full 3-seed complete: `artifacts/round2_gpt41mini_stage2_fullval/paired_stats_3seed.csv` (output of scripts/paired_bootstrap_ci.py).

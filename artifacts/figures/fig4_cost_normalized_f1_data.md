# Figure 4 — Data provenance

Single source of truth for the bars rendered by `scripts/plot_fig4_cost_normalized_f1.py`.

Source: `artifacts/round2_gpt41mini/round2_gpt41mini_main_table.csv` (chain-200 HotpotQA × 3 fixed methods × gpt-4.1-mini, seed=42).

| Method | F1 | API tokens per sample | F1 per 1k API tokens |
|---|---:|---:|---:|
| `peer_calibrated` | 0.7381 | 6,414 | 0.1151 |
| `static_roles` | 0.7454 | 4,662 | 0.1599 |
| `self_claim` | 0.7641 | 6,414 | 0.1191 |

Pareto-best cost-normalised F1: `static_roles` = 0.1599 F1/kTok. This visualisation makes §4.3 Finding 4 ('peer_calibrated is Pareto-dominated by a trivial baseline') numerically undeniable.

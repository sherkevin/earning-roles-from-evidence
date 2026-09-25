# Stationary estimator isolation (2026-09-25)

Fixed-theta, 2000-step synthetic selected-only stream with one-step feedback delay. All methods use the same epsilon-greedy policy form; truth and unselected labels are evaluation-only.

| method | expected reward | regret | prediction MSE | rank hit | policy entropy |
|---|---:|---:|---:|---:|---:|
| static | 0.368636 | 0.110405 | 0.074983 | 0.250000 | 1.386294 |
| associative | 0.450058 | 0.028983 | 0.037748 | 0.647475 | 0.349516 |
| diag_ls | 0.402190 | 0.076851 | 0.126985 | 0.413075 | 0.569328 |
| online_rls | 0.457843 | 0.021197 | 0.081980 | 0.794025 | 0.351023 |

This experiment isolates estimator/statistic mismatch from regime switching. It does not test real benchmark quality or A800 latency.

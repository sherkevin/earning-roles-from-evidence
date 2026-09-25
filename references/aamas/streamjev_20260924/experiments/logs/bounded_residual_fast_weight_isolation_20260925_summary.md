# Bounded residual fast-weight isolation (2026-09-25)

Synthetic selected-only stream, five seeds, 2000 decisions per scenario, one-step feedback delay; truth is evaluation-only.

| scenario/method | reward | regret | MSE | rank hit | decision p95 us | update p95 us |
|---|---:|---:|---:|---:|---:|---:|
| stationary/static | 0.368636 | 0.110405 | 0.074983 | 0.250000 | 37.813 | 0.000 |
| stationary/associative | 0.450058 | 0.028983 | 0.037748 | 0.647475 | 91.366 | 0.000 |
| stationary/online_rls | 0.457843 | 0.021197 | 0.081980 | 0.794025 | 38.623 | 0.000 |
| stationary/rfw_tr | 0.419226 | 0.059815 | 0.038872 | 0.478325 | 68.292 | 13.650 |
| switch/static | 0.498030 | 0.110458 | 0.074983 | 0.250000 | 26.444 | 0.000 |
| switch/associative | 0.518292 | 0.090195 | 0.068791 | 0.386075 | 95.392 | 0.000 |
| switch/online_rls | 0.523989 | 0.084498 | 0.075847 | 0.456875 | 69.373 | 0.000 |
| switch/rfw_tr | 0.546621 | 0.061866 | 0.044861 | 0.466492 | 92.411 | 17.750 |

This is a falsification preflight. It does not establish real benchmark quality or A800 performance.

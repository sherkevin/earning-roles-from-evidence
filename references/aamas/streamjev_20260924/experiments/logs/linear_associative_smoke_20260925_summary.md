# Linear associative updater smoke (2026-09-25)

This is a reproducible synthetic selected-only delayed-feedback smoke, not a real-data quality claim. All methods use the same hidden-regime stream, menus, sampled outcomes, and delays; learners receive only the selected candidate label when its delay expires.

Runner: `../linear_associative_smoke.py`
Command: `python3 references/aamas/streamjev_20260924/experiments/linear_associative_smoke.py --seeds 5 --horizon 100`
Files: `linear_associative_smoke_20260925_config.json`, `linear_associative_smoke_20260925_raw.jsonl`, `linear_associative_smoke_20260925_results.json`

Associative update:
$$S_k=\lambda^{k-k^-}S_{k^-}+\sum_{r:\tau_r=k}w_r y_r\phi(x_r),\quad Z_k=\lambda^{k-k^-}Z_{k^-}+\sum_{r:\tau_r=k}w_r\phi(x_r),$$
with $\phi(x)=[\max(x,0),\max(-x,0)]$, $w_r=\min(8,1/p_r)$, and $\hat y(c)=\phi(x_c)^\top S_k/(\phi(x_c)^\top Z_k+10^{-12})$.

| method | expected reward | realized reward | regret | post-switch reward | post-switch regret | decision p95 (µs) | update p95 (µs) |
|---|---:|---:|---:|---:|---:|---:|---:|
| static | 0.418252 | 0.398000 | 0.118841 | 0.526378 | 0.138004 | 14.081 | 0.000 |
| no_feedback | 0.418252 | 0.398000 | 0.118841 | 0.526378 | 0.138004 | 11.414 | 0.000 |
| online_rls | 0.425695 | 0.408000 | 0.111397 | 0.532121 | 0.132261 | 272.475 | 78.752 |
| associative | 0.418725 | 0.398000 | 0.118367 | 0.526378 | 0.138004 | 66.420 | 23.964 |

Paired expected-reward difference vs static:

- OnlineRLSHead: `+0.007444` (SD `0.011270`, n=5)
- associative: `+0.000474` (SD `0.000718`, n=5)
- no_feedback: `+0.000000`

Order and closed-form checks:

- 5/5 seeds passed same-arrival-batch reverse-order check; maximum absolute difference was 1.421e-14 for $S$ and 5.684e-14 for $Z$.
- 5/5 seeds matched the explicit exponentially weighted closed-form sum within floating-point tolerance.

Interpretation:

The recurrence is executable, fixed-state, and materially cheaper than dense RLS in this local CPU probe. It did not improve selection quality on this world: the associative reward is almost the uniform control, while RLS has a small positive paired delta whose interval would still be wide with n=5. The non-negative split feature map and coordinatewise kernel average do not capture the signed linear reward structure well enough. This is falsification evidence against treating the algebra alone as a performance contribution.

The timings are local Python measurements, not A800 or end-to-end service measurements; they exclude encoder, queue, serialization, and API costs.

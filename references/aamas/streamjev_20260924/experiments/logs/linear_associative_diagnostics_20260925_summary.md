# Associative failure diagnostics (2026-09-25)

This replay quantifies why the associative smoke was nearly uniform. It uses the same five hidden worlds and selected-only feedback; truth fields are evaluation-only.

| quantity | mean ± sd |
|---|---:|
| mean_oracle_best | 0.537092 ± 0.101272 |
| mean_uniform_menu | 0.412845 ± 0.111887 |
| mean_assoc_policy_expected | 0.413246 ± 0.111469 |
| headroom_oracle_minus_uniform | 0.124247 ± 0.019289 |
| mean_score_range | 0.029898 ± 0.007714 |
| p95_score_range | 0.065508 ± 0.021618 |
| mean_entropy | 1.386185 ± 0.000051 |
| mean_kernel_offdiag_std | 0.225756 ± 0.006980 |
| rank_hit_fraction | 0.452000 ± 0.178495 |
| post_switch_assoc_policy_expected | 0.550986 ± 0.202364 |

Interpretation:

- The oracle headroom shows that the menu contains better choices than uniform selection, so the environment is not intrinsically unlearnable.
- Associative scores have a small range and entropy close to $\log 4$, so the policy remains nearly uniform.
- The split non-negative map yields a dot-product kernel and a scalar kernel smoother; it does not recover the signed linear direction or cross-coordinate interactions used by the world.
- The shared context coordinates and intercept are present in every candidate in a menu, so they contribute common kernel mass and shrink candidate-specific differences.
- Random regime switches and only 100 selected labels leave little data per regime; forgetting mixes old regimes while the fixed feature map cannot relearn a new representation.
- This is a mechanism diagnosis, not a claim that every associative kernel would fail.

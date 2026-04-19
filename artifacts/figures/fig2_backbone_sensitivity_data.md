# Figure 2 — Data provenance

Single source of truth for the bars rendered by `scripts/plot_fig2_backbone_sensitivity.py`.

| Method | GLM-4-flash chain-200 (n=200) | gpt-4.1-mini chain-200 (n=200) |
|---|---:|---:|
| `peer_calibrated` | 0.5955 | 0.7381 |
| `static_roles` | 0.5802 | 0.7454 |
| `self_claim` | 0.5619 | 0.7641 |

Overlay marker: `peer_calibrated` fullval F1 = **0.7703** (n=7405). Source: `artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/metrics.json`.

`static_roles` and `self_claim` fullval are corrupted by upstream provider model drift and are pending rerun (U-006-decide). This figure therefore intentionally compares only chain-200 numbers across backbones, with fullval shown only where it is validated.

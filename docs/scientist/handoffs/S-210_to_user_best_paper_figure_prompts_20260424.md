# S-210 to user: Best-Paper figure prompts ready

Author: scientist
Target: user
Date: 2026-04-24
Priority: P1

## What I prepared

I created four AI-renderable figure prompts for the Best-Paper route:

1. `docs/paper/figures_prompts/fig3_r2_information_advantage_prompt.md`
2. `docs/paper/figures_prompts/fig4_r3_specialization_entropy_prompt.md`
3. `docs/paper/figures_prompts/fig5_small_model_capability_boundary_prompt.md`
4. `docs/paper/figures_prompts/fig6_best_paper_evidence_map_prompt.md`

The index file is:

`docs/paper/figures_prompts/best_paper_figure_prompt_index_20260424.md`

## Recommended rendering order

Render Figure 3 first. It is data-free and supports the strongest method claim: R2 recursive audit has an information advantage over terminal-only feedback.

Render Figure 5 second, but keep it as a placeholder template until the engineer produces real Phi-4 / SmolLM3 / gpt-4.1-mini matched metrics.

Render Figure 4 third if we want a specialization / emergence visual.

Render Figure 6 only if we want an internal roadmap or appendix-style evidence map.

## Output location

Please place final vector assets under:

`artifacts/figures/`

Preferred format: `.svg` or `.pdf`. PNG can be kept as preview only.

# S-230 Figure Prompt Claude-Style Revision

Date: 2026-04-27
Author role: scientist

## User Direction

The user clarified the intended figure roles:

1. Figure 1 should become a single-column comparison figure because it is only a paradigm contrast, not the method architecture.
2. Figure 2 should become the two-column main pipeline figure because it carries the overall EDO-Frame method structure.
3. Figure 2 should be more detailed and structurally closer to `docs/references/架构图/image4.png`.
4. The next visual style should follow Claude.ai warm minimalism: paper-like background, terracotta accent, generous whitespace, rounded cards, subtle shadows, and modern sans-serif labels.

## Files Updated

1. `docs/paper/figures_prompts/claude_warm_minimalism_style_20260427.md`
   - New shared style guide for the next render pass.
   - Records palette, typography, layout rules, agent icon rules, and a master prompt snippet.

2. `docs/paper/figures_prompts/fig1_paradigm_comparison_pixel_prompt.md`
   - Rewritten as a single-column compact comparison card.
   - Four rows: single call, fixed role chain, planner/debate, EDO-Frame.
   - Uses abstract dots/cards if needed instead of heavy pixel-agent panels.
   - Target asset changed to `fig1_paradigm_comparison_claude`.

3. `docs/paper/figures_prompts/fig2_edo_frame_pipeline_pixel_prompt.md`
   - Rewritten as the two-column main method architecture figure.
   - Uses the `image4.png`-like structure: large left workbench, right repeated action-cycle mini-diagrams, bottom evidence trail.
   - Makes memory, tools, audit, action schema, local graph, and reproducible logs visible.
   - Target asset changed to `fig2_edo_frame_pipeline_claude`.

4. `docs/paper/figures_prompts/best_paper_figure_prompt_index_20260424.md`
   - Updated to v3.
   - Records the width policy: Figure 1 single-column, Figure 2 two-column, Figure 3 optional/single-column or appendix-front depending on page budget.
   - Points to the new Claude warm style guide.

## Next Render Order

1. Render Figure 2 first because it is the main method figure.
2. Render Figure 1 second as a compact intro teaser.
3. Render Figure 3 only if Figure 2 does not absorb enough mechanism detail.

## Residual Note

The current prompt filenames still contain `pixel` for continuity, but the target asset names and active style have shifted to Claude warm minimalism. A future cleanup can rename prompt files after the new figures land.

## 2026-04-27 Follow-Up: Standalone Drop-In Prompts

The user clarified that only the fenced `Drop-In AI Image Prompt` block is copied into the image-generation UI. In response, the Figure 1 and Figure 2 drop-in prompts were expanded to be fully self-contained: each now includes the full Claude warm palette, typography rules, spacing rules, layout structure, required labels, negative constraints, paper-width requirement, and render-quality expectations inside the copied prompt itself. The shared style guide now records this as a hard rule for future figure prompts.

## 2026-04-27 Follow-Up: Figure 3 And Typography Pass

The user later clarified that all paper-facing figures must share one style, Figure 3 had not yet been revised, and the current renders were close to Claude's website style but still missed the typography. A quick public typography check found consistent references to Styrene / Styrene B for Claude/Anthropic UI labels and headings, with Tiempos Text / Anthropic Serif and sometimes Galaxie Copernicus-like serif accents for reading/editorial text.

Actions taken:

1. `fig3_action_detail_pixel_prompt.md` was rewritten from the old blue pixel-agent style into the same Claude warm minimalism family as Figures 1 and 2.
2. Figure 1 / Figure 2 / Figure 3 drop-in prompts now explicitly request Styrene B / Styrene labels, with close grotesk fallbacks and optional Tiempos / Anthropic Serif title accents.
3. Old non-main-body prompt files were deleted from the active prompt directory. The directory now keeps only the three paper-facing figure prompt files plus the style guide and index.
4. `best_paper_figure_prompt_index_20260424.md`, `USER_TODO.md`, and `SCIENTIST_TODO.md` were updated so future render instructions point to the cleaned prompt set.

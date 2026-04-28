# S-240 Figure Prompt A4-Card / Styrene Revision

Date: 2026-04-28
Author role: scientist

## 1. Trigger

The user reviewed the v2 figure direction and identified two style-level problems that apply to all three concept figures:

1. the outer figure background should be pure white like an A4 / ACL paper page, while the Claude warmth should live inside cards;
2. typography should match Claude.ai figure typography: Styrene only, with Medium/Bold for titles and Regular/Book for labels, and no serif fonts inside graphics.

## 2. Edits

Updated:

- `docs/paper/figures_prompts/claude_warm_minimalism_style_20260427.md`
- `docs/paper/figures_prompts/fig1_paradigm_comparison_pixel_prompt.md`
- `docs/paper/figures_prompts/fig2_edo_frame_pipeline_pixel_prompt.md`
- `docs/paper/figures_prompts/fig3_action_detail_pixel_prompt.md`
- `docs/paper/figures_prompts/best_paper_figure_prompt_index_20260424.md`
- `docs/coordination/USER_TODO.md`
- `docs/coordination/SCIENTIST_TODO.md`

The new shared prompt contract is:

```text
outer canvas: pure white #FFFFFF
internal cards: warm #F4F3EE / #FAF9F5
sub-cards/chips: white #FFFFFF
accent: terracotta #C15F3C
font family: Styrene only
headings: Styrene Medium/Bold
labels/chips: Styrene Regular/Book
no serif fonts inside figures
```

## 3. Status

`C-026` now asks the user to regenerate all three figures, not only Figure 2 / Figure 3. `figure1_v1.png` remains a temporary already-wired asset in the current PDF, but it is no longer treated as final publication-quality after the user's A4-card style correction.

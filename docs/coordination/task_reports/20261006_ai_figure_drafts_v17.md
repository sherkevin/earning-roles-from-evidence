# Task report — AI figure drafts v17

- **Date:** 2026-10-06
- **Status:** `PARTIAL`
- **Goal change requested:** `false`
- **Scientific readiness:** `false`

## Purpose

The user required the three paper figures to be redrawn through AI image generation, with every
version and prompt retained, instead of using HTML as the final visual source. This task creates
semantic/composition drafts and a handoff contract for professional redrawing.

## Versioned deliverable

All artifacts are under
[`ai_versions/v17_ai_draft_20261006`](../../../article/aamas2027/figures/ai_versions/v17_ai_draft_20261006/):

- `figure1_draft.png` and `figure1_prompt_v1.md` — the causal spine from situated use to
  responsibility-scoped evidence and later assignment;
- `figure2_draft.png`, `figure2_draft_v2.png`, and prompts v1/v2 — three information lanes for
  episode facts, public evidence, and legal decisions; v2 corrects the v1 `project` arrow;
- `figure3_draft.png` and `figure3_prompt_v1.md` — ArtifactRole/PeerSelect tracks, matched
  policies, and pre-registered endpoints;
- `figure_design_spec.md`, `README.md`, and `visual_review.md` — natural-language specifications,
  palette, gallery-derived style anchors, and platform acceptance checks.

The original generated outputs remain in the versioned generation archive. No draft overwrote an
older version. Current paper PDFs (`overview.pdf`, `method_state.pdf`, `experiment_map.pdf`) were
intentionally left unchanged until the user supplies professional platform renders.

## Visual review

Figure 1 has the cleanest current causal spine. Figure 2 v2 is the preferred semantic draft
because it fixes the v1 arrow endpoint; its dashed target-outcome route should be checked at final
paper scale. Figure 3 is a strong composition draft but its top contract ribbon should be typeset
if the professional platform output becomes cramped in a two-column column width.

The current drafts are not submission assets: exact typography, vector export/embedded fonts,
300-dpi or better rasterization, two-column legibility, and spelling must be checked after
professional redrawing.

## Goal reconciliation

The figure design requirement is `PARTIAL`: the semantic contracts and prompts are complete, but
the final assets and paper integration are intentionally pending. This task supplies no
scientific evidence and does not open the submission gate. `goal_change_requested=false`.

## Next action

Use the versioned prompts/specifications to obtain platform renders. Add them as
`figure{1,2,3}_platform_vN.<ext>` without overwriting drafts; then run a print-size review,
replace the active PDFs only after semantic approval, rebuild the paper, and recheck exactly eight
body pages.

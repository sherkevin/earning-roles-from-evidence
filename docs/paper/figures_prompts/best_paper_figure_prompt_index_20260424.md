# EDO Paper Figure Prompt Index

> Created: 2026-04-24
> Revised: 2026-04-28 v6 after user typography / A4-card correction
> Owner: scientist
> Governing style: `docs/paper/figures_prompts/claude_warm_minimalism_style_20260427.md`
> Scope: AI-rendered conceptual / architecture figures only. Quantitative result plots must be generated from engineer-validated artifacts.

---

## 1. Revised Figure Budget

Use **three coordinated paper-facing figures**, not seven independent diagrams.

The old prompt set was too fragmented: it separated R2, R3, small-model capability, evidence map, and trace into too many figures before the paper had enough validated evidence to justify them. The revised plan follows a tighter EMNLP-style sequence:

1. **Figure 1: Single-column paradigm comparison** - compact teaser showing what EDO adds over common agent-system paradigms.
2. **Figure 2: Two-column overall EDO-Frame pipeline** - the main method architecture figure showing how a task flows through local agents, memory, tools, audit, and reproducible logs.
3. **Figure 3: Key detail mechanism** - the one-hop governed action loop: note board memory, tag-gated tools, recursive delegation, audit, and tag-drift reselection.

Width policy:

```text
Figure 1: single-column compact comparison.
Figure 2: two-column primary method architecture.
Figure 3: single-column or appendix-front mechanism zoom-in, depending on page budget.
```

If page budget becomes tight, keep Figure 2 first. Figure 1 can remain a compact single-column teaser. Figure 3 can move to appendix only if Figure 2 absorbs enough mechanism detail cleanly.

## 1.1 Render QA And Fix Direction

The first render pass showed that the three-figure plan is reasonable, but the
agent identities and typography were not visually locked:

```text
Figure 1: readable comparison, but baseline and EDO agents use slightly different sprite conventions.
Figure 2: good pipeline structure, but local agents became different characters and one node label drifted into a stray "k".
Figure 3: strong layout, but Agent i became a smooth vector avatar and Peer j was duplicated.
Typography: close to Claude, but too generic; all figure text must use Styrene only, with Medium/Bold for headings and Regular/Book for labels. No serif fonts should appear inside graphics.
```

For the next render pass, use `claude_warm_minimalism_style_20260427.md`. The user specifically requested a Claude.ai-like warm premium paper aesthetic, with Figure 1 converted to a single-column comparison and Figure 2 promoted to a detailed two-column pipeline. The outer canvas should be pure white like A4 paper; Claude warmth should live inside rounded cards. `docs/references/架构图/image4.png` is the closest local structural reference for Figure 2: a large warm workbench plus repeated mini-mechanism diagrams.

2026-04-28 v1/v2 gate update: `figure1_v1.png` is temporarily wired into the main paper, but the user now wants all three figures regenerated in the same A4-white plus Claude-warm-card format. `figure2_v1.png` and `figure3_v1.png` remain blocked for direct replacement: Figure 2 needs a cleaner two-column render with no design-scaffold label, no duplicate panel title, and conservative logged-evidence wording; Figure 3 needs fewer elements, semantic panel labels, and prose action labels such as "call tool" / "update memory".

2026-04-28 later v2 asset check: `figure2_v2.png` is accepted and wired into the main paper as a two-column method figure. `figure3_v2.png` is rejected because it visibly includes a typography note and duplicates `Peer j`; the Figure 3 prompt now explicitly forbids visible font/style notes and duplicate peer nodes. Figure 1 still needs a final v6-style replacement because `figure1_v1.png` predates the white-A4 / Styrene-only correction.

---

## 2. Active Prompts

### Figure 1: Paradigm Comparison

File:

```text
docs/paper/figures_prompts/fig1_paradigm_comparison_pixel_prompt.md
```

Role:

```text
intro / related-method contrast
```

Reader takeaway:

```text
EDO differs from single calls, fixed role chains, and planner/debate patterns because organization forms locally.
```

Render priority:

```text
P1 compact visual hook; single-column only.
```

### Figure 2: Overall Pipeline

File:

```text
docs/paper/figures_prompts/fig2_edo_frame_pipeline_pixel_prompt.md
```

Role:

```text
main method architecture
```

Reader takeaway:

```text
An input task becomes local agent actions, note-board memory, tag-gated tools, recursive audit, and a reproducible evidence package inside a warm workbench-style architecture.
```

Render priority:

```text
P0 main-body two-column figure.
```

### Figure 3: Key Detail Mechanism

File:

```text
docs/paper/figures_prompts/fig3_action_detail_pixel_prompt.md
```

Role:

```text
method detail / mechanism zoom-in
```

Reader takeaway:

```text
At each hop, an agent uses local task tags, profile tags, memory, and tool cards to choose an auditable action, then updates state through audit feedback.
```

Render priority:

```text
P0 main-body or appendix-front figure. Do not drop unless Figure 2 absorbs its content cleanly.
```

---

## 3. Prompt Cleanup

Only the three paper-facing figure prompt files remain active:

```text
fig1_paradigm_comparison_pixel_prompt.md
fig2_edo_frame_pipeline_pixel_prompt.md
fig3_action_detail_pixel_prompt.md
```

The old fragmented prompt files were deleted from the active prompt directory because they are not planned as main-body figures. Their ideas are folded into the three-figure system:

```text
R2 audit intuition -> Figure 3
R3 state / specialization intuition -> Figure 3
small-model capability boundary -> not AI-rendered until validated data exists
best-paper evidence map -> internal planning only
qualitative trace -> appendix only after a real trace is selected
```

---

## 4. What Not To Draw With AI Prompts

Do not ask an image model to invent or render:

```text
F1 / EM / token values
confidence intervals
leaderboard bars
baseline result tables
error-taxonomy counts
dataset-specific numeric matrices
```

These must come from scripts and validated artifacts.

The Figure 1 "comparison" is a **conceptual paradigm comparison**, not an empirical performance chart.

---

## 5. Rendering Order

1. Render `fig2_edo_frame_pipeline_pixel_prompt.md` first as the two-column main method figure.
2. Render `fig1_paradigm_comparison_pixel_prompt.md` second as the compact single-column teaser.
3. Render `fig3_action_detail_pixel_prompt.md` third only if the paper still needs a separate mechanism zoom-in after Figure 2 is revised.

Recommended final asset paths:

```text
artifacts/figures/fig1_paradigm_comparison_claude.{svg,pdf,png}
artifacts/figures/fig2_edo_frame_pipeline_claude.{svg,pdf,png}
artifacts/figures/fig3_action_detail_claude.{svg,pdf,png}
```

Prefer `.svg` or `.pdf` as the paper source. Keep `.png` only as a preview.

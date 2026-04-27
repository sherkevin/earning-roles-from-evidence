# USER_TODO - User Decisions And Execution State

Maintainer: user coordinator.
Scope: user-owned decisions, user execution tasks, and cross-role requests that need user action.

Encoding policy: this file is rebuilt in English-only UTF-8 as of 2026-04-27.

Full pre-rebuild source is preserved at:

- `docs/archive/todo_mojibake_backup_20260427/USER_TODO.md`
- earlier backup: `docs/archive/USER_TODO_mojibake_backup_20260424.md`

Do not paste historical mojibake back into this active file. Add new rows in English only.

## A. Active User Decisions

| Status | ID | Priority | Decision | Current Result | Downstream Effect | Source / Notes |
|---|---|---|---|---|---|---|
| DONE | `U-025-decide` | P0 | Cost-controlled external API strategy for canonical evidence. | User approved option (a): hybrid claim-first API gate. Local GPU / open-weight runs are for exploration and diagnostics; paid API is reserved for claim-critical cells only when the user later reopens quota. | Canonical paid `gpt-4.1-mini` launches remain parked by `U-EXEC-008`; no paid API call should be launched now. | `docs/scientist/analysis/S-222_user_decision_sync_local_first_20260427.md`; `docs/engineer/results/E-041_e030_wave1_launch_packet_20260426.md` |
| DONE | `U-024-decide` | P1 | Paper-level positioning for the local small-model emergence line. | User approved option (c): dual-axis positioning. Keep `gpt-4.1-mini` as the canonical strong-model axis; use Phi-4-mini / SmolLM3-3B as a local capability-boundary axis. | Scientist may scope local-emergence wording, but paper claims still require positive and stable local evidence. | `docs/paper/small_model_emergence_response_20260423.md`; `docs/scientist/analysis/S-222_user_decision_sync_local_first_20260427.md` |
| OPEN | `U-EXEC-009` | P2 | Submission / ambition route: EMNLP sprint, ARR follow-up cycle, or longer Best-Paper track. | Not yet decided. | Affects paper ambition, figure density, experiment breadth, and reviewer trigger cadence. | Best decided after `E-042` local Wave-0 and the next evidence-state update. |
| OPEN | `U-005-cleanup-decide` | P3 | Whether to clean old `dead` run directories. | Deferred. | Does not block the paper. | Recommended after paper freeze / camera-ready cleanup. |
| OPEN | `U-008-decide` | P3 | Whether to move `idea.md` and `experiment.md` under `docs/`. | Deferred. | Structural cleanup only; not on the current evidence path. | Recommended after paper freeze. |

## B. Active User Execution Tasks

| Status | ID | Priority | Task | Why It Matters | Current Guidance |
|---|---|---|---|---|---|
| DONE / PARKED | `U-EXEC-008` | P0 | newapi / paid API quota recharge or availability confirmation. | Controls whether canonical paid `gpt-4.1-mini` Wave-1 can launch. | User chose no paid API recharge / launch for now. First use the no-paid server-local open-weight route. Engineer `E-042` is the active next step. |

## C. Cross-Role Requests To User

| Status | ID | Priority | Sender | Request | Impact | Current Result |
|---|---|---|---|---|---|---|
| DONE | `C-025` | P0 | scientist + engineer | Reply to the `U-025` route choice. | Previously blocked paid canonical evidence planning. | Closed by user decision on 2026-04-27: `U-025=(a)`, paid execution parked for now. |
| DONE | `C-024` | P1 | scientist + engineer | Reply to the `U-024` paper-positioning choice. | Previously blocked whether local emergence enters the paper narrative. | Closed by user decision on 2026-04-27: `U-024=(c)`. |
| TODO | `C-026` | P1 | scientist | Re-render final publication-quality EDO concept figures from the self-contained Claude warm minimalism drop-in prompts. | Blocks any useful presentation-readiness full review. | Active prompt set is now only Figure 1 / Figure 2 / Figure 3 plus the style/index files. Render `fig2_edo_frame_pipeline_pixel_prompt.md` first as the two-column main pipeline, `fig1_paradigm_comparison_pixel_prompt.md` second as the single-column comparison teaser, and `fig3_action_detail_pixel_prompt.md` third if a separate mechanism zoom-in remains needed. All three prompts now enforce the same Claude/Anthropic typography direction: Styrene B / Styrene labels with optional Tiempos / Anthropic Serif title accent. Copy only the fenced `Drop-In AI Image Prompt` block. Rejection criteria remain: no stray `k`, no `compac chips`, no duplicate `Peer j`, no mixed icon family, no old blue pixel style, and final paper assets should preferably be SVG/PDF. |

## D. Critical Completed Decisions

| Date | ID | Status | Summary |
|---|---|---|---|
| 2026-04-27 | `U-025-decide` | DONE | User approved hybrid claim-first API gate; paid API execution remains parked while local open-weight execution goes first. |
| 2026-04-27 | `U-EXEC-008` | DONE / PARKED | User chose no paid API recharge / launch for the next step; scientist dispatched engineer `E-042`. |
| 2026-04-27 | `U-024-decide` | DONE | User approved dual-axis positioning: canonical strong-model axis plus local capability-boundary axis. |
| 2026-04-27 | `DOC-LANG-001` | DONE | New project documents and TODO updates should be written in English to avoid mojibake / encoding drift. Rule recorded in `.cursor/rules/collaboration-workflow.mdc`. |
| 2026-04-20 | `U-022-decide` | DONE | Axis A full-system SOTA candidates locked as MA-RAG + ReAgent. |
| 2026-04-20 | `U-021-decide` | DONE | Appendices may be supplementary, but the main body must remain self-contained. |
| 2026-04-20 | `U-020-stage2-fullval-launch-decide` | DONE / REGRESSED | Original 3-seed fullval approval later hit quota truncation; resumed / guarded strategy superseded full rerun. |
| 2026-04-20 | `U-018-decide` | DONE | Add Multi-Agent Debate (MAD) as the third external baseline. |
| 2026-04-20 | `U-014-decide` | DONE | External baseline set included AutoGen + ChatEval at that stage. |
| 2026-04-20 | `U-013-decide` | DONE | MuSiQue added as the second benchmark. |
| 2026-04-20 | `U-012-decide` | DONE | Stage-2 mechanisms R1 split, R2 audit, and R3 vector belief should all be pursued. |
| 2026-04-19 | `U-011-decide` | DONE | Choose the Stage-2 route rather than a Stage-1 negative-result framing. |
| 2026-04-19 | `U-010-decide` | DONE | Local git version control approved. |
| 2026-04-19 | `U-009-decide` | DONE | LaTeX source and buildable paper stay under `article/`. |
| 2026-04-19 | `U-004-decide` | DONE | `ModelDriftError` belongs in appendix / limitations, not the main paper narrative. |
| 2026-04-19 | `U-003-decide` | DONE | Two-paper direction merged into one long-paper LaTeX draft. |
| 2026-04-19 | `U-002-decide` | DONE | Rebuttal records should live under `artifacts/rebuttals/`. |
| 2026-04-19 | `U-001-decide` | DONE | Use a single `SCIENTIST_TODO.md` for scientist state. |

For older or lower-priority historical decisions, use the archived full source listed at the top of this file.

## E. Revision Log

| Date | Author | Change | Notes |
|---|---|---|---|
| 2026-04-27 | scientist | Updated `C-026` after the Claude typography and Figure 3 style pass. | Active prompt directory now keeps only the three paper-facing figure prompts plus style/index files; Figure 3 has been converted from blue pixel style to Claude warm minimalism. |
| 2026-04-27 | scientist | Updated `C-026` after S-230 figure prompt revision. | User should render from self-contained Drop-In prompts; Figure 2 is now the two-column main pipeline, Figure 1 is a single-column comparison teaser. |
| 2026-04-27 | scientist | Rebuilt this file in English-only UTF-8 after user approval. | Full original source preserved in `docs/archive/todo_mojibake_backup_20260427/USER_TODO.md`. |

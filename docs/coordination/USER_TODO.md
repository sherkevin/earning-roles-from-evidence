# USER_TODO - User Decisions And Execution State

Maintainer: user coordinator.
Scope: user-owned decisions, user execution tasks, and cross-role requests that need user action.

Encoding policy: this file is rebuilt in English-only UTF-8 as of 2026-04-27.

Full pre-rebuild source is preserved at:

- `docs/archive/todo_mojibake_backup_20260427/USER_TODO.md`
- earlier backup: `docs/archive/USER_TODO_mojibake_backup_20260424.md`

Do not paste historical mojibake back into this active file. Add new rows in English only.

## A. Active User Decisions

### 2026-09-16 AAMAS redirection and time-sensitive actions

- RECORDED / `U-AAMAS-2027`: user requests a substantive project/manuscript rebuild after the EMNLP rejection, incorporating actual reviews and independent scientific judgment, targeting AAMAS. The next verified main-track cycle is AAMAS 2027. Preserve old sources and evidence; new draft is `article/aamas2027/`.
- RECORDED / `U-AAMAS-DOCS`: on 2026-09-16 the user requests requirements first, per-requirement gaps/tasks second, feasible execution afterward, and consolidation into a clean consistent document set. [REQUIREMENTS.md](../paper/aamas2027/REQUIREMENTS.md) and [AAMAS_TASKS.md](AAMAS_TASKS.md) are the active pair.
- RECORDED / `U-AAMAS-C`: user selects C, acquired specialization from initially comparable agents, and makes workflows persistent/composable first-class MAS objects alongside skills, tools and memory. This supersedes the provisional recommendation to start with fixed private evidence (A). Early-experience lock-in and continual improvement are research hypotheses requiring evidence. Active design and task state remain in the canonical AAMAS ledger.
- Author action state, urgent account deadline, reviewer/Findings choices, AI disclosure, submission IDs and receipts are maintained only under **A-T12** in [AAMAS_TASKS.md](AAMAS_TASKS.md). No accounts or submissions were created by this work.
- RECORDED: prior no-paid-API execution policy remains in force. The current internal draft is not submission-ready; the old S-518 handoff is superseded by the canonical ledger.

Verified sources/calendar and current scientific requirements: `docs/paper/aamas2027/REQUIREMENTS.md`. Scope, gaps, statuses and execution: `docs/coordination/AAMAS_TASKS.md`. S-518 is a historical first-pass record.

| Status | ID | Priority | Decision | Current Result | Downstream Effect | Source / Notes |
|---|---|---|---|---|---|---|
| SUPERSEDED | `U-025-decide` | P0 | Cost-controlled external API strategy for canonical evidence. | Superseded 2026-05-15: user retired paid API execution. Paper-facing comparisons now use server-local models with the same local backbone across frameworks. | No paid API call should be launched for this submission; the old paid launcher packet is archival. | `docs/scientist/analysis/S-377_local_same_model_sota_pivot_20260515.md`; `docs/engineer/results/E-187_local_same_model_policy_pivot_20260515.md` |
| UPDATED | `U-024-decide` | P1 | Paper-level positioning for the local small-model emergence line. | Updated 2026-05-15: local server backbones are the main experimental route, not a side axis. Qwen2.5-3B-Instruct is the current paper-facing same-model framework-comparison backbone; Phi-4-mini remains supporting evidence. | Scientist should frame claims as local same-backbone SOTA on the tested QA family, not paid-backbone universal SOTA. | `docs/scientist/analysis/S-377_local_same_model_sota_pivot_20260515.md`; `docs/paper/final_experiment_matrix.md` |
| DONE | `U-032-local-same-model-sota` | P0 | Whether to make server-local same-model comparisons the authoritative submission route. | User confirmed 2026-05-15: piad/paid API is no longer pursued; all frameworks should be evaluated on the same server-local model, and the paper can claim SOTA within that controlled setting. E188 is now running to strengthen the HotpotQA same-Qwen framework breadth beyond the existing n=200/fullval MAS spine. | Closes `C-027` as retired and directs future work to local, predeclared, no-paid experiments only. | Source: user directive 2026-05-15; `docs/scientist/analysis/S-377_local_same_model_sota_pivot_20260515.md`; E188 log `docs/engineer/logs/E-188_qwen_hotpotqa_n500_framework_breadth_20260515.md`. |
| SUPERSEDED | `U-EXEC-009` | P2 | Submission / ambition route. | User redirected the rejected EMNLP project to AAMAS on 2026-09-16. | AAMAS 2027 audit and internal manuscript reconstruction complete; empirical rebuild remains open. | `U-AAMAS-2027`; S-518 execution record. |
| DONE | `U-029-third-backbone` | P2 | Whether to add a third open-weight backbone to the cross-backbone evidence axis. | User approved: add a third open-weight backbone. Scientist/engineer route: use `Qwen2.5-3B-Instruct` as the default third-backbone gate because it is a strong small open-weight instruction model and complements Phi-4 / SmolLM3. | Opened engineer `E-115`; E-114 shows idle 11GB GPUs cannot serve vLLM without sudo-installed build deps, so E-115 waits for E-110 to free 24GB endpoints. | Approval source: user message 2026-05-05; blocker note: `docs/engineer/results/E-114_11gb_gpu_vllm_blocker_20260505.md`. |
| DONE | `U-030-no-paid-fullval-baselines` | P1 | Whether to launch no-paid MA-RAG fullval plus MAD fullval on Phi-4-mini after E-108/E-109/E-110 complete. | User approved. | Opened engineer `E-116` to run no-paid MA-RAG + MAD fullval after E-110 frees Phi-4 endpoints; this is the no-paid route for the R-FULL-035 matched-recent-baseline cap. | Approval source: user message 2026-05-05; audit: `docs/engineer/analysis/best_paper_gap_audit_20260505.md` Cap B. |
| DONE | `U-031-ablation-scope` | P2 | Which paper-claimed Stage-2 mechanisms to actually implement vs explicitly bracket as future work. | User approved implementation path: do not leave Stage-2 mechanisms only as future work; implement and ablate them. | Opened engineer `E-117` for recursive audit / split-stage / persona-tag / governed-memory implementation and paper-grade no-paid ablation gates. | Approval source: user message 2026-05-05; audit: `docs/engineer/analysis/best_paper_gap_audit_20260505.md` Cap C. |
| OPEN | `U-005-cleanup-decide` | P3 | Whether to clean old `dead` run directories. | Deferred. | Does not block the paper. | Recommended after paper freeze / camera-ready cleanup. |
| OPEN | `U-008-decide` | P3 | Whether to move `idea.md` and `experiment.md` under `docs/`. | Deferred. | Structural cleanup only; not on the current evidence path. | Recommended after paper freeze. |

## B. Active User Execution Tasks

| Status | ID | Priority | Task | Why It Matters | Current Guidance |
|---|---|---|---|---|---|
| CLOSED | `U-EXEC-008` | P0 | newapi / paid API quota recharge or availability confirmation. | Historical paid route only. | User retired paid API execution on 2026-05-15. Do not request recharge or launch paid jobs for this submission; use server-local models only. |
| SUPERSEDED | `U-EXEC-010` | P0 | ARR / EMNLP 2026 submission execution. | The paper was submitted and rejected; actual reviews are in the repository. The former submission-readiness decision is historical. | Follow the AAMAS 2027 actions above. The new draft is internal and needs new empirical evidence; do not reuse the former readiness verdict. Source: S-518 execution record and actual OpenReview reviews. |

## C. Cross-Role Requests To User

| Status | ID | Priority | Sender | Request | Impact | Current Result |
|---|---|---|---|---|---|---|
| DONE | `C-025` | P0 | scientist + engineer | Reply to the `U-025` route choice. | Previously blocked paid canonical evidence planning. | Closed by user decision on 2026-04-27: `U-025=(a)`, paid execution parked for now. |
| DONE | `C-024` | P1 | scientist + engineer | Reply to the `U-024` paper-positioning choice. | Previously blocked whether local emergence enters the paper narrative. | Closed by user decision on 2026-04-27: `U-024=(c)`. |
| RETIRED | `C-027` | P0 | engineer | Former canonical paid `E-030` / `E-041` HotpotQA-200 Wave-1 execution gate. | Paid canonical matrix is no longer part of the submission route. | User retired paid API execution on 2026-05-15. Keep `docs/engineer/results/E-092_paid_wave1_launcher_update_20260504.md` as an archival dry-run packet only; do not reopen it as a blocker. |
| DONE | `C-026` | P1 | scientist | Re-render final publication-quality EDO concept figures from the self-contained Claude warm minimalism drop-in prompts. | Previously blocked final visual/layout R-PART review. | Completed by scientist self-render: deterministic local `figure1_v4.pdf` / `figure1_v4.png` generated by `scripts/render_figure1_v4.py`, wired into `article/latex/edo_paper.tex`, and build-verified page-compliant (main body page 8, 0 overfull hboxes) via `S-300`. Figure 2 v2 and Figure 3 v3 remain accepted and wired. |
| DONE | `C-029` | P2 | engineer | Reply to `U-029-third-backbone`. | Unblocked third-backbone planning. | User approved adding a third open-weight backbone; default selected route is `Qwen2.5-3B-Instruct`, tracked as engineer `E-115` after E-110 frees 24GB endpoints. |
| DONE | `C-030` | P1 | engineer | Reply to `U-030-no-paid-fullval-baselines`. | Unblocks no-paid fullval baseline work. | User approved no-paid MA-RAG + MAD fullval; engineer row `E-116` will launch after E-110 completes. |
| DONE | `C-031` | P2 | engineer + scientist | Reply to `U-031-ablation-scope`. | Unblocks Stage-2 mechanism implementation / ablation work. | User approved implementation path rather than future-work bracketing; engineer row `E-117` opened. |

## D. Critical Completed Decisions

| Date | ID | Status | Summary |
|---|---|---|---|
| 2026-04-27 | `U-025-decide` | DONE | User approved hybrid claim-first API gate; paid API execution remains parked while local open-weight execution goes first. |
| 2026-04-27 | `U-EXEC-008` | DONE / PARKED | User chose no paid API recharge / launch for the next step; scientist dispatched engineer `E-042`. |
| 2026-04-27 | `U-024-decide` | DONE | User approved dual-axis positioning: canonical strong-model axis plus local capability-boundary axis. |
| 2026-05-15 | `U-032-local-same-model-sota` | DONE | User retired paid API execution and made server-local same-model framework comparison the paper-facing SOTA route. |
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
| 2026-05-05 | engineer | Added `U-030-no-paid-fullval-baselines` (P1) + `U-031-ablation-scope` (P2) + `C-030` + `C-031` after Best-Paper gap audit identified Cap B (matched fullval baselines) and Cap C (missing Stage-2 ablations) as the two highest-impact remaining structural caps after E-108/109/110 land. | Cross-link: `docs/engineer/analysis/best_paper_gap_audit_20260505.md`. The no-paid MA-RAG/MAD fullval path (U-030) is the highest-lift no-paid action available. |
| 2026-05-15 | scientist+engineer | Added `U-032-local-same-model-sota`, retired `C-027`, and closed `U-EXEC-008` after the user clarified that paid API execution is no longer pursued. | Cross-link: `docs/scientist/analysis/S-377_local_same_model_sota_pivot_20260515.md`; `docs/engineer/results/E-187_local_same_model_policy_pivot_20260515.md`. |
| 2026-05-05 | engineer | Authored `docs/engineer/analysis/best_paper_gap_audit_20260505.md` joint cross-role audit. | Triggered by user question "现在距离 best paper 还差什么"; identifies 3 hard structural caps (cross-backbone, matched SOTA, ablation completeness) with closure costs and decision owners. |
| 2026-05-05 | engineer | Added `U-029-third-backbone` (P2) and `C-029` (P2) after E-108 + E-109 + E-110 filled all phi4-mini endpoints; engineer recommends approving a third open-weight backbone gate on the idle 11GB GPUs to strengthen reviewer-flagged cross-backbone breadth. | This is a critical-decision escalation per `engineer-role-rules.mdc §4` (changing the targeted set of baselines). |
| 2026-05-04 | engineer | Updated `C-027` after user reconfirmed no paid launch for now. | Canonical paid Wave-1 remains parked; `E-092` launcher is ready but inactive. Continue no-paid local closure and artifact packaging first. |
| 2026-04-29 | scientist | Updated `C-026` with latest-version-only figure rendering policy. | Figure 1 should next render as `figure1_v2`; Figure 3 should next render as `figure3_v3`; old non-versioned figures are historical rejects. |
| 2026-04-29 | scientist | Hardened `C-026` Figure 1 / Figure 3 prompts after user directive to keep improving while engineering is blocked. | Added hard render contracts and pre-return QA checklists to reduce repeated image-model failures: extra labels, non-white exterior, old blue/pixel style, duplicate `Peer j`, visible font/style notes, and typo labels. |
| 2026-04-29 | scientist | Inspected latest Figure 1/2/3 v3 assets. | Accepted `figure3_v3.png` as usable if page budget permits; rejected `figure1_v3.png` for corrupted `global / conversational control` text; kept Figure 2 v2 as current accepted architecture figure. |
| 2026-04-29 | scientist | Rechecked existing figure versions for `C-026`. | Existing `figure*_v*` files do not clear final Figure 1 / Figure 3 readiness; keep `C-026` open. |
| 2026-04-28 | engineer | Added `C-027` after the canonical matrix blocker audit. | The full matrix is not blocked by missing planning; it is blocked by the parked paid canonical execution gate. `E-041` is ready once the user explicitly reopens Wave-1. |
| 2026-04-28 | engineer | Updated `C-027` after `E-052` launcher hardening. | A guarded dry-run-first launcher and status script now exist, so reopening Wave-1 can move directly to monitored execution. |
| 2026-04-28 | scientist | Updated `C-026` after user requested A4-white outer canvas and Styrene-only Claude typography. | All three figures should be regenerated from the updated drop-in prompts; `figure1_v1.png` remains temporary but is no longer final-quality. |
| 2026-04-28 | scientist | Updated `C-026` after v2 figure inspection. | `figure2_v2.png` is accepted and wired into LaTeX; final Figure 1 and Figure 3 assets remain needed. |
| 2026-04-27 | scientist | Updated `C-026` after the Claude typography and Figure 3 style pass. | Active prompt directory now keeps only the three paper-facing figure prompts plus style/index files; Figure 3 has been converted from blue pixel style to Claude warm minimalism. |
| 2026-04-27 | scientist | Updated `C-026` after S-230 figure prompt revision. | User should render from self-contained Drop-In prompts; Figure 2 is now the two-column main pipeline, Figure 1 is a single-column comparison teaser. |
| 2026-04-27 | scientist | Rebuilt this file in English-only UTF-8 after user approval. | Full original source preserved in `docs/archive/todo_mojibake_backup_20260427/USER_TODO.md`. |

# REVIEWER_TODO - Reviewer State

Maintainer: reviewer.
Scope: full-paper review triggers, partial review tasks, review artifacts, and reviewer-to-scientist handoffs.

Encoding policy: this file is rebuilt in English-only UTF-8 as of 2026-04-27.

Full pre-rebuild source is preserved at:

- `docs/archive/todo_mojibake_backup_20260427/REVIEWER_TODO.md`

Do not paste historical mojibake back into this active file. Add new rows in English only.

## A. Role Boundaries

Reviewer does:

- `R-FULL-XXX`: user-approved full-paper reviews only.
- `R-PART-XXX`: scientist / engineer / user requested partial reviews of a specific section, figure, gate, or artifact.
- Writes review artifacts under `artifacts/idea_reviews/` or handoffs under `docs/reviewer/handoffs/`.
- Adds the minimal scientist S-104 trigger required by the collaboration rule after a review lands.

Reviewer does not:

- Modify paper source, core code, experiment configs, or role TODO state beyond explicit reviewer workflow exceptions.
- Trigger full-paper reviews without user approval.
- Run experiments.

## B. Active Review Queue

| Status | ID | Priority | Request | Blocked By | Notes |
|---|---|---|---|---|---|
| DONE | `R-FULL-026` | P1 | User explicitly triggered a fresh full-paper review using `BP-EXPERIMENTS` as the single reviewer lens. | none | Completed at `artifacts/idea_reviews/reviewer_20260427_152649_26_3384de/review.md`; scientist S-104 response is `S-234`. |
| WAITING | next `R-PART` visual gate | P1 | Run a narrow figure/layout gate after user fixes Figure 2 / Figure 3. | `C-026` final figure re-render. | Do not run until Figure 2 removes stray `k` and uses one sprite family, and Figure 3 fixes `compac chips` plus duplicate `Peer j`. |

## C. Recent Full Reviews

| ID | Date | Target | Artifact | Verdict | Key Finding | Scientist Follow-Up |
|---|---|---|---|---|---|---|
| `R-FULL-026` | 2026-04-27 15:26 | `article/build/edo_paper.pdf` SHA `3384DEEABF2B18A1` | `artifacts/idea_reviews/reviewer_20260427_152649_26_3384de/review.md` | overall 4.5, weak reject | Latest PDF remains honest and page/anonymity-safe, but BP-EXPERIMENTS still caps it for single dataset/slice, single-seed local row, absent external baselines, missing causal component ablations, missing transfer, and missing error analysis. | `S-234` completed. |
| `R-FULL-025` | 2026-04-27 13:36 | `article/build/edo_paper.pdf` SHA `93A983ED1827FD6F` | `artifacts/idea_reviews/reviewer_20260427_133650_25_93a983/review.md` | overall 4.5, weak reject | Updated PDF is more honest and structurally stronger with Figure 1 plus local Phi-4-mini diagnostic, but BP-EXPERIMENTS still caps it: single-dataset, mostly single-seed, no matched recent SOTA result baselines, no completed component ablations, no multi-dataset transfer, and Figure 2/3 readiness defects. | `S-229` pending S-104 triage. |
| `R-FULL-024` | 2026-04-26 12:09 | `article/build/edo_paper.pdf` SHA `F914B89A4E45F1EF` | `artifacts/idea_reviews/reviewer_20260426_120902_24_f914b8/review.md` | overall 4.0, weak reject | Completed evidence remains HotpotQA chain-200 / seed=42 / no paired CI / no external result baseline / no delivered R1-R2-R3; weak benchmark-claim alignment; Figure 1 placeholder. | `S-218` completed. |
| `R-FULL-023` | 2026-04-24 16:08 | same PDF SHA `F914B89A4E45F1EF` | `artifacts/idea_reviews/reviewer_20260424_160801_23_f914b8/review.md` | overall 4.0, weak reject | P5 oral-gate review reconfirmed empirical-solidity cap. | `S-212` completed. |
| `R-FULL-022` | 2026-04-24 14:16 | same PDF SHA `F914B89A4E45F1EF` | `artifacts/idea_reviews/reviewer_20260424_141624_22_f914b8/review.md` | overall 4.0, weak reject | Formalization improved but evidence remained restricted Stage-1 / HotpotQA-only / single-seed / no external 2025 baseline. | Superseded by stricter later triage. |
| `R-FULL-021` | 2026-04-23 14:28 | same PDF SHA `F914B89A4E45F1EF` | `artifacts/idea_reviews/reviewer_20260423_142849_21_f914b8/review.md` | overall 4.5, weak reject | Method hygiene improved, but D4 / experiment solidity remained binding. | Superseded by later R-FULL-023/024. |

For older full-review history, use the archive file listed above and `artifacts/idea_reviews/review_index.jsonl`.

## D. Recent Partial Reviews

| ID | Date | Scope | Artifact / Handoff | Verdict | Key Finding | Follow-Up |
|---|---|---|---|---|---|---|
| `R-PART-006` | 2026-04-27 | Optimized reviewer dispatch prompt for the split-lens workflow. | `prompts/reviewer_templates/optimized_reviewer_dispatch_bp_experiments.md` | completed | Added a reusable reviewer takeover / fresh full-review trigger prompt that selects `BP-EXPERIMENTS` as the sole lens, points to `full_prompt_bp_experiments_sota_statistics.md`, preserves mandatory S-104 handoff, and routes novelty-first review to a separate `BP-NOVELTY` batch. | No S-104 trigger; this was reviewer workflow maintenance, not a paper review batch. |
| `R-PART-005` | 2026-04-27 | Reviewer prompt split / single-lens entrypoint hygiene. | `prompts/reviewer_templates/full_prompt_bp_*.md`; `prompts/reviewer_templates/README.md`; `prompts/reviewer_template.md` | completed | Added one reviewer-facing full prompt entrypoint per best-paper lens and strengthened warnings that `common_best_paper_requirements.md` is a shared guardrail, not a second lens or schema. | No S-104 trigger; this was reviewer workflow maintenance, not a paper review batch. |
| `R-PART-004` | 2026-04-27 13:55 | Solution map for `R-FULL-025` reviewer findings. | `docs/reviewer/handoffs/R-PART-004_to_scientist_r_full_025_solution_map_20260427.md` | completed | Translated the `R-FULL-025` BP-EXPERIMENTS caps into an advisory, evidence-bound repair order: `E-045` stability, `E-046` ablation, `E-047` transfer, `E-048` error analysis, then Figure 2/3 visual gate and eventual paid external baselines only if user reopens quota. | Scientist may use during S-104 judgment; not binding and not a replacement for scientist acceptance decisions. |
| `R-PART-003` | 2026-04-27 10:27 | Open-source framework/tooling research for SOTA-oriented EDO engineering. | `docs/reviewer/handoffs/R-PART-003_to_engineer_open_source_framework_tooling_sota_20260427.md` | completed | Recommended mature framework reuse as references/adapters/baselines: LangGraph, AutoGen/AG2, CrewAI, LlamaIndex/Haystack/RAGFlow, mem0/Letta/Zep/MemoryOS, MCP, OpenCompass/AgentBench/GTA/RAGAS. | Engineer `E-043`; Scientist should treat as useful but not binding. |
| `R-PART-002` | 2026-04-27 10:07 | Layout/reference/appendix-figure gate after S-219 page optimization. | `artifacts/idea_reviews/reviewer_20260427_100701_partial_3a9872/review.md`; `docs/reviewer/handoffs/R-PART-002_to_scientist_layout_gate_20260427.md` | partial pass, not full-review ready | Official build passes and `tab:evidence-status` is fixed, but Figure 2/3 visual blockers remain. | Scientist `S-221` completed; figure fix remains `C-026`. |
| `R-PART-001` | 2026-04-26 19:00 | Figure/layout gate after Figure 1/2/3 insertion and EDO-Frame prose. | `artifacts/idea_reviews/reviewer_20260426_190000_partial_d8ced2/review.md`; `docs/reviewer/handoffs/R-PART-001_to_scientist_layout_gate_20260426.md` | partial fail | Build succeeded but had undefined `tab:evidence-status`; main body exceeded 8-page gate; Figure 2/3 still needed fixes. | Scientist `S-219` completed and page gate was fixed. |

## E. Review Index And Aggregates

Primary review metadata:

- `artifacts/idea_reviews/review_index.jsonl`
- `artifacts/idea_reviews/scoreboard.md`
- `artifacts/idea_reviews/fix_themes.md`

Latest review IDs known in the active state:

- latest full review: `R-FULL-026`
- latest partial reviewer task: `R-PART-006`
- latest layout/figure gate: `R-PART-002`

## F. Revision Log

| Date | Author | Change | Notes |
|---|---|---|---|
| 2026-04-27 | scientist | Marked `R-FULL-026` done after locating its review artifact during `S-233` blocker audit. | Scientist S-104 triage recorded in `docs/scientist/analysis/S-234_r_full_026_s104_triage_20260427.md`; reviewer index artifacts may still need regeneration by reviewer tooling. |
| 2026-04-27 | reviewer | Completed `R-PART-006` optimized reviewer dispatch prompt. | Artifact: `prompts/reviewer_templates/optimized_reviewer_dispatch_bp_experiments.md`. |
| 2026-04-27 | reviewer | Completed `R-PART-005` reviewer-template split. | Added five `full_prompt_*.md` single-lens entrypoints and updated README / common-template warnings. |
| 2026-04-27 | reviewer | Started `R-PART-005` reviewer-template split. | Goal: one full prompt file per reviewer perspective; no mixed-lens review entrypoint. |
| 2026-04-27 | reviewer | Completed `R-PART-004` solution map. | Handoff: `docs/reviewer/handoffs/R-PART-004_to_scientist_r_full_025_solution_map_20260427.md`. |
| 2026-04-27 | reviewer | Started `R-PART-004` solution map for `R-FULL-025`. | User requested emphasis on solving reviewer findings, not just listing criticisms. |
| 2026-04-27 | reviewer | Completed `R-FULL-025` and indexed the batch. | Artifact: `artifacts/idea_reviews/reviewer_20260427_133650_25_93a983/review.md`; mandatory scientist S-104 trigger is `S-229`. |
| 2026-04-27 | reviewer | Started `R-FULL-025` from explicit user trigger. | This satisfies the "add a TODO before doing the task" instruction for the new full-paper review batch. |
| 2026-04-27 | scientist | Rebuilt this file in English-only UTF-8 after user approval. | Full original source preserved in `docs/archive/todo_mojibake_backup_20260427/REVIEWER_TODO.md`; do not restore mojibake tail content. |

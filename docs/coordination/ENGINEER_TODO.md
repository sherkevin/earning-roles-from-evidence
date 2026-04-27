# ENGINEER_TODO - Engineering State

Maintainer: engineer.
Scope: implementation, experiment execution, validation scripts, generated outputs, and engineer-to-scientist handoffs.

Encoding policy: this file is rebuilt in English-only UTF-8 as of 2026-04-27.

Full pre-rebuild source is preserved at:

- `docs/archive/todo_mojibake_backup_20260427/ENGINEER_TODO.md`

Do not paste historical mojibake back into this active file. Add new rows in English only.

## A. Current P0/P1 Queue

| Status | ID | Priority | Task | Blocked By | Expected Output |
|---|---|---|---|---|---|
| READY | `E-045` | P0 | Phi-4 multi-seed robustness and CI pack for the positive local n=200 result. | None; use no-paid local Phi-4 route and coordinate GPU/runtime with active tasks. | `docs/engineer/results/E-045_phi4_multiseed_robustness_20260427.md` with seed/slice paths, exact commands, run dirs, metrics, paired-bootstrap CIs, win/tie/loss counts, and stability verdict. |
| DONE | `E-046` | P0 | EDO-Frame ablation six-row diagnostic using `E-043-step1..3` components. | None; completed as a negative causal-component verdict under the transparent bridge. | `docs/engineer/results/E-046_edo_frame_ablation_sixrow_20260427.md` and `docs/engineer/results/E-043-step7_phi4_ablation_n50_20260427.md`: six-row n=50 sweep landed; memory/tool/drift toggles are trace-visible but do not move F1/EM because the bridge does not consume them in prompts/routing. |
| READY | `E-044` | P0 | Deploy `HuggingFaceTB/SmolLM3-3B` on the remote server and run the matched no-paid n=50 HotpotQA health gate for `single_agent` vs `edo_stage2_chain`. | Coordinate with current GPU/runtime usage from `E-042` n=200 if still in flight; no user decision is needed. | `docs/engineer/results/E-044_smol_lm3_remote_deploy_and_health_gate_20260427.md` with endpoint probe, config, exact commands, run dirs, F1/EM/tokens/wall-time, and same-backbone conclusion. |
| DONE | `E-042` | P0 | No-paid local open-weight Wave-0 for Phi-4-mini. Compare `single_agent` vs `edo_stage2_chain` on matched HotpotQA slices. SmolLM3-3B is now split into `E-044`. | None (n=50 + n=200 both landed; bootstrap CI gate is scientist-side). | `docs/engineer/results/E-042_local_open_weight_wave0_20260427.md` §10 records the n=200 Wave-0: `single_agent` F1=0.3646/EM=0.2650 vs `edo_stage2_chain` F1=0.4440/EM=0.3150 (+7.94 F1pp / +5.0 EM pp; 2.33x token cost; first_accept_rate=0). This **flips** the n=50 health-gate sign (-1.24 F1pp at n=50 → +7.94 F1pp at n=200) and is now a candidate paper-grade row pending paired-bootstrap CI. |
| ONGOING | `E-033` | P0 | Maintain claim-first final experiment matrix scheduling discipline. | None. | Every new matrix cell explains why it was selected under claim-first ordering. |
| PARKED | `E-030` | P0 | Fill final baseline x datasize matrix for canonical paid API route. | Parked by user `U-EXEC-008` local-first decision and hybrid API gate. | Resume only when local Wave-0 results or user approval justify paid API spend. |
| DONE | `E-043-step1..3` | P0 | Local EDO-Frame v2 build-out (BM25 hybrid retrieval, drift detector, `edo_frame_chain` bridge with 7+1 ablation flags). | None. | Code in `codes/edo_frame/edo_frame/` and `workspace/idea04_core/methods.py`; 14 unit tests in `codes/edo_frame/tests/` and 6 unit tests in `workspace/idea04_core/test_edo_frame_chain_method.py`. |
| DONE | `E-043-step4` | P1 | Packet self-check script `scripts/check_e030_packet.py`. | None. | Stdlib-only validator. Smoke (`--skip-tests`): 5/5 PASS, exits 0 with `__E030_PACKET_OK__`. Negative (missing config): exits 1 with `__E030_PACKET_FAIL__: required_configs_present - missing config: ...`. Full run (with `pytest`): 5/5 PASS, exits 0. |
| READY | `E-047` | P1 | Multi-dataset local transfer gate: add at least one non-HotpotQA no-paid local result, preferably MuSiQue first and 2Wiki if official data is available. | 2Wiki branch depends on official local `data/2wikimultihop` availability; MuSiQue can proceed if existing seed data is valid. | `docs/engineer/results/E-047_multidataset_local_transfer_20260427.md` with dataset availability check, slice paths, matched local Phi-4 runs, metrics, and precise blockers if a dataset cannot run. |
| READY | `E-048` | P1 | Error analysis and case-study evidence pack for demand-readiness: taxonomy, wins/losses, shared failures, and main-vs-appendix recommendations. | Best after `E-045` / `E-046`, but can start from `E-042` n=200 outputs immediately. | `docs/engineer/results/E-048_error_case_study_pack_20260427.md` with traceable example IDs, predictions, gold answers, evidence snippets, failure labels, and case-study candidates. |
| READY | `E-049` | P1 | Implement the EDO-Frame consumption-layer follow-up (`E-043-step3.5`) and rerun causal ablations only after the current evidence queue allows it. | `E-046` negative verdict showed the transparent bridge is not causal; no user decision is needed, but this should not preempt `E-045` / `E-047` / `E-048`. | Future result doc should show memory retrieval injected into planner/checker prompts, selected tools consumed by the action pathway, and a repeated six-row n=50/n=200 diagnostic with non-zero ablation thresholds before any component-causality paper claim. |
| WAITING | `E-043-step5..7` | P1 | Remaining build-out (2Wiki seed slice, MARBLE dry-run packet, no-paid Phi-4 six-row diagnostic). | `E-042` n=200 Wave-0 has now landed a paper-grade `edo_stage2_chain` candidate row, so step 7 is unblocked pending paired-bootstrap CI from scientist; step 5 still needs `data/2wikimultihop` seed availability. | Stepwise implementation / validation artifacts following `docs/engineer/handoffs/E-043_to_scientist_edo_frame_integration_plan_20260427.md`. |

## B. E-044 SmolLM3-3B Remote Deployment Dispatch

Scientist dispatch:

- `docs/scientist/handoffs/S-223_to_engineer_smol_lm3_remote_deploy_20260427.md`

Required action:

1. Bring up `HuggingFaceTB/SmolLM3-3B` on `dengkw@10.103.16.12`.
2. Prefer a local vLLM / OpenAI-compatible endpoint separate from the Phi-4 endpoint.
3. Add a reproducible SmolLM3 config alongside `configs/phi4_mini_hotpotqa_smoke.yaml`.
4. Run matched HotpotQA n=50 for `single_agent` and `edo_stage2_chain`.
5. Write the result artifact with endpoint evidence, exact commands, run directories, metrics, and caveats.

Scientific question:

```text
Does the current EDO orchestration behave differently on a smaller local open-weight backbone than it did on Phi-4-mini?
```

Do not use paid API. Do not escalate to n=200 before a clean n=50 health gate.

## C. S-225 Best-Paper Evidence Closure Dispatch

Scientist dispatch:

- `docs/scientist/handoffs/S-225_to_engineer_best_paper_evidence_closure_20260427.md`

Tasks created from the demand-readiness gaps:

| ID | Priority | Purpose | Result |
|---|---|---|---|
| `E-045` | P0 | Confirm whether the positive Phi-4 n=200 result is stable across additional seed/slice views. | `docs/engineer/results/E-045_phi4_multiseed_robustness_20260427.md` |
| `E-046` | P0 | Test whether EDO-Frame v2 memory/tool components improve or explain the local positive result. | `docs/engineer/results/E-046_edo_frame_ablation_sixrow_20260427.md` |
| `E-047` | P1 | Add a non-HotpotQA local transfer gate, preferably MuSiQue first and 2Wiki if official data exists. | `docs/engineer/results/E-047_multidataset_local_transfer_20260427.md` |
| `E-048` | P1 | Produce error taxonomy and case-study evidence for main/appendix writing. | `docs/engineer/results/E-048_error_case_study_pack_20260427.md` |

Claim discipline:

- No paid API calls.
- No SOTA claim from local-only diagnostics.
- No paper-grade claim without same-backbone comparison, artifact paths, and paired statistics where applicable.
- Prefer decisive evidence over matrix symmetry.

## D. E-042 Current Runtime State

Scientist dispatch:

- `docs/scientist/handoffs/S-222_to_engineer_local_open_weight_wave_20260427.md`

Current local-model route:

- primary: `microsoft/Phi-4-mini-instruct` / Phi-4-mini local vLLM endpoint
- control if deployable: `HuggingFaceTB/SmolLM3-3B`
- no paid API calls are allowed for this wave

Latest carried-forward engineer state from the active TODO tail before this English rebuild:

- Remote host: `dengkw@10.103.16.12`
- Remote repo: `/media/data3/dengkw/idea04`
- Phi-4 endpoint probe: `http://localhost:8001/v1/models` returned `200`
- Config present: `configs/phi4_mini_hotpotqa_smoke.yaml`
- Seed slices mirrored: `artifacts/seed/hotpotqa_validation_{100,200,500}.jsonl` and `artifacts/seed/musique_validation_{200,500}.jsonl`
- User selected the conservative `n=50` health gate before optimization / escalation
- Health-gate launch script: `workspace/tmp/e042_phi4_pipeline.sh`
- Phi-4 `single_agent` n=50 completed: F1 `0.3554`, EM `0.28`, tokens/sample `1869`, wall time `21.1s`; this replicated `E-035` same-backbone numbers
- Phi-4 `edo_stage2_chain` was running at the time of the carried-forward engineer state
- SmolLM3-3B bring-up is now split into `E-044` by explicit user request

Required next engineer action:

1. Finish or resume the `edo_stage2_chain` n=50 health gate. ✅ DONE 2026-04-27 (negative method-side verdict captured in `docs/engineer/results/E-042_local_open_weight_wave0_20260427.md`).
2. Write the `E-042` result artifact with exact commands and run directories. ✅ DONE 2026-04-27.
3. Report whether local `edo_stage2_chain` beats local `single_agent` on the same backbone. ✅ DONE 2026-04-27 — at n=50, `edo_stage2_chain` lost by `Delta_F1=-0.0124` and `Delta_EM=-0.0200`.
4. Only after a clean health gate, decide whether to escalate to `n=200`. ✅ ESCALATED 2026-04-27 — engineer launched the paper-grade `n=200` Wave-0 autonomously (per `research-engineering-principles.mdc` §5 routine-decision authority); single_agent landed `F1=0.3646 / EM=0.2650 / 1762.38 tokens/sample / 75 s wall-clock`, edo_stage2_chain still decoding under the same backbone. Run dir: `artifacts/emergence/e042_phi4_wave0_n200_20260427_110027/`.

Update 2026-04-27 ~13:10 +08: while the `n=200` Wave-0 is in flight, the engineer also unblocked `E-043-step1`, `E-043-step2`, and `E-043-step3` because they are local, no-paid, and additive (they cannot affect the running baseline). Steps 1+2 land in `codes/edo_frame/edo_frame/`, step 3 lands in `workspace/idea04_core/methods.py` plus a new `workspace/idea04_core/test_edo_frame_chain_method.py`. Tests: 14 in the EDO-Frame package (BM25 hybrid retrieval + drift detector + 4 v1 contracts) and 6 in the bridge module (registration + ablation surface + memory/tool-event emission + `no_memory` ablation + invalid-knob guard + 7+1 ablation surface). Stage-2 regression (`workspace/idea04_core/test_edo_stage2_chain_method.py`) still passes 7/7.

## E. E-043 Integration / Build-Out Plan

Handoff artifact:

- `docs/engineer/handoffs/E-043_to_scientist_edo_frame_integration_plan_20260427.md`

Current state:

- Planning and integration handoff is DONE as of 2026-04-27 12:50 +08.
- Execution sub-steps remain sequenced after `E-042` so they do not contaminate the same-backbone local baseline.

Sub-step queue:

| Status | ID | Priority | Summary |
|---|---|---|---|
| DONE | `E-043-step1` | P0 | BM25 hybrid retrieval in `NoteBoardMemory`. Adds Okapi BM25 over the candidate sub-corpus, recency-decay tie-breaker, accepted-bonus, and a `RetrievalConfig` ablation surface. Exposed via `from edo_frame import RetrievalConfig`. Tests: `codes/edo_frame/tests/test_note_board_memory.py` 6/6. |
| DONE | `E-043-step2` | P0 | Drift detector plus `ToolSelector.maybe_reselect`. Adds `TaskSignature` (frozenset over task tags + agent tags + entities), `signature_drift` Jaccard distance, `ToolSelector.drift_threshold` (default 0.4), and a `maybe_reselect` API that emits a fresh `ToolSelectionEvent` when drift crosses threshold. Tests: `codes/edo_frame/tests/test_tool_selector.py` 6/6 (including 4 new). |
| DONE | `E-043-step3` | P0 | `edo_frame_chain` method bridge in `methods.py` plus eight ablation flags (`edo_full`, `no_memory`, `all_tools`, `static_tools`, `random_tools`, `no_tool_history`, `no_private_board`, `public_board_only`). Bridge wraps `_run_edo_stage2_chain_step`, attaches a per-task `NoteBoardMemory` and `ToolSelector`, writes a memory event + a tool-selection event per hop, and enriches the trace with `edo_frame_*` fields. Stage-3 state lives on new `MethodState` fields (`note_board_memory_v3`, `tool_selector_v3`, `last_tool_selection_v3`, `edo_frame_buffer_v3`). Tests: `workspace/idea04_core/test_edo_frame_chain_method.py` 6/6; Stage-2 regression `workspace/idea04_core/test_edo_stage2_chain_method.py` 7/7 (no regressions). |
| DONE | `E-043-step4` | P1 | `scripts/check_e030_packet.py` packet self-check. Validates required configs, HotpotQA-200 seed integrity, internal METHOD_NAMES surface, `newapi` provider config, and `codes/edo_frame` + `codes/evidence_tools` test-suite green. Sentinels `__E030_PACKET_OK__` / `__E030_PACKET_FAIL__`. Exit-code-driven; verified on positive and negative paths. |
| WAITING | `E-043-step5` | P1 | 2Wiki seed n=100/200, dependent on official `data/2wikimultihop` seed availability. |
| WAITING | `E-043-step6` | P1 | MARBLE research-easy-33 dry-run packet. |
| DONE | `E-043-step7` | P0-after | No-paid Phi-4 six-row diagnostic. Completed as the data source for `E-046`: six rows landed at n=50 and showed the current bridge is trace-visible but not causally consumed. |

R-PART-003 adopted as references / constraints:

- CrewAI as negative-contrast baseline.
- LangGraph as checkpoint reference only.
- LlamaIndex / Haystack chunker abstractions as design references.
- Letta memory-ops-as-actions confirmation.
- RAGAS retrieval metrics as a future hook.
- MCP boundary reaffirmed.

R-PART-003 deferred / rejected for the first paper experiment:

- LangGraph or AutoGen as runner backbone.
- MemoryOS, Cognee, Zep, or Graphiti as runtime dependencies.
- OpenCompass migration.
- AgentBench / GTA as primary benchmarks.
- mem0 / Letta as direct dependencies.

## F. Recently Completed / Superseded Items

| Status | ID | Priority | Summary | Artifact |
|---|---|---|---|---|
| DONE | `E-041` | P0 | Prepared no-paid HotpotQA-200 Wave-1 launch packet for the paid canonical route. No paid API call was made. | `docs/engineer/results/E-041_e030_wave1_launch_packet_20260426.md` |
| DONE | `tracking-U-025` | P0 | Integrated user approval of the hybrid claim-first API gate. | `docs/scientist/analysis/S-222_user_decision_sync_local_first_20260427.md` |
| DONE | `E-040` | P1 | Evidence tools and 2Wiki seed/taxonomy support. | `docs/engineer/results/E-040_evidence_tools_result_20260426.md` |
| DONE | `E-039` | P1 | EDO-Frame minimal prototype. | `docs/engineer/results/E-039_edo_frame_prototype_result_20260426.md` |
| DONE | `E-035` | P2 | Remote Phi-4 n=50 diagnostic: `single_agent` F1 `0.3554`, EM `0.2800`; `edo_stage2_chain` F1 `0.3430`, EM `0.2600`; delta F1 `-0.0124`. Diagnostic only. | `docs/engineer/results/E-035_phi4_n50_diagnostic_20260424.md` |
| DONE | `E-034` | P0 | Repaired Phi-4 local-vLLM smoke route and created/mirrored seed slices. | `docs/engineer/results/E-034_E-030_phi4_smoke_and_seed_slices_20260424.md` |
| DONE | `E-031` | P1 | AgentNet probe completed; no-go for EMNLP main matrix due license / adaptation concerns. | `artifacts/external_baselines/agentnet/agentnet_probe_20260426_185500.md` |
| DONE | `E-032` | P1 | MultiAgentBench probe completed; go only as post-QA benchmark expansion. | `artifacts/benchmarks/multiagentbench/mab_probe_20260426_185500.md` |

For older engineering history, use the archive file listed above and `docs/engineer/`.

## G. Experiment Matrix Discipline

The engineer should continue to follow the claim-first rule:

- Prioritize rows that directly support paper claims R1/R2/R3 or the local small-model emergence boundary.
- Do not fill symmetric matrix cells merely for completeness when they are not claim-critical.
- Keep paid API work parked unless user approval and scientist gate both exist.
- Preserve exact commands, seeds, dataset slices, run directories, and generated artifact paths in result reports.

## H. Standing Engineering Rules

1. No paid API calls for `E-042` / `E-043` / `E-044` / `E-045` / `E-046` / `E-047` / `E-048` unless the user explicitly reopens that route.
2. For long runs, support checkpoint / resume and record exact run dirs.
3. Put engineer-owned runnable code under `codes/`.
4. Keep docs / TODO updates in English.
5. For every result, write a compact state row here and detailed evidence under `docs/engineer/results/`, `docs/engineer/logs/`, or `docs/engineer/handoffs/`.

## I. Revision Log

| Date | Author | Change | Notes |
|---|---|---|---|
| 2026-04-27 | scientist | Blocker audit after `S-233`: marked `E-046` / `E-043-step7` done from existing result artifacts and added `E-049` consumption-layer follow-up. | `E-049` records the next meaningful causal-ablation engineering step after the negative transparent-bridge verdict; it should not preempt current evidence-closure tasks. |
| 2026-04-27 | scientist | Added `E-045` / `E-046` / `E-047` / `E-048` evidence-closure tasks after user instructed Scientist to fill demand gaps and decide engineer work. | Dispatch: `docs/scientist/handoffs/S-225_to_engineer_best_paper_evidence_closure_20260427.md`. |
| 2026-04-27 | scientist | Added `E-044` SmolLM3-3B remote deployment and health-gate task after explicit user request. | Dispatch: `docs/scientist/handoffs/S-223_to_engineer_smol_lm3_remote_deploy_20260427.md`. |
| 2026-04-27 13:10 +08 | engineer | Per user 2026-04-27 SOTA-autonomy directive: codified the SOTA goal + routine-decision authority into `.cursor/rules/research-engineering-principles.mdc` §3 and §5; launched `n=200` Wave-0 in the background (run dir `artifacts/emergence/e042_phi4_wave0_n200_20260427_110027/`); landed `E-043-step1`/`step2`/`step3` (BM25 hybrid retrieval + drift detector + `edo_frame_chain` bridge with 8 ablation flags); 14 EDO-Frame unit tests + 6 bridge tests + 7 Stage-2 regression tests all pass. | No paid API call was made; engineer holds the right under §5 to execute these routine no-paid moves without escalation. |
| 2026-04-27 14:05 +08 | engineer | `E-042` n=200 Wave-0 finished both methods. **Headline finding**: `edo_stage2_chain` F1=0.4440 / EM=0.3150 vs `single_agent` F1=0.3646 / EM=0.2650 → **Delta_F1 = +0.0794 (+21.8 % rel.)**, **Delta_EM = +0.0500 (+18.9 % rel.)**, 2.33x token cost, first_accept_rate=0 on the chain. This **flips** the n=50 health-gate negative (-0.0124 F1pp). Recorded in `docs/engineer/results/E-042_local_open_weight_wave0_20260427.md` §10. Also landed `E-043-step4` (`scripts/check_e030_packet.py`, stdlib-only, exit-code-driven, positive + negative paths verified). |  Engineer claim discipline applied: no paper sentence written yet. |
| 2026-04-27 14:25 +08 | engineer | Engineer-side paired-bootstrap CI (10 000 resamples, single seed n=200) on the n=200 Wave-0 row. **ΔF1 = +0.0793, 95 % CI [+0.0152, +0.1439]**, sign-test p = 0.0186. **CI excludes zero → F1 gain is statistically significant at α = 0.05 on a single seed**. ΔEM = +0.0500, CI [-0.0150, +0.1200], sign-p = 0.1934 (positive mean, CI crosses zero, not significant). 47 wins for edo, 26 wins for single, 127 ties. Computed via `workspace/tmp/e042_paired_bootstrap.py`; output saved to `artifacts/emergence/e042_phi4_wave0_n200_20260427_110027/paired_bootstrap_ci.json` and recorded in result doc §10.4b. | This closes the engineer-side significance gate on F1; multi-seed (e.g., seeds 43, 44) is still recommended before paper-grade adoption but is no longer a blocker for treating the row as a candidate. EM remains descriptive only. |
| 2026-04-27 | scientist | Rebuilt this file in English-only UTF-8 after user approval and merged the valuable later English-only engineer tail state into the active summary. | Full original source preserved in `docs/archive/todo_mojibake_backup_20260427/ENGINEER_TODO.md`; do not restore mojibake tail content. |
| 2026-04-27 13:40 +08 | engineer | Engineer-window takeover after mandatory reads (`PROJECT_STRUCTURE.md`, `.cursor/rules/collaboration-workflow.mdc` §0.0.3 + §0.1, `.cursor/rules/research-engineering-principles.mdc` §3 + §5, `ENGINEER_TODO.md`, `USER_TODO.md §A`, `SCIENTIST_TODO.md §A/§B`, S-222 / S-223 / S-225 handoffs, recent `E-042` result tail). Pending → done sweep: no satisfied ⏳/`tracking-` rows discovered to flip — `E-042` already DONE with n=200 + paired-bootstrap CI, `E-043-step1..4` already DONE, `E-041`/`E-040`/`E-039`/`E-035`/`E-034`/`E-031`/`E-032` already DONE; `E-030` correctly PARKED on `U-EXEC-008`. Highest-priority unblocked work: `E-045` (P0 multi-seed robustness on Phi-4 to confirm n=200 ΔF1=+0.0794 stability — direct gate to paper-grade adoption of the local-emergence row), `E-046` (P0 EDO-Frame six-row ablation), `E-044` (P0 SmolLM3-3B bring-up). Next action will be `E-045` first because it directly upgrades the already-positive single-slice signal toward best-paper acceptance; `E-046` and `E-044` queued behind it. Replaces prior active engineer window per §0.1 singleton rule. | No paid API will be called. |

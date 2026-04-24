# ENGINEER_TODO - engineering task state index

> Purpose: current engineering task state, blockers, priorities, acceptance criteria, and result links.
>
> Detailed logs/results should go to `docs/engineer/logs/` and `docs/engineer/results/`.
> Historical engineering context still exists in `docs/coordination/implementation_log.md`; migrate gradually instead of bulk-moving.

## Active Queue

| Status | ID | Priority | Blocked | Task | Acceptance | Result link | Notes |
|---|---|---|---|---|---|---|---|
| ⏳ | E-030 | P0 | `U-EXEC-008` for canonical `gpt-4.1-mini` LLM calls | Fill the final baseline × datasize matrix from legacy ticket E-030. | Each new matrix cell has run dir + `metrics.json` + log/note; deterministic `n=500` seed slices exist locally and remotely. | `docs/paper/final_experiment_matrix.md`; latest infra result: `docs/engineer/results/E-034_E-030_phi4_smoke_and_seed_slices_20260424.md` | Claim-first order per E-033. Today: `newapi` still depleted, so no canonical LLM cells launched. |
| ⏳ | E-033 | P0 | none | Apply claim-first matrix scheduling discipline before every E-030 run. | Every new `E-030_cell_*` entry names why that cell was chosen under claim-first ordering. | legacy spec: `docs/coordination/implementation_log.md` `[final_experiment_matrix_workstream_20260423]` | Ongoing policy; do not close until E-030 core matrix is complete. |
| ⏳ | E-035 | P2 | remote background job running | Check Phi-4 n=50 diagnostic follow-up after repaired n=5 smoke. | Remote `artifacts/emergence/phi4_mini_n50_*/{single_agent,edo_stage2_chain}/metrics.json` exist or failure is logged with tail + caveat. | Remote launcher log: `logs/r43_phi4_n50_pipeline_20260424_143025.log`; script: `workspace/tmp/r43_phi4_n50_pipeline.sh` | Background process observed: `run_e017_fullval_seed.py --method edo_stage2_chain --n 50` on local_vllm. Not paper-grade and not an E-030 matrix cell. |

## Done / Archive

Use this section for compact state closure. Keep long details in `docs/engineer/...`.

| Status | ID | Priority | Completed | Result link | Notes |
|---|---|---|---|---|---|
| ✅ | takeover-20260424-1426 | P0 | 2026-04-24 14:26 +08:00 | `docs/engineer/logs/E-034_phi4_smoke_repair_log_20260424.md` | Takeover after mandatory read + pending sweep. Replaced prior engineer window under singleton rule. |
| ✅ | E-201 | P1 | 2026-04-24 14:26 +08:00 | `docs/engineer/logs/E-034_phi4_smoke_repair_log_20260424.md`; `docs/engineer/results/E-034_E-030_phi4_smoke_and_seed_slices_20260424.md` | New engineering layout adopted for this substantial run; TODO now holds only state + links. |
| ✅ | E-034 | P0 | 2026-04-24 14:26 +08:00 | `docs/engineer/logs/E-034_phi4_smoke_repair_log_20260424.md`; `docs/engineer/results/E-034_E-030_phi4_smoke_and_seed_slices_20260424.md` | Repaired Phi-4 local-vLLM smoke route and produced checkpointed n=5 artifacts. Smoke result is diagnostic only, not paper-grade. |
| ✅ | E-030_seed_500_slices_20260424 | P0 | 2026-04-24 14:26 +08:00 | `docs/engineer/results/E-034_E-030_phi4_smoke_and_seed_slices_20260424.md` | Created and mirrored `artifacts/seed/hotpotqa_validation_500.jsonl`, `artifacts/seed/musique_validation_500.jsonl`, and restored `data/musique/validation.jsonl` locally + remotely. |

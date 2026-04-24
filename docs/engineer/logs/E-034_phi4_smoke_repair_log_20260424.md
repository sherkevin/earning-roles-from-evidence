# E-034 Phi-4 Smoke Repair Log (2026-04-24)

## Scope

Repair the server-only Phi-4-mini emergence smoke so it produces traceable
artifacts instead of empty directories. This is a P0 reproducibility fix for the
R41h/R42 emergence branch, not a paper-grade matrix cell.

## Starting State

- `newapi` probe on the server still failed:
  - remaining balance: `$0.003610`
  - required pre-charge: `$0.004000`
  - status: `insufficient_user_quota`
- Canonical `gpt-4.1-mini` matrix/fullval runs remain blocked on user recharge.
- vLLM endpoint on `http://localhost:8001/v1/models` was healthy and served
  `phi4-mini`.
- `nvidia-smi` showed the active vLLM process using physical GPU 4
  (`20986 MiB / 24576 MiB` at probe time). The pipeline's historical PID file
  still labels its logical launch GPU as `1`; the actual observed physical GPU
  should be treated as the reliable resource record for this run.

## Root Causes Found

1. Remote `scripts/run_e017_fullval_seed.py` rejected `single_agent`; its
   `--method` choices only allowed `edo_stage2_chain` and
   `fixed_peer_calibrated`.
2. The emergence pipeline used an old fullval raw-input path that was not
   present on the server.
3. `run_e017_fullval_seed.py` cleared explicit `LLM_BACKEND=local_vllm`, which
   would have made a local GPU smoke silently fall back toward canonical
   provider routing.
4. After preserving `local_vllm`, the runtime integrity guard correctly blocked
   a config/runtime mismatch: config requested `gpt-4.1-mini` while runtime
   resolved `phi4-mini`.

## Fixes

- `scripts/run_e017_fullval_seed.py`
  - includes `single_agent` in `ALLOWED_METHODS`;
  - preserves explicit `LLM_BACKEND=local_vllm` routing instead of clearing it.
- `workspace/tmp/r42_emergence_pipeline.sh`
  - uses `artifacts/seed/hotpotqa_validation_100.jsonl` as the source sample file;
  - passes `--samples-jsonl` explicitly;
  - runs the two smoke methods sequentially with `--workers 1`;
  - exports `OUT_ROOT` so the delta summary reads the exact current run.
- `configs/phi4_mini_hotpotqa_smoke.yaml`
  - added as a dedicated smoke config with `main_model: phi4-mini`, preserving
    the runtime integrity contract.

## Verification Commands

Local:

```powershell
python -m py_compile scripts/run_e017_fullval_seed.py
python scripts/run_e017_fullval_seed.py --help
python -m py_compile scripts/create_jsonl_head_slice.py
```

Remote:

```bash
python3 -m py_compile scripts/run_e017_fullval_seed.py
grep -n 'main_model: phi4-mini' configs/phi4_mini_hotpotqa_smoke.yaml
bash workspace/tmp/r42_emergence_pipeline.sh
```

SSH/SCP note: commands used `ssh -i school` / `scp -i school`; the client warned
`Identity file school not accessible`, but SSH still authenticated via available
default credentials and every verification command emitted `__SSH_OK__`.

## Successful Run

- Remote log: `logs/r42_emergence_pipeline_20260424_141721.log`
- Remote output root:
  `artifacts/emergence/phi4_mini_n5_20260424_141721`
- Methods:
  - `single_agent`
  - `edo_stage2_chain`
- Samples: first 5 rows from `artifacts/seed/hotpotqa_validation_100.jsonl`
- Seed: `42`
- Backend: `local_vllm`
- Resolved model: `phi4-mini`
- Checkpoint/resume: each method directory has `_ckpt_preds.jsonl`.

## Caveats

- `n=5` is smoke only. It proves the pipeline, logging, checkpoint, and model
  route work; it does not close an E-030 matrix cell and must not be used as
  paper-grade evidence.
- `Delta_Phi4` on this smoke is negative, but at `n=5` that is only a diagnostic
  signal. Do not turn it into a scientific conclusion without a larger run.
- Canonical `gpt-4.1-mini` comparison remains blocked on `U-EXEC-008` recharge.

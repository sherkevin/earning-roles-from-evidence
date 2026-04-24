# E-034 / E-030 Result Summary (2026-04-24)

## 1. Phi-4 Emergence Smoke

Artifact root:

- Remote: `artifacts/emergence/phi4_mini_n5_20260424_141721`
- Log: `logs/r42_emergence_pipeline_20260424_141721.log`

| Method | n | F1 | EM | tokens/sample |
|---|---:|---:|---:|---:|
| `single_agent` | 5 | 0.4444 | 0.4000 | 1652.8 |
| `edo_stage2_chain` | 5 | 0.4000 | 0.4000 | 3895.6 |

Delta:

- `Delta_Phi4_F1 = -0.0444`
- `Delta_Phi4_EM = +0.0000`

Trust level:

- Useful as an engineering smoke: yes.
- Useful as paper-grade empirical evidence: no.
- Safe statement: the Phi-4 local-vLLM route now works end-to-end with
  checkpointed logs for both methods.
- Unsafe statement: EDO fails or succeeds on Phi-4-mini. `n=5` is too small.

## 2. E-030 Deterministic 500-Sample Slices

Created and mirrored locally + remotely:

| File | Rows | SHA256 |
|---|---:|---|
| `artifacts/seed/hotpotqa_validation_500.jsonl` | 500 | `6cd7e766290f71e799c0455b1797be975f2106984c850ebfa00185634f47fcaa` |
| `artifacts/seed/musique_validation_500.jsonl` | 500 | `f8a7590f4848a7cf7c8fd2b93a8eaa4764e8429d061817e15c9e8eebd8f6cf04` |
| `data/musique/validation.jsonl` | 4834 | `cfb362195dacf77316e2ce85393e1737ea344e5298ba42c88577d69f27fe96bd` |

Reproduction commands:

```bash
python scripts/create_jsonl_head_slice.py \
  --src artifacts/seed/hotpotqa_validation_full.jsonl \
  --out artifacts/seed/hotpotqa_validation_500.jsonl \
  --n 500

python scripts/download_musique.py
python scripts/prep_musique_seed.py \
  --n 500 \
  --out artifacts/seed/musique_validation_500.jsonl \
  --src data/musique/validation.jsonl
```

Verification:

- Local HotpotQA regeneration compared identical to the checked slice.
- Local MuSiQue regeneration compared identical to the checked slice.
- Remote SHA256 matched local SHA256 for both 500-sample slices and the MuSiQue
  source file.

## 3. Blockers

- `U-EXEC-008` is still blocking all canonical `gpt-4.1-mini` E-030 paper-grade
  matrix cells. Server probe result: remaining balance `$0.003610`, required
  pre-charge `$0.004000`, `insufficient_user_quota`.
- HotpotQA/MuSiQue `n=500` slices are ready, but no `gpt-4.1-mini` runs should
  be launched until the quota probe reports `newapi ACTIVE`.

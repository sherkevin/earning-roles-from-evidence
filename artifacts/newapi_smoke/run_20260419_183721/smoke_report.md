# E-008 newapi smoke report — 2026-04-19 18:37 (engineer Day 1)

> Phase block: `[E-008_newapi_smoke_20260420]` in `docs/coordination/implementation_log.md`.
> Triggered by user 04-20 instruction "审查目前 todo + 一步一步严谨科学的去做下去" + R6/R7 sprint kickoff E-008 P0 critical-path ticket.
> All sprint chain-200 / fullval batches must wait until this report exists per pinned cautions C-1 #3.

## Verdict

**PASS** — newapi (xh.v1api.cc) endpoint is fully functional and now natively wired into `workspace/idea04_core/llm_providers.py`. ModelDriftError pre-send guard fires on cross-family substitutions. Sprint Day 1.5 onward (E-002 split policy onward) may now safely consume newapi for any chain-200 / fullval batch.

## Probe results

### Probe 1: `GET https://xh.v1api.cc/v1/models`

- HTTP 200 in **188 ms**
- **132 models** returned (vs. 5 currently listed in `configs/llm.json newapi.models`)
- First 10 model ids: `chatgpt-4o-latest`, `claude-3-5-haiku-20241022`, `claude-3-7-sonnet-20250219`, `claude-3-7-sonnet-20250219-thinking`, `claude-4-sonnet`, `claude-4-sonnet-thinking`, `claude-haiku-4-5-20251001`, `claude-haiku-4-5-20251001-thinking`, `claude-haiku-4.5`, `claude-opus-4`
- Full response saved to [`models_list.json`](./models_list.json)

### Probe 2: `POST https://xh.v1api.cc/v1/chat/completions` (single sample, `gpt-4.1-mini`)

- HTTP 200 in **2 032 ms**
- `model` field returned by API: `gpt-4.1-mini` (matches request, no silent drift)
- Usage: `prompt_tokens=12, completion_tokens=2, total_tokens=14`
- Answer: `'OK'` (matches `Reply with exactly: OK` prompt)
- Full response saved to [`chat_smoke.json`](./chat_smoke.json)

### Probe 3: full `call_llm` round-trip via `configure_runtime()`

- `configure_runtime('gpt-4.1-mini', enforce_model=True)` succeeded
- `resolved_model()` returned `'gpt-4.1-mini'`
- `call_llm()` answered `'OK'`, `_sent_provider='newapi'` (auto-routed via new dispatch logic)
- Log: [`drift_negative_smoke.log`](./drift_negative_smoke.log) (positive section)

### Probe 4: ModelDriftError pre-send guard (negative smoke)

- Called `call_llm(model='gpt-99-fake-not-exists', ...)` with active runtime contract `gpt-4.1-mini`
- `ModelDriftError` raised **before** HTTP request was issued
- Error message excerpt: `[RUNTIME INTEGRITY] call_llm() would send model='gpt-99-fake-not-exists' but runtime contract requires 'gpt-4.1-mini'.`
- Log: [`drift_negative_smoke.log`](./drift_negative_smoke.log) (negative section)

## Code changes (`workspace/idea04_core/llm_providers.py`)

- New helper `_ensure_v1_suffix(base_url)` — auto-appends `/v1` if missing (newapi `base_url` in `configs/llm.json` is `https://xh.v1api.cc` without `/v1`)
- `normalize_llm_config()` extended to handle `newapi` block + `oversea_status` + `newapi_status` flat keys
- `_is_oversea_model()` extended to also match models in `newapi_model` catalogue
- New `_is_newapi_routable(model_name, cfg)` helper
- New `_newapi_is_primary(cfg)` helper — True iff `newapi._status` starts with `"PRIMARY"` AND `oversea._status` contains `"deprecated"`
- New `newapi_target(m)` function in `resolve_llm_chat_target` (template = `oversea_target`)
- Dispatch order updated:
  - Explicit `LLM_BACKEND=newapi` → `newapi_target`
  - Auto-detect: oversea-style model + `_newapi_is_primary(cfg)` → newapi (the new default for `gpt-4.1-mini` since R8/R9 commit)
  - Otherwise: oversea-style → oversea (back-compat with old `LLM_BACKEND=oversea` flow)
  - newapi-only models → newapi
  - else → zhipu

## Routing assertions (5/5 pass)

| # | Test | Expected provider | Actual |
|---|------|-------------------|--------|
| 1 | `gpt-4.1-mini` default (no env)              | `newapi` (auto via PRIMARY)            | newapi |
| 2 | `gpt-4.1-mini` + `LLM_BACKEND=oversea`      | `oversea` (back-compat)                | oversea |
| 3 | `gpt-4.1-mini` + `LLM_BACKEND=newapi`       | `newapi` (explicit)                    | newapi |
| 4 | `glm-4-flash` default                        | `zhipu`                                | zhipu |
| 5 | `meta/llama-3.1-8b-instruct` default         | `nvidia` (NIM slash routing)           | nvidia |

## Backward-compat verification (per pinned cautions C-2)

- `python scripts/validate_logs.py artifacts/round2_gpt41mini/run_20260414_115739/fixed_peer_calibrated` → `[OK]` (200 samples, 100%)
- `python scripts/validate_logs.py artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated` → `[OK]` (7 405 samples, 100%)

No byte-identity regression on R0 / fullval canonical artifacts.

## Files written this E-008

- `artifacts/newapi_smoke/run_20260419_183721/models_list.json`
- `artifacts/newapi_smoke/run_20260419_183721/chat_smoke.json`
- `artifacts/newapi_smoke/run_20260419_183721/drift_negative_smoke.log`
- `artifacts/newapi_smoke/run_20260419_183721/smoke_report.md` (this file)

## Files modified this E-008

- `workspace/idea04_core/llm_providers.py` — see "Code changes" above

## Pinned cautions acknowledged

- C-1 (provider 红线 — newapi 走 PRIMARY，oversea 仍可走 explicit env back-compat)
- C-7 #2 (key 不硬编码 — 全部从 `configs/llm.json` 读)
- C-7 #3 (jsonl 不 echo key — 仅 head8 prefix 写入 console，不 persist)
- C-2 (Stage-1 byte-id 回归 — R0 + fullval `validate_logs` 仍 [OK])

## Unblocks

- Engineer: E-002 (split policy LLM call), E-005 (Stage-2 fullval batch), E-007 (external baseline if not dropped per U-016), E-010..E-012 (external baseline reproduce/swap/compare; still pending U-014/U-015/U-016 for those)
- All future sprint LLM calls now have a tested PRIMARY route to gpt-4.1-mini via newapi without env shenanigans.

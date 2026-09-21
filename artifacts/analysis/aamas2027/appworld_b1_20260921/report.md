# AppWorld B1 feasibility — 2026-09-21

## Current decision

AppWorld remains the primary benchmark candidate. Qwen2.5-3B is rejected as the main B1 backbone after a clean no-experience run on dev task `6c2c621_1`.

The first 3B run was diagnostic-only because a 256-token per-turn cap visibly truncated Python code. The preregistered repeat changed only that cap to 1024. Infrastructure then ran cleanly: Qwen2.5-3B, 16K context, RTX 2080 Ti, vLLM 0.19.1, `TRITON_ATTN`, no evaluator-private truth in policy.

The clean repeat finished 20 steps without `complete_task` and scored 1/8 official evaluator tests. The trace repeatedly invented nonexistent note APIs and violated AppWorld file-system constraints. This is sufficient for the development gate to stop prompt-tuning Qwen2.5-3B.

## Next backbone

The initial stronger-backbone plan pinned `Qwen/Qwen3-14B@40c069824f4251a91eefaf281ebe4c544efd3e18` for self-hosted inference. **That runtime plan was superseded before any Qwen3-14B AppWorld run.** The user explicitly selected API inference to remove GPU/vLLM/attention/cache engineering from the scientific feasibility gate.

Current development backbone: `qwen3.8-max`, called from `U-CGPCVWR0-0024.local` through the user's existing local model router at `http://127.0.0.1:8317/v1`. A pre-migration smoke returned HTTP 200 and the requested `API_OK` output. The project stores no upstream API secret; the router resolves its credential from the user's existing environment.

Benchmark, split, task population, evaluator boundary and experience treatment remain unchanged. This is a runtime/backbone substitution only. The frozen API gate is `qwen38_api_smoke_manifest.json`; the superseded self-hosted manifest is retained for provenance.

## Boundary

These are development feasibility results, not confirmatory method evidence. No experience-versus-no-experience claim is tested until a non-floor backbone passes the sanity family.

## Donor audit update

The simple `6c2c621` family remains appropriate for backbone sanity, but not for the cleanest exposure experiment: the only train family containing `file_system.create_file` is `6104387`, which requires ~191–202 API calls and includes Spotify account deletion. It is therefore not used as the primary exposure donor.

For the main causal family `530b157`, train donors are substantially cleaner:
- `29caf6f`: 10 calls; phone contact/text retrieval plus text sending.
- `60d0b5b`: 8 calls; contact resolution plus Venmo transaction creation.
The dev target `530b157` requires 18 calls and composes phone context/text behavior with Venmo payment. This is the preferred family for task-exposure capability differentiation after the backbone sanity gate passes.

## Evaluator-only slot audit for 530b157

The dev target's official ten assertions admit a natural offline partition without exposing private truth to the policy:

- **Payment slot audit (S2):** exactly one Venmo transaction; correct receiver; correct public description; correct hidden grocery amount.
- **Acknowledgement slot audit (S3):** exactly one global text; correct receiver; correct public acknowledgement text.
- **Global/safety:** answer/completion semantics; allowed changed-model set; no deletion of existing user text records.

This partition is used only after execution for audit/scoring. Hidden receiver IDs, grocery amounts, and evaluator state are never supplied to an execution policy, experience artifact, router, or workflow binder.

## qwen3.8-max API backbone gate result

The frozen API backbone gate completed on `U-CGPCVWR0-0024.local` after the migrated environment passed AppWorld's official 147/147 task verification. The gate ran all three dev siblings in family `6c2c621` with no private experience and no evaluator-private truth available to the policy.

Results: `6c2c621_1`, `6c2c621_2`, and `6c2c621_3` each passed all **8/8** official evaluator assertions and each issued exactly one `apis.supervisor.complete_task` call. The preregistered gate required >=2/3 successes; observed result was **3/3**, so `qwen3.8-max` is accepted as the non-floor development backbone. Total runtime was 253.819 seconds. Raw trajectories remain under AppWorld's local `experiments/outputs/aamas_b1_qwen38_api_gate_20260921`; the project stores the compact result in `qwen38_api_gate_result.json`.

This is a backbone-feasibility result only. It does not test or support claims about private task exposure, specialization, earned roles, or evidence-conditioned workflow rebinding.

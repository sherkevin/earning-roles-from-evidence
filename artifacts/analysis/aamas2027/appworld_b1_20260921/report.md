# AppWorld B1 feasibility — 2026-09-21

**Checkpoint, 2026-09-22:** research/experiments are paused by the user. The latest completed result is the terminal four-model ceiling screen recorded below. No donor acquisition, exposure treatment or workflow-rebinding experiment followed. Earlier "next" directions in this chronological report are historical; the [canonical task ledger](../../../../docs/coordination/AAMAS_TASKS.md) governs any later resumption.

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

## `530b157` no-experience dynamic-range gate: ceiling

After the v3 exposure contract was frozen on Shervin and before any donor acquisition, the Mac execution machine ran `qwen3.8-max` with **no private experience** on all three `530b157` dev siblings. The complete record was synchronized back to Shervin before the scientific decision was recorded.

All three tasks achieved official success with **10/10 evaluator assertions**, and each issued exactly one `apis.supervisor.complete_task` call. Mean passed-test fraction was 1.0; total runtime was 385.970 seconds. The v3 contract predeclared 3/3 official success as a **ceiling**, so the qwen3.8-max donor-acquisition/treatment matrix is stopped without running C/CA/CB/CAB.

This does not falsify task-exposure specialization; it means this model/family pairing has no content-score headroom for the development contrast. Per contract, the next experiment must version the backbone/dynamic-range protocol rather than lower step budgets or tune prompts after observing the ceiling.

## v4 alternative backbone screen: MiniMax-M3 ceiling

The first v4 alternative candidate, `MiniMax-M3`, completed the same no-experience `530b157_1/_2/_3` screen. After the complete record was synchronized to Shervin, all three tasks were verified as official successes with **10/10** assertions and one completion call each. Mean passed-test fraction = 1.0; runtime = 118.283 seconds.

This is `CEILING_REJECT` under the frozen v4 rule. MiniMax-M3 is therefore not used for donor acquisition. The next candidate is the second predeclared router-catalog entry, `bailian/glm-5.2`.

## v4 alternative backbone screen: GLM ceiling

The second frozen candidate, `bailian/glm-5.2`, also completed all three no-experience `530b157` tasks successfully. After synchronization to Shervin, each task was verified at **10/10** official assertions with one completion call; mean passed-test fraction = 1.0 and runtime = 263.073 seconds.

This is `CEILING_REJECT`. The final predeclared candidate is `moonshot/kimi-k3`.

## v4 terminal: all configured alternative API backbones are ceiling on `530b157`

The final frozen candidate, `moonshot/kimi-k3`, also scored **3/3 official successes**, with **10/10** assertions and one completion call on every sibling; mean passed-test fraction = 1.0 and runtime = 253.020 seconds. It is therefore `CEILING_REJECT`.

The complete v4 fixed-order screen is now exhausted: `MiniMax-M3`, `bailian/glm-5.2`, and `moonshot/kimi-k3` all hit the same 3/3 content ceiling. qwen3.8-max had already hit that ceiling before the v4 screen. No donor acquisition or treatment matrix was run. The scientifically relevant conclusion is a **dynamic-range failure for this model/family pairing**, not a negative result about specialization. The next design must create legitimate headroom through a new predeclared development regime, not by post-hoc prompt or budget degradation.

## A-T03 checkpoint after v4 backbone screening

The canonical record is maintained on Shervin. The complete free-API backbone screen on the development family `530b157` has reached its terminal rule: qwen3.8-max, MiniMax-M3, bailian/glm-5.2, and moonshot/kimi-k3 all achieved ceiling performance before any donor acquisition.

Observed pattern:

- qwen3.8-max: 3/3 siblings, 10/10 evaluator assertions each.
- MiniMax-M3: 3/3 siblings, 10/10 evaluator assertions each.
- bailian/glm-5.2: 3/3 siblings, 10/10 evaluator assertions each.
- moonshot/kimi-k3: 3/3 siblings, 10/10 evaluator assertions each.

Decision boundary:

The exposure-effect experiment is not run under this regime because the dependent variable has no dynamic range. This should be interpreted as a development-regime limitation, not as a conclusion against experience-induced capability differentiation.

Next work must begin with a new frozen contract on Shervin before any execution-machine run.

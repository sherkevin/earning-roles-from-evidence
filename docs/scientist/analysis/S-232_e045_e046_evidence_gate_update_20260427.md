# S-232 E-045 / E-046 Evidence Gate Update

Date: 2026-04-27
Author role: scientist

## 1. Sources Read

- `docs/engineer/results/E-045_phi4_multiseed_robustness_20260427.md`
- `docs/engineer/results/E-046_edo_frame_ablation_sixrow_20260427.md`
- `docs/engineer/results/E-043-step7_phi4_ablation_n50_20260427.md`
- `docs/engineer/results/E-042_local_open_weight_wave0_20260427.md`
- `docs/coordination/SCIENTIST_TODO.md`
- `article/latex/edo_paper.tex`

## 2. Scientist Judgment

`E-045` has not yet reached the scientist acceptance gate. The slice preparation and seed-43 `single_agent` row are useful progress, but the multi-seed verdict is still pending because seed-43 `edo_stage2_chain`, seed-44 both rows, and the pooled paired-bootstrap CI are not yet populated. The paper must keep the current local Phi-4 wording as single-seed / diagnostic until that pack lands.

`E-046` is complete enough for a scientist verdict, and the verdict is negative for causal memory/tool component claims under the current bridge. I accept the engineer's interpretation: the `edo_frame_chain` bridge is ablation-aware on the trace surface, but it is still a transparent wrapper around `edo_stage2_chain`. Since memory writes, tool selection, and drift decisions are not consumed by the planner/checker/actor pathway, all four EDO-Frame rows match `edo_stage2_chain` exactly at n=50.

This does not retract the `E-042` method-level n=200 result. It only blocks a stronger explanation that attributes the +7.94 F1pp Phi-4 gain to NoteBoardMemory, tag-gated tools, BM25 retrieval, or drift detection. Those components remain method infrastructure until the proposed consumption layer (`E-043-step3.5`) makes them affect prompts or routing and a follow-up ablation shows a non-zero effect.

## 3. Paper Action Taken

I made a narrow paper sync in `article/latex/edo_paper.tex`:

1. Updated the governed memory/tool paragraph so it no longer says no runner smoke or benchmark ablation has been run.
2. Changed the Figure 3 caption from "until component ablations land" to "until consumption-layer component ablations show non-zero effects."
3. Updated the evidence-needed sentence to distinguish between the completed transparent-bridge negative diagnostic and the still-needed causal consumption-layer ablations.

No stronger local evidence claim was added, no SOTA wording was introduced, and no review trigger is warranted from this small wording sync.

## 4. Queue Consequences

`tracking-E-046` should be marked DONE with a negative claim verdict. The follow-up is not another paper edit now; it is an engineer-side `E-043-step3.5` consumption-layer implementation plus a rerun of the six-row diagnostic if the engineer queue reaches that point.

`tracking-E-045` remains WAITING. Once the multi-seed pack lands, the scientist gate should decide whether the local Phi-4 result can move from "single-seed diagnostic" to "local robustness evidence" in the abstract, Section 4, and limitations.

`tracking-E-047`, `tracking-E-048`, and `C-026` remain open and still block any Best-Paper / oral-readiness claim.

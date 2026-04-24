# Small-Model Emergence Response

**Date**: 2026-04-23  
**Owner**: scientist  
**Source ticket**: `SCIENTIST_TODO.md` `S-179`  
**Upstream context**: `docs/paper/small_model_emergence_plan.md`, `ENGINEER_TODO.md` `[r41h_emergence_pivot_proposal_20260421_0945]`, `[r42b_r41h_pivot_execution_20260421]`, `idea.md §14`, `experiment.md §1`

---

## 1. Executive verdict

My recommendation is **Option C, but staged**:

1. **Continue the local small-model emergence line now** using the already-approved server-only path (`Phi-4-mini` primary, `SmolLM3-3B` control).
2. **Do not discard the existing `gpt-4.1-mini` line**. It should remain the strong-model control / calibration axis.
3. **Do not rewrite the paper around emergence yet** until the local smoke clears the first evidence gate:
   - `Δ_small = F1(Stage-2) - F1(single_agent) > 0` on the same small backbone;
   - answer formatting / extraction is stable enough that the gain is not a parsing artifact;
   - ideally `Δ_small > Δ_large`, where `Δ_large` is the same quantity under `gpt-4.1-mini`.

This is better than the alternatives:

- **A only** is too risky before we see a positive small-model signal.
- **B only** keeps the current cost pressure and leaves the most title-aligned hypothesis unused.
- **D** is useful as a fallback variant, not as the first-choice paper strategy.

So the unresolved user decision is **paper-level positioning**, not whether the engineer may keep the local infrastructure moving. The engineer already has a legitimate green light for the server-only `Phi-4-mini` execution path from the earlier user instruction recorded in `ENGINEER_TODO.md`.

---

## 2. Scientist recommendation on backbone choice

### 2.1 Primary model

Use **`microsoft/Phi-4-mini-instruct` (3.8B)** as the primary small-model backbone.

Reason:

- the user already explicitly steered the engineer away from the older `Qwen2.5-7B` path and toward `Phi-4-mini`;
- it is small enough that a positive `Stage-2 > single_agent` gap would be much more persuasive as an "organization recovers capability" result;
- it is cheap to host and easy to scale on the current server;
- it creates a cleaner contrast to the existing `gpt-4.1-mini` strong-model line.

### 2.2 Control model

Use **`HuggingFaceTB/SmolLM3-3B`** as the control.

Reason:

- it is smaller than Phi-4-mini, so it tests whether the emergence effect strengthens as the backbone gets weaker;
- it is fully open and easier to defend on reproducibility grounds;
- it is already part of the engineer's deployed path.

### 2.3 Why not Qwen as the first local target

`Qwen3.5-9B` is still scientifically interesting, but **not** the best first local backbone for the emergence claim:

- it is too close to the "strong model" regime, so a positive result is easier to read as "better base model + more compute" instead of "organization recovered missing capability";
- it weakens the small-model headline;
- the user has already pushed the implementation toward `Phi-4-mini`.

My recommendation is therefore:

- **primary**: `Phi-4-mini`
- **control**: `SmolLM3-3B`
- **defer Qwen** unless Phi-4/Smol gives ambiguous or unstable results

---

## 3. What can and cannot be claimed as "emergence"

This boundary must stay aligned with `idea.md §14`.

### 3.1 Allowed claim if the experiment succeeds

If the local experiment shows `Δ_small > 0`, we may claim:

> Organizing multiple weak agents through delegation + verification recovers capability that the same weak backbone does not exhibit in a single-agent setting.

This is a **capability-boundary / organization-level emergence** claim.

### 3.2 Claims that are still NOT justified

Even if the local result is positive, we should **not** yet claim:

- spontaneous role emergence;
- self-organized specialization without priors;
- fully decentralized emergent persona formation;
- proof that the current delivered system has already realized the full EDO mechanism.

Reason:

- the delivered prototype still uses a **fixed role-prior topology**;
- `idea.md §14.2` explicitly says fixed role prompts and fixed task-to-role scaffolds are not themselves emergence.

So the correct wording is closer to:

- **"organizational emergence at the model-capability boundary"**
- **"capability recovery through delegation + verification"**

and not:

- "fully emergent specialization"
- "self-organized roles"

until the R1/R2/R3 real-implementation agenda lands.

---

## 4. Single-agent baseline design

The correct null baseline is the **existing `single_agent` implementation**, not a newly hand-crafted prompt.

Grounding in code:

- `methods.py` already registers `single_agent` in `METHOD_NAMES`;
- its policy is "always accept";
- it reuses the standard `_llm_generate_answer()` path instead of a separate bespoke pipeline.

### 4.1 Fairness rule

For the emergence experiment, the single-agent baseline should remain:

- **same backbone**;
- **same raw question payload**;
- **same evidence exposure path that the current code gives the root actor**;
- **same temperature / decoding defaults**;
- **no concatenated decomposer+synthesizer mega-prompt**;
- **no extra retrieval, reflection, or multi-turn scaffold** that the Stage-2 side does not get "for free".

In other words, keep `single_agent` as the **clean structural null**:

> same model, same task, one direct answer call, no organization.

This preserves the interpretation:

> any measured gain comes from organization structure, not from a stronger hand-authored prompt.

### 4.2 Prompt-design conclusion

Scientist recommendation:

- **do not invent a new one-off single-agent super-prompt**
- keep the current implementation as the canonical baseline
- if needed, only document it in the appendix as "the root-agent direct-answer path"

---

## 5. Metric and cost reframing

For local open-weight runs, the existing `cost-normalized F1` story cannot be reused unchanged, because the **API-dollar term is zero**.

So the local emergence axis should use **dual accounting**:

1. **Quality delta**: `Δ(B) = F1_multi(B) - F1_single(B)`
2. **Token proxy**: `tokens/sample`
3. **Infra proxy**: `GPU-hours` or wall-clock
4. **Economic note**: `API-$ / sample = 0` for the local axis

Scientist writing recommendation:

- for the local axis, headline the result as **"quality gain at zero API cost"**
- do **not** overclaim token efficiency if Stage-2 uses more local tokens than `single_agent`

That means:

- `gpt-4.1-mini` axis still supports the current Pareto / cost-normalized story
- `Phi-4-mini` / `SmolLM3` axis supports an **emergence / capability-recovery** story

This is exactly why **Option C** is stronger than A or B alone.

---

## 6. Interaction with `experiment.md §1`

Current rule:

- `experiment.md §1.1-§1.2` keeps **`gpt-4.1-mini`** as the canonical main-table backbone;
- heterogeneous or non-canonical backbones are currently appendix / stress / future-work only.

### 6.1 Scientist judgment

Do **not** edit `experiment.md` yet.

Reason:

- we still do not know whether the local emergence effect is positive;
- changing the canonical backbone policy before the smoke result would be premature.

### 6.2 What to do if the user picks Option C or A

If the user confirms `U-024-decide` as `C` or `A`, then the right change is **not** to delete the canonical rule, but to add a **narrow exception**:

> `gpt-4.1-mini` remains the canonical strong-model axis; user-approved local open-weight backbones may appear as a second, explicitly-labeled emergence axis in §4.x / appendix when the paper's primary research question shifts from "Pareto on one strong backbone" to "organization-induced capability recovery across backbone regimes".`

This keeps the old line interpretable and avoids tearing up the experiment spec too early.

---

## 7. Decision to dispatch to the user

I recommend creating a new canonical user decision:

## `U-024-decide`

**Question**: what is the paper-level position of the local small-model emergence line?

- **A**: full pivot to emergence framing
- **B**: keep current Pareto framing only; local small-model work stays appendix / stress
- **C**: dual-axis paper: local emergence as the new differentiating axis, `gpt-4.1-mini` retained as strong-model control (**recommended**)
- **D**: small-model line stays pre-research only, not part of the current paper

### 7.1 My recommendation

Recommend **C**.

### 7.2 Why C is best

- it uses the already-started `Phi-4-mini` / `SmolLM3` work instead of wasting it;
- it avoids betting the whole paper on a result that has not yet passed smoke;
- it preserves the strongest existing control axis (`gpt-4.1-mini`);
- it gives the paper a better best-paper trajectory:
  - **organization helps weak models** becomes the interesting new claim;
  - **organization does not meaningfully help strong models** becomes the control;
  - the contrast is cleaner than the current marginal Pareto-only story.

### 7.3 Operational interpretation

Until `U-024-decide` is answered:

- engineer may continue the already-approved local infra / smoke path;
- scientist should **not** yet rewrite the full paper around emergence;
- the current unresolved item is the **paper positioning**, not the server setup.

---

## 8. Immediate next steps

1. Let the current `Phi-4-mini` smoke finish (`n=5`).
2. If sane, scale to `n=50`.
3. Run the matched `gpt-4.1-mini × single_agent` smoke once quota is available.
4. Then judge:
   - if `Δ_Phi4 <= 0`, downgrade local line to appendix/falsification;
   - if `Δ_Phi4 > 0` but noisy, keep as secondary;
   - if `Δ_Phi4 > 0` and clearly exceeds the strong-model delta, promote the emergence axis in the paper.

---

## 9. Bottom line

This pivot is scientifically worth pursuing, but only under a **disciplined claim boundary**:

- **run it now**
- **do not overclaim**
- **keep `gpt-4.1-mini` as control**
- **use `Phi-4-mini` primary + `SmolLM3-3B` control**
- **record the unresolved paper-positioning question as a user decision**

That is the clean scientist stance for `S-179`.

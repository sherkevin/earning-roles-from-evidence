# AnyJev shared-stack integration note

> **Historical baseline note (2026-09-24).** This file records the companion
> project's pinned AnyJev/Qwen integration and smoke evidence. It is a scheduled
> refit and shared-protocol baseline, not the selected backbone or the final
> real-time training method. The current decision boundary is in
> [`ADR 0012`](../../../docs/user/decisions/0012-do-not-lock-laya-or-rls.md).

Date: 2026-09-24

The companion tool-selection audit selected [AnyJev](https://github.com/nokia-applied-research/AnyJev) at commit `a59a69eaa91e62dc9b42924f8491f76d1b1972ea` (Apache-2.0). This repository adopts the same framework and `Qwen/Qwen3-4B` base model for peer selection so that improvements are comparable across the two projects.

The companion audit verified 16 selected-only binary observations with the AnyJev fake backend: the first L2 head fit at observation 8, refit at observation 16, and predictions were unchanged after export/load. Upstream fake-backend tests reported `24/24 passed`. The raw artifacts are copied under `raw/` for provenance; no model weights are included here.

## Shared candidate protocol

Each candidate is scored by the same binary question, while its task-specific state is canonical JSON:

```json
{
  "candidate_kind": "peer|tool",
  "candidate_id": "provider/name/version/config",
  "task_snapshot": {},
  "candidate_capability": {},
  "candidate_input": {},
  "state_schema_version": "candidate-state-v1"
}
```

The wrapper calls `Question.noul` for each candidate and returns `p_correct`, uncertainty, the sampled propensity, and a state version. A tool result label is `correct=1/0`; a peer result label is the frozen first-round delivery rubric (`accepted/useful=1`, failed/rejected=0). All labels are selected-only and may arrive after a delay.

The pre-action state must not include the selected tool's output or the recipient's post-execution artifact outcome. Those go into a separate immutable feedback event:

```json
{
  "event_id": "...",
  "episode_id": "...",
  "task_type": "tool|peer",
  "actor_id": "...",
  "candidate_uid": "provider/name/version/config",
  "context_hash": "...",
  "selected": true,
  "label": 0,
  "reward_observed_at": "...",
  "feedback_delay_ms": 0,
  "policy_version": "...",
  "propensity": 0.5
}
```

If a benchmark produces every tool output before choosing among them, that is output reranking and must be reported separately from cost-saving pre-execution tool selection.

## Shared update boundary

AnyJev's `observe` stores labels and refits the full history at thresholded counts. We retain that behavior as the scheduled-refit baseline. The proposed dynamic selector owns the event-level part:

```text
base_score = AnyJev(question, candidate_state)
adjusted_score = base_score + private_residual(agent_or_selector, candidate_id, context)
choice = sample_or_argmax(adjusted_score + exploration_bonus)
label arrival -> update private residual + append immutable event
periodic checkpoint -> AnyJev fit_head/recalibration + locked validation
```

The implementation must use a bounded replay buffer, exponential forgetting or an equivalent drift policy, delayed-feedback bookkeeping, and atomic snapshot/restore. It must report prequential reward, regret, calibration, update cost, and recovery after restart.

The shared selector uses a local HF/vLLM AnyJev backend with hidden states. The
`内部` idealab messages endpoint can still be used to generate candidate
content or an external label, but it cannot provide the hidden-state/logit
interface required by AnyJev L2.

## Current limitation

AnyJev's current `Question.choice` implementation has a letter-readout limit of 26 options. We avoid this in the shared path by scoring candidates independently with `noul`; the peer graph still supplies only local neighbors, and the tool selector can shortlist a large registry before scoring. We will not claim arbitrary-menu support until a real backend test establishes it.

The full source audit and raw smoke result live in the companion project at `/Users/jingwu/work/benchmark/task/task47-jev-source-evaluation/report.md`; the pinned manifest and smoke JSON are preserved locally in this directory.

# Peer-judged role formation: reuse-first assembly plan

**Date:** 2026-09-24  
**Status:** implementation design; scientific method and benchmark remain open until the gates below pass

The machine-readable counterpart is [`configs/aamas2027/reuse_assembly_v1.json`](../../../configs/aamas2027/reuse_assembly_v1.json); it is a conditional engineering lock, not a positive experiment manifest.

This document turns the selected story into a buildable plan. It does not claim
that the missing role update has already been implemented or that any positive
effect has been measured.

## 1. Story and method boundary

An agent's role is earned from the way an actual collaborator judges and uses a
specific delivered contribution. A producer creates an attributable artifact in
the context of a real dependency. The consumer can accept it, use it, repair it,
or reject it. A later lawful outcome can correct a mistaken local judgment. The
resulting public role evidence changes what responsibility the producer receives
later. Agents and workflows co-evolve: the agent is not a fixed plug-in being
qualified for a frozen workflow.

The paper must show the full chain:

```text
dependent task → producer artifact → situated recipient judgment
→ actual use/repair/rejection → source-aware role evidence
→ later responsibility → team utility and cost
```

The central intervention is the judgment-to-role update. Generic reputation,
self-description, a detached LLM score, a binary terminal-success EMA, a router,
or a workflow library is not the contribution by itself. A role label without a
changed later assignment is not a role-learning result.

## 2. Functions we must implement

The following are the smallest functional boundaries. Only F5–F9 are new
scientific glue; the remaining functions should be inherited from a benchmark or
runtime wherever possible.

| ID | Required function | Evidence required before use |
|---|---|---|
| F1 | Benchmark/task-root adapter with pinned commit, split, native tests and task identity | task manifest, source hash, held-out roots |
| F2 | Agent runtime, tools, workspace and conversation loop | import/API smoke and one scripted tool trace |
| F3 | Versioned task/workflow state and resumable episode | checkpoint and replay fixture |
| F4 | Attributable producer artifact with source/provenance | producer id, parent task, files/messages, commit or artifact hash |
| F5 | Recipient pre-action judgment seal | consumer id, context, judgment, uncertainty, time and visible information |
| F6 | Post-action use/repair/accept/reject attribution | exact artifact used, edits/rework, tests and downstream action |
| F7 | Lawful terminal correction | outcome source, observability boundary and correction timing |
| F8 | Public source-aware role evidence separate from local belief | evidence record links producer, judge, context and artifact; no identity-only EMA |
| F9 | Future assignment scheduler | later task opportunity and assignment change are logged before outcome |
| F10 | Same-information controls | fixed/no-role, pooled, raw acceptance, contextual trust/bandit and terminal-only arms |
| F11 | Native/independent scorer and conflict/merge policy | scorer provenance, oracle or test audit, failure fixture |
| F12 | Raw JSONL event/cost log and deterministic replay | per-call trace, API usage, errors, seed, manifest and replay hash |

F5–F9 must be one executable loop. Separate scripts that produce a score or a
role table after the episode do not satisfy the mechanism requirement.

Current progress: the OpenHands runtime smoke and REUSE-2 protocol fixture pass
the zero-LLM integration gate. REUSE-1's native CooperBench audit passes task
integrity, patch application, gold tests and expected conflict checks, but the
official Docker scorer remains unavailable and the handoff adapter is not yet
tested. The fixture proves ordering and provenance logging only; F7–F11 and all
benchmark/scientific gates remain open.

## 3. Reuse map and adaptation budget

The source audit is deliberately conservative. The detailed benchmark manifest is
in [references/aamas/reuse_design_20260924/benchmarks/README.md](../../references/aamas/reuse_design_20260924/benchmarks/README.md),
and the runtime smoke is in
[openhands_smoke/README.md](../../references/aamas/reuse_design_20260924/runtime/openhands_smoke/README.md).
A row is an engineering source,
not a scientific endorsement; every adapter must preserve the source's license
and record deviations.

| Need | Reuse candidate and pinned source | License/status | Thin adapter we write | What the source does **not** establish |
|---|---|---|---|---|
| Real dependent coding tasks | CooperBench, audited source/task commits in `references/aamas/cooperbench_20260923/` | top-level repository license is currently absent; task-level licenses and official scorer need separate audit | task-root loader, independent event schema, consumer review/use/rework wrapper, held-out split manifest | no recipient acceptance/use field, no role update, no later assignment; official Docker scorer not yet validated |
| Agent/workspace/tool loop | OpenHands Software Agent SDK, commit `e21d77673b738f056676044600c4ad81c5a575c8`, SDK 1.49.5 | MIT; CPython 3.12 zero-LLM smoke captured 5 persisted events and reached `FINISHED`; Pre/Post hooks returned structured `allow` | peer message channel, provenance seal, role store, checkpoint/clone hooks, budget accounting | no peer-judged roles or causal assignment protocol |
| Multi-agent coding workflow ideas | MARBLE, pinned config/source under `references/aamas/reuse_design_20260924/benchmarks/marble/` | MIT | only borrow task/config vocabulary or use as a fixed-workflow comparator | roles/graph are preset; not evidence of earned roles or consumer correction |
| Natural multi-agent environment fallback | AgentWorld, pinned files under `references/aamas/reuse_design_20260924/benchmarks/agentworld/` | MPL-2.0 | use only if server/scorer can be frozen and a real handoff event is exposed | game coordination and task completion do not automatically provide attributable producer artifacts or transferable role evidence |
| Close conceptual comparison | Meta-Team, source audit in `references/aamas/metateam_reuse_20260923/` | no detected repository license; do not copy code | reimplement only a paper-level L2 profile/reassignment control if needed | its adaptation/profile mechanism is not our situated consumer judgment and cannot serve as our implementation |
| Stateful API task infrastructure | AppWorld, pinned source/data in current requirements | existing benchmark license/scorer audit; single-agent default | diagnostic adapter only unless a natural dependent boundary is demonstrated | prior runs showed no complete judgment→role→future-duty chain |

The engineering rule is “one source, one adapter, one acceptance test.” Do not
mix several frameworks until a single-source vertical slice passes F1–F6.

## 4. Benchmark decision

**Primary engineering/scientific candidate: CooperBench at commit
`63b9d44d9f39a02fccf5bf0052db48a917a011fd`.** It gives us real
repositories, separated feature work, merge conflicts, and native tests. That
supports a natural producer→consumer setting: one agent proposes a feature patch,
another receives the patch in its task context, decides whether and how to use it,
repairs or rejects it, and a later dependent task creates the future assignment
opportunity. The benchmark is therefore a better starting point than a generic
chat or game benchmark.

This is a **conditional** lock. Before any paper experiment, we must pass:

1. A complete two-agent vertical slice on a held-out task root, with the consumer
   seeing a bounded producer artifact and with use/rework recorded separately from
   final tests.
2. A legal redistribution decision. Until the CooperBench top-level license is
   clarified, keep its source/data as an audited external dependency and write an
   independent adapter; do not copy its harness/scorer.
3. An official scorer run or an independently audited native-test scorer, with
   conflict/oracle behavior documented.
4. A task-level split and dependence analysis so multiple feature pairs are not
   counted as independent organizations.
5. Feasible same-information controls and a total-cost budget.

The first development item is the existing Click task 2800 smoke, not a result:
the two feature patches had a direct conflict, each reference patch passed its
own native tests, and the combined reference patch passed both test sets. The
smoke demonstrates dependency structure only. It does not establish a consumer
judgment or the role-learning claim.

**Fallbacks:** MARBLE and AgentWorld are legally clearer engineering sources,
but neither currently exposes the complete producer artifact → situated consumer
use/rework → later responsibility chain. AppWorld remains a diagnostic fallback
because its natural unit is a single agent stateful task. A fallback can become
primary only after it passes the same five gates; convenience alone is not a
reason to weaken the story.

## 5. Baseline matrix

All arms use the same task roots, initial agent/tool/model state, legal
observations, opportunity stream, storage and API budget. The arms may diverge
after their policies act, but a control must not inherit the proposed arm's
realized memories or workflow.

| ID | Baseline | Purpose | Required matching information |
|---|---|---|---|
| B0 | pooled single agent / centralized selector | upper bound for coordination without peer roles | all artifacts and task state; same budget |
| B1 | fixed/no-role self-organization | ordinary collaboration without learned roles | same messages/artifacts; no role update |
| B2 | raw recipient acceptance | tests whether a simple acceptance rate explains the effect | same recipient judgment events |
| B3 | contextual trust or bandit | strongest same-information allocation control | producer, judge, task context, outcome and uncertainty |
| B4 | terminal-only feedback | tests whether later global success alone is sufficient | same terminal outcomes, no situated consumer signal |
| B5 | closest peer-feedback method (e.g. paper-level Meta-Team/L2 control) | protects against claiming generic adaptation as novelty | same history and budget, only where implementation is faithful |
| P | proposed source-aware judgment→role update | candidate mechanism | recipient judgment + attributed use/rework + lawful correction |

If B3 performs as well as P under matched information and cost, the contribution
must be narrowed or rejected. If B2 matches P, the extra use/rework machinery is
not justified. If P changes labels but not future assignments or utility, it is
not a role-learning result.

## 6. Minimal build order

1. Freeze a CooperBench task-root manifest and license/scorer note.
2. Run the OpenHands zero-LLM scripted tool/event/checkpoint smoke.
3. Build F1–F4 only and replay the existing Click dependency without an LLM.
4. Add F5–F6 and make a consumer's use/rework visible in the raw log.
5. Add F7–F9 and run a synthetic deterministic fixture that proves a judgment can
   change a later assignment before any paid API call.
6. Implement B0–B4 with identical event schemas and budgets; add B5 only after a
   faithful source audit.
7. Run one small real-API development slice using the user's configured Idealab
   “内部” route. Log configuration, every request/response, costs, failures,
   source hashes, seeds and raw per-sample outcomes before interpreting anything.
8. Freeze the independent confirmation manifest only if the vertical slice,
   scorer, control and cost gates pass.

The first implementation milestone is therefore not “train a better agent.” It
is a reproducible, legally usable vertical slice that can replay one real
producer→consumer→role→future-duty chain and expose every cost and decision.

## 7. Stop conditions

Stop and revise the benchmark/method if the recipient cannot make a judgment
before acting, if use/rework cannot be attributed to one artifact, if the later
assignment is selected by the same hidden evaluator, if the scorer cannot be
audited, or if a same-information baseline explains the gain. A positive task
score without this chain is an engineering success, not evidence for the paper.

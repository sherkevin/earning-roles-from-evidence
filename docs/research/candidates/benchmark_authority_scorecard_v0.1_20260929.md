# Benchmark authority and experiment-cell scorecard v0.1

- **状态**：`CANDIDATE_NOT_ACTIVE`
- **日期**：2026-09-29
- **用途**：把 benchmark 选型与实验矩阵变成可审计候选，不替换 active benchmark plan，也不默认激活 primary/secondary 关系。
- **科学权限**：本文件不授权新的 API、GPU 或 A800 结果；所有 cells 仍为 design-only。

## 1. 候选轨道判定

| track | upstream anchor | this project adds | claim it can carry | current status |
|---|---|---|---|---|
| `PeerSelect` | `graph-ipd@00ef417f60053569175b2b50d0f0e25ff8eb7007`, MIT, arXiv:2608.28977 | selected-only peer selector, delayed updater and drift/latency instrumentation | local peer selection and online-update mechanism | `MECHANISM_CANDIDATE` |
| `ArtifactRole` | TeamBench `@d185aef1916fd86a9ba554d581fd256319a973af`, MIT | producer→recipient delivery, responsibility scorer, later assignment and full cost | situated judgment→attributable evidence→future assignment | `TASK_CANDIDATE` |

`PeerSelect` cannot carry the artifact judgment claim. `ArtifactRole` is the only
candidate that can carry the paper's full causal chain, but it is not yet an
authoritative frozen benchmark: the wrapper, root split, scorer, independent
streams and later assignment remain open. The active primary/secondary relation
was subsequently confirmed as `ArtifactRole` primary and `PeerSelect` secondary in
ADR 0042; this candidate scorecard does not change that active decision.

## 2. Authority and adaptation scorecard

| candidate | claim fit | authority/reproducibility | root diversity | label independence | contamination/replay | decision |
|---|---|---|---|---|---|---|
| graph-ipd / PeerSelect | `PASS` for mechanism only | `PARTIAL_PASS` (paper, pinned commit, MIT; local smoke patched one upstream argument path) | `OPEN` for independent streams | `PASS` for selected payoff in native protocol | `OPEN` for our adapter | use as secondary/mechanism candidate |
| TeamBench-derived DIST1 | `PARTIAL` (delivery/consumer protocol) | `PARTIAL` (pinned upstream; derived task material) | `OPEN`; seed variants are not independent roots | `OPEN`; historical task-text leakage was found | `OPEN`; strict scorer/runner gate pending | development diagnostic only |
| TeamBench-derived PIPE3 | `CANDIDATE` for full chain | `PARTIAL` (pinned upstream; derived adapter) | `OPEN`; needs independent root/stream evidence | `PARTIAL`; Qp/Qr/adoption and attribution seam exist, producer-defect and later assignment do not | `OPEN`; live runner and confirmation replay pending | confirmation candidate, not frozen |
| Meta-Team L2-style profile adapter | `CANDIDATE` as closest semantic adapter; `NO-GO` as direct drop-in | pinned paper; code commit pinned but no detected LICENSE/COPYING, so semantic reimplementation only | published tasks have multiple domains; our adapter still needs independent streams | native profile reflection is not structured recipient adoption/producer attribution | original method sees terminal/trajectory information; public adapter must trim it and expose a fixed schema | `NOT_IMPLEMENTED / QUALIFICATION_REQUIRED` |
| DecisionBench | `FAIL` for full role chain; `PARTIAL` as selector/delegation control | pinned paper/code/data revisions | useful task diversity, wrong causal unit | profiles/judges are offline, no native recipient adoption label | clean source available, wrong target | selector/delegation control only |
| CooperBench | `FAIL` for full role chain; `PARTIAL` as collaboration substrate | pinned paper/repository revision; license provenance recorded | multiple repositories, but role/feature assignment is prebound | no native recipient verdict/later duty update; solo fallback | scorer/merge paths need explicit separation | engineering substrate only |

The scorecard treats a benchmark as authoritative only when the upstream source
and our claim boundary are both explicit. A wrapper does not inherit authority
for fields that the upstream benchmark never measured.

## 3. Baseline readiness

| arm | purpose | current executable evidence | remaining gate |
|---|---|---|---|
| `uniform`, `no_update`, `terminal_only`, `contextual_trust` | lower bound, static prior, terminal signal, strongest same-info control | common policy factory and zero-call tests | versioned runner and root parity |
| `raw_acceptance`, `pooled_controller` | raw-signal and shared-history controls | projection/replay seams and zero-call tests | real runner, public ownership parity, cost accounting |
| `RARE` | responsibility-gated candidate | repaired CPU state, gate-identification diagnostics, and v5 shared selection/event-time adapter qualification | independent producer label, closest parity, complete live runner |
| Meta-Team-L2-public / original-info / ablation | external semantic control and information upper bound | public profile schema boundary passed zero-call; no executable generator/adapter yet | source-input binding, faithful public builder/replay, fixed parser/summary budget, information/cost map |

No row is baseline-frozen until its runner, information, cost, state and
selected-only/UNKNOWN semantics are executable on the same root and schedule.

## 4. Candidate cell manifest contract

The machine-readable design is
[`n03_candidate_cell_manifest_v0.2.json`](../../../configs/aamas2027/n03_candidate_cell_manifest_v0.2.json).
Each cell freezes track/root/split, policy arm, responsibility case, arrival
schedule, independent stream unit, primary endpoint, cost fields, and the stop
rule. It deliberately contains no result values and sets API/GPU permission to
false. A future active manifest must be created only after the primary/secondary
track decision and baseline parity review.

## 5. Reusable upstream assets

- TeamBench generator/spec and pinned commit for task material and native grading boundaries.
- PIPE3 responsibility matrix, sidecar, ledger replay and OpenHands hash-chain fixtures for protocol qualification.
- graph-ipd persistent graph/neighbor/payoff protocol and CPU smoke setup for mechanism diagnostics.
- Meta-Team paper semantics and its published task traces for a possible profile/routing comparator; the original information view is an upper-bound diagnostic, while the public adapter must be independently reimplemented.
- DecisionBench delegation/cost traces and CooperBench merge/test traces for selector/delegation and engineering adapters; neither is a faithful full benchmark for the core claim.

## 6. Stop conditions

Do not activate a cell if a task leak, non-independent root, hidden-result read,
recipient/producer attribution failure, missing later assignment, unfair
baseline information, or incomplete cost/UNKNOWN denominator is found. Such a
cell remains `BLOCKED` with its raw failure evidence.

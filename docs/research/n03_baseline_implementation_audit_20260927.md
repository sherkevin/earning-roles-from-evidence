# N03 baseline implementation audit

日期：2026-09-27
状态：`PARTIAL / NOT FROZEN`
目标依据：[`docs/coordination/GOAL.md`](../coordination/GOAL.md) v1.0
候选 manifest：[`configs/aamas2027/n03_benchmark_baseline_candidate_v2.json`](../../configs/aamas2027/n03_benchmark_baseline_candidate_v2.json)

这份审计回答一个具体问题：候选 baseline 是否已经有能在同一事件流上运行的实现，还是只存在于设计文档和名字列表中。审计不改变 Goal、不把历史 synthetic 结果升级为 PeerRoleBench 结果，也不启动新的 API 或 GPU 实验。

## 1. 检查范围和证据

检查了以下固定代码和记录：

- `references/aamas/streamjev_20260924/online_head.py`：`OnlineRLSHead` 的 selected-only 更新、propensity、去重和 snapshot；
- `references/aamas/streamjev_20260924/experiments/selected_only_rls.py`：`static`、`online_rls`、`label_shuffle`、`no_feedback` 的 synthetic runner；
- `references/aamas/streamjev_20260924/experiments/{linear_associative_smoke,stationary_estimator_isolation,bounded_residual_fast_weight_isolation}_20260925.py`：历史 associative/diagonal/RFW challenger；
- `references/aamas/streamjev_20260924/protocol.py` 与 `replay_adapter.py`：共享事件和 terminal feedback 的协议组件；
- `scripts/peerrolebench_real_closed_loop.py` 与 [`scripts/peerrolebench_pipe3_runner_adapter.py`](../../scripts/peerrolebench_pipe3_runner_adapter.py)：当前真实 runner 与 PIPE3 root-specific seam；
- N03 candidate manifest、baseline freeze candidate、Stream-JEV method specification 和既有 experiment logs。

固定回归命令：

```text
python3 -m pytest -q references/aamas/streamjev_20260924
```

结果为 `15 passed`。该结果只说明参考 runtime 的协议和 RLS 实现可执行，不说明任何 peer-role baseline 已完成资格化。

## 2. 逐项实现状态

| manifest 名称 | 当前可见实现 | 状态 | 不能直接用于正式比较的原因 |
|---|---|---|---|
| `uniform` | `selected_only_rls.py` 中的零 head 均匀采样 | `PARTIAL` | 只在 synthetic runner 内联；没有接入 DIST1/PIPE3 的统一 policy 接口、成本账本和真实 delivery |
| `no_update` | `static`/`no_feedback` 的均匀行为可作为近似 | `PARTIAL` | 这不是带任务上下文的冻结 selector；`static` 与 `no_feedback` 实际上没有区分，不能把别名当作最终 no-update baseline |
| `raw_acceptance` | 未发现 peer-role controller 实现 | `OPEN` | 没有定义 acceptance 的合法来源、责任归因、延迟和 selected-only 更新边界 |
| `terminal_only` | `replay_adapter.py` 能构造 terminal feedback；测试覆盖延迟 | `PARTIAL` | 只有反馈协议，没有在同一候选菜单、propensity、历史和预算下运行的 terminal-only policy |
| `contextual_trust` | 未发现实现 | `OPEN` | 这是 RARE 的强同信息替代解释，必须消费完全相同的公开 judgment/action/延迟事件，不能用独立的私有标签替代 |
| `pooled_controller` | 未发现实现 | `OPEN` | 共享 controller 的历史范围、跨 agent 公开边界和成本口径尚未落地 |
| `RARE` | 只有方法合同和事件语义文档，没有已接入 controller | `OPEN` | responsibility-aware 过滤、`(producer, context, version)` 绑定、UNKNOWN no-update 和未来 assignment 尚未由同一个 runner 执行 |
| `rls` | `OnlineRLSHead`、单测和 synthetic selected-only logs | `PARTIAL` | 可以作为更新器 comparator；尚未在合格 PeerRoleBench root 上运行，不能称为 role-learning 结果 |
| `online_logistic` | 未发现实现 | `OPEN` | 需要与 RLS 使用相同表示、事件、propensity、延迟和 checkpoint 预算 |
| `periodic_refit` | 未发现独立实现 | `OPEN` | 既有 AnyJev/Stream-JEV 说明是设计或历史参考，尚无同信息 refit runner 和成本/时延日志 |

历史 `associative`、`diag_ls` 和 `rfw_tr` 是参考目录里的 challenger 实验实现，不自动等同于 manifest 中的 `contextual_trust`、`pooled_controller` 或 RARE。它们使用 synthetic hidden-regime world，最多支持算法 runtime 诊断，不能填补 peer judgment→role evidence→future assignment 的缺口。

## 3. 信息公平性检查

当前最容易造成误判的是把以下三件事混在一起：

1. **有一个能更新的头**：`OnlineRLSHead.update()` 已经满足逐条 selected-only 标签更新、去重和快照恢复的工程接口；
2. **有一个能比较的 policy**：需要所有条件共享候选集合、propensity 流、合法历史、反馈延迟、请求预算和完整成本；当前真实 runner 仍是 DIST1 专用，PIPE3 只有静态 adapter seam；
3. **有一个能支持故事的信号**：必须能区分 producer contract、recipient 自身处理、adoption 和 terminal outcome，并把责任明确绑定到未来 assignment；当前 PIPE3 lineage preflight 已通过离线控制矩阵，但 runner/scorer 过程隔离和真实候选链仍未资格化。

因此，参考目录里的 synthetic `online_rls` 优于 `static` 的数值不能回答“situated peer judgment 是否改善未来责任分配”。同样，`label_shuffle` 只能是 selected-only 关联的负对照，不能代替同信息 contextual trust。

## 4. 与 Goal 的对照

| Goal 硬标准 | 本次结论 | 状态 |
|---|---|---|
| 故事线保持 situated judgment→role evidence→future responsibility | 没有改变；RARE 仍是候选机制 | `MAINTAINED` |
| benchmark 权威且能观测完整链 | TeamBench-derived 双 root 仍是候选；PIPE3/runner 未冻结 | `OPEN` |
| baseline 能充分排除替代解释 | baseline 名单已写出，但只有 RLS 和部分 synthetic controls 有代码 | `PARTIAL` |
| 实时更新、稳定性和准确率有证据 | 只有参考 runtime/历史 synthetic 证据，没有真实 role efficacy | `OPEN` |
| 不因失败自动降低 Goal 或创新标准 | 本次没有提出降级 | `UNCHANGED` |

## 5. 下一步的最小闭环

在启动新的真实 API 前，需要把 baseline 从名字变成可审查对象：

1. 为统一 event stream 定义一个 `BaselinePolicy` 接口，明确 `observe_decision`、`observe_feedback`、`choose`、`snapshot` 和合法信息边界；
2. 先实现不依赖新模型的 `uniform`、真正冻结的 `no_update`、`terminal_only` 和同信息 `contextual_trust`；
3. 再接入 RLS comparator 与 RARE candidate，逐条检查它们是否读到了相同事件；
4. `raw_acceptance`、`pooled_controller`、`online_logistic`、`periodic_refit` 在实现和审计前保持 `OPEN`，不能仅为填满表格而用别名；
5. 每个 policy 先通过离线 ledger replay 和 information-parity matrix，再允许进入 PIPE3 的有限真实链。

这个顺序不要求先确定最终 backbone，也不会把 RLS 误写成创新。只有当 baseline 可以在相同 root、相同信息和相同成本下运行，N04 的“RARE 是否超过强替代解释”问题才有可证伪性。

`goal_change_requested=false`。

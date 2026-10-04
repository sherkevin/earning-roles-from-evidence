# 三份标准在 canonical adapter 之后的收敛审计

日期：2026-10-04
状态：`PARTIAL / NOT_READY`
审计对象：storyline v1.1、method v1.1、benchmark/baseline v1.1 及其三份 active evaluation
`goal_change_requested=false`

## 目的

本任务在 canonical PIPE3 public-input parity v21、raw-acceptance adapter v4 和
terminal-only adapter v5 完成后，重新核对三份唯一生效验收文档。审查只判断证据
是否打开对应科学门，不把离线 fixture 的可达性、一次 policy update 或 schema
一致性写成角色学习、自进化、实时训练或 benchmark 效果。

## 新增证据

- `experiments/logs/n03_canonical_pipe3_parity_20261004_v21/`：七臂公共输入、
  read-cut、arrival、UNKNOWN、late rejection、offer mutation、namespace 和 replay
  资格通过；0 API、0 GPU。
- `experiments/logs/n03_canonical_raw_adapter_20261004_v4/`：native
  `DecisionSidecar → RawAcceptanceSidecar → project_raw_acceptance` 后进入同一
  七臂 stream；raw arm 一次 eligible/update，六臂 ignore；七类错误在 runner
  启动前 fail-closed；0 API、0 GPU。
- `experiments/logs/n03_canonical_terminal_adapter_20261004_v5/`：独立
  `TerminalOutcomeSidecar → project_terminal_outcome` 使用 `terminal-success-v1`；
  terminal arm 一次 eligible/update，六臂 ignore；八类错误在 runner 启动前
  fail-closed；0 API、0 GPU。

上述回执均明确 `scientific_claim_allowed=false`、`benchmark_qualified=false`，
并保留早期失败版本。它们是工程资格，不是科学结果。

## 三份验收文档的当前判定

| 文档 | 当前状态 | 本次关闭的内容 | 仍未满足的硬门 |
|---|---|---|---|
| 故事线与创新点 | `NOT_READY` | 责任边界、证据来源和失败时序更可执行 | situated judgment 是否比 raw/terminal 提供增量信息；是否改变 future assignment；未见 root 的质量、返工和完整成本 |
| 方法论 | `NOT_READY` | public projection、selected-only、UNKNOWN/no-op、跨进程 replay、history mutation 防护 | 最终 updater/backbone、真实 selected-only 延迟、p50/p95、drift、forgetting、状态/服务成本和四格科学消融 |
| Benchmark + baseline | `NOT_READY` | raw/terminal 两类 source adapter 的 canonical 接缝和 fail-closed 规则 | 权威冻结、结构独立第二 root、closest published adapter、同信息 live parity、独立 live history、later-use 与 confirmation split |

## Goal 门映射

- **G0：`PARTIAL`。** 问题、责任语义和反驳边界清楚，但还没有最小失败结果
  证明 situated judgment 的独立信息价值。
- **G1：`PARTIAL`。** 单 root 的协议工程底座更完整；benchmark authority、第二
  structural root、污染/精度与 clean replay manifest 仍未闭合。
- **G2：`PARTIAL`。** 方法合同和状态恢复边界通过；真实在线更新、实时服务、漂移
  响应、抗遗忘和成本仍无证据。
- **G3：`OPEN`。** 尚无冻结后的真实 API independent live-history scientific
  comparison。
- **G4：`OPEN`。** 尚无独立 confirmation root/stream。
- **G5：`OPEN`。** 论文可继续写设计、矩阵和限制，但不能填写方法收益或训练效果。

## 关键边界，防止任务漂移

1. 七臂 public-input digest 相同只证明 schema/协议 parity，不证明 baseline 公平或
   scientific parity。
2. raw/terminal 的“一次 update”只证明 source adapter reachability，不证明 delayed
   credit、peer suitability、assignment utility 或自进化。
3. history 四格中选择概率改变只证明 selector 消费了 deterministic fixture history，
   不证明长期角色形成、泛化或实时训练。
4. 离线 CPU 回放没有 latency、token、GPU、人工判断和返工成本，不能支撑 real-time
   或 cost claim。

## 下一道唯一门

冻结一份 **canonical seven-arm executable manifest**，把 situated judgment、raw
acceptance 和 independent terminal outcome 三个 source projection 放进同一个 stream，
逐项固定：候选菜单与版本、公开 `φ`、read-cut、arrival/propensity、state cap、
selected-only、完整 cost schema、registry/history mutation、UNKNOWN/no-update、
独立 policy namespace 和 positive/negative cell。通过条件是所有 arm 都能从同一
manifest 运行，错误映射在 runner 启动前拒绝，且每格都有可重放的成本/输入/选择回执。

这道门完成前不启动新的正式 API 流、不提交 A800、不把 Goal 降级。它通过后再做一条
有界真实 API independent live history；第二 root 与 confirmation 仍需单独资格化。

## 复核与结论

本次独立审查没有提出 Goal 变更，也没有产生新的科学结论。下一步应优先完成清单冻结
和 baseline parity，而不是继续增加低价值协议分支。三份 active 文档保持原版本和
`NOT_READY` 状态。

证据：

- [canonical parity replay v21](20261004_canonical_pipe3_parity_replay_v21.md)
- [canonical raw adapter](20261004_canonical_raw_adapter_qualification.md)
- [canonical terminal adapter](20261004_canonical_terminal_adapter_qualification.md)
- [source adapter/history replay](20261004_source_adapter_mutation_replay.md)
- [independent audit message](../../coordination/TASK_REPORTS.md)

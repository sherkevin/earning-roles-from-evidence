# Policy matrix runner qualification — 2026-09-30

## 结论

七个当前 policy arm 已有一个可重复的 root-level **离线 parity contract**：同一候选
菜单、同一随机种子、同一显式 event-time schedule、同一 selected-only 反馈入口和
同一 snapshot/restore 检查可以在一个 runner 中执行。七个 hand-authored cases
（recipient judgment、producer-attributed defect、terminal outcome、late
correction、raw acceptance、explicit UNKNOWN、unselected feedback）在 v9 全部通过，七个 arm 的
replay snapshot 均一致；v9 还将冻结 candidate registry digest、protocol event
identity、source lineage 与 offer 中的 versioned candidate key 绑定，并对每个 case
检查预期的 source/update/UNKNOWN/selected-only 语义。runner 按 live PIPE3 合同在每次
choose 前消费当前 read cut 已到达的反馈；迟到反馈不会改写已封存的选择。

这关闭的是 baseline 实现和协议的离线子门，不是 benchmark freeze，也不是方法效果或
科学结果。运行配置明确记录 `real_api_calls=0`、`gpu_jobs=0`、
`scientific_claim_allowed=false`。

## 实现与边界

新增 `scripts/peerrolebench_policy_matrix_runner_v1.py`，统一调用现有 policy factory、
candidate registry、PIPE3 public offer 和 global arrival schedule。runner 在 policy
选择前检查：

- `read_cut <= decision_index` 且 offer 在 read cut 可用；
- 每条 public feedback 都出现在预注册 schedule，arrival index 与 schedule 一致；
- UNKNOWN 必须带显式 `unknown_reason`；
- source selection、candidate key 和 selected-only 反馈 lineage 对得上；
- 每个 arm 均记录 selected/eligible/unknown/ignored/unselected、更新计数和 reason；
- 结束后直接 snapshot/restore，并比较 canonical snapshot。

这仍是部分 root-level contract：它绑定每条实际提供的 feedback 与预注册 schedule，但
尚未要求每个后续 offer 显式重放此前全部可见信息，也不能证明隔离进程中的 policy 没有
读取 operator/private state；这两项留给正式 live runner。

七个 arm 使用显式 `exploration=0.10`，避免 RARE 的默认探索率与 comparator 默认值
不同；这只是本次离线 contract 的预注册参数，不能据此声称同信息或优越性。不同 arm
仍保留各自合法 source：raw acceptance、terminal outcome、contextual judgment、
pooled history 和 RARE responsibility-aware judgment。`raw_acceptance` 明确作为
recipient judgment protocol event 的公开投影，不把它伪装成独立 terminal event；这使
raw arm 的正向路径可检查，同时保留它不能读取 responsibility/private fields 的边界。

## 失败与修复记录

没有覆盖或删除早期失败：

| 版本 | 结果 | 原因 |
|---|---|---|
| v1 | `FAILED_OFFLINE` | registry 构造字段与当前实现不一致，配置前即失败；后补写失败回执 |
| v2 | `FAILED_OFFLINE` | `model_config_digest` 不满足 registry digest 合同 |
| v3 | `FAILED_OFFLINE` | late-correction fixture 的 read cut 早于 decision index |
| v4 | `FAILED_OFFLINE` | 共享 fixture 对某 arm 产生了未选择候选的 feedback，runner 错误地将其当 fatal |
| v5 | `QUALIFIED_OFFLINE` | 显式跳过未选择候选并记入 `n_unselected`；selected-only 事件才可更新 |
| v6 | `QUALIFIED_OFFLINE` | 在 v5 基础上绑定冻结 registry/digest，拒绝未注册 candidate key |
| v7 | `QUALIFIED_OFFLINE` | 加入 protocol/source lineage、决策序列校验、真实 UNKNOWN 与 unselected case，并将语义断言纳入通过条件 |
| v8 | `QUALIFIED_OFFLINE` | 将每个 case 的 schedule rows/digest 写入 pre-run config，避免 runner 与自生成 schedule 自洽通过 |
| v9 | `QUALIFIED_OFFLINE` | 修正为 observe-before-choose；加入 raw acceptance 正向 case、早/迟反馈断言、自反馈拒绝，并重新封存七 case |

v1 的 pre-config failure、v2–v4 的 `failure.json`，以及 v5–v8 的成功/诊断
`config.json` 与 raw/summary 保留在各自日志目录；v9 的原始逐 arm trace、
metrics、cost ledger 和 summary 保留在
[`experiments/logs/n03_policy_matrix_runner_20260930_v9/`](../../../experiments/logs/n03_policy_matrix_runner_20260930_v9/)。
`unknown_reason` 也被加入 public evidence schema，使 runner 的 UNKNOWN 分母能在
schema 层被保存。

## 审计结果

- 命令：`python3 scripts/peerrolebench_policy_matrix_runner_v1.py --out-dir experiments/logs/n03_policy_matrix_runner_20260930_v9`
- 定向测试：9 passed；相关 PeerRoleBench 回归：265 passed。
- 两条命令的 stdout/return code 记录在
  [`test_output.json`](../../../experiments/logs/n03_policy_matrix_runner_20260930_v9/test_output.json)。
- 没有调用 LLM、没有提交 Nebula/A800、没有修改历史 N02 结果。
- v9 中 `contextual_trust`/`pooled_controller` 在 recipient judgment case 更新，
  `terminal_only` 只在 terminal case 更新，RARE 能处理晚到 correction；这些是接口
  行为检查，不是质量差异的估计。
- v9 的 raw acceptance case 实际只更新 raw arm；unselected case 实际记录了每个 arm 的
  `n_unselected=1` 且没有更新，UNKNOWN case 实际记录显式 reason 且没有更新。一个共享 hand-authored fixture 仍不能支持 arm
  间效果比较：不同 arm 可能选择不同 candidate，因此正式 benchmark 必须为每个 arm
  使用同 root、同 schedule、独立 live history 的 paired cells。

## 对 Goal 与下一道门的影响

本任务没有降低 `docs/coordination/GOAL.md`，也没有把 active benchmark/baseline
标成冻结。它只把 parity audit 中的一项缺口从“没有统一离线入口”推进到“有可审计的
offline root runner contract”。仍未完成：真实 PIPE3 runner、独立 producer-quality
label、完整 producer/recipient/judge/scorer/repair/replay cost ledger、later assignment
消费、closest published adapter、同信息 contextual-vs-RARE parity，以及独立
confirmation root。科学 readiness 继续为 `false`，下一步仍不能直接启动效果 API 或
A800。

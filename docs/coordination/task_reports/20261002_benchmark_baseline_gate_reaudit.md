# Benchmark、baseline 与实验矩阵复审 — 2026-10-02

状态：`PARTIAL / NOT_READY`。本报告复审 `role-evidence-judgment-beta-v1` 接入预览接缝后的三项硬门：benchmark 选型、baseline 可比性、实验矩阵与结果解释。它不冻结 benchmark，不改变 active benchmark-baseline 版本，也不降低 Goal。

## 审查输入

- 验收标准：[`benchmark_baseline_v1.2_20260929_eval.md`](../../research/versions/evaluation/benchmark-baseline/benchmark_baseline_v1.2_20260929_eval.md)；
- 当前计划：[`benchmark_baseline_v1.1_20260930.md`](../../research/versions/benchmark-baseline/benchmark_baseline_v1.1_20260930.md)；
- 选择接缝：`scripts/peerrolebench_role_evidence_selection.py`；
- 无状态 comparator：`scripts/peerrolebench_role_evidence_scorer.py`；
- v2 回执：[`n03_role_evidence_assignment_scorer_20261002_v2`](../../../experiments/logs/n03_role_evidence_assignment_scorer_20261002_v2/)；
- 前置反馈通道门：[`20261002_pipe3_feedback_channel_gate.md`](20261002_pipe3_feedback_channel_gate.md)。

## 逐门判定

| 门 | 当前证据 | 判定 | 不能声称的内容 |
|---|---|---|---|
| Benchmark 适配与权威 | TeamBench commit、PIPE3/PIPE2 材料与责任审计已固定；第二 structural root 仍等待 authority 选择；`PeerRoleBench-TB` 仍是 derived candidate | `OPEN` | 不能写“benchmark 已通过”或宣称跨 root 泛化 |
| Baseline 名单覆盖 | uniform/no-update/raw/terminal/contextual/pooled/RARE 的七 arm 合同与离线 v16 matrix 存在；Meta-Team-L2-public 仍为 `NO-GO/qualification required` | `PARTIAL` | 不能把离线矩阵当成公平 live comparison 或 SOTA 结果 |
| 信息可比性 | comparator 只读取 read-cut 前 public judgment，排除 `quality_score/Qp`；相同 B/C menu、base、state、fresh RNG 下 judgment mutation 会改变 score/probability，quality mutation 不改变 score | `PARTIAL` | 不能声称 evidence 已在完整 runner 中因果改变 future choice |
| 反馈与更新一致性 | v1.3 已拒绝“只提交 terminal credit 就算 contextual update”；声明 feedback source 的 arm 必须产生对应 update | `OPEN` | 不能把 `credit_committed` 当作 policy learning |
| 实验矩阵 | root/arm/cost/UNKNOWN/arrival 的 offline manifest 已有；canonical live runner 尚未消费 comparator，independent histories、measured cost、later-use 仍缺 | `OPEN` | 不能启动正式效果流或 A800 |
| 结果合理性 | 当前只有零调用 contract tests：v2 定向 10 项、全量有效回归 376 项；LLM/API=0、GPU=0、scientific claim=false | `NOT_READY` | 不能填写 quality、cost、real-time、forgetting 或 acceptance 数字 |

## 这次接入真正关闭的范围

`preview_role_evidence_selection_with_public_judgment` 使公共 recipient judgment 有了一个明确、可审计、无状态的 assignment-side comparator。它先产生 `RoleEvidenceScore`，再复用既有 preview→`LaterAssignment`→exact selection commit；不调用持久 updater，不改变默认 hand-authored overlay，不放宽 B evidence→B assignment subject invariant。它把“判断内容被读取后能否影响候选分数”从未定义问题收紧为可测试的 mutation contract，但尚未成为 RARE 的最终更新方法。

## 仍然存在的科学缺口

1. 七个 arm 还没有全部绑定到同一条 canonical live episode；尤其 raw acceptance、terminal-only、contextual trust 与 assignment comparator 的 eligible/UNKNOWN、延迟、成本和 update 语义还不能在真实 history 中逐格对齐。
2. 第二 structural root 的 authority 尚未由作者确认。PIPE2 的 derived CSV repair 只是决策证据；valid-subset、MULTI3 adapter 和暂缓第二 root 都不能静默选定。
3. 当前 comparator 的正向 mutation 只在 hand-authored B/C evidence fixture 中证明；还没有真实 recipient judgment、独立 later-use/outcome 或未见 root 的 quality-cost 结果。没有这些证据，故事线的闭环仍停在工程接缝。
4. closest published adapter、完整成本、独立 live streams、统计精度和 drift/forgetting 测量均未通过。

## 下一条最短可验证路径

在不启动 API/A800 的前提下，先把 comparator 作为 assignment-side opt-in 接到现有 source-bound canonical runner，要求每个 arm 明确 `accepted_sources` 与实际 updater 的一一对应，并为 B/C 两个候选保留 judgment、quality、menu、state、RNG 全部不变的双向 mutation receipts。只有该 runner 通过并且第二 root authority 有明确决定，才生成冻结的 live cell manifest；随后才允许一条有预算上限的真实 API 小流。任何失败保持 `UNKNOWN/NOT_READY`，不修改 Goal。

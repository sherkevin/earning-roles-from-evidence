# PIPE2 Scheme-B observation bridge compatibility audit

日期：2026-10-08。结果：`BLOCKED_BY_HANDOFF_SEMANTICS`；没有调用 API、GPU 或候选代码。

## 目的

ADR0049 已确认：recipient 的 accept/rework/reject 应保留为 noisy observation，不能
直接变成 producer credit。仓库已有 typed observation bridge，可以验证这个边界，但它
原本假定 recipient 收到 producer-owned source files。本轮检查 PIPE2 的真实 material
adapter 是否满足这个前提，避免把不兼容的桥接硬接到 runtime receipt 上。

配置与原始 JSONL：

- [config](../../../experiments/logs/n03_pipe2_observation_bridge_compatibility_20261008_v1/config.json)
- [events](../../../experiments/logs/n03_pipe2_observation_bridge_compatibility_20261008_v1/events.jsonl)
- [summary](../../../experiments/logs/n03_pipe2_observation_bridge_compatibility_20261008_v1/summary.json)
- [runner](../../../scripts/peerrolebench_pipe2_observation_bridge_compatibility.py)

## 事实

PIPE2 的 producer payload 包含 `pipeline/extract.py`，而 recipient payload 只包含
`pipeline/transform.py`、`pipeline/load.py` 及公开支持文件。recipient 的必需输入是
`artifact/extracted_rows.json`，schema 为 `pipe2-extracted-rows-v1`；它不是 producer
源代码的拷贝。现有 `FrozenObservationContract`/`build_judgment_observation` 要求
recipient pre/post snapshot 包含 producer-owned paths，并用 delivered source 文件做
逐路径比较，这与 PIPE2 的可见性合同不一致。

PIPE2 runtime qualification 的回执还只有 producer contract、recipient self 和
artifact adoption。它没有真实 recipient judgment、consumer action、terminal outcome，
也没有 recipient 的 pre/post source manifest。`output_sha256` 或 adoption status 不能
被重命名为 J、A 或 Y；这样会凭空制造 Scheme-B 训练信号。

## 结论与下一步

当前 observation bridge **不能**直接用于 PIPE2 runtime 回执；现有零调用 v1 fixture
使用 synthetic digest，不能作为资格证据，保留但不计入科学 gate。安全复用需要新版本
化 handoff descriptor，至少分别封存：

1. artifact path/schema/hash（与 producer source provenance 分开）；
2. recipient action 前后的 source manifest 或 operator-sealed changed-path descriptor；
3. explicit J、A、独立 terminal Y 及其 event-time lineage；
4. 相同 menu、public feature、read-cut、arrival、propensity 与成本范围的强同信息对照。

在这些字段进入实际 runner 前，PIPE2 继续 `benchmark_qualified=false`、
`scientific_claim_allowed=false`、`gpu_runs_allowed=false`。这一步没有修改 Goal、active
method 或历史结果；它只排除了一个会改变 benchmark 可见性和伪造标签的错误接线。

## Goal 对照

| 标准 | 本轮推进 | 仍未满足 |
|---|---|---|
| 故事线/创新 | 明确 observation 与 credit 的工程边界 | 评价对后续选择的真实增量 |
| 方法论 | 复用 typed bridge 的正确前提，拒绝隐式字段 | PIPE2 descriptor、合法 J/A/Y、实时更新 |
| benchmark/baseline | 保持真实 PIPE2 visibility，不把 runtime summary 当标签 | second root authority、same-info parity、独立 history 与结果 |

本轮 1 项定向测试通过；没有科学效果结论。下一步应为 PIPE2 编写 descriptor 设计卡
和零调用 schema/mutation qualification，完成后才考虑真实 recipient judgment 调用。

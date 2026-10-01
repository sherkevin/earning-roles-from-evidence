# Task report — PIPE2 v2 runtime handoff qualification (2026-10-01)

## Goal alignment

- **对应标准**：ER-G3/ER-G4 的执行、归因和可复核性前置门。
- **状态**：`PARTIAL`。v2 在有效 seed 子集上通过有限的 runtime handoff/scorer qualification；完整 TeamBench-derived root 仍被 fixture validity gate 阻塞。
- **goal_change_requested**：`false`。
- **科学边界**：这是零调用工程资格，不是 benchmark 分数、角色学习、在线更新、LLM 效果或 A800 结果。

## v2 修正

`peerrolebench_pipe2_material_adapter_v2.py` 固定了显式的
`peerrolebench-pipe2-materials-v2` contract：producer 只写 `pipeline/extract.py`；
recipient 只写 `pipeline/transform.py` 和 `pipeline/load.py`；`data/source.csv`
只作为 producer 的公开输入；`pipeline/run_pipeline.py` 是 operator/orchestrator
只读文件，不进入 recipient payload，也不会被 recipient 重跑。sandbox worker 只加载
实际执行的 Python 文件，Markdown spec 留在 manifest/context receipt 中。

Producer correctness 从公开 `extract.py` 的 AST 常量 `COLUMNS`/`KEY_COLUMNS` 和
`source.csv` 推导：按原始顺序保留 key columns 均非空的行。Recipient contract 从
公开 `transform.py` 的 `COL_TYPES` 推导：只有 `str` 字段 strip 并截断到 255，数值
字段保持原值。父进程不使用 hidden `expected_output.csv` 生成 handoff label；该文件
只作为独立 fixture-integrity audit 输入。

## 交接矩阵与诊断

对每个有效 seed，运行独立的 producer×recipient 2×2 矩阵：

1. original producer artifact → original recipient；
2. original producer artifact → corrected recipient control；
3. corrected producer artifact → original recipient；
4. corrected producer artifact → corrected recipient control。

每个 cell 都记录 producer/recipient arm、请求 digest、sealed artifact digest、source
row/key sequence、output row/key sequence、output digest 和 source paths。artifact
adoption 只有在 key sequence 和 row count 完全相等时才为 PASS；重复、重排、丢行和多余
行均失败。candidate runtime/resource/transport error 保持 `UNKNOWN`，不转成负标签。

canary 是独立的 sensitivity diagnostic，不计入 handoff lineage。另有两个 parent-owned
negative controls：`drop_row` 与 `ignore_artifact`，用于证明 scorer 能发现丢行和忽略
交付物；它们不进入科学标签。

## 新 v2 结果

### 有效 seed 0/2

回执：`experiments/logs/n03_pipe2_runtime_adoption_qualification_20261001_v8/`。

- `status=QUALIFIED_OFFLINE`；producer discrimination、handoff matrix、canary
  sensitivity、negative controls 均为 `true`。
- 两个 seed 共 8 个真实交接 cell，原始/修正版 recipient 与 producer 的责任差异均被
  父进程独立识别；每个 cell 都执行了真实 sandbox worker。
- 0 LLM API、0 GPU、0 native TeamBench grader；`scientific_claim_allowed=false`。

### 完整 seed 0–9

回执：`experiments/logs/n03_pipe2_runtime_adoption_qualification_20261001_v9/`。

- valid seeds：`0,2,3,5,7,8`；invalid fixtures：`1,4,6,9`。
- `status=FAILED_OFFLINE`，不是代码执行失败，而是完整 root 的 fixture gate 未通过；
  invalid seed 不产生 producer/recipient label，因此汇总资格保持 false。
- seed 1/4/6/9 的 source 与 expected CSV 因 generator 用未转义逗号产生额外 `None`
  字段。该缺陷属于 benchmark generator/data contract，不属于候选 agent 的质量。

## 验收判定

已满足：显式 v2 material contract；真实 producer→artifact→recipient 2×2 执行；完整
key sequence/row count adoption 检查；独立 canary 与负对照；逐 cell provenance；
UNKNOWN 保守分类；原始日志、配置、sandbox receipt 和 summary 可重放。

仍未满足：完整 root 的 fixture validity；native ledger/replay；真实 LLM actor；独立
live histories；later assignment/use outcome；baseline parity；benchmark freeze；
confirmation split；任何在线训练或 A800 证据。

## 后续动作

1. 保留 v1/v2/v3/v4/v5/v6 历史回执，不把旧 canary 叙述回填为 v2 证据。
2. 将 v3 fixture audit 的 `INVALID_FIXTURE` 结果纳入 benchmark authority gate；不静默
   修写、删 seed 或把有效子集升格为独立 benchmark。
3. 继续 PIPE3/第二 root 的 same-information baseline、独立 history、later-use 和
   完整 cost qualification；在这些门通过前不启动真实 API/A800 效果实验。

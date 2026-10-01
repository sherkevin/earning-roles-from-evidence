# Task report — PIPE2 generated fixture shape audit (2026-10-01)

## Goal alignment

- **对应标准**：ER-G3 benchmark authority 与 fixture validity；任何 invalid input 都不能产出 peer label。
- **状态**：`BLOCKED_BY_FIXTURE`。这是对候选 generator 的审计，不是 Goal 降级或 benchmark 冻结。
- **goal_change_requested**：`false`。

## 审计范围

- TeamBench pin：`d185aef1916fd86a9ba554d581fd256319a973af`。
- task：`PIPE2_data_pipeline`；seed `0–9`，其中 TeamBench README 将 0–2 作为 public、3–9 作为 hidden/rotating seed 范围。
- `peerrolebench_pipe2_fixture_shape_audit.py` 只读取 pinned generator 生成的 source/expected CSV，检查 `csv.DictReader` 的字段集合是否与声明 schema 完全一致；不执行 candidate、native grader、LLM 或 GPU。
- 回执：`experiments/logs/n03_pipe2_fixture_shape_audit_20261001_v1/`。

后续 v2/v3 审计改用 `io.StringIO(..., newline="")` 保留合法 quoted multiline 字段，
检查 `DictReader.fieldnames`、重复/错序 header、空数据和 CSV parse error；每个 seed
单独记录 generator exception，TeamBench HEAD、dirty 状态、generator/registry hash、
workspace/source/expected hash 与 structural root。最新回执为
`experiments/logs/n03_pipe2_fixture_shape_audit_20261001_v3/`，固定提交和工作树前置条件
均通过；v2/v3 不修改 v1 历史日志。

## 结果

| seed | schema | shape status |
|---:|---|---|
| 0 | employees | VALID |
| 1 | products | **INVALID_FIXTURE** |
| 2 | transactions | VALID |
| 3 | customers | VALID |
| 4 | projects | **INVALID_FIXTURE** |
| 5 | employees | VALID |
| 6 | products | **INVALID_FIXTURE** |
| 7 | transactions | VALID |
| 8 | customers | VALID |
| 9 | projects | **INVALID_FIXTURE** |

生成器用 `','.join(row)` 写 CSV；products/projects 的描述字段含逗号且没有 CSV 引号，
导致 source 与 expected 都被 `csv.DictReader` 解析出额外 `None` 列。public seed 0–2
中 1/3 无效；seed 3–9 中 3/7 无效。invalid fixture 不发 peer label，不能被当作
producer contract failure，也不能通过重写数据或静默排除来制造 root 通过。

## 验收结论

这项审计解释了 PIPE2 runtime qualification 的 seed-1 阻塞，并把问题从单个案例提升为
generator-level validity defect。seed 0/2 的运行时 control discrimination 仍是有效的
工程证据，但不能把有效 seed 子集写成完整 TeamBench root 的科学样本。PIPE2 仍保持
`CONDITIONAL`，不进入 frozen manifest、真实 API 或 A800。

审计中的 `expected_output.csv` 只用于独立的 fixture-integrity audit；v2 runtime 的
producer/recipient handoff label 从公开 extractor constants、`source.csv` 和公开
transform constants 推导。审计不把 oracle 文件形状错误重新解释为 agent 失败。

## 后续动作

1. 在 benchmark lock 中预注册 fixture validity gate；先决定是否由上游修复、选择公开且
   自洽的 seed 子集，或放弃该 root。这个决定需要共同确认，不由实验失败自动降级 Goal。
2. 在决定前保留所有十个 seed 的原始生成结果与 v1/v6/v8/v9 runtime 回执，不重算历史分数。
3. 继续完成 PIPE3/第二 root 的 independent history、baseline parity、later-use 与完整
   cost gate；不因有效 seed 子集通过而启动科学效果流。

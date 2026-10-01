# Task report — PIPE2 material/ownership qualification (2026-10-01)

## Goal alignment

- **对应标准**：ER-G3/ER-G4；第二 structural root 的真实 handoff、责任切分、oracle 隔离和可 replay 证据。
- **状态**：`PARTIAL`。PIPE2 的材料和交付形状资格通过，第二 root 仍不能冻结。
- **goal_change_requested**：`false`。

## 运行前冻结与真实输入

- TeamBench pin：`d185aef1916fd86a9ba554d581fd256319a973af`。
- task：`PIPE2_data_pipeline`，seed `0/1/2`；运行前写入 config，使用 pinned generator 在内存生成任务。
- producer ownership：`pipeline/extract.py`；recipient ownership：`pipeline/transform.py`、
  `pipeline/load.py`、`pipeline/run_pipeline.py`；`expected_output.csv`、tests、requirements
  留在 operator-only hidden paths。
- 运行回执：`experiments/logs/n03_pipe2_material_qualification_20261001_v1/`。
- LLM API=0、GPU=0、`scientific_claim_allowed=false`。

## 结果

- 3 个 seed 均通过 neutral task text、source comment/docstring 清理、ownership disjoint、
  hidden path 不泄漏和 public delivery schema 检查。
- recipient 在交付前明确等待 `artifact/extracted_rows.json`；附加合法形状的 producer
  artifact 后才可进入 ready 状态。
- artifact 的 `correctness_label` 固定为 `null`。本轮没有把一行 hand-authored fixture
  当作 producer correctness，也没有执行 candidate source。
- `python3 -m pytest -q tests`：**337 passed**；定向 PIPE2 测试 3 项通过，`py_compile`
  与 `git diff --check` 通过。

## 验收结论

已满足：PIPE2 比 MULTI3 更清晰的 extractor→transform/load handoff 已落实为 typed
material contract，oracle 与质量标签没有泄漏到 agent payload。

仍未满足：真实 producer extractor execution、recipient 对该 artifact 的实际 transform/load
使用、parent-side producer/recipient/adoption scorer、责任 gate、native ledger/replay、
later assignment、independent live history、baseline parity 和 confirmation split。

## 下一步

实现一个零调用 runtime/scorer qualification：在 sandbox 中执行 producer extractor，封存
其真实 rows artifact；recipient 只能读取该 artifact 完成 transform/load；parent scorer
分别测 producer contract、recipient self、sink adoption，并保留 failure/UNKNOWN。通过后
再决定 PIPE2 是否进入 candidate cell manifest，不启动正式 API/A800。

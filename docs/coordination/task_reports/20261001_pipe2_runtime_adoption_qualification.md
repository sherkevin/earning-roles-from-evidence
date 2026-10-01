# Task report — PIPE2 runtime, responsibility and adoption qualification (2026-10-01)

## Goal alignment

- **对应标准**：ER-G3/ER-G4；主轨候选必须能实际执行 producer→artifact→recipient，并把 producer contract、recipient self、artifact adoption 分开计量。
- **状态**：`PARTIAL`。seed 0/2 的运行时与父进程 scorer 资格通过；完整 seed 集合因 seed 1 的 fixture 数据错误不能通过 root qualification。
- **goal_change_requested**：`false`。

## 后续审查修正（2026-10-01）

本报告最初引用的 v5/v6 运行器把 parent 生成的 synthetic canary artifact 写成了
“真实 producer artifact”，并且旧版 material contract 还把 `pipeline/run_pipeline.py`
放在 recipient payload 中。该表述和边界已撤回；历史日志保持不可变，只作为早期
工程失败/诊断记录。新的 v2 adapter 与 runner 见
[PIPE2 v2 runtime report](20261001_pipe2_runtime_adoption_v2.md)，其结果不能回填到
本报告的 v5/v6 receipt。

## 冻结范围与执行边界

- TeamBench pin：`d185aef1916fd86a9ba554d581fd256319a973af`；task：`PIPE2_data_pipeline`。
- 新增 `peerrolebench_pipe2_runtime_worker.py`：在已通过的 pinned sandbox 中实际加载 producer `extract.py` 或 recipient `transform.py`/`load.py`。worker 只接收公开 CSV 或 sealed `pipe2-extracted-rows-v1` artifact，不包含 expected output、tests、labels 或 scorer assertions。
- 新增 `peerrolebench_pipe2_runtime_qualification.py`：父进程独立计算 producer contract、recipient self 和 artifact adoption；transport/resource/malformed response 保持 `UNKNOWN`，不转为负标签。
- 每个有效 seed 同时运行原始代码与手工修正版 control。control 只修复公开 spec 中的三处缺陷，用于验证评分能够区分候选责任，不是模型结果。
- LLM API=0、GPU=0、native TeamBench grader=0；`scientific_claim_allowed=false`。

## 结果与证据

### 有效 seed 子集

回执：`experiments/logs/n03_pipe2_runtime_adoption_qualification_20261001_v5/`。

- seed 0/2 均通过 producer discrimination：原始 extractor=`FAIL`，修正版 control=`PASS`。
- seed 0/2 均通过 recipient discrimination：原始 transform/load 的 self contract=`FAIL`，修正版=`PASS`。
- recipient 使用含 canary 的真实 producer artifact；修正版输出保留 canary，`artifact_adoption=PASS`。原始 recipient 的列顺序/截断缺陷仍被 self scorer 检出，但 adoption 可以单独为 PASS，说明三个责任维度没有被压成一个标签。
- 这些是零调用工程资格，不是 benchmark score、在线学习结果或角色形成证据。

### 完整 seed 集合

回执：`experiments/logs/n03_pipe2_runtime_adoption_qualification_20261001_v6/`；早期运行失败 `v1/v2` 也保留。

- seed 0/2 为 `VALID`，重复得到上面的 runtime discrimination。
- seed 1 被标为 `INVALID_FIXTURE`，没有发出 peer label。其 `data/source.csv` 与 `data/expected_output.csv` 有未声明的额外 `None` 列：未转义逗号使 `csv.DictReader` 产生第五个字段；这使“正确 producer→expected output”在公开 CSV 契约下不可自洽。
- 因为存在无效 fixture，三 seed root 的 `runtime_adoption_scorer_qualified=false`。不能通过删掉 seed 1、改写数据或把它当作候选失败来升格该 root。

## 验收判定

已满足：实际 producer/recipient 代码执行；sealed artifact 传递；父进程责任分解；原始/修正版控制可区分；adoption canary；资源/transport 保守 UNKNOWN；详细 config/raw/response/summary 回执。

仍未满足：完整 root fixture 修复或排除的共同确认；native ledger/replay 接入；real LLM actor；independent live histories；later assignment；baseline parity；benchmark freeze；confirmation split；任何在线训练或 A800 证据。

## 后续动作

1. 将 seed 1 的 CSV schema defect 纳入 benchmark authority/fixture audit；在没有共同确认前不修改历史数据、不重算历史结果。
2. 保留 seed 0/2 作为 runtime qualification evidence，但不把有效子集升格为独立 benchmark。
3. 先完成 PIPE3/PIPE2 统一责任 scorer、ledger/replay 与同信息 baseline parity，再决定是否编写新的 candidate manifest；在此之前不启动真实 API/A800。

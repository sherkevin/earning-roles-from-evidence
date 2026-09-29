# 2026-09-29 Benchmark 轨道选择审计

- **状态**：`PARTIAL`（完成 first-principles 角色划分；等待用户确认后才能激活 benchmark 计划版本）
- **对应 Goal**：ER-G1（核心因果链）、ER-G3（benchmark 适配性与权威性）
- **Goal 变更请求**：`false`
- **证据类型**：只读文档审计；无 LLM/API/GPU。

## 结论

当前有两个不同层次的问题被放在同一个“主 benchmark”名下：

1. `PeerSelect/IPD` 能干净测试局部图、selected-only payoff、在线更新、探索和漂移恢复；
2. `ArtifactRole/PeerRoleBench-TB` 才能测试本文不可替代的 situated judgment、责任归因、later assignment 和 artifact quality/cost。

从 Goal 的核心因果链反推，推荐 **ArtifactRole 作为论文 primary claim track，PeerSelect 作为前置机制 qualification/secondary track**。两个轨道共用 selector/update/event API，但 benchmark、label、scorer、统计分母和 claim-evidence matrix 分开。

详细候选方案见 [`benchmark_track_decision_v0.1_20260929.md`](../../research/candidates/benchmark_track_decision_v0.1_20260929.md)。该文件明确标记为 `CANDIDATE_NOT_ACTIVE`，没有静默修改 active benchmark 计划。

## Goal 对照

| 标准 | 状态 | 说明 |
|---|---|---|
| ER-G1 核心故事 | `MAINTAINED` | primary 仍由真实 artifact recipient judgment 承载，不被 payoff benchmark 替代。 |
| ER-G3 benchmark 适配 | `PARTIAL` | 轨道关系已澄清，但 authority/root/污染/clean replay 和独立 stream 仍未通过。 |
| ER-G4 实验准备 | `OPEN` | 还没有按两轨道生成冻结 cell manifest 或 baseline parity。 |
| Goal 变更 | `UNCHANGED` | 没有删除、放宽或替换目标。 |

## 下一步

等待用户确认 primary/secondary 关系；确认后才新建 active benchmark 计划版本，并为两个轨道分别冻结 benchmark scorecard、closest published baseline、parity 表和实验矩阵。确认前不启动新的正式 API/A800。

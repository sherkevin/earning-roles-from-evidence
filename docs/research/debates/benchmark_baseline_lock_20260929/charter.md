# Benchmark/Baseline Lock Debate Charter

- **阶段**：B — benchmark/baseline lock
- **目标 venue**：AAMAS
- **研究项目**：Earning Roles
- **当前目标**：判断 ArtifactRole/PeerRoleBench-TB 是否承载论文 primary claim，以及 PeerSelect/IPD 是否只承担机制资格与 secondary 证据；同时审查 benchmark authority、root independence、label identifiability、baseline executable parity 和最小 kill experiment。
- **不可静默改变的 Goal**：`docs/coordination/GOAL.md` ER-G1–ER-G7
- **active 规范**：`docs/research/canonical/active_versions.json`
- **当前人类决策门**：primary/secondary 关系尚未由用户最终确认，不能自动改写 active benchmark 计划。

## 候选关系

### Candidate A — ArtifactRole primary

真实 producer delivery → recipient use/rework/reject → responsibility-aware producer evidence → later assignment → unseen quality/full cost。

PeerSelect/IPD 只用于先验证局部候选、selected-only feedback、延迟更新、漂移恢复和实时成本，不把 payoff 结果替代 artifact responsibility claim。

### Candidate B — PeerSelect/IPD primary

以持久 peer、局部图和 selected-only payoff 为核心科学对象，ArtifactRole 只作外部案例或后续 transfer。

风险：只能支持 selector/update 机制，不能单独支持 recipient situated judgment、producer attribution 和 artifact adoption 的主线。

## 约束

- 不把 TeamBench-derived wrapper 自动称为公认 benchmark；上游 authority、commit、license、root taxonomy 和 clean replay 必须逐项核验。
- 不把 seed、改名或同一 generator 的轻微变体当成独立 root。
- 所有 baseline 必须有统一 factory、runner、snapshot/restore、同一 candidate menu、信息、propensity、arrival schedule、预算和完整成本合同。
- raw acceptance 必须保留独立 public channel，不能复用 responsibility gate 后的 projection，否则无法识别责任过滤的增量。
- `UNKNOWN` 不得被转成负例或更新信号；protocol qualification 不等于科学效果。
- 未通过 benchmark/baseline gate 前，不启动正式效果流或 A800。

## 决策输出

辩论只能产出：支持、反对、保留、最小决定性实验、kill criterion 和需要用户确认的具体选择。不能用 agent 票数直接修改 active 文档。

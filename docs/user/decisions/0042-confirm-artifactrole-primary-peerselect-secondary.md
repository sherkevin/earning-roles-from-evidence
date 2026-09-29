# ADR 0042 — Confirm ArtifactRole as primary and PeerSelect as secondary

日期：2026-09-30
状态：Accepted
范围：earning-roles 的 benchmark、baseline 和实验轨道

## Context

项目同时有两个互补问题：PeerSelect/IPD 能干净检验局部候选、selected-only
反馈、在线更新和漂移恢复；ArtifactRole/PeerRoleBench-TB 才能检验真实交付、
recipient situated judgment、责任归因、future assignment 和质量—完整成本闭环。
把它们合并成一个分数会让 payoff 机制结果替代论文真正的角色学习问题。

在候选 scorecard、上游版本审计、baseline parity 审查和 Goal 对照完成后，用户
确认采用以下轨道关系。

## Decision

1. `ArtifactRole` 是论文 primary benchmark/claim track。它承载主问题和主结果：
   `真实交付 → recipient judgment/use → attributable producer evidence →
   pre-execution future assignment → unseen quality/full cost`。
2. `PeerSelect` 是机制 secondary track。它只验证局部 peer selection、selected-only
   payoff、在线更新、探索、漂移恢复、延迟和服务成本，不单独支撑 situated judgment
   或 producer attribution claim。
3. 两个轨道可以共享 selector/update/event API，但必须分开维护 benchmark、label、
   scorer、统计分母、成本口径和 claim-evidence matrix；结果不得合并成单一总分。
4. 该决议只确认轨道关系，不冻结具体 benchmark、RARE、backbone、closest baseline、
   root split 或任何实验结果。各项仍须通过 active 评价标准和独立 qualification。
5. 在主轨 benchmark、baseline parity、later assignment、独立 root/stream 和实验
   manifest 通过前，不启动正式效果 API 流或 A800。

## Rationale

这保持了论文不可替代的因果链，同时用更干净的 PeerSelect 环境先排除“选择器根本
无法在线学习”的替代解释。副轨是机制资格和外部有效性辅助证据，不是主轨缺失时的
替代品。

## Consequences

- active benchmark 计划升级为 v1.1，并明确 primary/secondary 与分轨实验顺序。
- 下一阶段必须为两个轨道分别完成 root authority、closest baseline、parity 和 cell manifest；
  主轨优先完成完整 runner 与 later-assignment 资格。
- 如果 PeerSelect 成功而 ArtifactRole 失败，论文只能报告机制资格，不能声称角色学习
  闭环成立；如果 contextual trust 在主轨解释全部收益，RARE 主张停止。

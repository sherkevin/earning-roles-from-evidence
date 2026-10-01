# Benchmark 权威性与因果字段复核（candidate，2026-10-01）

## 目的与结论

本报告只复核公开 benchmark 的权威性、原生字段和可复用资产，不修改当前
`benchmark_baseline_v1.1` active 计划，也不把任何零调用 qualification 写成科学结果。

结论是：截至本次审查，没有一个现有公开 benchmark 原生同时提供以下四个字段：

1. producer 的可归因交付与版本 lineage；
2. recipient 对该交付的 situated judgment；
3. recipient 的 use/rework/reject 与独立 adoption 结果；
4. later assignment 在执行前读取该证据并产生可测的未来结果。

因此，“直接拿一个现成 benchmark 跑出角色学习效果”不是诚实的实验设计。可行的
做法是使用公认 benchmark 的任务、隔离和确定性 grader 作为权威底座，公开、预注册
并冻结一个薄的因果协议扩展；论文必须把 `TeamBench` 与我们的 `PeerRoleBench-TB`
扩展分开命名，不能把扩展伪装成 upstream benchmark 原生能力。

## 公开基准逐项审查

| 基准 | 原生强项 | 缺失的核心字段 | 在本项目中的合法用途 |
|---|---|---|---|
| [TeamBench](https://arxiv.org/html/2605.07073) / [官方仓库](https://github.com/ybkim95/TeamBench) | OS 强制 Planner/Executor/Verifier 隔离；851 templates/931 seeded instances；确定性 shell grader；Solo/Restricted/Full Team/No-Plan/No-Verify 消融 | Verifier 是当前提交的 verdict，不是跨任务 public role evidence；没有 producer adoption history 与 later assignment | **主轨权威底座**：复用 generator、sandbox、grader、角色越权审计、judge–grader disagreement 和 compute-matched solo；因果扩展必须单独冻结 |
| [CooperBench](https://github.com/cooperbench/CooperBench) / [论文](https://arxiv.org/html/2601.13295) | 真实代码仓库、feature conflict、Redis handoff、solo/coop/team 设置、native tests | 原生 assignment 预先给定；缺 structured recipient acceptance/adoption 与 future duty update；merge 失败路径存在 fallback 风险 | **外部有效性 substrate**：验证代码交付/冲突场景；必须显式禁用 fallback 并补 ownership/adoption ledger |
| [MultiAgentBench/MARBLE](https://aclanthology.org/2025.acl-long.421/) | 多种 topology、research/coding 等任务、milestone KPI 和公开框架 | profiles、角色和工作流预先指定；部分评估依赖 LLM judge；没有 situated recipient evidence → later assignment | topology/协作机制副轨；不能支撑主故事的 role formation claim |
| [Collab-Overcooked](https://aclanthology.org/2025.emnlp-main.249/) | 资源隔离、非对称知识、明确的两方 handoff、过程指标和 30 个任务 | 固定 chef/assistant seat；游戏模拟；没有可交换 peer identity、producer attribution 或 later role update | handoff/repair stress test；不能替代 artifact 主轨 |
| [AgentCollabBench](https://arxiv.org/html/2605.08647) | 900 human-validated diagnostic tasks；instruction decay、tracer durability、belief contagion、leakage 指标 | 诊断 failure mode 而非 artifact ownership/judgment/assignment；没有 selected-only responsibility learning | robustness/过程诊断外部报告；不作为主 benchmark |
| [PeerSelect-IPD / graph-ipd](https://github.com/geronest/graph-ipd) | 局部图、selected-only payoff、漂移和在线更新可控 | payoff 不是 artifact delivery/adoption；没有 recipient judgment 与责任归因 | **机制副轨**：验证选择/更新数学，不替代主轨 |

## Benchmark 与 baseline 的可执行边界

主轨继续采用 `ArtifactRole`，但 benchmark 语义应拆成两层：

- **权威层**：TeamBench 固定 commit、任务 generator、OS 权限、grader 和其原生
  ablation；这些可以直接引用 upstream 结果/协议。
- **因果扩展层**：`PeerRoleBench-TB` 增加 producer delivery、recipient judgment/use/
  rework、责任 gate、native `RoleEvidenceUpdate`、pre-execution `LaterAssignment`、
  later outcome 和完整成本。它是基于 TeamBench 的派生协议，必须单独发布 manifest、
  adapter、scorer、replay 和 contamination audit。

主轨 baseline 分两组，不能混成一个 headline：

1. **benchmark 原生协作对照**：TeamBench `Solo`、`Restricted`、`Full Team`、
   `Team-No-Plan`、`Team-No-Verify`，报告 pass/partial score、role violation、
   verifier–grader disagreement、compute-matched single-agent 和按 Solo 难度分层的
   team uplift。
2. **同信息 peer-selection 对照**：`uniform`、`no_update`、`raw_acceptance`、
   `terminal_only`、`contextual_trust`、`pooled_controller`、RARE candidate，以及
   预注册的 public-only/original-info/profile-only closest adapter。它们共享候选菜单、
   read cut、arrival order、propensity、预算和 UNKNOWN/no-update 规则。

CooperBench 的 `solo/coop/team` 只能作为第二环境对照；MARBLE、Collab-Overcooked 和
AgentCollabBench 只能作为机制或 robustness 外部验证。任何副轨提升都不能写成
`situated judgment` 主张的证据。

## 复用资产与必须新增的内容

可直接复用：TeamBench 的 generator、sandbox、grader、任务污染审计和 human-study
结构；CooperBench 的容器/Redis/git-conflict substrate；MARBLE 的 topology/config
骨架；Collab-Overcooked 的 resource-isolation handoff 设计。

必须新增且预注册：producer/recipient ownership schema、canonical ledger、public
role-evidence offer、assignment-before-selection plan、adoption/use scorer、late
correction、独立 stream split、完整成本、UNKNOWN 分母和 statistical analysis plan。
当前代码已经资格化其中若干协议接缝，但 benchmark 仍不能冻结，直到第二 structural
root、独立 live histories、executable baseline parity、closest adapter 和 confirmation
split 同时通过。

## 验收状态

- 权威 benchmark 底座：`PARTIAL`（TeamBench 证据充分，因果扩展尚未冻结）。
- 主轨字段完整性：`OPEN`（later assignment/adoption/independent histories 未完成）。
- baseline 选择：`PARTIAL`（矩阵已列出，真实同信息执行与 closest adapter 未通过）。
- Goal：未修改，`goal_change_requested=false`。

# 有机整体创新的量化验证方案

- 日期：2026-09-28
- 状态：CANDIDATE_VALIDATION_PLAN
- 对应故事线：storyline_v1.1
- 说明：这是内部验证设计，不是已完成实验，不改变 Goal。

## 核心假设

把 situated judgment、责任过滤、延迟更新和 future assignment 组织成一个闭环后，系统在同一信息、预算、候选集合和任务流下，会产生已有单组件或已有组件组合无法稳定产生的三类性质：

1. responsibility-aware attribution；
2. third-party future-owner transfer；
3. delayed feedback 下的质量—成本改善与稳定更新。

## 模块集合与正交干预合同

J/A/U/F 不是四个可以随意开关的功能包。为了让消融可识别，所有条件都保留同一条
immutable episode stream；只改变 policy 看到的投影或 state transition：

- **J**：是否把封存的 recipient judgment/action 投影给 policy。J=0 仍执行并记录 recipient action，但 policy 只能看到预注册的 raw/terminal channel；J=1 才读取 situated channel。
- **A**：是否启用责任/归因闸门。A=0 使用预注册的 raw eligibility；A=1 只接受 producer contract、recipient action 和 `UNKNOWN` 规则共同通过的事件。
- **U**：是否启用 versioned、幂等、按 arrival/watermark 处理的在线更新算子。U=0 冻结 policy state；U=1 只改变状态转移，不改变 feedback 输入或 assignment 规则。
- **F**：是否在执行开始前读取不含 chosen agent/propensity 的 `AssignmentEvidenceOffer`
  （task/index/role、candidate menu、公开 evidence、arrival watermark）形成 selection。
  F=0 不把 bundle 传给 policy；F=1 读取经过版本/digest 绑定的 bundle。policy 随后才
  产生 chosen peer、propensity 和 exploration draw；LaterAssignment 只记录 selection
  之后的 lineage/adoption，不再作为 F 的输入。两者必须共享 candidate menu、RNG、预算
  和 exploration。

raw acceptance、terminal-only、contextual trust/bandit 和 matched composition 是独立的 baseline arms，不混入二值 factorial 因素。只有这一定义下，`do(J,A,U,F)` 才有可解释的 2⁴ 条件。

## 指标

令 `M(z)` 表示二值条件 `z=(J,A,U,F)` 下，在完全相同的信息、候选集合、探索机会、API/工具预算和状态容量下的预注册主指标。主指标优先使用：

M = Q_unseen - lambda * C_complete

其中 Q_unseen 是未见 root 上的质量，C_complete 是 producer、recipient、judge、重试、返工、通信、scorer 和 replay 的完整成本，lambda 在开发前固定。

同时报告：

- 判断对独立 producer contract/later-use 的增量预测；
- future owner 实际采用 evidence 的比例；
- assignment regret 与 propensity；
- update/selection p50/p95、service lag、backlog 和状态字节；
- 旧 root holdout 的遗忘峰值、恢复窗口和 UNKNOWN 率。

## 组合是否形成整体机制

### 1. 整体增量与全因子对比

令 `z=(J,A,U,F)∈{0,1}^4`，`M(z)` 是同一 immutable stream 上预注册的质量—成本主指标。
整体增量为 `Δ_F=M(1,1,1,1)-M(0,0,0,0)`，并与最强 matched composition baseline 比较。

不能只报告 full corner 的差值作为全局主效应。全因子主效应为：

`μ_i = (1/8) Σ_{z_{-i}} [M(z_i=1,z_{-i})-M(z_i=0,z_{-i})]`。

预先指定的二阶交互为：

`μ_{ij} = (1/4) Σ_{z_{-ij}} [M(1,1,z)-M(1,0,z)-M(0,1,z)+M(0,0,z)]`。

同时与 raw acceptance、terminal-only、contextual trust/bandit、pooled controller 及最强已有组件组合比较。只有在 confirmation root 上仍有增量，才进入整体创新结论。

### 2. 留一必要性（局部诊断）

`N_i=M(1,1,1,1)-M(z_i=0,z_{-i}=1)` 只作为 full-corner 的局部诊断，不能替代上面的全因子主效应。

J、A、U、F 各自要对应一个机制性质。如果移除某模块没有改变任何预注册性质，该模块不能被写成必要机制。

### 3. 非加性交互

对预先指定的模块对，只使用上面定义的全因子 `μ_{ij}`。只把跨 root、跨 stream 且置信区间支持的正交互解释为协同。单次正结果、只在开发 root 出现或被成本抵消的交互不够。

### 4. 闭环门

J、A、U、F 不是只看分数。以下四箭头必须分别有事件和权限证据：

situated judgment → attributable evidence → future assignment → unseen utility。

任一箭头缺失，整体机制最多是信号或协议结果，不能写成闭环创新。

## 对照矩阵

| 条件 | J | A | U | F | 目的 |
|---|---:|---:|---:|---:|---|
| `0000` | 0 | 0 | 0 | 0 | frozen/raw control |
| `z∈{0,1}^4` | z₁ | z₂ | z₃ | z₄ | 正交主效应与交互 |
| matched composition | 由最强已有组件组合 | 外部 comparator | 外部 comparator | 外部 comparator | 防止把已有组合误归为整体机制 |

raw acceptance、terminal-only、contextual trust/bandit 另列为 baseline，不伪装成 factorial cell。

所有条件共享同一候选集合、初始状态、探索机会、模型/API、预算、可见性、event stream 和任务根划分。未知反馈不产生更新；开发结果不能改写 confirmation split。资格测试必须在 event-time interleaving 中证明：反馈在下一次 decision watermark 之前到达时才可能影响下一次 decision；单纯把所有 decisions 先注册、再离线 replay feedback 不能证明闭环影响。

## 停止和解释

- 若 full 与 matched composition 无差异：不支持整体创新，检查机制定义或测量；
- 若只有 J+A 有效、U/F 无效：只能主张责任感知判断信号；
- 若 full 只改善开发 root：判为过拟合或任务特异；
- 若质量提升被完整成本和遗忘抵消：不支持主质量—成本主张；
- 若责任归因失败：停止闭环实验，不把 consumer 错误标给 producer。

这套设计的目标是让“有机整体”成为可量化、可反驳的研究命题，而不是一句包装性描述。

## 零调用资格结果（2026-09-28，已作审计修正）

两段完整 PIPE3 协议 episode 的 hash-chain replay 已通过，说明账本可以记录 J/A/U/F 所需的协议事件；但 assignment 与下一 selection 的 agent/propensity 相同，不能证明 policy 实际读取了 evidence。原始事件和运行配置见 [factorial mapping qualification](../coordination/task_reports/20260928_factorial_mapping_qualification.md)。

这还不是 factorial 实验。当前没有任何 scientific cell ready：A 缺 producer-score/attribution projection，U 缺 version/correction/watermark interleaving qualification，F 的 pre-decision offer/consumption attestation 尚未接入真实 runner；现有 replay 也不能证明更新影响了后续 decision。下一道 gate 是先做四个正交 projection/state-transition seam 的零调用 mutation qualification，再冻结真实 factorial card。完成前不启动真实 factorial API 或 A800。

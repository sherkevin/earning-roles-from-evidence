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

## 模块集合

当前只把以下四个模块作为候选机制的组成部分：

- J：recipient 的 situated judgment 与真实使用动作；
- A：producer/recipient 责任过滤和 UNKNOWN 语义；
- U：延迟、乱序、版本和低成本在线更新；
- F：执行前的 future assignment 消费与反馈闭环。

模块只是实验因素，不预先声称每个模块单独创新。

## 指标

令 M(S) 表示只启用模块子集 S 时，在完全相同的信息、候选集合、探索机会、API/工具预算和状态容量下的预注册主指标。主指标优先使用：

M = Q_unseen - lambda * C_complete

其中 Q_unseen 是未见 root 上的质量，C_complete 是 producer、recipient、judge、重试、返工、通信、scorer 和 replay 的完整成本，lambda 在开发前固定。

同时报告：

- 判断对独立 producer contract/later-use 的增量预测；
- future owner 实际采用 evidence 的比例；
- assignment regret 与 propensity；
- update/selection p50/p95、service lag、backlog 和状态字节；
- 旧 root holdout 的遗忘峰值、恢复窗口和 UNKNOWN 率。

## 组合是否形成整体机制

### 1. 整体增量

Delta_F = M(J,A,U,F) - M(empty)。

同时与 raw acceptance、terminal-only、contextual trust/bandit、pooled controller 及最强已有组件组合比较。只有在 confirmation root 上仍有增量，才进入整体创新结论。

### 2. 留一必要性

N_i = M(F) - M(F without i)。

J、A、U、F 各自要对应一个机制性质。如果移除某模块没有改变任何预注册性质，该模块不能被写成必要机制。

### 3. 非加性交互

对预先指定的模块对：

I_ij = M(F) - M(F without i) - M(F without j) + M(F without i and j)。

只把跨 root、跨 stream 且置信区间支持的正交互解释为协同。单次正结果、只在开发 root 出现或被成本抵消的交互不够。

### 4. 闭环门

J、A、U、F 不是只看分数。以下四箭头必须分别有事件和权限证据：

situated judgment → attributable evidence → future assignment → unseen utility。

任一箭头缺失，整体机制最多是信号或协议结果，不能写成闭环创新。

## 对照矩阵

| 条件 | J | A | U | F | 目的 |
|---|---:|---:|---:|---:|---|
| no-update | 0 | 0 | 0 | 0 | 执行与先验下界 |
| raw acceptance | 部分 | 0 | 0 | 0 | 观察 acceptance 的增量 |
| contextual trust | 可见 | 可见 | 简化 | 可见 | 最强同信息控制 |
| J-only | 1 | 0 | 0 | 0 | 判断本身是否足够 |
| J+A | 1 | 1 | 0 | 0 | 责任过滤是否产生增量 |
| J+A+U | 1 | 1 | 1 | 0 | 延迟更新是否提供增量 |
| full integrated | 1 | 1 | 1 | 1 | 完整机制 |
| matched composition | 由最强已有组件组合 | 同 full | 同 full | 同 full | 防止把旧组件组合误当新机制 |

所有条件共享同一候选集合、初始状态、探索机会、模型/API、预算、可见性和任务根划分。未知反馈不产生更新；开发结果不能改写 confirmation split。

## 停止和解释

- 若 full 与 matched composition 无差异：不支持整体创新，检查机制定义或测量；
- 若只有 J+A 有效、U/F 无效：只能主张责任感知判断信号；
- 若 full 只改善开发 root：判为过拟合或任务特异；
- 若质量提升被完整成本和遗忘抵消：不支持主质量—成本主张；
- 若责任归因失败：停止闭环实验，不把 consumer 错误标给 producer。

这套设计的目标是让“有机整体”成为可量化、可反驳的研究命题，而不是一句包装性描述。

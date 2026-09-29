# Benchmark 轨道选择候选决议 v0.1

- **状态**：`CANDIDATE_NOT_ACTIVE`
- **日期**：2026-09-29
- **不改变**：active benchmark 计划、Goal、故事线和方法论
- **用途**：在用户确认前，把 PeerSelect/IPD 与 ArtifactRole/TeamBench 的关系写清楚，避免继续用两个不同问题争论“主 benchmark”。

## 1. 从 Goal 反推 primary claim

项目 Goal 的不可替代因果链是：

```text
真实交付物
→ recipient 实际使用/返工/拒绝时的 situated judgment
→ 可归因的 producer role evidence
→ 下一次执行前的 assignment 改变
→ 未见任务上的质量与完整成本变化
```

因此，最终论文的 primary scientific claim 必须由能观察这条链的 `ArtifactRole` 任务轨道承载。一个只有博弈 payoff 的 partner-selection 环境可以证明 selector、局部图、selected-only feedback 或在线更新的可识别性，但不能证明 recipient judgment、责任归因和 artifact adoption。

## 2. 候选轨道的角色

### Track A：PeerSelect/IPD

用持久节点和无向局部图提供干净的 selector 机制环境：候选只来自邻居，选择后才获得 selected-only payoff，反馈可延迟，更新成本可直接测量。它适合做：

- selector/update 的数学与在线服务 sanity check；
- graph locality、exploration、drift recovery、latency 和 forgetting 的机制消融；
- 在复杂 LLM 任务进入前，排除“选择器根本不能学”的替代解释。

它不应单独支持本文的核心 role-learning 结论，也不应与 ArtifactRole 的质量/成本结果合并成一个分数。

### Track B：ArtifactRole/PeerRoleBench-TB

用真实 producer→recipient 交付、recipient action、adoption、责任 gate 和 later assignment 承载核心故事。它适合做：

- situated judgment 相对 raw/terminal 信息的增量；
- producer defect 与 recipient-only error 的责任识别；
- later assignment 是否改变未见 root 的质量、返工和完整成本；
- shared selector/update API 在真实 LLM 任务中的外部有效性。

它目前仍是 TeamBench-derived 候选协议：DIST1 有历史泄露问题，PIPE3 还没有完成独立 root、later assignment、多 stream 和统一 baseline parity，不能因为已有工程链就宣布冻结。

## 3. 候选结构（推荐但未激活）

推荐把 **Track B 作为论文 primary benchmark/claim track**，把 **Track A 作为前置机制 qualification 与 secondary benchmark**：

```text
Track A：先证明 selector/update 在干净局部图和 selected-only 信号下可识别
    ↓ 只证明进入复杂任务的必要条件，不替代主结果
Track B：再证明 situated judgment → attributable evidence → later assignment
        在未见 ArtifactRole root 上产生质量—成本后果
```

这个结构最符合 Goal，同时避免把 TeamBench 的 LLM、源码、scorer 和责任问题与 selector 学习一次性混在一起。两个轨道共享底层 selector/update/event API，但分别拥有 benchmark、label、scorer、统计分母和 claim-evidence matrix。

## 4. 不能提前声称的内容

- Track A 通过不等于本文方法在 artifact collaboration 中有效；
- Track B 的单条 v6 链通过不等于 peer selection 或 role learning 有效；
- 两轨道都不能用 protocol fixture、单 seed、工程 smoke、最好结果或 post-hoc label 代替独立 live histories；
- 若 Track A 通过而 Track B 失败，结论是 selector 机制具备必要的可运行性，但 ArtifactRole 外部有效性未建立；
- 若 Track B 在同信息 contextual trust 下无增量，不能借 Track A payoff 提升来挽救核心 claim。

## 5. 激活前必须解决的三件事

1. 用户确认 primary/secondary 关系；若不同意本候选，需明确选择另一种关系及其 claim 边界；
2. 为 Track A 和 Track B 各自固定 authority/root/污染/clean replay scorecard，不把 graph-ipd 或 TeamBench-derived wrapper 自动称为公认 benchmark；
3. 为每轨道分别生成完整 cell manifest 和 baseline parity 表，再决定是否执行新的真实 API 流。

在用户确认前，本文件不替代 `docs/research/versions/benchmark-baseline/benchmark_baseline_v1.0_20260928.md`，也不计入 scientific readiness。

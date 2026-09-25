# Benchmark 适配性复审

> 日期：2026-09-25  
> 状态：范围修正建议，尚未替代用户决议 0008  
> 问题：CooperBench 是否适合作为 peer-judged role formation 的 benchmark？

## 结论

如果 benchmark 的含义是“下载后直接运行并测量完整科学问题”，CooperBench 不够恰当。

它适合被称为 **code-collaboration task substrate**：有真实代码库、base commit、feature patch、merge pressure 和 native tests；但它原生没有：

- recipient 的结构化 situated judgment；
- producer artifact 是否被采用、修复或独立重做的 lineage；
-跨 task 的 persistent identity 与 later assignment；
- 关闭 solo fallback 后的严格双人 scorer。

因此不能把原生 `both_passed` 当成 role formation 结果。

## 为什么不是简单换一个现成 benchmark

当前审查过的公开环境各自只覆盖一段：

| 资源 | 能测什么 | 缺什么 |
|---|---|---|
| DecisionBench | 异构 peer/model selection、成本和 profile routing | 没有 recipient artifact use/rework 和后续职责变化 |
| CooperBench | 代码交付、冲突、native tests | 没有 situated judgment、lineage、later assignment，且原生预分配角色 |
| AgentWorld | stateful multi-agent transfer 和黑箱协作 | 角色/技能预设，不能直接证明 role formation |
| MARBLE/TeamBench/AgentNet | 固定角色、dynamic routing、verifier 或图协作控制 | 没有完整 judgment → evidence → assignment 链 |

所以不存在一个现成 benchmark 可以直接覆盖本论文的完整问题。硬把 CooperBench 叫作 benchmark，会掩盖真正需要验证的新协议。

## 建议的三层结构

### 第一层：PeerRoleBench-v0（待验证）

用公开任务 substrate 复用任务和 objective tests，但由本项目定义角色形成协议：

```text
task root
  -> exchangeable persistent assignment
  -> producer receipt
  -> pre-terminal recipient judgment
  -> attributable use / repair / redo
  -> strict terminal scorer
  -> explicit role-evidence update
  -> later assignment on a new root
```

这应被称为 **CooperBench-derived PeerRoleBench protocol**，不能写成 CooperBench 原生结果。新增的协议层本身就是实验方法的一部分，必须公开 schema、scorer、split 和失败处理。

### 第二层：DecisionBench selector slice

仅用于比较 selector 的探索、适应、成本和 calibration。DecisionBench 的 quality 是候选模型/工作流的任务得分，不是 recipient 对交付物的采用信号，因此不能单独支撑 role formation。

### 第三层：AgentWorld 或其他协作环境

只做 external stress。若身份、技能和职责仍由 task file 预设，结果不能解释为角色学习。

## 最小可行 gate

先用两个 task-root 做 zero-LLM smoke：

1. 同一 task-root 让两个 persistent、同能力 agent 都有资格承担 producer；
2. P、recipient-redo、raw-acceptance、no-role-update 使用同一任务和预算；
3. recipient 在 terminal scorer 前封存 judgment；
4. scorer 保存 producer tree、recipient tree、patch lineage、merge status 和 test results；
5. 禁用 `solo-agent1` fallback，或将其单列为失败/诊断；
6. 下一 task-root 的 assignment 必须引用显式 evidence update；
7. 如果无法区分“交付本身有用”“判断有用”“判断改变了未来职责”，就停止扩大实验。

如果这两个 root 不能通过，CooperBench 只保留为 integration diagnostic；本项目应把主张收窄为 artifact-aware peer selection。如果通过，再按 task-root/repository 分组做 held-out split，正式命名并发布 PeerRoleBench-v0。

## 与决议 0008 的关系

决议 0008 仍然有效地冻结了 CooperBench、DecisionBench 和 AgentWorld 的候选层次；本复审把 CooperBench 的语义从“角色形成 benchmark”收紧为“角色形成 task substrate 候选”，并把 `PeerRoleBench-v0` 设为需要通过 gate 的协议候选。没有用户明确确认前，不修改 0008 的 Accepted 状态。


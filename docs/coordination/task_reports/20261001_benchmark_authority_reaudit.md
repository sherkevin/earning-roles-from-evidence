# Task report — benchmark authority re-audit (2026-10-01)

## Goal alignment

- **对应标准**：ER-G3/ER-G4；benchmark 选型权威性、baseline 时效性与实验矩阵可识别性。
- **状态**：`PARTIAL`。完成公开基准的一手页面/论文复核并明确权威底座与因果扩展边界；active benchmark 仍未冻结。
- **goal_change_requested**：`false`。

## 运行前冻结与来源

本轮是只读调研，不调用 LLM API、Nebula 或 GPU。来源为官方论文/仓库页面以及已归档
本地源码审计：TeamBench、CooperBench、MultiAgentBench/MARBLE、Collab-Overcooked、
AgentCollabBench 和 graph-ipd。详细字段矩阵见
[`benchmark_authority_review_20261001.md`](../../research/candidates/benchmark_authority_review_20261001.md)。

## 主要发现

1. TeamBench 是目前最适合主轨的**权威任务/隔离/grader 底座**，但其原生 Verifier verdict
   不是跨任务 role evidence，也没有 recipient adoption 与 later assignment。
2. CooperBench 更接近真实代码冲突与 handoff，但 assignment 预先给定，且原生 scorer
   不能直接证明 recipient adoption；它适合作外部有效性环境。
3. MARBLE、Collab-Overcooked、AgentCollabBench 和 graph-ipd 各自能覆盖 topology、
   handoff、过程鲁棒性或 online payoff 的一部分，均不能单独承载主故事。
4. 因此最干净的实验叙事是“公认 benchmark 底座 + 明确披露的因果协议扩展”，而不是
   继续寻找一个假设上已经包含全部字段的现成 benchmark。

## 对验收标准的结论

- 已满足：公开候选的强项、缺失字段、可复用资产和不可替代的主张边界已逐项记录；
  baseline 分成 TeamBench 原生协作对照与同信息 peer-selection 对照。
- 部分满足：TeamBench primary substrate 的权威性较强，PeerRoleBench-TB 因果扩展仍是
  derived protocol，不能写成 upstream 原生 benchmark。
- 未满足：第二 independent structural root、完整 live baseline parity、closest
  adapter、independent histories、later-use effect、完整成本与 confirmation split。

## 下一步

冻结 TeamBench primary substrate 的 manifest 与 native baseline mapping；随后只做一个
第二 root/independent-history 的零调用资格 audit，确认 producer/recipient/adoption
scorer 覆盖后再扩展真实 API。没有这些门，不启动 A800，也不把当前协议资格结果写成
方法收益。

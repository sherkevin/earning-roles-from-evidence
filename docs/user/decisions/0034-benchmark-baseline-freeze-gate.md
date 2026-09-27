# ADR 0034：在 root 与同信息 baseline 通过前不冻结 benchmark

- Status: Accepted for the current research iteration
- Date: 2026-09-27
- Supersedes: none
- Goal change requested: false

## Context

当前 TeamBench-derived `PeerRoleBench-TB` 只有一个已经用于真实 API 的 DIST1
诊断 root。PIPE3 的静态契约和父进程控制矩阵说明它可能提供第二种 producer→recipient
→sink 结构，但任务文本、真实 dispatch、独立 scorer/ledger IPC、异常覆盖和成本边界
尚未全部通过。MULTI3 的 schema ownership 和实际 delivery binding 仍更不确定。

已有 N02 两条完整链证明了受限 runner 和 API 传输可以工作，但 peer 同构、概率未变，
且不能承担 benchmark 或方法效果结论。若现在同时改变 root、baseline 和更新方法，任何
结果都无法解释为 situated judgment 的增量。

## Decision

在以下条件全部通过前，不把 benchmark 标为 frozen，不启动新的真实 API 小链或 A800：

1. 至少两个结构不同的 root 有版本化 manifest；seed/改名不能冒充 root；
2. 每个 root 的 task text、可见文件、producer/recipient ownership、hidden scorer、
   operator ledger 和 UNKNOWN 规则通过独立检查；
3. development/confirmation split 在看到结果前封存；
4. `uniform`、`no_update`、`raw_acceptance`、`terminal_only`、同信息
   `contextual_trust`、`pooled_controller` 和 RARE 使用同一候选集合、propensity、
   信息、预算和成本口径；
5. 主指标、停止规则和失败处理写入实验 card。

当前候选顺序固定为 PIPE3 主候选、MULTI3 fallback；DIST1 只作为 development/诊断
候选，直到其信息边界重新核准。

## Consequences

这会暂缓一条看似“能跑”的新 API 链，但避免把 benchmark 缺陷、评分器资源 UNKNOWN
或 baseline 信息差误写成方法失败/成功。现有 runner、ledger、scorer 和 TeamBench
材料继续保留并可复用；如果 PIPE3 资格失败，只需按同一 manifest/baseline 合同审查
MULTI3，不重新发明实验流程。Goal v1.0、RARE 的科学问题和实时性/稳定性硬标准不变。

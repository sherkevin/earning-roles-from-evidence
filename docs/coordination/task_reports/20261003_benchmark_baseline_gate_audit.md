# 2026-10-03 Benchmark、baseline 与实验矩阵增量审计

## 结论

当前三项门均为 `PARTIAL/NOT_READY`；Goal 不变，正式效果流和 A800 继续关闭。

### Benchmark 选型

`PeerRoleBench-TB` 仍是 TeamBench-derived candidate，不是冻结 benchmark。PIPE3 仍是
单一 structural root 候选；PIPE2 的 derived recipe 在 shape/runtime/责任 plumbing 上
通过，但 authority 尚未共同确认，且修复改变了 root identity，不能升格第二科学 root。
PIPE2 的 40 个 producer×recipient replay 全为 UNKNOWN，缺真实 judgment/action/ownership/
terminal；N02 两条真实 API 链也因缺 producer defect registration 被当前 gate 判为
`PENDING_ATTRIBUTION`。MULTI3 仍是 conditional-low，Meta-Team closest adapter 仍
`NO-GO/QUALIFICATION_REQUIRED`。

### Baseline parity

已有 v16 只证明 hand-authored offline implementation parity；PIPE3/P0 只证明 producer-owned
CPU delayed-update 接缝，recipient/mixed 控制会保护性 UNKNOWN。七个 arm 尚没有 canonical
live runner、独立 history、later-use outcome 和完整实测成本。当前 `contextual_trust` 与
RARE 的特征、correction 能力和更新语义不同，不能称 strongest same-information baseline；
`role-evidence-judgment-beta-v1` 只是 assignment-side comparator，不是七 arm parity。
Meta-Team-L2-public 仍未实现/冻结。

### 实验矩阵

评价文档列出的因素尚未转化为可执行 scientific cell manifest：缺少独立 live histories、
每个 arm 的合法 source adapter、E0→E1 `PeerHistoryV1`/later-use、成本和精度/UNKNOWN
预算。PeerHistoryV1 的 5/5 零调用 contract 只关闭状态接缝，不识别 peer suitability 或
角色形成。

## 最小下一步

1. 在共同确认第二 root authority 之前，不修改 active benchmark 或 split；保留 PIPE2
   为 candidate derived root。
2. 在选定 root 上把 PeerHistoryV1 与 policy factory 接入 canonical PIPE3，先做零调用
   matched replay、mutation、lineage 和同信息 parity。
3. 为每个 arm 固定 accepted-source/update 语义与相同 feature schema，写出可执行 cell
   manifest，包含 independent streams、later assignment、成本、precision 和 UNKNOWN
   分母。
4. 只有这些门通过后，再做一条有界真实 API 小链；A800 仍等待真实瓶颈和冻结 challenger。

本审计不修改 Goal、active benchmark、method 或故事线；`goal_change_requested=false`。

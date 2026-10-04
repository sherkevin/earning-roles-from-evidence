# Peer-history 工程门之后的唯一下一步

日期：2026-10-04
状态：`NEXT_GATE_DESIGN_ONLY`

## 当前判断

append、history/no-history/reset、跨进程恢复、两条 history permutation/candidate mismatch/scope isolation 已有零调用回执，但它们仍使用 hand-authored canonical fixture。它们证明了存储、读取、顺序和拒绝边界，不能单独证明下一次读取的 history 一定来自真实 canonical ledger 的 source→target provenance。

在这个 provenance 门关闭前，不能把第二 structural root、same-information baseline parity 或真实 API 结果写成可解释的科学比较；否则即使选择变化，也无法排除 history 错绑、未来结果泄漏或错误 candidate/version 合并。

## 唯一 next gate：canonical provenance qualification

复用现有 `HistoryBindingReceiptV1`、`RoleEvidenceOffer`、native `PeerRoleLedger`、`LaterAssignment`、target selection/delivery/judgment/action/outcome、`DelayedCreditLedger` 和 `PeerHistoryV2`，不新造 learner。只新增一张资格卡/runner（若现有组件已经覆盖某项，使用既有回执而不重复实现）。

### 正例指标

至少一条 source+target canonical chain 必须 100% 从 ledger 重建 receipt：

- source/target event IDs、delivery/artifact/judgment/action/outcome digest、producer/version、candidate registry/menu、role/scope、assignment read cut、target decision/arrival index 和 exact delayed-credit digest 全部一致；
- `assignment → selection → task_start → target outcome → credit → history append` 顺序可 replay；replay 后 history state/projection digest 与原始 append 相等；
- duplicate feedback exactly-once，重复调用为 `NOOP`，不增加 entry/update；
- public projection 只含白名单聚合字段，不泄漏 raw artifact、prompt、gold、private scorer 或 target outcome 细节；
- 每格记录 valid/invalid/UNKNOWN 分母、snapshot/receipt bytes、wall time、API/GPU/token/tool/update 成本和 component hashes。

### 负例指标

逐格替换 source/target ID、artifact/offer/selection digest、candidate@version、read cut、role/scope、arrival order、delayed-credit lineage，并重复 append/replay。每格必须是 `UNKNOWN` 或 `NOOP`，selection/update/append 次数为 0；false accept=0。资源/进程失败保留 stderr/raw receipt，不转成 FAIL 标签。

## 通过后的顺序

仅当所有正例通过、所有负例 false accept=0 且跨进程 replay digest 一致，才进入：

1. 固定公共 `φ`、candidate menu、arrival schedule、propensity、state cap 和完整 cost schema；
2. 资格化七 arm same-information parity；
3. 再选择第二 root authority 并冻结 split；
4. 最后才运行有界真实 API。A800 仍需等真实训练瓶颈和方法 challenger 冻结。

## 明确禁止启动

在本门通过前，不启动正式效果流、第二 root live confirmation、same-information scientific comparison、A800、或任何用 UNKNOWN 补标签的实验；不修改 active benchmark/baseline 文档，不降低 Goal。

`goal_change_requested=false`。

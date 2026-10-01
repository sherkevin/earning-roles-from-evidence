# Baseline manifest hardening v2 — 2026-10-01

状态：`PARTIAL`
Goal 变更：无。这个结果只关闭离线 implementation-parity 子门，不冻结 benchmark/baseline。

## 证据边界

v14（commit `fc827ee8bd73d520218ec8ab3ac6939a8ba2cdbb`）和 v15（commit
`264cd6e2b6e2a97d4dfdabc18714c7dc378f5062`）是修复过程中的历史 receipt：它们分别缺少
新的回执字段，且 late-correction 的累计 public prefix 被记为 `n_duplicate=1`。两份
receipt 原样保留，不能支持当前 hardened 结论。

提交 `073708e` 后，v16 在 `experiments/logs/n03_policy_matrix_runner_20261001_v16/`
重新执行七个 hand-authored case，结果为 `QUALIFIED_OFFLINE`，0 API、0 GPU、
`scientific_claim_allowed=false`。config 在首个 case 之前封存了每 case manifest；每个
manifest 绑定 current source/generator/scorer identity、registry/schedule digest、逐 offer
RNG schedule digest、root seed membership、arm order、visibility rule 和预算。runner 还
拒绝 prefix 重排、重复反馈 ID 的内容漂移，并分别记录 selected×classification 交叉分母和
正常的 `n_revisible_prefix_rows`。

## 通过的内容

- 同一离线菜单、arrival schedule、policy arm 和 snapshot replay 的实现一致性；
- 公开反馈 prefix 的顺序、内容不可变性、selected-only/UNKNOWN 分类和 correction lineage；
- manifest 缺失、错误 hash、错误 schedule/RNG digest、非法预算以及 bypass 的拒绝路径。

## 没有通过或尚未开始的内容

manifest 中的 RNG digest 是逐 offer schedule 的封存，不等于由 root seed 推导随机数；
`root_seed` 也没有替代 live episode 计数。该 runner 仍使用 hand-authored offers，尚未
绑定 TeamBench generator、真实 neutral material、canonical ledger、独立 history、实际
成本、later assignment/outcome 或同信息 strong baseline。因此 v16 不能证明 benchmark
权威性、公平 scientific comparison、在线方法效果或 A800 必要性。

下一步是把同样的 manifest 语义接到 versioned PIPE3 canonical-ledger runner；在此之前不
启动正式 API/A800 效果流。

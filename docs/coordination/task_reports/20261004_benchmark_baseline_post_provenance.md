# Provenance 门之后的 benchmark/baseline gate 审计

日期：2026-10-04
状态：`NOT_READY`（科学比较仍未放行）

## 审计目的

把最新的 canonical history provenance v2 回执与现有 baseline matrix v16 对齐，判断我们是否已经有资格启动真实 baseline comparison。审计只读取既有配置、回执和 active benchmark/baseline 评价标准；不重跑 hand-authored matrix，不调用 API/GPU，不改变 active benchmark/baseline 文档。

## Gate 结果

| 门 | 状态 | 证据与边界 |
|---|---|---|
| canonical provenance | `PASS`（工程） | `6af20fb` 的 v2：valid ledger chain、8 类 mutation UNKNOWN/零 append、duplicate `NOOP`；仍是 pinned fixture，不是 live stream |
| 七 arm 离线实现 parity | `PASS`（工程） | `n03_policy_matrix_runner_20261001_v16`：7 hand-authored cases、同菜单/schedule/registry/RNG/snapshot checks；0 API/0 GPU |
| 公共 feature `φ` parity | `OPEN` | v16 仍使用 hand-authored feature/feedback rows，未把 canonical history projection 和 receipt read-cut 接入每个 arm |
| same-information scientific parity | `OPEN` | contextual trust、RARE、raw/terminal/pooled 尚无独立 live history、later-use 和完整 cost 的 paired cell |
| benchmark authority | `OPEN` | TeamBench-derived PeerRoleBench-TB 仍候选；第二 structural root/authority 和 confirmation split 未冻结 |
| closest published adapter | `OPEN/NO-GO` | Meta-Team L2-style 仍未完成 public adapter/成本/assignment qualification |
| 结果合理性 | `OPEN` | 没有 assignment-level future quality/regret、完整成本、UNKNOWN 分母和 95% interval 的科学结果 |

## 不能推出的结论

provenance 通过只说明 history 不容易与 source/target 责任链错绑；v16 通过只说明七个 policy 的离线状态机能在同一 hand-authored stream 上运行。两者都不能证明 RARE 胜过 contextual trust、history 改善团队质量、实时更新满足 p95、或 benchmark 已具备 AAMAS confirmation 证据。

## v19 完成与下一张卡（只冻结，不启动）

上一张 **canonical-PIPE3 public-input parity qualification** 已由 v19 完成；
下一张卡只做公开合同和对照资格收紧，再决定是否进入真实小流：

1. 增加正向 `raw_acceptance` 与 `terminal_only` source-adapter cells；
2. 对 registry 与 history projection 做独立 mutation/replay qualification；
3. 把 public φ exposure contract 与 per-arm state namespace 接入正式 baseline manifest；
4. 再考虑独立 API streams；不得用 matched replay 代替 live effect；
5. closest adapter、第二 root、confirmation、A800 仍在这些门通过后按顺序处理。

预注册通过指标：所有 arm 的公共输入 digest、candidate menu、read cut、arrival schedule、探索预算和成本 schema 一致；每个 arm 的 policy state digest 独立；任何 mutation/late/unknown cell 的 false accept=0；无质量/效果结论。

`goal_change_requested=false`。

## v19 amendment

`n03_canonical_pipe3_parity_20261004_v19` completed the next engineering card
with status `QUALIFIED_OFFLINE_PUBLIC_INPUT_PARITY`.  The canonical ledger,
`RoleEvidenceOffer`, delayed-credit history projection, menu, read cuts,
arrival schedule, public φ and per-arm state namespaces now have an auditable
zero-call path.  The v18 intermediate result is retained because its φ
accidentally included terminal quality/status for RARE while contextual trust
did not consume them; v19 excludes those fields.  This closes only the
public-input/schema sub-gate.  It does not close scientific same-information
parity: the valid cell contains one recipient-judgment row, so positive
raw-acceptance and terminal-only adapters remain open, as do registry/history
mutation qualification, benchmark authority, second root, independent live
history and assignment-level outcome evidence.

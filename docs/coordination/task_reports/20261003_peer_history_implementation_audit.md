# PeerHistoryV1 实现审计：可复用存储 seam，但尚不能支撑角色学习

日期：2026-10-03
状态：`BLOCKED_BY_EVIDENCE`（下一次 live runner 前必须补齐 lineage 与消费接缝）

## 任务与 Goal 对照

本审计检查上一任务新增的 `PeerHistoryV1` 是否真的实现了 Goal 要求的“他人的
situated judgment 形成可识别的角色证据，并在未来 assignment 中改变行为”。它不重跑
API/GPU，也不修改 active method、benchmark 或 Goal；目的是阻止把序列化/聚合资格
误报成角色学习机制。

## 代码证据

实现位于 `scripts/peerrolebench_peer_history.py`，v2 zero-call receipt 位于
`experiments/logs/n03_peer_history_qualification_20261003_v2/`。审查
重点是 `HistoryEntryV1`、`AssignmentSealV1.append()` 和 `selector_projection()`。

1. **它没有改变 producer 的执行能力。** 模块只追加 entry、计算
   `smoothed_rate/cost_mean` 并返回 opaque projection；没有 producer-side read hook、
   policy factory、update callback 或生成行为适配。它最多支持 selector reputation，
   不能单独支持“peer 已经变得更擅长该角色”的表述。
2. **source/target 绑定不完整。** entry 没有 source evidence/publication ID、recipient
   key、target episode ID、read-cut、assignment phase 或 independent later-outcome
   lineage。seal 只验证 subject/scope/arrival 顺序，因此一条记录可在没有证明
   `source → publish → future assignment → target outcome → delayed credit` 的情况下
   进入 history。
3. **terminal-only 记录可伪装成正向 history。** `PASS/FAIL` 只强制要求
   `later_outcome_label`，没有强制 `recipient_judgment_label` 非空；这允许没有 situated
   judgment 的终局标签贡献到 `smoothed_rate`。
4. **没有 mechanism-level falsifiability。** 没有 selector consumption、propensity、
   decision digest、history/no-history/shuffled/reset execution 或 update-latency
   receipt。离线 qualification 因而只能证明 append/replay，而不能证明 history
   改变了未来选择，更不能证明质量/成本收益。

## 结论

`PeerHistoryV1` 可以保留为 fail-closed 的存储/投影 seam，但当前状态不能进入正式
scientific cell，也不能支撑“自进化 peer”或“角色学习有效”的论文句子。它暴露的是
实现与证据边界，不是实验失败导致的 Goal 降级。

## 必须完成的最小修复

在下一次真实 runner 之前，需要一个 canonical-ledger-bound adapter，而不是继续扩展
聚合字段：

- entry 必须绑定 source publication、recipient judgment/action、target assignment、
  read-cut 与 later outcome 的不可变 ID 和 arrival 顺序；
- `PASS/FAIL` 必须同时有完整 recipient judgment，或明确降为 `UNKNOWN/no-update`；
- selector 必须实际消费 projection 并记录 decision/propensity/input digest，更新只能
  在 target outcome 到达后发生；
- 至少运行 history、no-history、history-shuffled、reset-history 四格，同一 public
  feature/cost/UNKNOWN 规则下比较未来 assignment、terminal quality、regret、成本和
  update latency；
- 如果论文要声称 producer execution capability 改善，另加 preregistered
  producer-read/adaptation arm；否则把 estimand 限定为 candidate suitability/assignment。

`goal_change_requested=false`。在这些 seam 修复前不启动新的 API episode，也不启动 A800。

## 本次跟进的最小硬化

为关闭其中一个可直接利用的漏洞，`PeerHistoryV1` 已版本化为
`peer-history-v2`：`PASS/FAIL` entry 现在同时要求非空
`recipient_judgment_label` 与 `later_outcome_label`；缺少 situated judgment 的终局行会
被拒绝。新增测试 6 项通过，`n03_peer_history_qualification_20261003_v3` 为
`QUALIFIED_OFFLINE`（5/5，0 API、0 GPU）。这只修复了 terminal-only 伪装，不代表
source/target lineage、selector consumption 或 history/no-history 科学矩阵已经完成。
